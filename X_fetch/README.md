# Distributed X/Twitter Intelligence Ingestion System

## Overview

This project implements a production-grade distributed system for ingesting X/Twitter intelligence. It focuses on indirect discovery of public X/Twitter posts, minimizing direct interaction with the platform, and extracting structured tweet data via GraphQL interception rather than DOM scraping. The system is designed for horizontal scalability, resilience, and maintainability, operating as an OSINT-style ingestion pipeline.

## Key Features

*   **Indirect Discovery:** Utilizes advanced SearXNG query patterns, temporal slicing, and multiple search engines (Google, Bing, Brave, DuckDuckGo, Qwant) to discover tweet URLs.
*   **High-Value Fetching:** Prioritizes tweet URLs based on various metrics like keyword density, influencer score, and recency.
*   **GraphQL Interception:** Extracts structured tweet data directly from GraphQL responses, enhancing robustness against frontend changes.
*   **Distributed Architecture:** Composed of multiple specialized agents for discovery, fetching, interception, session management, extraction, deduplication, persistence, and monitoring, with enhanced anonymity via Tor and performance with Lightpanda.
*   **Anti-Bot Evasion:** Incorporates Tor proxy rotation, browser fingerprint randomization, and adaptive throttling to avoid detection.
*   **Scalability:** Designed for horizontal scaling with Docker and Kubernetes, supporting distributed Scrapy workers and autoscaling browser agents.
*   **Observability:** Integrated with Prometheus, Grafana, and OpenTelemetry for comprehensive monitoring and telemetry.

## High-Level Architecture

The system is built around a set of distributed agents communicating via a queueing system (Redis Streams or Kafka). The overall flow involves discovering potential tweet URLs, prioritizing them, fetching them using headless browsers with network interception, extracting GraphQL data, normalizing it, deduplicating, and finally persisting it to various storage solutions.

For a detailed architectural breakdown, refer to [ARCHITECTURE.md](ARCHITECTURE.md).

## Technology Stack

*   **Programming Language:** Python (with `asyncio`)
*   **Web Crawling:** Scrapy (orchestration), Lightpanda, Playwright, Tor (for proxy rotation)
*   **Search Engines Integration:** SearXNG (Official Metasearch Engine), Google Search, Bing, Brave Search, DuckDuckGo, Qwant, Google News RSS
*   **Queueing:** Redis Streams / Kafka
*   **Databases:** PostgreSQL (structured data), ElasticSearch/OpenSearch (search)
*   **Object Storage:** S3 / MinIO (raw payload archival)
*   **Containerization:** Docker
*   **Orchestration:** Kubernetes
*   **API Framework:** FastAPI
*   **Observability:** Prometheus, Grafana, OpenTelemetry

## Folder Structure

```
x_intelligence_system/
├── agents/                  # Implementations of distributed agents
├── core/                    # Shared models, configuration, and utilities
├── infrastructure/          # Docker, Kubernetes, and database configurations
├── tests/                   # Unit and integration tests
├── docs/                    # Project documentation
├── scripts/                 # Helper scripts
├── .env.example             # Example environment variables
├── README.md                # Project README
├── requirements.txt         # Python dependencies
└── main.py                  # Main entry point
```

## Setup and Installation

### Prerequisites

*   Docker and Docker Compose
*   Python 3.9+
*   `uv` (or `pip`) for Python dependency management

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/x_intelligence_system.git
cd x_intelligence_system
```

### 2. Environment Variables

Create a `.env` file based on `.env.example` and fill in your configurations.

```bash
cp .env.example .env
# Edit .env with your specific settings (e.g., proxy URLs, Kafka servers)
```

### 3. Install Python Dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Docker Compose Setup (Local Development)

For local development and testing, you can spin up core services using Docker Compose:

```bash
docker-compose -f infrastructure/docker-compose/docker-compose.yml up -d
```

This will start Redis, PostgreSQL, Elasticsearch, SearXNG, Tor proxy, and Lightpanda browser.

### 5. Initialize Databases

*   **PostgreSQL:** The `schema.sql` will be automatically applied on first startup via Docker Compose.
*   **Elasticsearch:** You may need to manually create the index using the `index_schema.json`:

    ```bash
    curl -X PUT "localhost:9200/tweets?pretty" -H 'Content-Type: application/json' -d @infrastructure/elasticsearch/index_schema.json
    ```

## Running the System

The system is designed to run as a collection of independent agents. You can run them individually or orchestrate them via Kubernetes.

### Running Agents Locally

Each agent can be started as a separate Python process. For example:

```bash
python main.py --agent discovery
python main.py --agent browser_fetch
# ... and so on for other agents
```

*(Note: `main.py` and agent specific entry points are placeholders and need to be fully implemented.)*

### Scrapy Orchestration

To run the Scrapy spider (which acts as an orchestrator):

```bash
scrapy crawl x_intelligence_spider
```

This assumes Redis is running and accessible as configured in `scrapy_orchestrator.py`.

### Kubernetes Deployment

Refer to the `infrastructure/kubernetes/` directory for example deployment configurations. You will need a Kubernetes cluster configured and `kubectl` installed.

```bash
kubectl apply -f infrastructure/kubernetes/deployment.yaml
```

## Monitoring and Telemetry

Access Prometheus metrics at `http://localhost:PROMETHEUS_PORT` (default 8000) after starting the `MonitoringAgent`.

Integrate with Grafana for dashboards and alerts.

## Production Hardening

Before deploying to production, review and implement the recommendations in [PRODUCTION_HARDENING.md](PRODUCTION_HARDENING.md).

## Contributing

Contributions are welcome! Please refer to `CONTRIBUTING.md` (to be created) for guidelines.

## License

This project is licensed under the MIT License. See the `LICENSE` file (to be created) for details.
