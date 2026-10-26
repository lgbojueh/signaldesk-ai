from .retrieval import retrieve

CATEGORY_RULES = {
    "Authentication": ["401", "403", "login", "token", "jwt", "auth", "permission"],
    "Networking": ["dns", "timeout", "connection refused", "network", "hostname", "port"],
    "Database": ["postgres", "mysql", "database", "sql", "connection pool"],
    "Security": ["tls", "ssl", "certificate", "vulnerability", "encryption"],
    "Performance": ["cpu", "memory", "slow", "latency", "performance"],
    "Deployment": ["docker", "container", "deploy", "nginx", "ci/cd"],
}


def classify(text: str) -> str:
    lower = text.lower()
    scores = {
        category: sum(1 for keyword in keywords if keyword in lower)
        for category, keywords in CATEGORY_RULES.items()
    }
    category, score = max(scores.items(), key=lambda item: item[1])
    return category if score else "General Support"


def severity(text: str) -> str:
    lower = text.lower()
    if any(word in lower for word in ["outage", "production down", "data loss", "security breach", "all users"]):
        return "critical"
    if any(word in lower for word in ["cannot", "failed", "connection refused", "500", "unavailable"]):
        return "high"
    if any(word in lower for word in ["slow", "intermittent", "warning", "degraded"]):
        return "medium"
    return "low"


def analyze(title: str, description: str) -> dict:
    query = f"{title} {description}"
    category = classify(query)
    sev = severity(query)
    sources = retrieve(query)
    top_score = sources[0]["score"] if sources else 0.0

    if top_score >= 0.75:
        confidence = "high"
    elif top_score >= 0.4:
        confidence = "medium"
    else:
        confidence = "low"

    escalation = sev == "critical" or confidence == "low"

    steps = [
        "Capture the exact error, affected environment, and recent change history before making changes.",
    ]
    if sources:
        steps.extend([
            f"Use {sources[0]['id']} as the primary runbook and verify its checks against the affected environment.",
            "Compare the failing path with a known-good path to isolate configuration, network, authentication, or application differences.",
            "Record the result of each check so the incident can be reproduced or escalated with evidence.",
        ])
    if escalation:
        steps.append("Escalate to a human owner with logs, timestamps, attempted checks, and the cited knowledge articles attached.")
    else:
        steps.append("If the issue is resolved, document the root cause and update the knowledge base with any missing detail.")

    summary = (
        f"Classified as {category} with {sev} severity. "
        f"The strongest knowledge match is {sources[0]['id'] if sources else 'none'}, "
        f"so recommendation confidence is {confidence}."
    )

    return {
        "category": category,
        "severity": sev,
        "confidence": confidence,
        "escalation": escalation,
        "summary": summary,
        "steps": steps,
        "sources": [
            {
                "id": source["id"],
                "title": source["title"],
                "excerpt": source["body"],
                "score": source["score"],
            }
            for source in sources
        ],
    }
