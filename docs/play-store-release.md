# Play Store Release Checklist

## Completed in this repository

- The frontend is installable as a standalone Progressive Web App with a manifest, app icon, theme color, and cached shell fallback.
- The frontend image accepts `NEXT_PUBLIC_API_URL` at build time.
- The API CORS allowlist is configured through `CORS_ORIGINS`.

## Before an Android build

1. Deploy the frontend and API on public HTTPS domains. Set `NEXT_PUBLIC_API_URL` to the public API URL while building the frontend image and set `CORS_ORIGINS` to the public frontend origin.
2. Use a managed PostgreSQL instance, a unique long `JWT_SECRET_KEY`, TLS, backups, error monitoring, and a production OpenAI key only through the hosting platform's secret store.
3. Test registration, login, diagnostic submission, a lesson, a topic quiz, sign-out, and an expired session on physical Android devices.
4. Publish a public privacy policy covering account data, learning responses, analytics, data retention, deletion requests, and any AI provider processing. Add a support email and a data-deletion contact path.

## Android and Play Console

1. Package the deployed HTTPS app with a Trusted Web Activity or Capacitor. Do not package `localhost`; an Android release must point at the deployed domain.
2. Create a unique package name such as `com.praneetha.adaptiveai`, configure an adaptive launcher icon, increment `versionCode` for every release, and generate a signed Android App Bundle (`.aab`).
3. Target Android API 36 or higher for new submissions from August 31, 2026. See the [official target API guidance](https://developer.android.com/google/play/requirements/target-sdk).
4. Complete Play Console identity verification and package-name registration, configure Play App Signing, and use internal testing before production.
5. Prepare the store listing: app name, short/full descriptions, 512px icon, feature graphic, phone screenshots, category, support email, privacy-policy URL, Data safety form, and content rating.

## Release gate

Do not submit until the public HTTPS deployment, privacy policy, signed `.aab`, internal test pass, and Play Console declarations are complete. A Google Play account and the signing/verification actions cannot be created from this repository.
