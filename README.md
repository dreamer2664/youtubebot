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

## What the "Compliance Audit" is, in plain words

### The rule

> All videos uploaded via `videos.insert` from **unverified API projects created after
> 28 July 2020** are restricted to **private viewing mode**. — Google's own docs

So: upload a video through this tool today and it lands on your channel **locked as
private**. Locked means:

- you cannot make it public from the API,
- you cannot make it public from YouTube Studio,
- **there is no appeal**,
- the only fix is to re-upload it later from an audited project.

That is why this tool refuses `upload --privacy public` while `audit_passed: false`.
It is protecting you from burning uploads you would have to redo.

### What the audit actually is

A free form. A human at YouTube's API team reads it and decides whether your project
follows the YouTube API Services Terms of Service. If they say yes, your project becomes
"audited" and the private lock stops applying to new uploads.

It is **not** a fee, not a certification, and not an automated check. There is no
guaranteed approval and no published timeline — people report weeks, and rejections happen.

### How to do it

1. Go to <https://support.google.com/youtube/contact/yt_api_form>
2. Sign in with the **same Google account that owns the Cloud project**.
3. Fill in the form honestly. It will ask roughly:
   - **What does your API client do?** Describe it plainly: *"A personal tool that
     generates short educational videos about [topic] and uploads them to my own
     YouTube channel."*
   - **Which endpoints do you use?** `videos.insert`, `videos.list`, `videos.update`,
     `thumbnails.set`, `channels.list`.
   - **How do users authorise access?** OAuth 2.0, one user — me — via a desktop client.
   - **How is data stored / deleted?** Locally on my own machine; nothing is shared.
   - **Expected daily traffic?** 1–3 uploads per day, well under the 100/day default.
   - **How can users revoke access?** Link your privacy policy field to
     <https://security.google.com/settings/security/permissions>.
4. Submit and wait for email.

### The honest catch

Google rejects personal/hobby projects fairly often, and there is a known loop: if you
say the app is for personal use, they may reply *"your project does not require
verification"* — which is true for **OAuth** verification but does **not** lift the
YouTube private lock. If that happens, reply to the email explaining specifically that
you need `videos.insert` unlocked for public viewing, which requires the API audit
rather than OAuth verification.

Set expectations accordingly: **plan on private/unlisted working today, and treat public
as a maybe-later.**

### What the audit is NOT

- Not the same as OAuth app verification. You can skip OAuth verification entirely by
  adding yourself as a test user — but that does not unlock public uploads.
- Not something you can buy. There is no paid fast lane.
- Not something Selenium can dodge. Browser automation violates the ToS and risks your
  channel. Not worth it.

### What to do in the meantime

There is no privacy setting that dodges this. Developers report trying
`privacyStatus: unlisted` and still getting the video locked to private, and Google's
wording is "all videos uploaded via `videos.insert`" with no exception carved out for
unlisted. **Treat every API upload as private until the audit passes.**

Two practical options:

1. **Build your backlog now, upload later.** `generate` costs no YouTube quota at all —
   it only uses Gemini and FFmpeg. Queue up 20 videos, and upload them the day your
   audit is approved.
2. **Upload the ones you want visible manually** through youtube.com, which is not
   affected by any of this, and keep the tool for everything else.

Do not reach for Selenium to get around it. It violates the ToS and risks the channel.

---

## Setup

### Windows (PowerShell)

Fastest path — this does FFmpeg, the venv, dependencies, config and credentials in one go:

```powershell
cd $HOME
git clone https://github.com/dreamer2664/youtubebot.git
cd youtubebot
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

It will also find `client_secret*.json` in your Downloads folder and copy it into place
automatically. Re-run it once after it installs FFmpeg, since PATH changes need a new window.

<details><summary>Or do it by hand</summary>

```powershell
winget install Gyan.FFmpeg        # then close and reopen PowerShell
cd $HOME
git clone https://github.com/dreamer2664/youtubebot.git
cd youtubebot
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item config.example.yaml config.yaml
notepad config.yaml
python main.py preflight
```

</details>

> **Python version note.** 3.14 is very new and some dependencies may not have
> wheels for it yet. If `pip install` fails, install Python 3.12 from
> python.org and use `py -3.12 -m venv venv` instead.

> If `Activate.ps1` is blocked by execution policy:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

### Linux / macOS

```bash
sudo apt install ffmpeg          # or: brew install ffmpeg
git clone https://github.com/dreamer2664/youtubebot.git
cd youtubebot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp config.example.yaml config.yaml
python main.py preflight
```

### Google Cloud credentials (once, ~15 minutes, free)

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

Open `config.yaml` and paste it in:

```yaml
ai:
  provider: "gemini"
  gemini_api_key: "AQ.your-key-here"
  gemini_model: "gemini-flash-latest"
```

`config.yaml` is git-ignored, so it will not be committed. On Linux/macOS you can use
`export GEMINI_API_KEY="..."` instead; the environment is checked first. On Windows
PowerShell that would be `$env:GEMINI_API_KEY="..."`, but it only lasts for that window,
so `config.yaml` is the better choice there.

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
