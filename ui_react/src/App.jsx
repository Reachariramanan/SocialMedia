import React, { useCallback, useState, useRef, useEffect } from 'react'
import NerveBar from './components/NerveBar'
import Canvas from './components/Canvas'
import CommandPalette from './components/CommandPalette'
import SettingsPanel from './components/SettingsPanel'
import useSnapshot from './hooks/useSnapshot'
import useAgentRun from './hooks/useAgentRun'
import useRuns from './hooks/useRuns'
import useDiscover from './hooks/useDiscover'
import useFeeds from './hooks/useFeeds'
import useXtraction from './hooks/useXtraction'
import useSystemStatus from './hooks/useSystemStatus'
import useCommandPalette from './hooks/useCommandPalette'
import useSchedules from './hooks/useSchedules'

export default function App() {
  const snap = useSnapshot()
  const runsHook = useRuns()
  const agentRun = useAgentRun(useCallback(() => runsHook.reload(), [runsHook.reload]))
  const discover = useDiscover()
  const feeds = useFeeds()
  const xtraction = useXtraction()
  const systemStatus = useSystemStatus()
  const schedules = useSchedules()

  // Left pane mode: 'reports' | 'discover' | 'schedules'
  const [mode, setMode] = useState('reports')
  // Active query shown in discover panel header
  const [activeQuery, setActiveQuery] = useState('')

  // Settings panel
  const [settingsOpen, setSettingsOpen] = useState(false)
  // Active report skill — persisted to localStorage so it survives page refresh
  const [activeSkill, setActiveSkill] = useState(
    () => localStorage.getItem('z-report-skill') || 'html_report_writer'
  )
  const handleSkillChange = (skillId) => {
    setActiveSkill(skillId)
    localStorage.setItem('z-report-skill', skillId)
  }

  // Apply persisted theme on first mount
  useEffect(() => {
    const saved = localStorage.getItem('z-theme') || 'z'
    document.documentElement.setAttribute('data-theme', saved)
  }, [])

  // When a tag is clicked from signal stream or timeline:
  // switch to discover mode and search all 3 sources simultaneously
  const handleTagClick = useCallback((tag) => {
    const query = tag.startsWith('#') ? tag : `#${tag}`
    setActiveQuery(query)
    setMode('discover')

    // Search RSS + Google News (feeds)
    feeds.setInput(query)
    feeds.doFetch(query)

    // Search SearXNG + discover URLs
    discover.setInput(query)
    discover.doDiscover(query)
  }, [feeds, discover])

  const palette = useCommandPalette({
    runs: runsHook.runs,
    onLocationSelect: snap.loadLocation,
    onStartRun: () => {},
    onDiscoverOpen: () => setMode('discover'),
    onFeedsOpen: () => setMode('discover'),
  })

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <NerveBar
        location={
          snap.location
            ? `${snap.location.city ? snap.location.city + ', ' : ''}${snap.location.country}`
            : (snap.snapshot?.location || 'Worldwide')
        }
        lastRefresh={snap.lastRefresh}
        onRefresh={snap.refresh}
        loading={snap.loading}
        onOpenPalette={palette.toggle}
        systemHealth={systemStatus}
        onOpenSettings={() => setSettingsOpen(p => !p)}
        settingsOpen={settingsOpen}
      />
      <Canvas
        mode={mode}
        setMode={setMode}
        snapshot={snap.snapshot}
        snapshotLoading={snap.loading}
        runs={runsHook.runs}
        selectedRun={runsHook.selected}
        html={runsHook.html}
        runHistory={runsHook.history}
        onSelectRun={runsHook.selectRun}
        onDeleteRun={runsHook.remove}
        reloadRuns={runsHook.reload}
        runsLoading={runsHook.loading}
        agentRun={agentRun}
        activeSkill={activeSkill}
        discover={discover}
        feeds={feeds}
        xtraction={xtraction}
        systemStatus={systemStatus}
        onTagClick={handleTagClick}
        activeQuery={activeQuery}
        schedules={schedules}
      />
      <CommandPalette
        isOpen={palette.isOpen}
        search={palette.search}
        setSearch={palette.setSearch}
        close={palette.close}
        filteredLocations={palette.filteredLocations}
        filteredRuns={palette.filteredRuns}
        actions={palette.actions}
        selectLocation={palette.selectLocation}
        onSelectRun={runsHook.selectRun}
      />
      {settingsOpen && (
        <SettingsPanel
          onClose={() => setSettingsOpen(false)}
          activeSkill={activeSkill}
          onSkillChange={handleSkillChange}
        />
      )}
    </div>
  )
}
