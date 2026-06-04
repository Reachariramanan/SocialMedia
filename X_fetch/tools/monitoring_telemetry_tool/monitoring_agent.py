from prometheus_client import start_http_server, Counter, Gauge, Histogram
import time
from core.config.settings import settings
from core.utils.common import setup_logging

logger = setup_logging("MonitoringAgent")

class MonitoringAgent:
    def __init__(self):
        # Define Prometheus metrics
        self.request_count = Counter('x_intel_requests_total', 'Total requests made', ['agent', 'status'])
        self.queue_lag = Gauge('x_intel_queue_lag', 'Current queue lag', ['topic'])
        self.processing_time = Histogram('x_intel_processing_seconds', 'Time spent processing a tweet')

    def start_monitoring_server(self):
        logger.info(f"Starting Prometheus server on port {settings.PROMETHEUS_PORT}")
        start_http_server(settings.PROMETHEUS_PORT)

    def record_request(self, agent: str, status: str):
        self.request_count.labels(agent=agent, status=status).inc()

    def update_queue_lag(self, topic: str, count: int):
        self.queue_lag.labels(topic=topic).set(count)

    def track_processing_time(self):
        return self.processing_time.time()
