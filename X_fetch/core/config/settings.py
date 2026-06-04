import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    
    # PostgreSQL
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "postgresql://user:password@localhost:5432/x_intel")
    
    # ElasticSearch
    ELASTICSEARCH_URL: str = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    
    # SearXNG
    SEARXNG_URL: str = os.getenv("SEARXNG_URL", "http://localhost:8888")
    
    # Proxies
    RESIDENTIAL_PROXY_URL: str = os.getenv("RESIDENTIAL_PROXY_URL", "")
    TOR_HTTP_PROXY: str = os.getenv("TOR_HTTP_PROXY", "http://localhost:8118")
    TOR_SOCKS_PROXY: str = os.getenv("TOR_SOCKS_PROXY", "socks5://localhost:9050")
    TOR_CONTROL_PORT: int = int(os.getenv("TOR_CONTROL_PORT", 9051))
    
    # Lightpanda
    LIGHTPANDA_CDP_URL: str = os.getenv("LIGHTPANDA_CDP_URL", "ws://localhost:9222")

    # Monitoring
    PROMETHEUS_PORT: int = int(os.getenv("PROMETHEUS_PORT", 8000))

settings = Settings()
