# UMAR AI Cyber

Railway-ready web version of UMAR AI: OpenRouter free model router, Uzbek-language chat, safe static code security review, and Linux terminal learning demo.

## Local

```bash
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 and enter your own OpenRouter API key. Key is not persisted to disk.

## Railway

Deploy this repository as a Python service; the included `railway.json` sets start command and health check. Generate a Railway domain after successful deployment.

**Limitations:** OpenRouter free-tier has rate limits. Terminal is simulated, not a Linux shell. Security lab only scans code pasted by its owner. Do not use it to access others' sites.
