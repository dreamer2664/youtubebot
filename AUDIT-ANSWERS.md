# YouTube API Compliance Audit — copy-paste answers

The form is here: **https://support.google.com/youtube/contact/yt_api_form**

Sign in with the **same Google account that owns your Cloud project**.

Your project ID is `my-uploader-508220` (from your client_secret.json).

Fill in anything marked `[BRACKET]` and submit. Realistic time: about 10 minutes.

---

## Application / project name

```
youtubebot
```

## Project ID

```
my-uploader-508220
```

## What does your API client do?

```
youtubebot is a personal desktop tool that I built and operate myself. It generates
short educational videos about [YOUR TOPIC] and uploads them to a single YouTube
channel that I own and operate.

The workflow is: I run the tool on my own computer, it writes a script, generates
narration and still images, assembles them into a video file locally, and then uploads
that file to my own channel through videos.insert. I review every video before it is
published.

There are no other users. The only Google account that authorises this client is my
own, and the only channel it writes to is my own.
```

## Which YouTube API Services does your client use?

```
videos.insert        - uploading the generated video to my channel
videos.list          - checking upload and processing status
videos.update        - correcting metadata after upload
thumbnails.set       - setting the video thumbnail
channels.list        - confirming which channel is authorised
```

## How do users authorise access?

```
OAuth 2.0 for an installed (desktop) application, using the google-auth-oauthlib
desktop flow. There is exactly one authorising user: me.

Requested scopes:
  https://www.googleapis.com/auth/youtube.upload
  https://www.googleapis.com/auth/youtube.force-ssl

The refresh token is stored locally on my own machine with restrictive file
permissions and is never transmitted anywhere else.
```

## How is API data stored, and how is it deleted?

```
No YouTube API data leaves my computer. The only data retrieved is my own channel
metadata from channels.list and the status of videos I uploaded myself, held in a
local state file so the tool can resume after an interruption.

I do not collect, store, aggregate, sell or share any user data, and the client is
not accessible to anyone other than me.

Deleting the local state file and revoking the authorisation at
https://security.google.com/settings/security/permissions removes all of it
immediately.
```

## How can users revoke access?

```
Authorisation can be revoked at any time at
https://security.google.com/settings/security/permissions
which immediately invalidates the stored refresh token.
```

## Expected daily and peak traffic

```
Daily: 1 to 3 videos.insert calls.
Peak: no more than 5 videos.insert calls in a day.
Read calls: under 50 units per day.

This is far below the default allocation of 100 videos.insert calls and 10,000 units
per day. I am not requesting a quota extension, only the ability to publish publicly.
```

## Privacy policy URL

```
https://github.com/dreamer2664/youtubebot
```

(Your repo already states that no user data is collected. If the form insists on a
dedicated page, create `PRIVACY.md` in the repo with that one sentence and link it.)

## Why is this access necessary?

```
I want to publish the videos I generate to my own channel. Without an approved audit,
every upload is locked to private viewing mode, which defeats the purpose of the tool.
The tool exists only to publish my own original content to my own channel.
```

---

## If they reply "your project does not require verification"

This happens, and it does **not** mean you are done. That reply is about *OAuth*
verification, which is a different thing from this audit. Reply to the email:

```
Thank you. To clarify: I am not asking about OAuth app verification. I understand a
personal-use client does not need its consent screen verified.

My issue is the YouTube-specific restriction that videos uploaded via videos.insert
from an unverified API project created after 28 July 2020 are locked to private
viewing mode. I need that restriction lifted so the videos I upload to my own channel
can be viewed publicly, which I understand requires an API compliance audit rather
than OAuth verification.

Could you please review my project for that audit? Project ID: my-uploader-508220.
```

---

## While you wait

`generate` costs **no YouTube quota** and needs no audit at all. So:

```powershell
python main.py generate --count 10
```

Build the backlog now, upload the day you are approved. Nothing is wasted by waiting.
