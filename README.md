# AI Video Production Assistant

A small Python project that turns a video topic into a beat-by-beat
production guide with scripts, supporting images, on-screen text, editing
notes, and estimated durations.

The planned V1 workflow is:

```text
Topic
  -> Planning Agent
  -> Production Agent
  -> Review/edit script.md and approve
  -> Image Agent
  -> Composer Agent
  -> production-guide.md
```

See `overallplan.md` for the complete V1 plan and `imageplan.md` for the
original picture-agent plan.

## Current status

The Planning Agent is implemented. The Production Agent is the next
test-driven milestone: its expected behavior is captured in
`tests/test_production.py`, while `agents/production.py` is intentionally left
for implementation. The reusable picture-search code remains available in
`tools/`.

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

At this milestone, `main.py` accepts a topic and prints the structured plan
created by the Planning Agent. Build the Production Agent against its tests,
then connect the documented `script.md` approval checkpoint before image work.

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
