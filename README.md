# Smart Door Server

Flask backend for a multi-user smart-home door sensor product. Mobile app users can register, create doors, register per-door device tokens, and receive updates when an ESP32-C3 posts door status changes.


## Project Structure

```text
Server/
├── app.py                 # Flask entrypoint
├── app/
│   ├── __init__.py        # application factory
│   ├── config.py          # env-based config
│   ├── extensions.py      # db, migrate, jwt
│   ├── models.py          # User, Door, DoorEvent, PushDevice
│   ├── routes/            # auth, door, device, push APIs
│   ├── schemas/           # request validation helpers
│   ├── services/          # domain services and notifications
│   └── serializers.py     # JSON response shaping
├── migrations/            # Alembic/Flask-Migrate migrations
├── tests/                 # pytest API coverage
├── requirements.txt
└── .env.example
```

## Setup

```bash
cd Smart-Door
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r Server/requirements.txt
cp Server/.env.example Server/.env
```

Set strong secrets in `Server/.env`:

```env
APP_ENV=development
FLASK_APP=app.py
SECRET_KEY=replace-with-a-random-secret-at-least-32-bytes
JWT_SECRET_KEY=replace-with-a-different-random-secret-at-least-32-bytes
DATABASE_URL=sqlite:///smart_door.sqlite3
CORS_ORIGINS=
NOTIFICATIONS_ENABLED=true
```

## Database

Run migrations from the `Server/` directory:

```bash
cd Server
flask db upgrade
```

For a new migration after model changes:

```bash
flask db migrate -m "describe change"
flask db upgrade
```

## Run

```bash
cd Server
flask run --host 0.0.0.0 --port 5000
```

Or:

```bash
python3 Server/app.py
```

## Tests

```bash
python3 -m pytest Server/tests
```

## API

All app-owned endpoints return JSON and use a Bearer token from login/register:

```bash
Authorization: Bearer <access_token>
```

### Register

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123","name":"Amitai"}'
```

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

### Current User

```bash
curl http://localhost:5000/api/me \
  -H "Authorization: Bearer <access_token>"
```

### Create Door

The mobile app generates a unique secret token, sends it to the server, then sends the same token to the ESP32-C3 over BLE. The server stores only a SHA-256 hash of the token.

```bash
curl -X POST http://localhost:5000/api/doors \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Front Door","location":"Entrance","token":"unique-secret-token-generated-by-app"}'
```

### List Doors

```bash
curl http://localhost:5000/api/doors \
  -H "Authorization: Bearer <access_token>"
```

### ESP32-C3 Status Update

```bash
curl -X POST http://localhost:5000/api/door-status \
  -H "Content-Type: application/json" \
  -d '{"token":"unique-secret-token-generated-by-app","status":"opened","battery_mv":3100,"device":"TzufGuard-ABC123"}'
```

Valid statuses are `opened` and `closed`. Unknown device tokens return `404` with code `unknown_door_token`.

### Register Push Token

```bash
curl -X POST http://localhost:5000/api/push-devices \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"platform":"android","push_token":"fcm-or-expo-token"}'
```

Push delivery currently uses a mock notification service that logs outgoing notifications. Replace `NotificationService.send_push` in `Server/app/services/notifications.py` with Firebase/FCM delivery when credentials are available.

## Security Notes

- Passwords are hashed with Werkzeug.
- Door tokens are treated as secrets and stored as SHA-256 hashes.
- Door tokens are never returned by API responses.
- Users can only access doors linked to their own account.
- Auth endpoints are structured so a rate limiter can be added at the blueprint/app boundary.
- CORS is disabled unless `CORS_ORIGINS` is configured.
