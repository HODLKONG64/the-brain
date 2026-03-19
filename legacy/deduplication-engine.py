"""
deduplication-engine.py - Deduplication Engine for GK BRAIN
Tracks all updates ever used to prevent repetitive lore content.
"""
import hashlib, json, os
BASE_DIR = os.path.dirname(__file__)
REGISTRY_FILE = os.path.join(BASE_DIR, "used-updates-registry.json")

def _hash(u): return hashlib.sha256(((u.get("url","") or u.get("source","")) + (u.get("title","") or "") + (u.get("content","") or "")[:100]).encode()).hexdigest()
def _load():
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE) as f: return json.load(f)
        except: pass
    return {"used": []}
def _save(r):
    try:
        r["used"] = r["used"][-2000:]
        with open(REGISTRY_FILE,"w") as f: json.dump(r,f)
    except Exception as e: print(f"[dedup] {e}")

def deduplicate_updates(updates):
    """Filter updates already used. Returns only new updates."""
    try:
        reg = _load(); used = set(reg["used"])
        return [u for u in updates if _hash(u) not in used]
    except Exception as e:
        print(f"[dedup] {e}"); return updates

def mark_used(update_ids):
    """Mark a list of update hashes as used."""
    try:
        reg = _load(); reg["used"].extend(update_ids); _save(reg)
    except Exception as e: print(f"[dedup] {e}")
