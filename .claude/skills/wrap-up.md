---
name: wrap-up
description: Use when the user says "wrap_up" or asks to summarize what was learned after completing a micro-step
---

# Wrap Up

Summarize the current micro-step into a clean learning note saved to `notes/`.

## Process

1. Identify what was just completed (the micro-step, tools used, concepts encountered)
2. Draft a note with this structure:
   - **Title:** `a1a-project-init.md` (match the micro-step name)
   - **What I did** — bullet list of actions taken
   - **Key concepts** — explain each new concept in plain language (assume beginner); use Mermaid diagrams where they help visualize relationships or flows
   - **Commands learned** — table of commands used and what they do
   - **Gotchas** — anything surprising or confusing encountered
   - **Questions for later** — things worth revisiting as knowledge grows
3. Show the draft to the user for review before saving
4. Save to `notes/` directory in the repo

## File Naming

Use the micro-step ID: `notes/a1a-project-init.md`, `notes/a1b-fastapi-health.md`, etc.

## Tone

Write as if explaining to a friend who's learning the same thing. Keep it casual but accurate.
