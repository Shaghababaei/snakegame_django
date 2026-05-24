# Snake Game Django

A simple Django web app for playing Snake in the browser and saving high scores
to a SQLite database.

## Features

- Browser-based Snake game rendered with an HTML canvas
- Player name entry before starting a game
- Score submission through a Django JSON endpoint
- Leaderboard page showing the top scores
- Django admin support for viewing players and scores

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
│   ├── views.py            # Game, leaderboard, and score API views
│   ├── urls.py             # App URL routes
│   └── templates/game/     # Game and leaderboard templates
├── manage.py               # Django management script
├── db.sqlite3              # Local SQLite database
└── venv/                   # Local virtual environment
```

## Getting Started

### 1. Clone or open the project

```bash
cd /Users/miss.babaee1377gmail.com/Desktop/django_snake
```

### 2. Activate the virtual environment

The project already includes a local virtual environment:

```bash
source venv/bin/activate
```

If you want to recreate the environment instead:

```bash
python3 -m venv venv
source venv/bin/activate
pip install Django
```

### 3. Apply database migrations

```bash
python manage.py migrate
```

### 4. Run the development server

```bash
python manage.py runserver
```

Open the app at:

```text
http://127.0.0.1:8000/
```

## App Routes

| Route | Description |
| --- | --- |
| `/` | Play the Snake game |
| `/leaderboard/` | View saved high scores |
| `/api/submit_score/` | Submit a score with JSON |
| `/admin/` | Django admin panel |

## Score API

The game submits scores automatically when a game ends. The API expects a POST
request with JSON:

```json
{
  "name": "Player Name",
  "points": 120
}
```

Successful response:

```json
{
  "status": "ok"
}
```

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

- Scores are ordered by highest points first, then newest score.
- The database uses SQLite by default and is stored in `db.sqlite3`.
- `DEBUG` is enabled, so this configuration is intended for local development.
