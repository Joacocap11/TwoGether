# TwoGether mobile

Expo Router app for the existing TwoGether FastAPI service. The app is online-only: there is no offline cache, Redux store, or mobile-specific API.

## Configure the API

1. Copy `.env.example` to `.env` and set `EXPO_PUBLIC_API_BASE_URL` to a reachable API origin, such as `http://192.168.x.x:8000` or the WireGuard address. A URL ending in `/api/v1` is also accepted. Do not commit `.env` and do not use a production IP in source.
2. If the API is only reachable over WireGuard, install/configure the WireGuard client on the phone and connect the tunnel before starting the app. Ensure the API host and port are allowed through the tunnel/firewall.
3. Plain HTTP is suitable only for local development/tunnel networks. Android and iOS may block cleartext HTTP in production builds; use HTTPS for deployed builds and configure the server certificate.

## Run

```sh
npm install
npm run start       # Expo dev server
npm run android     # Android emulator/device
npm run ios         # iOS simulator/device
npm run typecheck
npm run lint
```

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
