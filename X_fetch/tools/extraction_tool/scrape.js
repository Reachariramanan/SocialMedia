// popup.js

let scrapedPosts = [];
let savedPosts = [];
let currentTab = "scraped";

// ── Init ──
document.addEventListener("DOMContentLoaded", async () => {
  await loadSaved();
  updateSavedCount();
  setupTabs();
  setupButtons();
});

// ── Tab logic ──
function setupTabs() {
  document.querySelectorAll(".tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      currentTab = tab.dataset.tab;
      if (currentTab === "scraped") renderScraped();
      else renderSaved();
    });
  });
}

// ── Buttons ──
function setupButtons() {
  document.getElementById("btn-scrape").addEventListener("click", doScrape);
  document.getElementById("btn-save-all").addEventListener("click", saveAllScraped);
  document.getElementById("btn-export-json").addEventListener("click", exportJSON);
  document.getElementById("btn-export-csv").addEventListener("click", exportCSV);
  document.getElementById("btn-clear").addEventListener("click", clearSaved);
  document.getElementById("btn-open-x").addEventListener("click", () => {
    chrome.tabs.create({ url: "https://x.com" });
  });
}

// ── Scrape ──
async function doScrape() {
  setStatus("loading", "⟳ Scraping posts from page...");

  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  if (!tab || (!tab.url.includes("x.com") && !tab.url.includes("twitter.com"))) {
    setStatus("error", "⚠ Not on X/Twitter. Please open x.com first.");
    return;
  }

  try {
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: scrapePostsFromPage
    });

    const posts = results?.[0]?.result || [];

    if (!posts.length) {
      setStatus("error", "✗ No posts found. Try scrolling and try again.");
      renderEmpty("No posts detected. Try scrolling and scraping again.");
      return;
    }

    scrapedPosts = posts;
    setStatus("ok", `✓ Found ${scrapedPosts.length} post${scrapedPosts.length > 1 ? "s" : ""} on page.`);
    currentTab = "scraped";
    document.querySelectorAll(".tab").forEach(t => {
      t.classList.toggle("active", t.dataset.tab === "scraped");
    });
    renderScraped();

  } catch (e) {
    setStatus("error", "✗ " + e.message);
  }
}

