import os
import time
import redis
from flask import Flask, jsonify, request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest

app = Flask(__name__)

ALERT_THRESHOLD = 25


def alert_threshold():
    """Seuil d'alerte au-dessus duquel une notification est declenchee."""
    return ALERT_THRESHOLD


def sanitize_input(value):
    """Echappe les caracteres dangereux d'une entree utilisateur."""
    return value.replace("<", "&lt;").replace(">", "&gt;")


@app.route("/health")
def health():
    return jsonify(status="ok"), 200


@app.route("/status")
def status():
    return jsonify(service="projet-devops-groupe-demo", version="1.0"), 200


r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=6379,
    decode_responses=True
)


@app.route("/visite")
def visite():
    nb = r.incr("visites")
    return jsonify(visites=nb), 200


REQUESTS = Counter("http_requests_total", "Total", ["endpoint", "code"])
LATENCY = Histogram("http_request_duration_seconds", "Latence", ["endpoint"])
VERSION = Gauge("app_version_info", "Version", ["version"])
VERSION.labels(version="1.0").set(1)


@app.before_request
def start_timer():
    request.start_time = time.time()


@app.after_request
def log_metrics(response):
    if hasattr(request, "start_time"):
        LATENCY.labels(endpoint=request.path).observe(time.time() - request.start_time)
    REQUESTS.labels(endpoint=request.path, code=response.status_code).inc()
    return response


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
