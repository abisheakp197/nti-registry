"""GET /api/health"""

import json
from datetime import UTC, datetime

from lib.db import backend_info


def handle_health() -> tuple[int, dict[str, str], bytes]:
    return (
        200,
        {"Content-Type": "application/json"},
        json.dumps({
            "status": "ok",
            "service": "nti-registry",
            "spec": "NTI-Registry/1",
            "checked_at": datetime.now(UTC).isoformat(),
            "database": backend_info(),
        }).encode("utf-8"),
    )
