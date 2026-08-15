# AI Video Production Assistant

A small Python project that turns a video topic into a scene-by-scene
production guide with scripts, supporting images, on-screen text, editing
notes, and estimated durations.

The planned V1 workflow is:

```text
Topic
  -> Planning Agent
  -> Production Agent
  -> Image Agent
  -> Composer Agent
  -> production-guide.md
```

See `overallplan.md` for the complete V1 plan and `imageplan.md` for the
original picture-agent plan.

## Current status

The repository has been reorganized for the V1 architecture. The existing
picture-search workflow remains runnable while the four production stages are
implemented incrementally.

```text
aiagent/
├── main.py
├── config.py
├── models.py
├── agents/
│   ├── planning.py
│   ├── production.py
│   ├── image.py
│   └── composer.py
├── tools/
│   ├── browser.py
│   ├── downloader.py
│   └── selector.py
└── output/
```

At this milestone, `main.py` still runs the original picture-agent flow. The
agent modules are the scaffold for the next implementation steps.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Add an OpenAI API key to `.env`, then run:

```bash
python main.py
```

The image search uses an existing Google Chrome installation, so no Playwright
browser download is required.
