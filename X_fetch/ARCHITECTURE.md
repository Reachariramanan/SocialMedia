# Distributed X/Twitter Intelligence Ingestion System Architecture

## 1. Introduction

This document outlines the architecture for a production-grade distributed X/Twitter intelligence ingestion system. The system is designed to indirectly discover public X/Twitter posts, minimize direct interaction with X, fetch high-value tweet URLs, and extract structured tweet data from GraphQL responses. It emphasizes horizontal scalability, resilience, maintainability, and modularity.

## 2. System Goals

The primary goals of this system are:

1.  Discover public X/Twitter posts indirectly through search engines and feeds.
2.  Minimize direct interaction with X.
3.  Fetch only high-value tweet URLs.
4.  Extract structured tweet data from GraphQL responses instead of DOM scraping.
5.  Scale horizontally.
6.  Resist frontend breakages.
7.  Maintain modular architecture.
8.  Support async distributed crawling.
9.  Support future LLM/RAG indexing.
10. Operate as an OSINT-style ingestion pipeline.

## 3. High-Level Architecture

The system will be composed of the following distributed agents:

| Agent Name                     | Primary Function                                                                  |
| :----------------------------- | :-------------------------------------------------------------------------------- |
| Discovery Agent                | Identifies potential tweet URLs using advanced SearXNG patterns and temporal slicing.        |
| Feed Expansion Agent           | (To be defined later, if needed for expanding discovered feeds)                   |
| URL Prioritization Agent       | Scores and prioritizes discovered URLs based on various metrics.                  |
| Browser Fetch Agent            | Renders web pages using headless browsers (Lightpanda) and routes traffic through Tor.          |
| GraphQL Interception Agent     | Captures and processes GraphQL requests and responses for data extraction.        |
| Session + Identity Agent       | Manages Tor proxy rotation, cookies, and browser fingerprints for anti-bot evasion.          |
| Extraction + Normalization Agent | Parses raw GraphQL data into a standardized tweet schema.                         |
| Deduplication Agent            | Ensures uniqueness of ingested tweets and handles incremental updates.            |
| Persistence Agent              | Stores normalized tweet data and raw payloads into appropriate storage systems.   |
| Monitoring + Telemetry Agent   | Collects metrics, logs, and traces for system observability.                      |

## 4. Technology Stack

The system will leverage the following technologies:

*   **Programming Language:** Python (with `asyncio`)
    *   **Web Crawling:** Scrapy (for orchestration), Lightpanda, Playwright, Tor (for proxy rotation)
*   **Search Engines Integration:** SearXNG (Official Metasearch Engine), Google Search, Bing, Brave Search, DuckDuckGo, Qwant, Google News RSS
*   **Queueing:** Redis Streams / Kafka
*   **Databases:** PostgreSQL (for structured data), ElasticSearch/OpenSearch (for search)
*   **Object Storage:** S3 / MinIO (for raw payload archival)
*   **Containerization:** Docker
*   **Orchestration:** Kubernetes
*   **API Framework:** FastAPI
*   **Observability:** Prometheus, Grafana, OpenTelemetry

## 5. Folder Structure

The project will adopt a modular folder structure to ensure maintainability and scalability. The top-level directory will be `x_intelligence_system`.

```
x_intelligence_system/
├── agents/
│   ├── discovery_agent/
│   ├── feed_expansion_agent/
│   ├── url_prioritization_agent/
│   ├── browser_fetch_agent/
│   ├── graphql_interception_agent/
│   ├── session_identity_agent/
│   ├── extraction_normalization_agent/
│   ├── deduplication_agent/
│   ├── persistence_agent/
│   └── monitoring_telemetry_agent/
├── core/
│   ├── models/
│   ├── config/
│   └── utils/
├── infrastructure/
│   ├── docker-compose/
│   ├── kubernetes/
│   ├── postgres/
│   ├── elasticsearch/
│   └── searxng/
├── tests/
├── docs/
├── scripts/
├── .env.example
├── README.md
├── requirements.txt
└── main.py
```

### Folder Descriptions:

*   `agents/`: Contains the implementation for each distributed agent.
*   `core/`: Houses shared components like data models, configuration, and utility functions.
*   `infrastructure/`: Stores deployment configurations for Docker, Kubernetes, and database schemas.
*   `tests/`: Contains unit and integration tests.
*   `docs/`: Documentation files.
*   `scripts/`: Helper scripts for development, deployment, or data migration.
*   `.env.example`: Example environment variables file.
*   `README.md`: Project README.
*   `requirements.txt`: Python dependencies.
*   `main.py`: Main entry point for the application or a coordinator service.