// ── This function runs INSIDE the X page tab ──
function scrapePostsFromPage() {
  const results = [];
  const seenIds = new Set();
  const articles = document.querySelectorAll('article[data-testid="tweet"]');

  articles.forEach((article) => {
    try {

      // ── author username ──
      let username = "";
      let authorHref = "";
      article.querySelectorAll('[data-testid="User-Name"] a[href*="/"]').forEach(el => {
        const href = el.getAttribute("href") || "";
        if (href.startsWith("/") && !href.includes("/status/") && !href.includes("/i/")) {
          username = href.replace("/", "");
          authorHref = href;
        }
      });

      // ── author display name ──
      const nameEl = article.querySelector('[data-testid="User-Name"] span span');
      const name = nameEl ? nameEl.innerText.trim() : "";

      // ── author id ──
      let author_id = "";
      const uidLink = article.querySelector('a[href*="/i/user/"]');
      if (uidLink) {
        const m = uidLink.getAttribute("href").match(/\/i\/user\/(\d+)/);
        if (m) author_id = m[1];
      }

      // ── verified ──
      const verified = !!article.querySelector('[data-testid="icon-verified"]') ||
                       !!article.querySelector('svg[data-testid="verifiedIcon"]');

      // ── profile image ──
      let profile_image_url = "";
      const imgEl = article.querySelector('[data-testid="Tweet-User-Avatar"] img');
      if (imgEl) profile_image_url = imgEl.getAttribute("src") || "";

      // ── tweet id & url ──
      let id = "";
      let postUrl = "";
      article.querySelectorAll('a[href*="/status/"]').forEach(el => {
        const href = el.getAttribute("href") || "";
        if (href.includes("/status/")) postUrl = "https://x.com" + href;
      });
      const idMatch = postUrl.match(/\/status\/(\d+)/);
      if (idMatch) id = idMatch[1];

      // skip duplicates
      if (id && seenIds.has(id)) return;
      if (id) seenIds.add(id);

      // ── full tweet text ──
      let text = "";
      const textEl = article.querySelector('[data-testid="tweetText"]');
      if (textEl) {
        const parts = [];
        const walk = (node) => {
          if (node.nodeType === 3) {
            parts.push(node.textContent);
          } else if (node.tagName === "IMG") {
            parts.push(node.getAttribute("alt") || "");
          } else if (node.tagName === "A") {
            const expanded = node.getAttribute("data-expanded-url");
            if (expanded) { parts.push(expanded); }
            else { node.childNodes.forEach(walk); }
          } else {
            node.childNodes.forEach(walk);
          }
        };
        textEl.childNodes.forEach(walk);
        text = parts.join("").trim();
        if (!text) text = textEl.innerText.trim();
      }

      // ── lang ──
      const lang = textEl ? (textEl.getAttribute("lang") || "") : "";

      // ── createdAt + horse (human-readable time ago e.g. "7h", "2d") ──
      const timeEl = article.querySelector("time");
      const created_at = timeEl ? timeEl.getAttribute("datetime") : "";
      const horse = timeEl ? timeEl.innerText.trim() : "";

      // ── source ──
      const sourceEl = article.querySelector('[data-testid="source-label"] a');
      const source = sourceEl ? sourceEl.innerText.trim() : "Twitter Web App";

      // ── possibly_sensitive ──
      const possibly_sensitive = !!article.querySelector('[data-testid="sensitive-media-warning"]');

      // ── entities with character positions ──
      const hashtags = [];
      const mentions = [];
      const urls = [];

      if (textEl) {
        textEl.querySelectorAll("a").forEach(a => {
          const href = a.getAttribute("href") || "";
          const expanded = a.getAttribute("data-expanded-url") || "";
          const linkText = a.innerText.trim();

          // Find position in full text
          const start = text.indexOf(linkText);
          const end = start + linkText.length;

          if (href.startsWith("/hashtag/")) {
            hashtags.push({
              start: start >= 0 ? start : 0,
              end: end >= 0 ? end : 0,
              tag: linkText.replace("#", "").trim()
            });
          } else if (href.startsWith("/") && !href.includes("/status/") && !href.startsWith("/hashtag/") && !href.startsWith("/i/")) {
            mentions.push({
              start: start >= 0 ? start : 0,
              end: end >= 0 ? end : 0,
              username: href.replace("/", ""),
              id: ""
            });
          } else if (href.startsWith("http") || expanded) {
            urls.push({
              start: start >= 0 ? start : 0,
              end: end >= 0 ? end : 0,
              url: href,
              expanded_url: expanded || href,
              display_url: linkText
            });
          }
        });
      }

      // ── public_metrics ──
      const replyEl   = article.querySelector('[data-testid="reply"] span[data-testid="app-text-transition-container"]');
      const retweetEl = article.querySelector('[data-testid="retweet"] span[data-testid="app-text-transition-container"]');
      const likeEl    = article.querySelector('[data-testid="like"] span[data-testid="app-text-transition-container"]');
      const bookmarkEl = article.querySelector('[data-testid="bookmark"] span[data-testid="app-text-transition-container"]');

      const toNum = el => {
        if (!el) return 0;
        const t = el.innerText.trim().replace(/,/g, "");
        if (t.endsWith("K")) return Math.round(parseFloat(t) * 1000);
        if (t.endsWith("M")) return Math.round(parseFloat(t) * 1000000);
        return parseInt(t) || 0;
      };

      // ── attachments ──
      const media_keys = [];
      const poll_ids = [];
      const photoEls = article.querySelectorAll('[data-testid="tweetPhoto"]');
      const videoEls = article.querySelectorAll('[data-testid="videoComponent"]');
      photoEls.forEach((_, i) => media_keys.push(`photo_${id}_${i}`));
      videoEls.forEach((_, i) => media_keys.push(`video_${id}_${i}`));
      const pollEl = article.querySelector('[data-testid="cardPoll"]');
      if (pollEl) poll_ids.push(`poll_${id}`);

      // ── referenced_tweets ──
      const referenced_tweets = [];
      const quotedLink = article.querySelector('[data-testid="quoteTweet"] a[href*="/status/"]');
      if (quotedLink) {
        const qm = quotedLink.getAttribute("href").match(/\/status\/(\d+)/);
        if (qm) referenced_tweets.push({ type: "quoted", id: qm[1] });
      }
      const replyBanner = article.querySelector('[data-testid="reply"]');
      const replyingTo = article.querySelector('a[href*="/status/"][role="link"]');
      if (replyingTo && replyingTo !== quotedLink) {
        const rm = replyingTo.getAttribute("href").match(/\/status\/(\d+)/);
        if (rm && rm[1] !== id) referenced_tweets.push({ type: "replied_to", id: rm[1] });
      }
      const rtText = text.startsWith("RT @");
      if (rtText) referenced_tweets.push({ type: "retweeted", id: "" });

      // ── reply_settings ──
      const reply_settings = "everyone";

      // ── edit_history_tweet_ids ──
      const edit_history_tweet_ids = id ? [id] : [];

      // ── isAd (metadata only) ──
      const isAd = !!article.querySelector('[data-testid="placementTracking"]') ||
                   !!article.querySelector('div[aria-label="Ad"]');

      if (text || username) {
        results.push({
          id,
          text,
          author_id,
          created_at,
          conversation_id: id,
          lang,
          possibly_sensitive,
          source,
          author: {
            id: author_id,
            name,
            username,
            horse,
            verified,
            profile_image_url
          },
          entities: {
            hashtags,
            urls,
            mentions,
            annotations: []
          },
          public_metrics: {
            retweet_count:    toNum(retweetEl),
            reply_count:      toNum(replyEl),
            like_count:       toNum(likeEl),
            quote_count:      0,
            impression_count: 0,
            bookmark_count:   toNum(bookmarkEl)
          },
          referenced_tweets,
          attachments: {
            media_keys,
            poll_ids
          },
          geo: {},
          context_annotations: [],
          reply_settings,
          edit_history_tweet_ids,
          _meta: {
            post_url:   postUrl,
            scraped_at: new Date().toISOString(),
            page_url:   window.location.href,
            is_ad:      isAd
          }
        });
      }
    } catch (e) { /* skip broken post */ }
  });

  return results;
}

