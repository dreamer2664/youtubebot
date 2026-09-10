# YouTube Audit Form — exact answers

Form: **Modulo di controllo ed estensione della quota**
Your project ID: `my-uploader-508220`

Copy each block into the matching field. `[BRACKETS]` = you fill in.

> **The one rule:** be truthful. They reject applications that overclaim, and a personal
> tool pretending to be a company is the fastest route to a no. Everything below is
> written to be accurate as well as favourable.

---

## Sezione 1 — Tipo di richiesta

**Seleziona il motivo della richiesta** →
✅ **Completamento di una verifica di conformità per richiedere una quota aggiuntiva**

(First option. The form states every quota request includes a compliance audit, so this
single submission does both — you get audited *and* the private lock lifted.)

---

## Sezione 2 — Organizzazione e dati di contatto

| Field | Put this |
|---|---|
| **Presenti questa richiesta** | ✅ **In qualità di utente privato** |
| **Il tuo nome legale completo** | `Carlo Rella` |
| **Il nome legale della tua organizzazione** | `Utente stesso` |
| **Nome della società madre** | `Utente stesso` |
| **Sito web principale dell'organizzazione** | `https://github.com/dreamer2664/youtubebot` |
| **Indirizzo sede legale** | ⚠️ **your real home address** — do not invent one. This is a legal contact field and Google uses it to reach you about compliance. Street, city (Milano), province (MI), CAP. |
| **Categoria** | ⚠️ I can't see the dropdown options. Pick whichever is closest to *"Intrattenimento / Media e contenuti"* or *"Creazione di contenuti"*. Tell me the list and I'll pick. |
| **Dimensioni/tipo di organizzazione** | ✅ **Sviluppatore autonomo/impresa individuale** |

**Dati del contatto principale**

| Field | Put this |
|---|---|
| Nome | `Carlo Rella` |
| Email | ⚠️ **the same Google account that owns the project** |
| Contatto tecnico | ✅ **Coincide con il contatto principale** |
| Contatto commerciale | ✅ **Coincide con il contatto principale** |

---

## Sezione 3 — Modello di business e contatti Google

**Descrivi l'operato della tua organizzazione in relazione a YouTube** →

```
I am a private individual who creates and publishes original short-form videos to a
single YouTube channel that I own and operate myself.

I built a personal desktop tool, youtubebot, to help me produce those videos
consistently. It runs only on my own computer and has no users other than me. The
workflow is:

1. It drafts a short script on a topic I choose, using a text model.
2. It generates a voiceover and a set of still images.
3. It assembles those into a video file locally with FFmpeg.
4. It uploads that file to my own channel via videos.insert.

Every video is reviewed by me before it is published. All content is original to my
channel and I hold the rights to it.

The value to YouTube is a steady stream of original, topical content on my channel,
produced more consistently than I could manage entirely by hand. The tool exists purely
to publish my own content to my own channel. It is not a service for other people, it
has no users, and it does not access, aggregate or redistribute anyone else's data or
content.

I use only the endpoints I need: videos.insert to upload, videos.list to check
processing status, videos.update to correct metadata, thumbnails.set for thumbnails,
and channels.list to confirm which channel is authorised. My usage is 1 to 3 uploads
per day, far below the default allocation.
```

**Chi è il tuo pubblico di destinazione** →
✅ **Singoli creator di contenuti (YouTuber, influencer)**

**In che modo il tuo client API monetizza** →
✅ **Servizio senza costi (nessun costo addebitato agli utenti)**

**Attualmente hai un Google Partner Manager** →
✅ **No, non ho un rappresentante di Google**

**Come hai scoperto l'API YouTube Data** →
```
Through the official YouTube Data API documentation on developers.google.com.
```

**ID proprietario dei contenuti** → leave empty
**ID cliente Google Ads** → leave empty

---

## Sezione 4 — Panoramica del client API

| Field | Put this |
|---|---|
| **Nome del client API** | `youtubebot` |
| **Il nome contiene "YouTube"?** | ✅ **No, il nome non include "YouTube"** |
| **URL di accesso principale** | `https://github.com/dreamer2664/youtubebot` |
| **URL delle norme sulla privacy** | `https://github.com/dreamer2664/youtubebot/blob/main/PRIVACY.md` |
| **URL dei Termini di servizio** | leave empty |
| **Il tuo client API è accessibile pubblicamente?** | ✅ **No** |

> On that last one: the honest answer is **No** — it is a tool on your own computer, not
> a public service. Don't say yes to look bigger. They can check, and an inconsistency
> here is worse than a small tool.

---

## Sezione 5 — Casi d'uso e dettagli dell'estensione della quota

**Quanti numeri di progetto intendi aggiungere?** →
```
1
```

That project is `my-uploader-508220`. **Use exactly one project** — several projects to
multiply quota is a documented ToS violation and Google suspends accounts for it.

---

## Sezione 6 — Prove e documentazione

Optional, but it genuinely helps. The form says file upload is simulated, so if it will
not accept uploads, describe them in the text fields instead.

- **Diagramma dell'architettura** → `docs/architecture.png` in this repo
- **Diagramma dei flussi utente** → same image, or leave empty
- **Altri materiali di supporto** → a screenshot of the tool running and producing a video

Quality bar they state: 1280×720 or better, readable text, under 10 MB.

---

## Sezione 7 — Attestazioni

Tick **all** of them. You are confirming you read the ToS and developer policies, that
your answers are accurate, and that you consent to them processing the data. All true.

---

## After you submit

Expect weeks, and expect the possibility of this reply:

> *"Since your app is for personal use, your project does not require verification."*

That is a **non-answer** — it is about OAuth verification, not this audit, and it does
not lift the private lock. Reply to the email with:

```
Thank you. To clarify: I am not asking about OAuth app verification, and I understand a
personal-use client does not need its consent screen verified.

My request is the YouTube API compliance audit. Videos uploaded via videos.insert from
an unverified API project created after 28 July 2020 are locked to private viewing mode,
and I need that restriction lifted so the videos I upload to my own channel can be
viewed publicly. I understand this requires an API compliance audit rather than OAuth
verification.

Could you please review project my-uploader-508220 on that basis? I am happy to provide
a demonstration video of the client if that would help.
```

## Meanwhile

`generate` costs **no YouTube quota**, so build your backlog while you wait:

```powershell
python main.py generate --count 10
```
