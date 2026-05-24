# Django Snake

A Django web app for playing Snake in the browser, saving high scores, and
showing player profile images on the leaderboard.

## Features

- Canvas-based Snake game
- Single-player and two-player modes
- Desktop keyboard controls and mobile touch controls
- Player name entry before starting a game
- Optional profile image upload for each player
- Score submission through a Django JSON endpoint
- Leaderboard showing each player's best score
- Django admin screens for players and scores

## Tech Stack

- Python 3
- Django 6.0.4
- SQLite
- HTML, CSS, and JavaScript

## Project Structure

```text
.
├── config/                 # Django project settings and root URLs
├── game/                   # Snake game app
│   ├── models.py           # Player and Score models
│   ├── views.py            # Game, leaderboard, and API views
│   ├── urls.py             # App URL routes
│   └── templates/game/     # Game and leaderboard templates
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── media/                  # Uploaded profile images, created locally
```

## Getting Started

### 1. Open the project

```bash
cd /Users/miss.babaee1377gmail.com/Desktop/django_snake
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Run the development server

```bash
python manage.py runserver
```

Open the app at:

```text
http://127.0.0.1:8000/
```

## Controls

| Mode | Player | Controls |
| --- | --- | --- |
| Single player | Player 1 | Arrow keys or on-screen touch buttons |
| Two players | Player 1 | Arrow keys |
| Two players | Player 2 | W, A, S, D |

## Playing Together

Two users can play on the same keyboard by selecting `Two Players` before
starting the game. Player 1 enters a name and uses the arrow keys. Player 2
enters a separate name and uses `W`, `A`, `S`, and `D`.

Both players can save an optional profile image. When the game ends, each
player's score is submitted separately, and the leaderboard keeps each player's
best score.

## App Routes

| Route | Description |
| --- | --- |
| `/` | Play the Snake game |
| `/leaderboard/` | View saved high scores |
| `/api/leaderboard/` | Get the top 3 leaderboard users as JSON |
| `/api/leaderboard/all/` | Get all leaderboard users as JSON |
| `/api/users/<id>/profile_image/` | Get one user's profile image URL |
| `/api/submit_score/` | Submit a score with JSON |
| `/api/upload_profile_image/` | Upload a player profile image |
| `/api/schema/swagger-ui/` | Swagger UI for the API |
| `/admin/` | Django admin panel |

## Score API

The game submits scores automatically when a game ends. The endpoint stores a
score only when it is the player's first score or it beats that player's current
best score.

`POST /api/submit_score/`

```json
{
  "name": "Player Name",
  "points": 120
}
```

Successful response:

```json
{
  "status": "ok",
  "saved": true
}
```

## Leaderboard API

Returns the top 3 users by best saved score. Each user includes their player id
and profile image URL when one has been uploaded.

`GET /api/leaderboard/`

Use this endpoint for every leaderboard user:

`GET /api/leaderboard/all/`

Successful response:

```json
[
  {
    "id": 1,
    "name": "Player Name",
    "points": 120,
    "profile_image": "http://127.0.0.1:8000/media/profiles/example.webp"
  }
]
```

## Profile Image API

Returns a user's profile image URL by user id.

`GET /api/users/1/profile_image/`

Successful response when the user has an image:

```json
{
  "id": 1,
  "name": "Player Name",
  "profile_image": "http://127.0.0.1:8000/media/profiles/example.webp"
}
```

Successful response when the user has no image:

```json
{
  "id": 1,
  "name": "Player Name",
  "profile_image": null,
  "message": "user has not image profile yet"
}
```

Profile images are uploaded from the game screen. The upload must include a
player name and an image file.

`POST /api/upload_profile_image/`

Form fields:

| Field | Description |
| --- | --- |
| `name` | Player name |
| `image` | JPG, PNG, GIF, or WEBP image up to 10MB |

Successful response:

```json
{
  "status": "ok",
  "image_url": "/media/profiles/example.webp"
}
```

Uploaded files are stored under `media/profiles/` in local development.

## Admin

Create a superuser to access the admin panel:

```bash
python manage.py createsuperuser
```

Then sign in at:

```text
http://127.0.0.1:8000/admin/
```

## Running Tests

```bash
python manage.py test
```

## Development Notes

- SQLite is configured by default and uses `db.sqlite3`.
- Media files are served by Django only while `DEBUG = True`.
- The leaderboard shows up to 10 players, ordered by highest best score and then
  newest score.
- This configuration is intended for local development, not production.
