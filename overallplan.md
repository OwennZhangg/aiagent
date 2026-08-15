# AI Video Production Assistant — V1

## 1. Goal

Build a simple **4-agent AI video production assistant**.

The user gives one topic:

> Why did Formula 1 stop using V10 engines?

The system prepares everything needed to film and edit the video:

* title
* video structure
* scene scripts
* image requirements
* downloaded supporting images
* on-screen text
* editing notes
* estimated duration

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
Image Agent
  ↓
Composer Agent
  ↓
Final production guide
```

There are **4 agents total**.

---

# 3. Agent 1 — Planning Agent

## Purpose

Turn the topic into a rough video structure.

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
  "scenes": [
    {
      "scene": 1,
      "purpose": "Hook the viewer"
    },
    {
      "scene": 2,
      "purpose": "Explain the V10 era"
    },
    {
      "scene": 3,
      "purpose": "Explain why regulations changed"
    },
    {
      "scene": 4,
      "purpose": "Explain what replaced the V10"
    },
    {
      "scene": 5,
      "purpose": "Give a short conclusion"
    }
  ]
}
```

## Responsibilities

The Planning Agent should generate:

* title
* hook
* overall angle
* number of scenes
* purpose of each scene

It should **not** search for images or write detailed editing instructions.

---

# 4. Agent 2 — Production Agent

## Purpose

Take the rough structure and determine exactly what is needed for each scene.

It answers:

> What do I need to say and show?

## Input

The Planning Agent output.

## Output

For every scene:

```json
{
  "scene": 2,
  "purpose": "Explain the V10 era",
  "script": "In the early 2000s, Formula 1 cars used screaming 3-litre V10 engines.",
  "picture_description": "Ferrari F2004 Formula 1 car racing on track during the V10 era",
  "search_query": "Ferrari F2004 racing V10 Formula 1 2004"
}
```

## Responsibilities

The Production Agent generates:

* final scene script
* description of the desired picture
* descriptive image search query

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

# 5. Agent 3 — Image Agent

## Purpose

Find the best supporting image for each scene.

It answers:

> Which picture best matches what this scene needs?

## Input

For each scene:

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
output/video-name/scenes/scene2/selected.jpg
```

## V1 Behavior

If no good image is found:

* do not crash the entire run
* mark the scene as missing an image
* continue to the next scene

---

# 6. Agent 4 — Composer Agent

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

## Scene 1

### Script

F1 V10s sounded incredible, so why did Formula 1 get rid of them?

### Picture

scenes/scene1/selected.jpg

### On-screen text

Why did F1 kill the V10?

### Editing note

Start with the talking-head shot. Cut to the F1 image immediately after saying "V10s."

### Estimated duration

4 seconds


## Scene 2

### Script

In the early 2000s, Formula 1 cars used screaming 3-litre V10 engines.

### Picture

scenes/scene2/selected.jpg

### On-screen text

3.0L V10

### Editing note

Show the Ferrari image while mentioning the V10 era, then return to the talking-head shot.

### Estimated duration

7 seconds
```

## Composer Responsibilities

For each scene, the Composer produces:

* script
* selected picture
* on-screen text
* editing note
* estimated duration

The Composer should make the result clean and easy to follow while filming and editing.

---

# 7. Output Folder

Each run creates a new folder.

```text
output/
└── why-f1-killed-the-v10/
    │
    ├── production-guide.md
    ├── plan.json
    │
    └── scenes/
        ├── scene1/
        │   ├── candidate1.jpg
        │   ├── candidate2.jpg
        │   ├── candidate3.jpg
        │   ├── candidate4.jpg
        │   ├── candidate5.jpg
        │   └── selected.jpg
        │
        ├── scene2/
        │   └── ...
        │
        └── scene3/
            └── ...
```

For V1, these are the only important final files:

```text
production-guide.md
plan.json
scenes/
```

No database or frontend is needed.

---

# 8. Simple Data Models

Use Pydantic.

## Plan

```python
class PlannedScene(BaseModel):
    scene: int
    purpose: str


class VideoPlan(BaseModel):
    title: str
    hook: str
    angle: str
    scenes: list[PlannedScene]
```

## Production Scene

```python
class ProductionScene(BaseModel):
    scene: int
    purpose: str
    script: str
    picture_description: str
    search_query: str
```

## Final Scene

```python
class FinalScene(BaseModel):
    scene: int
    script: str
    picture: str | None
    on_screen_text: str
    editing_note: str
    estimated_duration: float
```

---

# 9. File Structure

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

# 10. Main Program

Keep `main.py` simple.

```python
topic = input("What video are you making today? ")

plan = planning_agent(topic)

production = production_agent(plan)

images = image_agent(production)

final = composer_agent(
    plan=plan,
    production=production,
    images=images
)

save_production_guide(final)
```

`main.py` should orchestrate the workflow rather than contain the actual agent logic.

---

# 11. Implementation Order

## Step 1 — Planning Agent

Build:

```text
topic
↓
title
hook
angle
scene purposes
```

Test with 5 different video topics.

---

## Step 2 — Production Agent

Build:

```text
video plan
↓
scene scripts
picture descriptions
search queries
```

At this point, manually inspect whether the queries would actually work in Google Images.

---

## Step 3 — Connect Existing Image Tool

Reuse the current:

```text
Google Images
→ download candidates
→ AI vision selector
```

Run it once for every scene.

---

## Step 4 — Composer Agent

Generate:

```text
production-guide.md
```

For every scene include:

```text
Script
Picture
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
✓ 5 scenes created

Preparing scenes...
✓ Scripts created
✓ Image queries created

Finding images...
Scene 1/5 ✓
Scene 2/5 ✓
Scene 3/5 ✓
Scene 4/5 ✓
Scene 5/5 ✓

Composing production guide...
✓ Done

output/why-f1-killed-the-v10/production-guide.md
```

Then actually use the guide to make one real video.

---

# 12. V1 Definition of Done

V1 is finished when:

* [ ] User enters one topic
* [ ] Planning Agent generates a useful video structure
* [ ] Production Agent writes each scene's script
* [ ] Production Agent creates descriptive image queries
* [ ] Image Agent searches Google Images
* [ ] Image Agent downloads candidates
* [ ] Existing vision model chooses the best candidate
* [ ] Each scene has a selected picture when possible
* [ ] Composer Agent generates on-screen text
* [ ] Composer Agent generates editing notes
* [ ] Composer Agent estimates scene duration
* [ ] `production-guide.md` is generated
* [ ] One failed image does not break the entire run
* [ ] The production guide is useful enough to make a real video from

---

# 13. Do Not Build Yet

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

# 14. V1 Product

The entire V1 should do one thing well:

```text
"What video am I making today?"
            ↓
       Planning Agent
            ↓
      Production Agent
            ↓
        Image Agent
            ↓
       Composer Agent
            ↓
   production-guide.md
```

The final guide tells the creator:

> **what to say, what picture to use, what text to put on screen, how to edit the scene, and approximately how long the scene should last.**

Then the creator films and edits the video themselves.