// ── Render saved posts ──
// ── Render scraped posts ──
function renderScraped() {
  const list = document.getElementById("post-list");

  if (!scrapedPosts.length) {
    renderEmpty("No posts scraped yet. Click Scrape Page.");
    return;
  }

  list.innerHTML = `<div class="section-header">— ${scrapedPosts.length} posts found —</div>`;
  scrapedPosts.forEach((post, i) => {
    const isAlreadySaved = savedPosts.some(s => s.id && s.id === post.id);
    list.appendChild(buildCard(post, i, isAlreadySaved, "scraped"));
  });
}

function renderSaved() {
  const list = document.getElementById("post-list");

  if (!savedPosts.length) {
    renderEmpty("No posts saved yet. Scrape and click Save.");
    return;
  }

  list.innerHTML = `<div class="section-header">— ${savedPosts.length} saved posts —</div>`;
  savedPosts.slice().reverse().forEach((post, i) => {
    list.appendChild(buildCard(post, i, true, "saved"));
  });
}

// ── Build a post card ──
function buildCard(post, index, isSaved, source) {
  const card = document.createElement("div");
  card.className = "post-card" + (isSaved ? " selected" : "");

  const timeStr = post.created_at
    ? new Date(post.created_at).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" })
    : "—";

  const tags = [];
  if (post._meta?.is_ad) tags.push('<span class="tag tag-ad">Ad</span>');
  if (post.attachments?.media_keys?.some(k => k.startsWith("photo"))) tags.push('<span class="tag tag-img">📷 Img</span>');
  if (post.attachments?.media_keys?.some(k => k.startsWith("video"))) tags.push('<span class="tag tag-vid">▶ Vid</span>');
  if (post.author?.verified) tags.push('<span class="tag" style="background:rgba(29,155,240,0.15);color:#1d9bf0;border:1px solid rgba(29,155,240,0.3)">✓ Verified</span>');

  const profileImg = post.author?.profile_image_url
    ? `<img src="${post.author.profile_image_url}" style="width:22px;height:22px;border-radius:50%;object-fit:cover;flex-shrink:0;" onerror="this.style.display='none'">`
    : "";

  card.innerHTML = `
    <span class="post-num">#${index + 1}</span>
    <div class="post-meta">
      <div class="post-author" style="display:flex;align-items:center;gap:6px;">
        ${profileImg}
        <span class="post-name">${escHtml(post.author?.name || "Unknown")}</span>
        <span class="post-handle">@${escHtml(post.author?.username || "")}</span>
      </div>
      <span class="post-time">${timeStr}</span>
    </div>
    <div class="post-text">${escHtml(post.text || "(no text)")}</div>
    <div class="post-footer">
      <div class="post-stats">
        <span class="post-stat">💬 ${post.public_metrics?.reply_count || 0}</span>
        <span class="post-stat">🔁 ${post.public_metrics?.retweet_count || 0}</span>
        <span class="post-stat">❤ ${post.public_metrics?.like_count || 0}</span>
        <span class="post-stat">🔖 ${post.public_metrics?.bookmark_count || 0}</span>
      </div>
      <div class="post-tags">${tags.join("")}</div>
    </div>
  `;

  // Click = save individual post
  card.addEventListener("click", () => {
    if (source === "scraped") {
      savePost(post);
      card.classList.add("selected");
      setStatus("ok", `✓ Saved: ${post.author?.name || post.author?.username}`);
    } else {
      // On saved tab, click opens the post URL
      if (post._meta?.post_url) chrome.tabs.create({ url: post._meta.post_url });
    }
  });

  return card;
}

