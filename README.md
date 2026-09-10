# youtubebot — free YouTube auto-upload pipeline

Generates videos with AI and uploads them to YouTube. **Everything here is free.**
Google does not charge money for the YouTube Data API; it charges *quota units*,
which are free and capped per day.

```
Gemini script  ->  Pollinations images  ->  edge-tts voice  ->  FFmpeg  ->  YouTube
   (free key)         (free, no key)        (free, no key)     (free)      (free quota)
```

---

## Cost and limits

| Thing | Free allowance |
|---|---|
| Video uploads (`videos.insert`) | **100 per day** |
| Other API calls | 10,000 units/day |
| Quota reset | Midnight Pacific (09:00 Italy, summer time) |
| Money | **€0** |

> Older guides say uploads cost 1,600 units each, giving you ~6 a day. That is
> outdated. Google now gives `videos.insert` its own 100-call daily bucket.

---

## ⚠️ Read this before uploading anything public

> All videos uploaded via `videos.insert` from **unverified API projects created after
> 28 July 2020** are restricted to **private viewing mode**. — Google's docs

Videos locked this way **cannot be unlocked**, not via the API and not via YouTube
Studio, and **there is no appeal**. You would have to re-upload every one of them.

To lift it, your project must pass the **YouTube API Services Compliance Audit**:
<https://support.google.com/youtube/contact/yt_api_form> (free, manual review, no
guaranteed approval).

This is *not* the same as OAuth app verification — you can skip OAuth verification
entirely by adding yourself as a test user.

**So:** while `privacy.audit_passed` is `false`, `upload --privacy public` refuses to
run. Generate and queue videos now; upload once Google approves you.

---

## Setup

### 1. Install

```bash
sudo apt install ffmpeg          # or: brew install ffmpeg / winget install Gyan.FFmpeg
pip install -r requirements.txt
cp config.example.yaml config.yaml
```

### 2. Google Cloud credentials (once, ~15 minutes, free)

1. <https://console.cloud.google.com/> → create a project. **Use exactly one** —
   creating several to multiply quota violates the ToS and Google suspends accounts for it.
2. Enable **YouTube Data API v3**.
3. <https://console.cloud.google.com/auth/branding> → User type **External**,
   add your own email as a **Test user** (this is what lets you skip OAuth verification).
4. <https://console.cloud.google.com/apis/credentials> → **Create Credentials →
   OAuth client ID → Desktop app** → **Download JSON**.
5. Save it here as `client_secret.json`.

Do **not** link a billing account. The API needs none.

### 3. Gemini API key (free, no card)

<https://aistudio.google.com/apikey>

Prefer not to put it in a file? Export it instead — the code checks the environment first:

```bash
export GEMINI_API_KEY="..."
```

### 4. Check it

```bash
python main.py preflight
```

---

## Use

```bash
python main.py generate                 # make one video
python main.py generate --count 3       # make three
python main.py generate --topic "..."   # override the channel topic for one run
python main.py queue                    # what's in the queue
python main.py upload --privacy private # upload as private (safe, works today)
python main.py upload                   # uses the privacy setting from config.yaml
python main.py auth --fresh             # re-authorise from scratch
python main.py publish                  # flip to public (only after the audit passes)
```

`generate` writes `out/<id>.mp4`, a matching `.jpg` thumbnail, and a `.meta.json`
with title, description and tags.

### Automatic, on a schedule

```bash
# Linux / macOS — crontab -e
0 9 * * * cd /path/to/youtubebot && /usr/bin/python3 main.py generate --count 1 >> run.log 2>&1
30 9 * * * cd /path/to/youtubebot && /usr/bin/python3 main.py upload >> run.log 2>&1
```

```powershell
# Windows — Task Scheduler, two daily tasks
python C:\path\to\youtubebot\main.py generate --count 1
python C:\path\to\youtubebot\main.py upload
```

---

## Configuration

Everything lives in `config.yaml`. The important keys:

| Key | What it does |
|---|---|
| `channel.topic` | Your niche. Drives every script and image. Be specific. |
| `channel.tone` | How the narration sounds. |
| `channel.voice` | Free neural voice. `python -c "import voiceover; voiceover.list_voices()"` lists them. |
| `channel.target_seconds` | Target length. 90–180 suits a new channel. |
| `privacy.status` | `private` / `unlisted` / `public`. |
| `privacy.audit_passed` | Flip to `true` only after Google approves your audit. |
| `ai.provider` | `gemini` (good scripts) or `template` (keyless fallback). |
| `ai.gemini_model` | `gemini-flash-latest` tracks the current model automatically. |

---

## Files

| File | Purpose |
|---|---|
| `main.py` | CLI |
| `config.py` | Config loading, env overrides |
| `scriptgen.py` | Gemini + offline template script writers |
| `images.py` | Pollinations image generation |
| `voiceover.py` | edge-tts voiceover |
| `assembler.py` | FFmpeg: Ken Burns motion, audio, thumbnails |
| `uploader.py` | OAuth, resumable upload, retries, audit gate |
| `jobqueue.py` | `state.json` job tracking |
| `hooks/pre-commit` | Blocks credentials from being committed |

> `jobqueue.py` is deliberately **not** named `queue.py` — that would shadow Python's
> stdlib `queue` module and break `urllib3`, which Google's HTTP transport depends on.

---

## Security

`client_secret.json`, `token.json` and `config.yaml` are git-ignored, and
`hooks/pre-commit` blocks commits containing GitHub tokens, Google API keys, Gemini
keys, OAuth secrets, refresh tokens or private keys.

Install the guard once:

```bash
cp hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
```

This repo is public, so that guard is not optional.

---

## Not recommended

- **Selenium / browser automation.** The usual "free workaround" for the public-upload
  lock. It violates the YouTube ToS, breaks whenever Google changes Studio's HTML,
  and risks your channel.
- **Third-party upload services.** They hold your tokens and their own quota.
- **Service accounts.** Cannot upload to a personal channel.
- **Multiple Cloud projects.** Quota does not stack; accounts get suspended.
