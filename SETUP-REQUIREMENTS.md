# YouTube Auto-Uploader — What You Need To Prepare

Everything in this project is **100% free**. No subscriptions, no credit card, no paid
services. Google does not charge money for the YouTube Data API — it charges *quota units*,
which are free and capped per day.

---

## 1. The one thing that decides everything: do your videos need to be PUBLIC?

This is the single most important question, and almost every tutorial skips it.

Google's documented rule (unchanged since 28 July 2020, still live in the current docs):

> "All videos uploaded via the `videos.insert` endpoint from unverified API projects created
> after 28 July 2020 will be **restricted to private viewing mode**. To lift this restriction,
> each API project must undergo an audit to verify compliance with the Terms of Service."

Source: https://developers.google.com/youtube/v3/docs/videos

What this means in practice:

| Your goal | Cost | What you must do |
|---|---|---|
| Videos **private or unlisted** | €0, works today | Nothing extra. Build it and go. |
| Videos **public** | €0, but gated | Pass the **YouTube API Services Compliance Audit** (free form, manual human review, no guaranteed approval, typically weeks) |

**Important detail most people get wrong:** OAuth app verification and the Compliance Audit
are **two different things**.

- *OAuth verification* — you can skip this. Personal-use apps under 100 users are an explicit
  documented exception; you just add yourself as a test user and click through an
  "unverified app" warning screen.
- *Compliance Audit* — this is the one that unlocks public uploads, and you cannot skip it.

Form: https://support.google.com/youtube/contact/yt_api_form

**And the trap:** a video that gets locked private because it came from an unverified project
**cannot be appealed and cannot be unlocked** — not via the API, not via YouTube Studio. You
have to re-upload it after your project is audited. So when you first test, **use a throwaway
video**, not a real one.

---

## 1b. ⚠️ UPDATE — I tested the "free AI" tools before recommending them

I don't want to hand you a plan that quietly turns into a paid tier, so I ran real requests
against each candidate. Here is what I actually found today, not what blog posts claim:

| Tool | What it does | Result of my live test |
|---|---|---|
| **Pollinations images** `image.pollinations.ai` | AI image generation | ✅ **Free, no key, no signup.** 3/3 requests returned valid 1024×576 JPEGs. Use this. |
| **Pollinations text** `text.pollinations.ai` | AI script writing | ❌ **Effectively dead for anonymous use.** `GET /openai/models` lists only `openai-fast`, and any prompt producing more than a few tokens returns `402 Payment Required` / `KEY_BUDGET_EXHAUSTED`. Trivial prompts pass; real script generation fails. Do not build on this. |
| **edge-tts** | Voiceover | ✅ **Free, no key.** Generated a valid 3.29 s MP3. This is Microsoft's neural TTS via an unofficial endpoint — reliable but no SLA, so the code treats it as replaceable. |
| **FFmpeg** | Video assembly, Ken Burns motion, thumbnails | ✅ Free, open source. v7.1.5 installed and working here. |
| **Gemini API** (Google AI Studio) | AI script writing | ✅ **Free with a free API key, no credit card.** Roughly 1,500 requests/day on Flash models. You need a few more scripts than that? Unlikely — you need ~1 per video. |
| Real AI **video** generation (Sora, Veo, etc.) | Text-to-video | ❌ Not free. Excluded. The honest free approach is AI images + motion + voiceover, which is how most faceless channels actually work. |

**Net result: one extra free key to get you — a Gemini API key.** Everything else stays keyless.
The code is written so that if you'd rather not get that key, it falls back to a built-in
template-based script writer, and the provider is swappable in one config line.

Get the Gemini key here (free, no card): https://aistudio.google.com/apikey

---

## 2. Your free daily limits (current, from Google's own docs)

Source: https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits

> "Projects that enable the YouTube Data API have a default quota allocation of
> **100 `search.list` calls, 100 `videos.insert` calls, and 10,000 units per day combined
> for all other endpoints**."

| Resource | Free allowance |
|---|---|
| Video uploads (`videos.insert`) | **100 per day** |
| Search (`search.list`) | 100 per day |
| Everything else (metadata, playlists, thumbnails) | 10,000 units/day combined |
| Quota reset | **Midnight Pacific Time** (09:00 in Italy, summer time) |

⚠️ **Correction to common advice:** you will find many articles saying uploads cost 1,600
units each, giving you ~6 uploads/day. That is **outdated**. Google now gives uploads their
own 100-call daily bucket. Unless you need more than 100 uploads a day, you will never need
to file for a quota extension.

---

## 3. Exactly what I need from you

### A. Google Account (€0)
1. A Google Account — the one that owns your YouTube channel.
2. **2-Step Verification enabled** on it (myaccount.google.com/security). YouTube requires it
   for API access, and OAuth token refresh fails oddly without it.
