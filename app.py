from flask import Flask, render_template, jsonify

app = Flask(__name__)

# ── Data ────────────────────────────────────────────────────────────────────

SITE_DATA = {
    "name": "KANHAV",
    "tagline": "Designer, builder, and thinker — crafting experiences that live at the intersection of code and intention.",
    "year": 2025,
}

PROJECTS = [
    {
        "id": "001",
        "name": "NEURAL CANVAS",
        "description": "A generative art system that translates emotion into visual language using machine learning and real-time rendering.",
        "tags": ["ML", "WebGL", "Generative"],
        "span": 7,
    },
    {
        "id": "002",
        "name": "VOID OS",
        "description": "Minimal operating system UI concept — rethinking the desktop metaphor from first principles.",
        "tags": ["UX", "Systems"],
        "span": 5,
    },
    {
        "id": "003",
        "name": "FREQ",
        "description": "Music visualizer that transforms audio frequencies into 3D sculptural forms.",
        "tags": ["Three.js", "Audio"],
        "span": 4,
    },
    {
        "id": "004",
        "name": "CARTOGRAPHY OF THOUGHT",
        "description": "An interactive knowledge graph that maps conceptual connections across disciplines — philosophy, mathematics, design, and engineering — revealing emergent patterns.",
        "tags": ["D3.js", "Graph Theory", "Data Vis"],
        "span": 8,
    },
]

ABOUT = {
    "bio": [
        "I'm <strong>Kanhav</strong> — a builder at the intersection of design and technology.",
        "My work explores how <strong>systems think</strong>, how <strong>interfaces feel</strong>, and how the tools we build shape the minds that use them. I believe in making things that are rigorous without being rigid, and aesthetic without being hollow.",
        "Currently focused on <strong>AI-native experiences</strong>, creative computation, and the philosophy of building.",
    ],
    "stats": [
        {"value": "12+", "label": "Projects Built"},
        {"value": "4",   "label": "Years Crafting"},
        {"value": "∞",   "label": "Curiosity"},
        {"value": "01",  "label": "Philosophy"},
    ],
    "skills": [
        "Design Systems", "React", "Python", "Machine Learning",
        "Three.js", "Typography", "Motion Design", "WebGL",
    ],
}

AIM = {
    "pillars": [
        {
            "letter": "A",
            "icon": "◈",
            "heading": "AMBITION",
            "desc": "Setting targets that feel impossible until they're not. Ambition without ego — fueled by genuine curiosity about what's achievable.",
            "num": "01 of 03",
        },
        {
            "letter": "I",
            "icon": "◉",
            "heading": "INTENTION",
            "desc": "Every pixel, every line of code, every decision carries weight. Intention means knowing *why* before knowing *how*.",
            "num": "02 of 03",
        },
        {
            "letter": "M",
            "icon": "◇",
            "heading": "MASTERY",
            "desc": "The endless pursuit of depth over breadth. Mastery is not a destination — it's the discipline of staying a student forever.",
            "num": "03 of 03",
        },
    ],
    "manifesto": "Build things that matter. Think in systems. Stay uncomfortable. The best work happens at the edge of what you know and what you dare to learn.",
    "manifesto_attr": "— Kanhav, on making",
}


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template(
        "index.html",
        site=SITE_DATA,
        projects=PROJECTS,
        about=ABOUT,
        aim=AIM,
    )


@app.route("/api/projects")
def api_projects():
    return jsonify(PROJECTS)


@app.route("/api/about")
def api_about():
    return jsonify(ABOUT)


@app.route("/api/aim")
def api_aim():
    return jsonify(AIM)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀  KANHAV: running at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
