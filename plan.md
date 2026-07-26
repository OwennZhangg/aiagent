# Picture Agent - Implementation Plan

## Goal

Build a simple AI agent that takes a text prompt, searches Google Images using Playwright, downloads five candidate images, asks OpenAI to choose the best one, and saves the selected image locally.

Example:

```
Input:
"red Ferrari side profile"

↓

Google Images

↓

5 candidate images

↓

OpenAI Vision

↓

Selected image

↓

images/selected.jpg
```

---

# MVP Scope

The project should only do the following:

- Accept a text prompt
- Open Google Images
- Search for the prompt
- Collect five candidate images
- Download them
- Ask OpenAI which one best matches the prompt
- Save the chosen image

Nothing else.

Do **not** build:

- GUI
- Web app
- FastAPI
- Database
- User accounts
- Retry logic
- Caching
- Metadata management

Keep the project as small as possible.

---

# Project Structure

```
picture-agent/

├── main.py
├── browser.py
├── selector.py
├── downloader.py
├── config.py

├── images/
│   ├── candidate1.jpg
│   ├── candidate2.jpg
│   ├── candidate3.jpg
│   ├── candidate4.jpg
│   ├── candidate5.jpg
│   └── selected.jpg

├── requirements.txt
├── .env
└── README.md
```

---

# Overall Workflow

```
User Prompt
      │
      ▼
Playwright
      │
      ▼
Google Images
      │
      ▼
Collect 5 Images
      │
      ▼
Download Candidates
      │
      ▼
OpenAI Vision
      │
      ▼
Best Image Index
      │
      ▼
Save Selected Image
```

---

# Module Responsibilities

## main.py

Responsible for orchestrating everything.

Flow:

1. Ask user for prompt
2. Search images
3. Download images
4. Ask OpenAI to choose
5. Save selected image
6. Print completion message

main.py should contain almost no logic.

Its job is simply calling functions.

---

## browser.py

Responsible ONLY for browser automation.

Tasks:

- Launch Chromium
- Navigate to Google Images
- Search the prompt
- Open image results
- Extract image URLs
- Download five candidate images

It should not know anything about OpenAI.

It should not decide which image is best.

---

## selector.py

Responsible ONLY for image selection.

Input:

- original prompt
- five candidate images

Output:

```
Best image number
```

Example:

```
3
```

Nothing more.

---

## downloader.py

Responsible ONLY for saving files.

Possible responsibilities:

- Save candidate images
- Copy selected image
- Replace previous images
- Ensure output directory exists

No AI.

No Playwright.

---

## config.py

Store things like:

- OpenAI API key
- Image directory
- Number of candidates

No application logic.

---

# Suggested Development Order

## Phase 1

Create project structure.

Nothing should use AI yet.

---

## Phase 2

Learn Playwright.

Goal:

Open Chrome.

Search Google Images.

Stop.

---

## Phase 3

Automatically search Google Images.

Input:

```
cat
```

Browser should perform:

- open page
- search
- wait for results

Nothing else.

---

## Phase 4

Figure out how Google Images works.

Understand:

- thumbnails
- full images
- image URLs

Experiment manually.

No AI.

---

## Phase 5

Download the first image.

Do not worry if it's the wrong image.

Just prove downloading works.

---

## Phase 6

Download five images.

Folder should look like:

```
images/

candidate1.jpg
candidate2.jpg
candidate3.jpg
candidate4.jpg
candidate5.jpg
```

---

## Phase 7

Integrate OpenAI.

Give the model:

- original prompt
- five images

Ask:

```
Which image best matches the prompt?

Reply ONLY with:

1
2
3
4
or
5
```

---

## Phase 8

Save the selected image.

Example:

```
selected.jpg
```

Done.

---

# Keep Every Module Small

A good rule:

If a file is doing two jobs,
split it.

Example:

Bad:

browser.py

- searches
- downloads
- AI
- saving files

Good:

browser.py

only browser.

---

# Error Handling (MVP)

Only handle obvious failures.

Examples:

- Browser won't launch
- Search returns no results
- Image download fails
- OpenAI request fails

Print the error.

Exit.

Do not build retry systems.

---

# Things To Learn

Instead of copying code,
understand these concepts:

## Playwright

Learn:

- launching browser
- opening pages
- locating elements
- clicking
- waiting
- reading attributes

---

## Google Images

Understand:

- thumbnail image
- full-resolution image
- image URLs

---

## OpenAI Vision

Learn:

- sending multiple images
- prompting clearly
- getting a structured answer

---

## Downloading Images

Understand:

- URLs
- binary files
- writing files

---

# Completion Criteria

The project is complete when this works:

```
python main.py
```

Console:

```
Enter image:

> red Ferrari side profile
```

Program:

```
Searching...

Downloading images...

Choosing best image...

Saved:

images/selected.jpg
```

No extra features are required.

If this works reliably,
the MVP is complete.

---

# Future Improvements (NOT NOW)

Possible ideas after the MVP:

- Better search queries using an LLM
- Download higher-resolution images
- Retry when no good image exists
- Rank instead of selecting one
- Automatic duplicate removal
- Scene-by-scene Reel generation
- Multiple search providers
- Progress bar
- CLI arguments
- GUI
- Batch processing

Ignore these until the MVP is working.