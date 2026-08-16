# AI Video Production Assistant — V1

## 1. Goal

Build a simple **4-agent AI video production assistant**.

The user gives one topic:

> Why did Formula 1 stop using V10 engines?

The system prepares everything needed to film one continuous talking-head take and edit it into a fast, visually active reel:

* title
* video structure
* short script beats
* selective supporting-image requirements
* an editable script approval checkpoint before image searches
* downloaded supporting images
* on-screen text
* editing notes
* estimated duration (usually 1–3 seconds per beat)

The user still films themselves and assembles the final video manually.

---

# 2. V1 Workflow

```text
Topic
  ↓
Planning Agent
  ↓
Production Agent
  ↓
Script approval gate
  ↓
Image Agent
  ↓
Composer Agent
  ↓
Final production guide
```

There are **4 agents total**.

The approval gate is a human checkpoint, not another agent.

---

# 3. Agent 1 — Planning Agent

## Purpose

Turn the topic into a sequence of short, connected script beats.

It answers:

> What story should this video tell?

## Input

```text
Why did Formula 1 stop using V10 engines?
```

## Output

```json
{
  "title": "Why F1 Killed the V10",
  "hook": "F1 V10s sounded incredible, so why did Formula 1 get rid of them?",
  "beats": [
    {
      "beat": 1,
      "purpose": "Create immediate curiosity"
    },
    {
      "beat": 2,
      "purpose": "Establish why fans loved the V10"
    },
    {
      "beat": 3,
      "purpose": "Introduce the first reason regulations changed"
    },
    {
      "beat": 4,
      "purpose": "Explain the efficiency and manufacturer pressure"
    },
    {
      "beat": 5,
      "purpose": "Show what replaced the V10"
    },
    {
      "beat": 6,
      "purpose": "Deliver the payoff"
    }
  ]
}
```

## Responsibilities

The Planning Agent should generate:

* title
* hook
* overall angle
* number of short beats
* purpose of each beat

It should **not** search for images or write detailed editing instructions.

---

# 4. Agent 2 — Production Agent

## Purpose

Take the rough structure and determine exactly what the creator says in each beat and whether a supporting visual is useful.

It answers:

> What do I need to say and show?

## Input

The Planning Agent output.

## Output

For every beat:

```json
{
  "beat": 2,
  "purpose": "Establish why fans loved the V10",
  "script": "They were loud, fast, and completely unforgettable.",
  "visual_needed": true,
  "visual_type": "photo overlay",
  "picture_description": "Ferrari F2004 Formula 1 car racing on track during the V10 era",
  "search_query": "Ferrari F2004 racing V10 Formula 1 2004"
}
```

## Responsibilities

The Production Agent generates:

* one short, conversational script line per beat
* whether a supporting visual is needed
* visual type and placement when needed
* description of the desired picture when needed
* descriptive image search query when needed

The creator remains the main visual. Do not assign a picture to every beat. Some beats should intentionally be talking-head only so the edit has room to breathe.

The search query should be specific and visual.

Bad:

```text
F1 history
```

Better:

```text
Ferrari F2004 red Formula 1 car racing 2004 V10
```

---

# 5. Script Approval Gate

## Purpose

Let the creator review and edit the complete script before the system starts the expensive image workflow.

```text
Topic
  → plan
  → production script
  → write script.md
  → creator reviews and edits
  → creator presses Enter
  → image work may begin
```

The program must pause after writing:

```text
output/video-name/script.md
```

The creator can edit the spoken lines directly in that file. After Enter is pressed, the program reloads those edits and saves the approved structured production data.

No Google Images searches, candidate downloads, or vision-selection calls may run before this approval step completes successfully. If the script is wrong, the run can stop here without spending the image-search cost.

This checkpoint should remain simple. V1 does not need a GUI or approval database.

---

# 6. Agent 3 — Image Agent

## Purpose

Find the best supporting image for each beat that actually needs one.

It answers:

> Which picture best supports what this beat is saying?

## Input

For each beat where `visual_needed` is `true`:

```text
script
picture description
search query
```

## Workflow

