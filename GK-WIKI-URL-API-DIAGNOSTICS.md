# GK WIKI URL & API DIAGNOSTICS

Diagnostic reference for resolving URL and API connectivity issues with `gkniftyheads.fandom.com`.

---

## 1. Correct API Endpoint

```
https://gkniftyheads.fandom.com/api.php
```

The code derives this as:
```python
WIKI_API = os.environ.get("FANDOM_WIKI_URL", "https://gkniftyheads.fandom.com").rstrip("/") + "/api.php"
```

**Common mistakes:**
- Including a trailing slash in `FANDOM_WIKI_URL` → fixed by `.rstrip("/")`
- Using `www.fandom.com/api/v1/` (wrong — that is the Fandom unified API, not the wiki API)
- Using the `/wiki/` URL instead of `/api.php`

---

## 2. Wiki URL Redirect Map

| URL | Status |
|---|---|
| `https://gkniftyheads.fandom.com/wiki/Main_Page` | Redirects to `GKniftyHEADS_Wiki` |
| `https://gkniftyheads.fandom.com/wiki/GKniftyHEADS_Wiki` | Canonical main page |
| `https://gkniftyheads.fandom.com/wiki/Main_Page?redirect=no` | Shows redirect page source (for editing) |

The rename was performed by FANDOM on 2026-03-07 for SEO purposes. Bot page writes use
**page titles** not URLs, so writes to `Main_Page` still work (MediaWiki follows redirects).

---

## 3. Health Check

```python
import requests, os
url = os.environ.get("FANDOM_WIKI_URL", "https://gkniftyheads.fandom.com")
r = requests.get(f"{url.rstrip('/')}/api.php", params={"action":"query","meta":"siteinfo","format":"json"}, timeout=10)
print(r.status_code, r.json().get("query",{}).get("general",{}).get("servername"))
```

Expected: `200` and `servername` containing `fandom.com`.

---

## 4. Login Diagnostic

```python
import requests, os
session = requests.Session()
api = os.environ.get("FANDOM_WIKI_URL", "https://gkniftyheads.fandom.com").rstrip("/") + "/api.php"
# Step 1: get login token
r = session.get(api, params={"action":"query","meta":"tokens","type":"login","format":"json"})
token = r.json()["query"]["tokens"]["logintoken"]
# Step 2: log in
r2 = session.post(api, data={
    "action":"clientlogin","loginreturnurl":"https://gkniftyheads.fandom.com",
    "logintoken":token,"username":os.environ["FANDOM_BOT_USER"],
    "password":os.environ["FANDOM_BOT_PASSWORD"],"format":"json"
})
print(r2.json().get("clientlogin",{}).get("status"))
```

Expected: `"PASS"`. If `"FAIL"`, check `FANDOM_BOT_USER` and `FANDOM_BOT_PASSWORD` secrets.

---

## 5. Common Error Responses

| Error | Likely cause | Fix |
|---|---|---|
| `Connection refused` / `timeout` | `FANDOM_WIKI_URL` wrong or network blocked | Verify secret; check GitHub Actions network access |
| `{"error":{"code":"badtoken"}}` | CSRF token expired | Re-query tokens before each edit |
| `{"error":{"code":"readapidenied"}}` | Wiki is private | Set wiki to public in Fandom admin |
| `{"clientlogin":{"status":"FAIL"}}` | Wrong credentials | Re-check `FANDOM_BOT_USER` / `FANDOM_BOT_PASSWORD` |
| HTTP 403 | Bot account blocked | Log in to Fandom and unblock the account |
| HTTP 429 | Rate limited | Honour `Retry-After` header |

---

## 6. Verifying a Successful Write

After a page edit, confirm with:

```
GET /api.php?action=query&prop=revisions&rvprop=ids,timestamp&titles=<page_title>&format=json
```

Check that the `timestamp` matches the current run time.
