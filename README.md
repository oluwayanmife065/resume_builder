# Resume Builder (Career Agent)

Local, privacy-first career agent that ingests master career profiles, writing samples, and target job descriptions to produce ATS-tailored resumes and cover letters compiled directly to PDF.

## Tech Stack
- **Python 3.11+**
- **Ollama** (local `qwen2.5:14b`)
- **Pydantic v2** (schema validation & grammar-constrained LLM output)
- **Jinja2 + Typst CLI** (deterministic PDF compilation)
- **Typer** (CLI interface)

## Project Structure
```
Resume Creator/
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── main.py
├── data/
│   ├── master_profile.json
│   ├── target_jd.txt
│   └── voice_samples/
├── templates/
│   ├── resume.typ.jinja
│   └── cover_letter.typ.jinja
└── src/
    ├── __init__.py
    ├── schema.py
    ├── extractor.py
    ├── generator.py
    └── compiler.py
```

# resume_builder