```text
Search query
  ↓
Google Images
  ↓
Download 5 candidates
  ↓
Existing vision selector
  ↓
Choose best image
  ↓
Save selected image
```

Reuse the existing browser, downloader, and image-selection system.

## Output

Example:

```text
output/video-name/beats/beat2/selected.jpg
```

## V1 Behavior

If no good image is found:

* do not crash the entire run
* leave the creator visible with no overlay
* mark the beat as missing an image
* continue to the next beat

---

# 7. Agent 4 — Composer Agent

## Purpose

Take everything produced by the other agents and turn it into one simple production guide.

It answers:

> How should all of this be presented so I can immediately film and edit?

## Input

```text
Planning Agent output
+
Production Agent output
+
selected image paths
```

## Output Format

```markdown
# Why F1 Killed the V10

## Beat 1 (0:00–0:02)

### Script

F1 V10s sounded incredible, so why did Formula 1 get rid of them?

### Supporting visual

None — creator only

### On-screen text

Why did F1 kill the V10?

### Editing note

Start immediately on the creator. Use a quick punch-in on “V10s.”

### Estimated duration

2 seconds


## Beat 2 (0:02–0:05)

### Script

They were loud, fast, and completely unforgettable.

### Supporting visual

beats/beat2/selected.jpg

### On-screen text

LOUD. FAST. UNFORGETTABLE.

### Editing note

Keep the creator visible and place the Ferrari image above their shoulder. Remove it at the end of the beat.

### Estimated duration

3 seconds
```

## Composer Responsibilities

For each beat, the Composer produces:

* script
* selected supporting picture, if needed
* short on-screen text, only when it adds emphasis or clarity
* editing note
* estimated duration

The Composer should treat the continuous talking-head recording as the base layer. Supporting visuals usually appear as overlays around or above the creator, with occasional creator-only beats to avoid visual clutter. Full-screen B-roll should be rare and intentional.

---

# 8. Output Folder

Each run creates a new folder.

```text
output/
└── why-f1-killed-the-v10/
    │
    ├── production-guide.md
    ├── plan.json
    ├── script.md
    ├── production.json
    │
    └── beats/
        ├── beat1/
        │   ├── candidate1.jpg
        │   ├── candidate2.jpg
        │   ├── candidate3.jpg
        │   ├── candidate4.jpg
        │   ├── candidate5.jpg
        │   └── selected.jpg
        │
        ├── beat2/
        │   └── ...
        │
        └── beat3/
            └── ...
```

For V1, these are the only important final files:

```text
production-guide.md
plan.json
script.md
production.json
beats/
```

No database or frontend is needed.

---

# 9. Simple Data Models

Use Pydantic.

## Plan

```python
class PlannedBeat(BaseModel):
    beat: int
    purpose: str


class VideoPlan(BaseModel):
    title: str
    hook: str
    angle: str
    beats: list[PlannedBeat]
```

## Production Beat

```python
class ProductionBeat(BaseModel):
    beat: int
    purpose: str
    script: str
    visual_needed: bool
    visual_type: str | None
    picture_description: str | None
    search_query: str | None
```

## Final Beat

```python
class FinalBeat(BaseModel):
    beat: int
    script: str
    picture: str | None
    on_screen_text: str | None
    editing_note: str
    estimated_duration: float
```

---

# 10. File Structure

Keep V1 small.

```text
aiagent/
│
├── main.py
├── config.py
│
├── agents/
│   ├── planning.py
│   ├── production.py
│   ├── image.py
│   └── composer.py
│
├── tools/
│   ├── browser.py
│   ├── downloader.py
│   └── selector.py
│
├── models.py
├── output/
├── requirements.txt
└── README.md
```

The existing image-search code can move into `tools/` with minimal changes.

---

# 11. Main Program

Keep `main.py` simple.

```python
topic = input("What video are you making today? ")

plan = planning_agent(topic)

production = production_agent(plan)

script_path = save_script_for_review(production)

approved_production = wait_for_script_approval(
    production,
    script_path
)

images = image_agent(approved_production)

final = composer_agent(
    plan=plan,
    production=approved_production,
    images=images
)

save_production_guide(final)
```

