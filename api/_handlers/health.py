"""GET /api/health"""


import json
from datetime import datetime, timezone


from lib.db import backend_info




def handle_health() -> tuple:
    return (
        200,
        {"Content-Type": "application/json"},
        json.dumps({
            "status": "ok",
            "service": "nti-registry",
            "spec": "NTI-Registry/1",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "database": backend_info(),
        }).encode("utf-8"),
    )
