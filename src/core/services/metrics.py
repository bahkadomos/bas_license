from prometheus_client import Counter, Gauge, Histogram


OUTGOING_REQUEST_COUNT = Counter(
    "outgoing_http_requests_total",
    "Total number of outgoing HTTP requests",
    ["method", "endpoint", "status_code"]
)

OUTGOING_REQUEST_LATENCY = Histogram(
    "outgoing_http_request_latency_seconds",
    "Latency of outgoing HTTP requests",
    ["method", "endpoint"]
)

OUTGOING_REQUESTS_IN_PROGRESS = Gauge(
    "outgoing_http_requests_inprogress",
    "Number of outgoing HTTP requests in progress",
    ["method", "endpoint"]
)
