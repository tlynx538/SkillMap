# Skill Map – Skills DNA Extractor

> Turn your resume into a graph‑based skill map.  
> Inspired by modern AI recruiting platforms (Workday Skills Cloud, Oracle Intelligent Matching).

This project implements a **full‑stack tool** that extracts a candidate’s “Skills DNA” from unstructured resume text using AI (Groq), stores it in a graph database (PostgreSQL + NetworkX), and visualises it as an interactive skill graph. The goal is to move beyond simple keyword lists and reveal **depth, recency, cross‑domain bridges, and evidence density** – exactly how modern talent platforms evaluate candidates.

---
## 📄 Motivation & Industry Context

Modern AI‑driven recruiting platforms (Workday, Oracle Taleo) no longer rely on simple keyword searches. They build a **mathematical and categorical representation** of a candidate’s potential – a “Skills DNA”.

- **Workday Skills Cloud** infers skills from plain text (job history, projects, certifications) using machine learning, maps them to a central ontology (e.g., “ML” = “Machine Learning”), and validates them with **duration, recency, and relevance**.
- **Oracle Intelligent Matching** converts resumes into mathematical representations, uses contextual NLP to disambiguate terms (e.g., “Java” the language vs. “Java” coffee), and returns a **star‑rated scorecard**.
- **Resume parsing** extracts experience markers, education, proficiency levels (beginner → expert), and conceptual themes (leadership, cloud architecture).

This project mimics those extraction mechanics and provides an **interactive graph** that shows exactly where your Skills DNA is strong (clusters, edges, bridge nodes) and where it needs work (isolates, weak evidence).

**Acknowledgement:** The core idea and methodology are based on the article  
[“Why Engineers Need a Skill Graph, Not a List”](https://skillgraph.medium.com/why-engineers-need-a-skill-graph-not-a-list-3b15c682545e) by Vinayak Jaiwant Mooliyil.

---

## 🚀 Features

- **AI‑powered skill extraction** – paste any resume/project text → Groq (Llama 3.3‑70B) extracts skills, depth scores (1‑5), recency scores (1‑5), and **edges** (which skills were used together on a specific project with outcomes).
- **Multi‑resume history** – each import creates a new independent resume session. Switch between them via dropdown.
- **Interactive skill graph** – built with Cytoscape.js. Nodes = skills, edges = projects. Coloured by clusters, bridges, isolates. Node size = depth.
- **Evidence density metrics** –  
  - *Skill Coverage Score* = total skills.  
  - *Evidence Density Score* = % of skills that have at least one edge (project evidence).  
  - Shows strongly evidenced skills (with edges) vs weakly evidenced skills (need better resume bullets).
- **Full analysis** – automatically detects **clusters** (areas of depth), **bridge nodes** (cross‑domain leverage), and **isolates** (unconnected skills).
- **Print‑ready report** – click “Print Page” to save as PDF with the exact graph, metrics, and tables.
- **No user accounts** – stateless, single‑user local tool.

---

## 🧱 Technology Stack

| Component       | Technology                                                                 |
|----------------|----------------------------------------------------------------------------|
| **Backend**     | FastAPI + SQLAlchemy (async) + PostgreSQL + NetworkX + Groq (AI)           |
| **Frontend**    | React + TypeScript + Tailwind CSS + Cytoscape.js + Vite                    |
| **AI Model**    | Groq (`llama-3.3-70b-versatile`) – free tier, 30 req/min                   |
| **Database**    | PostgreSQL (local)                                                         |
| **Package mgr** | `uv` (backend) + `yarn` (frontend)                                         |

---

---

## 🔧 Installation & Setup

### Prerequisites

- PostgreSQL (local) – [Download](https://www.postgresql.org/download/)
- Python 3.11+ with `uv` – `pip install uv`
- Node.js 18+ with `yarn` – `npm install -g yarn`
- Groq API key – [Get free key](https://console.groq.com)

### 1. Clone & prepare backend
```bash
cd backend
uv venv
source .venv/bin/activate        # or .venv\Scripts\activate on Windows
uv sync              # installs dependencies from pyproject.toml
```

### 2. Create PostgreSQL database
```bash
sudo -u postgres psql
CREATE USER skillmap WITH PASSWORD 'skillmap';
CREATE DATABASE skillgraph OWNER skillmap;
GRANT ALL PRIVILEGES ON DATABASE skillgraph TO skillmap;
\q
```

### 3. Run backend
```bash
python run.py
```
The first start automatically creates tables (resumes, skills, edges, artifacts).
API will be available at `http://localhost:8000`. Interactive docs: `http://localhost:8000/docs`

### 4. Frontend
```bash
cd ../frontend
yarn install
yarn dev
```
Open `http://localhost:5173.`

## 🖥️ Usage
- Import a resume – paste any text (resume, project notes, GitHub README). Optionally give it a name.

- AI extracts – skills (depth/recency) and edges (skill pairs with project/outcome).

- Review & adjust – tweak depth/recency sliders, add manual edges, attach artifacts (optional).

- Switch between resumes – use the dropdown in the header.

- Explore the graph – see clusters, bridge nodes, isolates. Click “Print Page” to save as PDF.

- Actionable insights – weakly evidenced skills tell you exactly which bullet points need strengthening.

## 📊 Example Analysis Output
- Skill Coverage Score: 25 skills

- Evidence Density Score: 48% (12 edges)

- Strongly Evidenced: Python, FastAPI, RabbitMQ, Celery, Redis, PyTorch

- Weakly Evidenced: SQL, Power BI, Airflow, DBT, Snowflake, Odoo

> The tool tells you exactly which skills need stronger project narratives.

# 🧠 How It Works (Skills DNA Extraction)
1. Resume text → Groq (Llama 3.3) with a structured prompt.

2. Output: JSON list of skills (depth & recency scores, evidence snippet) + edges (skill A, skill B, project, outcome).

3. Backend stores them in PostgreSQL with a resume_id.

4. NetworkX builds graph → computes connected components (clusters), isolates, and bridge nodes.

5. Frontend renders interactive graph (Cytoscape) and metrics.

> The depth/recency scoring follows the article’s 1‑5 scale (1 = heard of it, 5 = designed/taught in production). Edges require a specific project + outcome – this eliminates hollow keywords and surfaces genuine experience.

## 🙏 Acknowledgements
- Article – [[Why Engineers Need a Skill Graph, Not a List](https://skillgraph.medium.com/why-engineers-need-a-skill-graph-not-a-list-3b15c682545e)] 

- Groq – free AI inference that makes parsing affordable.

- FastAPI, SQLAlchemy, NetworkX – robust backend stack.

- Cytoscape.js – beautiful interactive graphs.

- Tailwind CSS – rapid UI styling.

## 📝 License
MIT – feel free to use, modify, and deploy for your own skill mapping needs.

Built as a practical implementation of the “Skill Graph” methodology.

Now go and build your Skills DNA – one edge at a time.

---