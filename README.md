# Punjab Education Intelligence Platform

Working prototype for the Punjab AI-Powered Education & Learning System assignment.

This is not a question generator. It is a small education intelligence platform:

**Curriculum → Knowledge → Learning → Assessment → Diagnosis → Personalised improvement → Measurable outcomes**

## Prototype scope

- Live corpus: **Grade 7 General Science**, PCTB-aligned, **5 complete chapters**
- Architecture is grade-agnostic so the same model can later cover Grades 1–10
- Hero chapter for the demo: **Photosynthesis and Nutrition in Plants**

## Run

```bat
run.bat
```

Or:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

**Live full system (use this from any phone or computer):** [https://divx-knows-mating-berlin.trycloudflare.com/](https://divx-knows-mating-berlin.trycloudflare.com/)

The GitHub Pages link ([https://maliyounas.github.io/punjab-ai-education-system/](https://maliyounas.github.io/punjab-ai-education-system/)) redirects to that live portal. Keep this PC and the app running while you share the link.

Optional: copy `.env.example` to `.env` and add an OpenAI or Gemini key. The prototype is fully functional without a key. With a key, generation is richer while remaining constrained to retrieved textbook chunks.

## Demo accounts

| Role | Username | Password |
|---|---|---|
| Administrator | `admin` | `admin123` |
| Teacher (Ayesha Khan) | `teacher` | `teacher123` |
| Student (Ahmed Ali) | `student` | `student123` |
| Management | `director` | `director123` |

## 15-minute demo path

1. Sign in as **teacher**
2. Open **Curriculum map** — Grade → Subject → Chapter → Topic → SLO → Concept, with source citations
3. Optionally **Ingest** `sample_curriculum/grade7_science_punjab.txt`
4. **Smart learning** on Chapter 2 Photosynthesis
5. **Generate** a quiz / homework / exam from the knowledge base
6. **Review & publish** (students cannot see AI items before approval)
7. Sign in as **student** (Ahmed), attempt the diagnostic, read the gap narrative
8. Generate targeted practice and open the **student dashboard**
9. Teacher copilot: “Show which SLOs students are struggling with”
10. Management **Punjab view**: student → class → school → district → Punjab

Ahmed’s seeded diagnostic already shows the assignment’s required story: he recalls the definition and equation of photosynthesis, but is weak at applying limiting factors and explaining how raw materials enter the leaf.

## Stack

HTML / CSS / JavaScript · FastAPI · SQLite · document parsing (PDF/DOCX) · TF-IDF retrieval over curriculum chunks · optional LLM

## Government-facing controls already in the prototype

- Urdu / English UI toggle
- Teacher review before publishing AI content
- Source references on generated items
- Audit log
- Curriculum version record
- Age-appropriate filter on generated text
- Student data limited to class analytics (no open PII export)
