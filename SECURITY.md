# Security policy

## Secrets

- All credentials belong in `.env`, which is git-ignored.
- `.env.example` must contain placeholders only.
- Never commit API keys, bot tokens, database tokens, or service-account JSON files.
- If a secret is exposed, **revoke it first**, then rotate it. Removing a commit is not enough because the old commit may still be accessible.

## Reporting

If you find a security issue in this project, please contact the maintainer through GitHub rather than opening a public issue with exploit details.

## Data handling

- Homework photos are processed for OCR; the app does not intentionally retain them after the response.
- Conversation memory is scoped to a user session; the bot does not ask for or build personal profiles.
- Avoid putting personal data in logs; review log output before sharing it.
