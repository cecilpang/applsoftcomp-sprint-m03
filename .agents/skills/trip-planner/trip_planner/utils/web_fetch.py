"""Web fetch wrapper for trip planner."""

import time
from typing import Optional


def webfetch(url: str, format: str = "text", timeout: int = 120) -> str:
    """Fetch content from URL using the webfetch tool."""
    from datetime import datetime

    for attempt in range(3):
        try:
            from functions import webfetch as wf

            result = wf(url=url, format=format, timeout=timeout)
            if result:
                return result
        except Exception as e:
            if attempt < 2:
                time.sleep(30)
                continue
    return ""
