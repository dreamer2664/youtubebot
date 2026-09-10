# Privacy Policy

**Last updated:** 10 September 2026

## Summary

youtubebot is a personal desktop tool operated by a single individual. It has no users
other than its owner, no accounts, no servers, and no analytics. **It collects no user
data.**

## What the tool does

youtubebot generates short original videos and uploads them to one YouTube channel owned
and operated by the same individual. It runs entirely on that person's own computer.

## What data is accessed

The tool accesses only the Google account and YouTube channel of the person running it,
through OAuth 2.0, using these scopes:

- `https://www.googleapis.com/auth/youtube.upload`
- `https://www.googleapis.com/auth/youtube.force-ssl`

The only data retrieved from the YouTube Data API is:

- the owner's own channel metadata (`channels.list`)
- the upload and processing status of videos the owner uploaded (`videos.list`)

## What data is stored

A small local state file on the owner's own machine, containing the IDs and status of
videos that the owner uploaded. This exists only so the tool can resume after an
interruption.

OAuth credentials are stored locally with restrictive file permissions and are never
transmitted to any third party.

## What data is shared

None. No data is sold, rented, aggregated, or shared with anyone. There is no server,
database, or third-party service involved other than Google's own APIs.

## Children

The tool collects no data from anyone and is not directed at children.

## Data retention and deletion

All data remains on the owner's own device. Deleting the local state file and revoking
access at <https://security.google.com/settings/security/permissions> removes everything
immediately.

## Contact

Via the issue tracker of this repository.

## Revoking access

Authorisation can be revoked at any time at
<https://security.google.com/settings/security/permissions>, which immediately
invalidates the stored credentials.