function renderEmpty(msg) {
  document.getElementById("post-list").innerHTML = `
    <div class="empty-state">
      <div class="icon">📋</div>
      <p>${msg}</p>
    </div>`;
}

// ── Save logic ──
function savePost(post) {
  // Avoid duplicate by postId
  if (post.id && savedPosts.some(s => s.id === post.id)) return;
  savedPosts.push({ ...post, savedAt: new Date().toISOString() });
  persistSaved();
  updateSavedCount();
}

function saveAllScraped() {
  let added = 0;
  scrapedPosts.forEach(p => {
    if (!p.id || !savedPosts.some(s => s.id === p.id)) {
      savedPosts.push({ ...p, savedAt: new Date().toISOString() });
      added++;
    }
  });
  persistSaved();
  updateSavedCount();
  renderScraped();
  setStatus("ok", `✓ Saved ${added} new posts. Total: ${savedPosts.length}`);

  const btn = document.getElementById("btn-save-all");
  btn.classList.add("success-flash");
  btn.textContent = "✓ Saved!";
  setTimeout(() => {
    btn.classList.remove("success-flash");
    btn.textContent = "💾 Save All";
  }, 1500);
}

async function loadSaved() {
  const result = await chrome.storage.local.get("savedPosts");
  savedPosts = result.savedPosts || [];
}

function persistSaved() {
  chrome.storage.local.set({ savedPosts });
}

function clearSaved() {
  if (!confirm(`Delete all ${savedPosts.length} saved posts?`)) return;
  savedPosts = [];
  persistSaved();
  updateSavedCount();
  if (currentTab === "saved") renderSaved();
  setStatus("ok", "✓ Cleared all saved posts.");
}

function updateSavedCount() {
  document.getElementById("saved-count").textContent = savedPosts.length + " saved";
  document.getElementById("saved-tab-count").textContent = savedPosts.length;
}

// ── Export JSON ──
function exportJSON() {
  if (!savedPosts.length) { setStatus("error", "No saved posts to export."); return; }
  const blob = new Blob([JSON.stringify(savedPosts, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `x-posts-${datestamp()}.json`;
  a.click();
  URL.revokeObjectURL(url);
  setStatus("ok", `✓ Exported ${savedPosts.length} posts as JSON.`);
}

// ── Export CSV ──
function exportCSV() {
  if (!savedPosts.length) { setStatus("error", "No saved posts to export."); return; }

  const headers = ["#","id","author_name","author_username","author_id","verified","text","created_at","lang","source","post_url","reply_count","retweet_count","like_count","bookmark_count","hashtags","mentions","urls","media","is_ad","possibly_sensitive","conversation_id","scraped_at"];
  const rows = savedPosts.map((p, i) => [
    i + 1,
    p.id || "",
    `"${(p.author?.name || "").replace(/"/g, '""')}"`  ,
    p.author?.username || "",
    p.author_id || "",
    p.author?.verified ? "Yes" : "No",
    `"${(p.text || "").replace(/"/g, '""')}"`  ,
    p.created_at || "",
    p.lang || "",
    p.source || "",
    p._meta?.post_url || "",
    p.public_metrics?.reply_count || 0,
    p.public_metrics?.retweet_count || 0,
    p.public_metrics?.like_count || 0,
    p.public_metrics?.bookmark_count || 0,
    `"${(p.entities?.hashtags || []).map(h => "#"+h.tag).join(" ")}"`,
    `"${(p.entities?.mentions || []).map(m => "@"+m.username).join(" ")}"`,
    `"${(p.entities?.urls || []).map(u => u.expanded_url).join(" ")}"`,
    `"${(p.attachments?.media_keys || []).join(" ")}"`,
    p._meta?.is_ad ? "Yes" : "No",
    p.possibly_sensitive ? "Yes" : "No",
    p.conversation_id || "",
    p._meta?.scraped_at || ""
  ]);

  const csv = [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `x-posts-${datestamp()}.csv`;
  a.click();
  URL.revokeObjectURL(url);
  setStatus("ok", `✓ Exported ${savedPosts.length} posts as CSV.`);
}

// ── Helpers ──
function setStatus(type, msg) {
  const el = document.getElementById("status");
  el.className = type;
  el.textContent = msg;
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function datestamp() {
  return new Date().toISOString().slice(0, 16).replace("T", "_").replace(":", "-");
}