`main.py` should orchestrate the workflow rather than contain the actual agent logic.

---

# 12. Implementation Order

## Step 1 — Planning Agent

Build:

```text
topic
↓
title
hook
angle
beat purposes
```

Test with 5 different video topics.

---

## Step 2 — Production Agent

Build:

```text
video plan
↓
short beat scripts
visual decisions
picture descriptions and search queries only where useful
```

At this point, manually inspect whether the queries would actually work in Google Images.

---

## Step 3 — Connect Existing Image Tool

Before connecting the image tool, add the human checkpoint:

```text
production output
→ write script.md
→ pause for review and edits
→ reload approved script
→ continue
```

Test that the image tool cannot be called before approval. Then reuse the current:

```text
Google Images
→ download candidates
→ AI vision selector
```

Run it only for beats that need a supporting picture.

---

## Step 4 — Composer Agent

Generate:

```text
production-guide.md
```

For every beat include:

```text
Script
Supporting visual (or creator only)
On-screen text
Editing note
Estimated duration
```

---

## Step 5 — Full Test

Run:

```bash
python main.py
```

Example:

```text
What video are you making today?

> Why did Formula 1 stop using V10 engines?

Planning video...
✓ 8 short beats created

Preparing beats...
✓ Scripts created
✓ Image queries created
✓ Script ready: output/why-f1-killed-the-v10/script.md

Review and edit script.md, save it, then press Enter to approve the script and continue to images:
✓ Script approved

Finding images...
Beat 1/8 — creator only ✓
Beat 2/8 — image selected ✓
Beat 3/8 — image selected ✓
...
Beat 8/8 — creator only ✓

Composing production guide...
✓ Done

output/why-f1-killed-the-v10/production-guide.md
```

Then actually use the guide to make one real video.

---

# 13. V1 Definition of Done

V1 is finished when:

* [ ] User enters one topic
* [ ] Planning Agent generates a useful video structure
* [ ] Planning Agent creates a fast hook with no greeting or slow setup
* [ ] Production Agent writes concise 1–3 second script beats
* [ ] Production Agent decides whether each beat needs a supporting visual
* [ ] Production Agent creates descriptive image queries only where useful
* [ ] Production Agent writes an editable `script.md`
* [ ] Program pauses for human script review
* [ ] Human edits in `script.md` are reloaded after approval
* [ ] No image searches, downloads, or vision calls happen before approval
* [ ] Image Agent searches Google Images
* [ ] Image Agent downloads candidates
* [ ] Existing vision model chooses the best candidate
* [ ] Each visual beat has a selected picture when possible
* [ ] Some beats intentionally remain creator-only
* [ ] Composer Agent generates on-screen text
* [ ] Composer Agent generates editing notes
* [ ] Composer Agent keeps the creator visible for most of the video
* [ ] Composer Agent describes overlay placement instead of defaulting to full-screen B-roll
* [ ] Composer Agent estimates beat duration
* [ ] `production-guide.md` is generated
* [ ] One failed image does not break the entire run
* [ ] The production guide is useful enough to make a real video from

---

# 14. Do Not Build Yet

Keep V1 focused.

Do not add:

* frontend
* database
* accounts
* authentication
* LangGraph
* TTS
* AI voice
* automatic video generation
* automatic video editing
* CapCut integration
* Premiere integration
* automatic posting
* analytics
* self-review agent
* web research agent
* memory
* batch videos

These can come later if the basic workflow proves useful.

---

# 15. V1 Product

The entire V1 should do one thing well:

```text
"What video am I making today?"
            ↓
       Planning Agent
            ↓
      Production Agent
            ↓
   Review/edit script.md
            ↓
       Press Enter
            ↓
        Image Agent
            ↓
       Composer Agent
            ↓
   production-guide.md
```

The final guide tells the creator:

> **what to say in each short beat, when to use a supporting visual, what text to put on screen, how to place the overlay while keeping the creator visible, and approximately how long each beat should last.**

Then the creator films and edits the video themselves.