3. A **verified YouTube channel** — youtube.com/account_features. Without this, uploads over
   15 minutes fail and live features are blocked.

### B. Google Cloud project + credentials (€0, ~15 minutes)
You will end up handing me **one file**: `client_secret_*.json`. That's the only credential
in this whole project. No API keys to copy-paste, no billing account, no credit card.

Step by step:

1. Go to https://console.cloud.google.com/ and sign in with that Google Account.
2. Accept the terms. **Create a new project** — name it something like `my-uploader`.
   - Do *not* link a billing account. The YouTube Data API needs none.
   - **Use exactly one project.** Creating several projects to multiply quota is a documented
     ToS violation and Google actively suspends accounts for it.
3. Enable the API: search "YouTube Data API v3" in the console search bar → **Enable**.
4. Configure the OAuth consent screen:
   - https://console.cloud.google.com/auth/branding
   - User type: **External**
   - App name: anything (e.g. `My Uploader`)
   - Support email: your own email
   - Add your own email under **Test users** — this is what lets you skip OAuth verification.
5. Create credentials:
   - https://console.cloud.google.com/apis/credentials
   - **+ Create Credentials → OAuth client ID**
   - Application type: **Desktop app** ← important, this is the free/simple path
   - Name it, create it, then click **Download JSON**.
6. Save that file into this project folder and rename it to `client_secret.json`.

### C. Scope the program will request (no action needed, just FYI)
- `https://www.googleapis.com/auth/youtube.upload` — upload only
- `https://www.googleapis.com/auth/youtube.force-ssl` — needed for editing metadata,
  setting thumbnails and scheduling

These are "restricted" scopes, but **personal use is a documented exception** to verification.
You'll see a scary "Google hasn't verified this app" screen the first time. Click
*Advanced → Go to (unsafe)*. That is normal and expected for a personal tool.

### D. Software on your machine (all €0)
- **Python 3.9 or newer** (check with `python3 --version`)
- **FFmpeg** — free. Used to normalise videos to YouTube's preferred format
  (MP4 / H.264 / AAC) and to generate thumbnails. Install:
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`
  - Windows: `winget install Gyan.FFmpeg`
- Four Python packages, all free, all verified to install cleanly:
  `google-api-python-client`, `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`

### E. A machine that stays switched on (only if you want unattended scheduling)
If you want uploads to happen while you sleep, something must be awake to trigger them.
Cheapest free options, in order of sanity:
- Your own PC/Mac with a scheduled task (cron / Task Scheduler) — genuinely free, most reliable
- An old laptop or Raspberry Pi you already own
- A free-tier cloud VM — free but the free tiers are the least dependable part of any plan

If you just want "drop files in a folder and they get uploaded when I run it", you need
**nothing** in this section.

---

## 4. Things that will cost you €0 but might surprise you

- **The first upload will be slow.** Resumable upload sends the file in 256 KB-multiple chunks;
  large files take a while and that's normal, not a bug.
- **Processing takes time after upload.** YouTube transcodes server-side. The video is not
  watchable the second the upload finishes — the program should poll `videos.list` for
  `processingDetails.processingStatus == "succeeded"`.
- **A 403 `quotaExceeded`** means you hit the daily cap. It resets at midnight Pacific. It
  does not mean you owe money.
- **Tokens expire.** The program must handle refresh automatically; you should only ever
  log in through a browser **once**.
- **`client_secret.json` is a secret.** Never commit it to Git. I'll add a `.gitignore`.

---

## 5. What I deliberately am NOT recommending

- **Selenium / browser automation.** It's the obvious "free workaround" for the public-upload
  lock, and it's all over the internet. But it violates the YouTube ToS, breaks every time
  Google changes Studio's HTML, and puts your channel at risk of termination. Not worth it.
- **Third-party "free upload" services.** They hold your OAuth tokens and their own quota.
  Most have hidden limits or paid tiers.
- **Service accounts.** They cannot upload videos to a personal channel — wrong credential
  type for this job.

---

## 6. Checklist before we write code

- [ ] Google Account with 2-Step Verification on
- [ ] YouTube channel verified (youtube.com/account_features)
- [ ] Google Cloud project created (**exactly one**)
- [ ] YouTube Data API v3 enabled
- [ ] OAuth consent screen configured, yourself added as test user
- [ ] OAuth client ID created as **Desktop app**
- [ ] `client_secret.json` downloaded into the project folder
- [ ] Python 3.9+ and FFmpeg installed
- [ ] **Decided: private/unlisted, or public (→ needs the audit form)?**

That last box is the only one that changes the architecture, so it's the one I most need
from you.
