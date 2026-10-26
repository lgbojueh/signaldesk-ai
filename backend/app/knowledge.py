KNOWLEDGE_BASE = [
    {
        "id": "KB-001",
        "title": "Docker service-to-service database connectivity",
        "tags": ["docker", "postgres", "database", "connection refused", "network"],
        "body": (
            "Inside Docker Compose, containers should connect using the service name instead of localhost. "
            "Verify that both services share a network, confirm the database port is listening, and check startup order. "
            "Use docker compose logs and an in-container connectivity check before changing application code."
        ),
    },
    {
        "id": "KB-002",
        "title": "DNS and name-resolution troubleshooting",
        "tags": ["dns", "hostname", "network", "resolution", "timeout"],
        "body": (
            "Confirm the hostname resolves to the expected address. Compare DNS results from the affected environment, "
            "check local resolver configuration, and separate name-resolution failures from transport failures."
        ),
    },
    {
        "id": "KB-003",
        "title": "HTTP 401 and authentication failures",
        "tags": ["401", "authentication", "token", "jwt", "session", "authorization"],
        "body": (
            "For 401 errors, verify credential presence, token expiration, issuer/audience expectations, clock skew, "
            "and whether the client is sending the Authorization header on the failing request."
        ),
    },
    {
        "id": "KB-004",
        "title": "High CPU incident triage",
        "tags": ["cpu", "performance", "latency", "process", "monitoring"],
        "body": (
            "Capture CPU utilization over time, identify the process or request path consuming resources, compare against "
            "recent deployments, and collect logs/metrics before restarting the service unless availability requires immediate action."
        ),
    },
    {
        "id": "KB-005",
        "title": "TLS certificate and HTTPS troubleshooting",
        "tags": ["tls", "ssl", "certificate", "https", "handshake"],
        "body": (
            "Validate certificate expiration, hostname/SAN coverage, trust chain, negotiated protocol, and server time. "
            "Record the exact handshake error before replacing certificates or disabling verification."
        ),
    },
]
