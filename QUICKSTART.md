# QUICKSTART — Windows

Run these **four lines** in PowerShell, one at a time:

```powershell
cd $HOME
git clone https://github.com/dreamer2664/youtubebot.git
cd youtubebot
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

That installs FFmpeg, creates a Python environment, installs the libraries, creates
`config.yaml`, and copies your `client_secret*.json` out of Downloads automatically.

**Then close PowerShell, open a new one, and re-run the last line once** — FFmpeg needs a
fresh window to be found.

---

## After that

```powershell
cd $HOME\youtubebot
.\venv\Scripts\Activate.ps1
notepad config.yaml
```

In `config.yaml`, set two things:

```yaml
channel:
  topic: "your channel topic here, be specific"

ai:
  provider: "gemini"
  gemini_api_key: "AQ.your-key-here"
```

Save, then:

```powershell
python main.py preflight     # tells you exactly what is still missing
python main.py auth          # opens a browser, log in once
python main.py generate      # makes a video into out\
python main.py upload --privacy private
```

`preflight` is the useful one. It checks FFmpeg, the libraries, your credentials and the
live YouTube API, and prints the exact console link to fix whatever is wrong.

---

## Why your earlier commands failed

They were Linux commands and you are on Windows. My mistake, not yours.

| You ran | Why it failed | Windows equivalent |
|---|---|---|
| `sudo apt install ffmpeg` | `sudo`/`apt` do not exist on Windows | `winget install Gyan.FFmpeg` (setup.ps1 does this) |
| `cp config.example.yaml config.yaml` | You were in `C:\Users\carlo`; the project was not there | `git clone` first, then `cd youtubebot` |
| `export GEMINI_API_KEY=...` | `export` is bash, not PowerShell | Put the key in `config.yaml` instead |
| `python main.py ...` | `main.py` was not in that folder | `cd $HOME\youtubebot` first |

Also: **Python 3.14 is very new.** If `pip install` fails, install Python 3.12 from
python.org — setup.ps1 will prefer it automatically.

---

## What the audit is

YouTube **force-locks to private** every video uploaded through an API project they have
not reviewed. You cannot unlock them — not in YouTube Studio, not via the API, and
**there is no appeal**. The only fix is re-uploading them later.

**The audit is a free form:** https://support.google.com/youtube/contact/yt_api_form

A person at YouTube reads it and decides whether your project follows their API terms.
No fee. No guaranteed approval. No published timeline — people report weeks.

It asks, roughly:

- **What does your app do?** → *"A personal tool that generates short videos about [topic]
  and uploads them to my own YouTube channel."*
- **Which endpoints?** → `videos.insert`, `videos.list`, `videos.update`,
  `thumbnails.set`, `channels.list`
- **How do users authorise?** → OAuth 2.0, one user (me), desktop client
- **How is data stored?** → Locally on my own machine, nothing shared
- **Expected traffic?** → 1–3 uploads per day
- **Privacy policy link** → https://security.google.com/settings/security/permissions

**The catch:** they reject personal projects often. If you say it is for personal use they
may reply *"your project does not require verification."* That is true for OAuth
verification but it does **not** lift the private lock. Reply to that email and say you
specifically need `videos.insert` unlocked for public viewing.

**Unlisted is not a workaround either** — developers report unlisted uploads get locked
too.

---

## So what should you actually do

`generate` costs **no YouTube quota at all** — it only uses Gemini and FFmpeg.

So build a backlog of videos now, and upload them the day your audit clears. Nothing is
wasted by waiting.
