# backend/services/football_data.py
import os
import requests

BASE = "https://api.football-data.org/v4"

class ApiError(RuntimeError):
    pass

def _headers():
    token = (os.getenv("FOOTBALL_DATA_TOKEN") or "").strip()
    if not token:
        raise ApiError("FOOTBALL_DATA_TOKEN is not set (or is empty)")
    return {
        "X-Auth-Token": token,
        "Accept": "application/json",
        "User-Agent": "SoccerPredictorScout/1.0"
    }

def _raise(e: requests.exceptions.RequestException):
    # Bubble up the API's response body so we can see *why* it rejected us
    detail = ""
    if getattr(e, "response", None) is not None:
        try:
            detail = e.response.text
        except Exception:
            pass
    msg = f"football-data request failed: {e}"
    if detail:
        msg += f" :: {detail[:400]}"
    raise ApiError(msg) from e

def get_teams(competition: str = "PL"):
    try:
        r = requests.get(f"{BASE}/competitions/{competition}/teams",
                         headers=_headers(), timeout=20)
        r.raise_for_status()
        data = r.json()
        return [
            {
                "id": t["id"],
                "name": t["name"],
                "shortName": t.get("shortName"),
                "tla": t.get("tla"),
                "crest": t.get("crest"),
            }
            for t in data.get("teams", [])
        ]
    except requests.exceptions.RequestException as e:
        _raise(e)
