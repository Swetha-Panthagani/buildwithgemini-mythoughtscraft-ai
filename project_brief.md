# My agent: StoryCraft AI (The Universal Blog & Story Studio)

One-liner: A conversational multi-agent studio that transforms raw ideas into engaging, universally accessible content across genres (tech simplification, poetry, and narrative fiction), generates matching cover visuals, and publishes to Medium as a draft or public story upon explicit user confirmation.

## Architecture & Subagents
- **Main Coordinator / Editor-in-Chief Agent**:
  - Understands the user's raw idea and determines the ideal genre and framing.
  - Engages the user ("grill-me" style questions) if an idea is ambiguous, underspecified, or needs a stronger angle before writing.
  - Generates cohesive cover art / blog header illustrations matching the piece.
  - Requests explicit user confirmation and asks whether to publish to Medium as a **Draft** or **Public Story**.
- **Specialized Subagents (Routing by Genre)**:
  1. **Tech Simplifier Subagent**: Combines ELI5 and structured technical explanations with relatable real-world analogies so anyone can understand complex concepts.
  2. **Human Poetry Subagent**: Captures deep emotion, cadence, and nuance while preserving authentic human poetic concept without sounding robotic.
  3. **Narrative / Life Story Subagent**: Crafts captivating short stories, life series, or novel chapters with vivid character arcs, reflections, and storytelling pacing.

## Tool Coverage
- **Memory**: Remembers author preferences across sessions (favorite themes, typical audience, preferred publishing format draft vs. public, past blog topics and style feedback).
- **Tools**:
  - `publish_to_medium(title, content, tags, publish_status, confirmed)`: Publishes to Medium as either a draft or public post with strict human-in-the-loop confirmation.
  - `save_draft(title, content, genre, cover_image_url)`: Stores local drafts.
  - `list_drafts()`: Retrieves saved drafts and publication status.
- **Catalog/UI (A2UI)**: Visual cards displaying article previews, genre badges (`Tech`, `Poetry`, `Story`), estimated read times, generated cover art previews, and publication status.
- **Image gen**: Generates evocative, high-quality blog cover illustrations tailored to the genre (`gemini-3.1-flash-lite-image`).
- **Sandbox**: Readability analysis (Flesch-Kincaid score) and poem rhythm/meter/word-count check.

Recommended for every project: memory, storage, tools, image generation, A2UI.
Agent-specific / stretch: Multi-agent routing (ADK subagents), human-in-the-loop publishing confirmation, Medium REST API integration.

## Detailed Workflow Specification (From /grill-me Alignment)
1. **Phase 1: Idea Ingestion & Grilling Loop**:
   - Evaluates incoming idea with an "Idea Clarity & Hook Score (1-10)".
   - Presents a 3-bullet angle outline and asks 1-2 sharp clarifying questions on target audience and tone before drafting.
   - Guardrail: Reasoning / grilling turn limit capped at 7 iterations. If reaching 7 turns without convergence, triggers `send_approval_email` to simulate sending an email to the user for formal approval to proceed.
2. **Phase 2: Drafting & Text Confirmation**:
   - Routes to genre subagent / specialized mode (Tech Simplifier with ELI5, Human Poet, Narrative Weaver).
   - Saves initial draft into Firestore (`storycraft_articles`).
   - Presents draft to user for review and confirmation.
3. **Phase 3: Visual Generation & Storage**:
   - Generates 16:9 widescreen editorial banner artwork using Gemini image generation (`gemini-3.1-flash-lite-image`).
   - Uploads to public bucket `storycraft-media-qwiklabs-gcp-03-63146160a304`.
   - Links public image URL to the draft in Firestore.
4. **Phase 4: Medium Publishing & Quality Analysis**:
   - Asks user for explicit publishing confirmation: **Draft** vs. **Public**.
   - Calls `publish_to_medium` (using `MEDIUM_INTEGRATION_TOKEN` if present in `.env`, otherwise simulated mode).
   - Computes readability (Flesch-Kincaid score) and rhythm/cadence analysis to ensure universal comprehension.
