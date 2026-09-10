# Sezione 4 e 5 — complete answers

Your project ID: `my-uploader-508220`
Your project **number**: `40430168862` ← confirm this against the Google Cloud welcome card before submitting

---

# SEZIONE 4 — Panoramica del client API

## Dettagli del client API

| Field | Answer |
|---|---|
| **Nome del client API** | `Curiosity Compass` |
| **Il nome contiene "YouTube"?** | ✅ **No, il nome non include "YouTube"** |
| **URL di accesso principale** | `https://dreamer2664.github.io/youtubebot/` |
| **URL delle norme sulla privacy** | `https://github.com/dreamer2664/youtubebot/blob/main/PRIVACY.md` |
| **URL dei Termini di servizio** | `https://github.com/dreamer2664/youtubebot/blob/main/TERMS.md` |
| **Il tuo client API è accessibile pubblicamente?** | ✅ **No** |

> The main URL is a GitHub Pages homepage I created at `docs/index.html`. It is not live
> until you enable Pages — see "Before you submit", step 1. If you would rather not enable
> Pages, use `https://github.com/dreamer2664/youtubebot` instead, which works immediately.

## Credenziali dell'account demo

**Leave this entire block empty.** Do not tick the acceptance box.

There is no demo account because there is no user-facing product, no login, and no premium
tier. It is a command-line tool that one person runs on their own computer. Inventing demo
credentials would be a false statement.

If the form refuses to submit without it, put in *Istruzioni speciali per l'accesso*:

```
Not applicable. This API client is a personal command-line tool with no user-facing
interface, no accounts and no sign-in for third parties. There is no demo account to
provide. I can supply a screen recording of the tool running on request.
```

---

# SEZIONE 5 — Casi d'uso e dettagli dell'estensione della quota

**Quanti numeri di progetto intendi aggiungere?** → `1`

## Progetto 1

| Field | Answer |
|---|---|
| **Numero di progetto Google Cloud** | `40430168862` |
| **Questo client API richiede OAuth 2.0?** | ✅ **Sì** |
| **Volume previsto di utilizzo dell'API** | ✅ **Meno di 1000 richieste al giorno** |

### Categoria dei casi d'uso — select ONE

✅ **Caricamento di video e gestione dell'account**

That is the honest and precise fit: the tool uploads videos and edits their metadata.

**Do not also select "Strumento aziendale interno."** It would be literally true (it is
proprietary and not distributed), but it triggers the *conditional evidence* requirement
for dashboard screenshots, and this tool has no dashboard. Fewer categories means fewer
documents you have to produce, and this one is accurate.

---

## Dettagli della quota per il Progetto 1

**Select these endpoints:**

- ✅ `videos.insert`
- ✅ `videos.list`
- ✅ `videos.update`
- ✅ `thumbnails.set`
- ✅ `channels.list`

**Do not** select `search.list` — you don't use it.

**Quale quota intendi richiedere in totale?**
✅ **Nessuna modifica/Quota predefinita (10.000 punti quota)**

Leave the separate `search.list` and `videos.insert` quota fields empty or at default.

**Why:** your usage is 1–3 uploads a day. The default allowance is already 100
`videos.insert` calls per day, so you are nowhere near needing more. Asking only for the
audit keeps the application simple, and a modest, well-justified request is much more
likely to be approved than a large speculative one.

---

# PROVE RICHIESTE — what to upload for each slot

The form says file upload is simulated, so if a slot will not accept a file, paste the
matching URL into the nearest text field and say the document is available at that link.

| Slot | File | How to get it |
|---|---|---|
| **Screenshot delle Norme sulla privacy** | `docs/evidence-privacy.png` | Open `PRIVACY.md`, screenshot the sections on YouTube, the Google Privacy Policy link, and deletion/revocation. Save as one image, 1280×720 or larger. |
| **Screenshot della home page** | `docs/evidence-homepage.png` | Screenshot `https://dreamer2664.github.io/youtubebot/` showing the privacy link in the footer. ⚠️ See the branding warning below. |
| **Documentazione relativa ai Termini di servizio** | `docs/evidence-terms.png` | Screenshot `TERMS.md`, or upload it as a PDF. |

## PROVE CONDIZIONALI

Because you selected *Caricamento di video e gestione dell'account* and OAuth = Sì, you need **(a)** and **(b)**:

**(a) OAuth flow screenshots** — three screens:

1. Consent screen → open this URL and screenshot it:

```
https://accounts.google.com/o/oauth2/auth?client_id=40430168862-urokiguqeiafti7rlhki13ulb26ku12d.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost&response_type=code&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube.upload+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube.force-ssl&access_type=offline&prompt=consent
```

2. Scopes → the same screen shows the two scopes being requested.
3. Revocation → screenshot `https://security.google.com/settings/security/permissions`

Combine the three into one PNG.

**(b) Upload interface screenshot** — the tool is a CLI, so screenshot your terminal
running:

```powershell
python main.py upload --privacy private
```

Show the command and its output. A terminal *is* the interface; that is a legitimate
answer, and pretending otherwise would be worse.

**(c)** and **(d)** — not required, you did not select those categories.

---

# ⚠️ One genuine conflict you should know about

The form asks for a homepage screenshot *"con il branding di YouTube visibile"* — with
YouTube branding visible.

**Do not put the YouTube logo or wordmark on your site.** The Developer Policies prohibit
using YouTube branding without approval, and that is the same rule that stopped you naming
the app `youtubebot`. Putting the logo on your homepage to satisfy this field could create
a bigger problem than the one it solves.

What the homepage **does** have, which is legitimate: a clear statement that the tool uses
the YouTube API Services, links to the YouTube API Services Terms and Developer Policies,
and a disclaimer that it is not affiliated with or endorsed by YouTube.

If the reviewer insists on visible branding, reply and ask rather than guessing:

```
The evidence request asks for a homepage screenshot showing YouTube branding. My client
is a personal desktop tool and the Developer Policies prohibit using YouTube branding
without written approval, so I have not displayed the logo. The homepage states that the
tool uses the YouTube API Services and links to the API Services Terms and Developer
Policies. Please let me know if you need anything further here.
```

---

# Before you submit

1. **Enable GitHub Pages** so the homepage URL works:
   repo → **Settings** → **Pages** → Source: **Deploy from a branch** →
   Branch: `main`, folder: `/docs` → Save.
   Live at `https://dreamer2664.github.io/youtubebot/` within a minute or two.
2. **Change the app name** to `Curiosity Compass` at
   `https://console.cloud.google.com/auth/branding?project=my-uploader-508220` so it
   matches the form.
3. **Confirm the project number** `40430168862` on the Google Cloud welcome card.
4. Take the four screenshots and drop them in `docs/`.
