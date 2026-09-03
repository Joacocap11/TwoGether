# TwoGether mobile

Expo Router app for the existing TwoGether FastAPI service. The app is online-only: there is no offline cache, Redux store, or mobile-specific API.

## Configure the API

1. Copy `.env.example` to `.env` and set `EXPO_PUBLIC_API_BASE_URL` to a reachable API origin, such as `http://192.168.x.x:8000` or the WireGuard address. A URL ending in `/api/v1` is also accepted. Do not commit `.env` and do not use a production IP in source.
2. If the API is only reachable over WireGuard, install/configure the WireGuard client on the phone and connect the tunnel before starting the app. Ensure the API host and port are allowed through the tunnel/firewall.
3. Plain HTTP works for local development/tunnel networks. Android release builds (including the EAS `preview`/`production` APK profiles below) explicitly allow cleartext traffic via the `expo-build-properties` plugin in `app.json`, since the production API is only reachable over private LAN/WireGuard HTTP, never a public IP. Do not disable that plugin without replacing the API with HTTPS first.

## Run

```sh
npm install
npm run start       # Expo dev server
npm run android     # Android emulator/device
npm run ios         # iOS simulator/device
npm run typecheck
npm run lint
```

## Build an installable Android APK

```sh
npx eas-cli build --platform android --profile preview
```

The `preview` profile (`mobile/eas.json`) produces a standalone APK (not an AAB), signed with
the Android keystore that EAS manages remotely for the `@joacocap11/twogether` project, and
bakes in `EXPO_PUBLIC_API_BASE_URL=http://192.168.1.15:3001/api/v1` — the same private LAN/
WireGuard API the web app uses. There is a `production` profile with the same settings for
parity; both currently build an internal-distribution APK, not a Play Store AAB.

To ship a new version:

1. Bump `version` in `app.json` (e.g. `1.0.1`) and increment `android.versionCode` by 1 (e.g.
   `2`). `versionCode` must always increase or Android will refuse to install the update over an
   existing install.
2. Re-run the build command above.
3. Download the `.apk` artifact EAS produces and publish it — see
   `AppDownloads/README.md` in the sibling `AppDownloads` project for the exact publish steps.

EAS reuses the same managed keystore across builds automatically; do not run `eas credentials` to
generate a new one, or existing installs will no longer accept future updates.

The app uses SecureStore for the bearer JWT. A 401 clears the session and returns to login. Login uses the API's URL-encoded OAuth form, and forced password changes must be completed before the tabs are available.

## Feature checklist

- [x] Bottom tabs: restaurants, tests, media, hotels, pull-to-refresh, loading/error/empty states.
- [x] Restaurant complete create/update payloads, UYU/USD historical currency, dish prices, ratings, category/search filters, photos and fullscreen image modal.
- [x] Tests complete create/update payloads, two outcome capture uploads, general image upload, detail/delete.
- [x] Media search/type filtering, two opinions/ratings, poster upload, detail/delete.
- [x] Hotels total price in UYU/USD, two opinions/ratings, image upload, detail/delete.
- [x] Account password change/logout and administrator user create/activate/deactivate/force-password actions.
- [x] Branding assets copied from `frontend/public/branding` into `mobile/assets`.

Dates sent to the API are ISO `YYYY-MM-DD`; API dates are displayed in the device locale (DD/MM/YYYY in Uruguay).
