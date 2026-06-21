# KANHAV: — Flask Portfolio

A dark, editorial personal portfolio built with Python + Flask.

## Project Structure

```
kanhav/
├── app.py               ← Flask app, routes & all site data
├── requirements.txt
├── templates/
│   └── index.html       ← Jinja2 template
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the development server
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

## Customising Content

All site content lives in `app.py` — no HTML editing needed:

- **`SITE_DATA`** — name, tagline, year
- **`PROJECTS`** — list of project dicts (id, name, description, tags, span)
- **`ABOUT`** — bio paragraphs, stats, skills list
- **`AIM`** — the three pillars and manifesto quote

### Example: adding a new project

```python
PROJECTS.append({
    "id": "005",
    "name": "MY NEW PROJECT",
    "description": "What it does.",
    "tags": ["Tag1", "Tag2"],
    "span": 6,   # out of 12 grid columns
})
```

## API Endpoints

The app also exposes JSON endpoints:

| Endpoint        | Returns          |
|-----------------|------------------|
| `GET /`         | Full HTML page   |
| `GET /api/projects` | Projects JSON |
| `GET /api/about`    | About JSON    |
| `GET /api/aim`      | A.I.M JSON    |
