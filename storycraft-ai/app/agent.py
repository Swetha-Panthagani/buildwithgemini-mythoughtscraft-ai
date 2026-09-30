# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

import json
from pathlib import Path
from google.adk.code_executors.agent_engine_sandbox_code_executor import AgentEngineSandboxCodeExecutor

from app.firestore_tools import (
    save_article,
    list_articles,
    get_article_by_id,
    update_article_status,
)
from app.storycraft_tools import (
    analyze_and_score_idea,
    send_approval_email,
    generate_cover_art,
    generate_story_video,
    analyze_story_quality,
    publish_to_medium,
    publish_to_linkedin,
    publish_to_devto,
    publish_to_instagram,
    create_genre_rich_video,
    publish_youtube_shorts,
    publish_youtube_longform,
    set_author_style_and_voice,
    search_poetry_database,
)


MODEL = "gemini-3.6-flash"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


# Shared tools for reading and writing drafts and checking quality
drafting_tools = [
    save_article,
    get_article_by_id,
    analyze_story_quality,
]

# 1. Tech Simplifier Subagent (ELI5 + structured clarity)
tech_simplifier_agent = Agent(
    name="tech_simplifier",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Tech Simplifier Subagent for StoryCraft AI. "
        "Your mission is to translate complex technical concepts into universally understandable, "
        "compelling stories and blogs using an ELI5 approach with vivid real-world analogies. "
        "Avoid heavy jargon or explain it immediately with everyday items. "
        "Use `save_article` to save new drafts and `analyze_story_quality` to verify high readability."
    ),
    tools=drafting_tools,
)

# 2. Human Poet Subagent (Authentic cadence, vivid imagery, emotional depth)
human_poet_agent = Agent(
    name="human_poet",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Human Poet Subagent for StoryCraft AI. "
        "You craft evocative, lyrical poetry that feels genuinely human, grounded, and emotionally resonant. "
        "Focus on sensory details, natural cadence, and sincere sentiment rather than cliché rhymes. "
        "Use `search_poetry_database` to look up classical poetry for stylistic inspiration, "
        "`save_article` to preserve drafts, and `analyze_story_quality` to check line structure."
    ),
    tools=[*drafting_tools, search_poetry_database],
)

# 3. Narrative Weaver Subagent (Short stories, series, character-driven fiction)
narrative_weaver_agent = Agent(
    name="narrative_weaver",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Narrative Weaver Subagent for StoryCraft AI. "
        "You write engaging fiction, short stories, and episodic life narratives with authentic dialogue, "
        "compelling pacing, and meaningful character arcs. "
        "Use `save_article` to store chapters or stories and `analyze_story_quality` to monitor flow."
    ),
    tools=drafting_tools,
)

# Initialize Agent Platform sandbox code executor from deployment_metadata.json if available
metadata_file = Path(__file__).resolve().parent.parent / "deployment_metadata.json"
code_executor = None
SANDBOX_ENV_NAME = "projects/766341849093/locations/us-east1/reasoningEngines/2360112704137461760/sandboxEnvironments/7996783253186936832"

if metadata_file.exists():
    try:
        with open(metadata_file) as f:
            metadata = json.load(f)
        agent_engine_res = metadata.get("remote_agent_runtime_id")
        if agent_engine_res:
            code_executor = AgentEngineSandboxCodeExecutor(
                sandbox_resource_name=SANDBOX_ENV_NAME,
                agent_engine_resource_name=agent_engine_res,
            )
    except Exception as e:
        code_executor = None

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.memory import VertexAiMemoryBankService
from .a2ui_utils import a2ui_callback

MEMORY_BANK_ID = "2360112704137461760"
GCP_PROJECT = "qwiklabs-gcp-03-63146160a304"
GCP_LOCATION = "us-east1"

# WRITE: after each turn, send the session to Memory Bank for durable extraction
async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None

# Memory service builder for redeployment on Agent Runtime
def memory_bank_service_builder():
    return VertexAiMemoryBankService(
        project=GCP_PROJECT,
        location=GCP_LOCATION,
        agent_engine_id=MEMORY_BANK_ID,
    )

try:
    from a2ui.schema.manager import A2uiSchemaManager
    from a2ui.basic_catalog.provider import BasicCatalog
    _has_a2ui_sdk = True
except ImportError:
    _has_a2ui_sdk = False

try:
    from app.a2ui_prompt import SYSTEM_INSTRUCTION as a2ui_instruction
except ImportError:
    a2ui_instruction = None

if not a2ui_instruction and _has_a2ui_sdk:
    schema_manager = A2uiSchemaManager(
        version="0.8",
        catalogs=[BasicCatalog.get_config("0.8")],
    )
    a2ui_instruction = schema_manager.generate_system_prompt(
        role_description=(
            "You are StoryCraft AI, the Editor-in-Chief and coordinator for a multi-genre creative studio.\n"
            "LONG-TERM MEMORY & PERSONALIZATION:\n"
            "- Actively track and remember all user preferences, writing styles, preferred tones, genres, recurring themes, characters, and aesthetic constraints.\n"
            "- When the user mentions any preference or asks you to remember a theme, acknowledge it and immediately incorporate it into all future creations.\n"
            "- Every turn automatically recalls relevant past preferences and durable facts to personalize the creative direction."
        ),
        workflow_description=(
            "1. Analyze incoming ideas with `analyze_and_score_idea` (provide 3 angles aligned with the user's preferred themes and ask 1-2 sharp clarifying questions).\n"
            "2. If reasoning exceeds 7 iterations, call `send_approval_email` to request user sign-off.\n"
            "3. Route drafting to specialized subagents:\n"
            "   - `tech_simplifier`: for tech, engineering, AI, and science topics with ELI5 clarity.\n"
            "   - `human_poet`: for poetry and lyrical verse.\n"
            "   - `narrative_weaver`: for fiction, personal essays, and short stories.\n"
            "4. Manage drafts in Firestore with `list_articles`, `get_article_by_id`, and `save_article`.\n"
            "5. Generate 16:9 editorial cover art with `generate_cover_art` matching the user's aesthetic preferences.\n"
            "6. Generate short cinematic story/concept videos with `generate_story_video` using Google's Omni model (gemini-omni-flash-preview).\n"
            "7. Check readability metrics with `analyze_story_quality`.\n"
            "8. Multi-platform publishing & export: Use `publish_to_medium`, `publish_to_linkedin`, `publish_to_devto` (for tech articles/tutorials), or `publish_to_instagram` (for aesthetic captions & visual cards).\n"
            "9. Multimedia & Video Studio:\n"
            "   - `create_genre_rich_video`: tailored video generation with audio narration (cinema + subtitles for stories, pure spoken-word voice for poetry, tutorial + code for tech).\n"
            "   - `publish_youtube_shorts`: create and publish 9:16 vertical shorts to YouTube.\n"
            "   - `publish_youtube_longform`: produce and publish full 16:9 episodes/podcasts to YouTube.\n"
            "10. Author Personalization: Call `set_author_style_and_voice` to register the user's bespoke tone, inspirational authors, and voice tuning guidelines.\n"
            "11. You can safely execute Python in a secure Agent Engine sandbox to run calculations, simulate algorithms, or verify code.\n"
            "12. When presenting story drafts, idea pitches, poems, or cover images to the user, render structured A2UI cards."
        ),
        ui_description=(
            "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
            "Never nest a Card inside a Card. "
            "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
            "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
            "nothing in adk web). "
            "You may include one Image component, but only when you have a public https "
            "URL for the image (for example the URL an image tool returns after uploading "
            "to a public bucket). Set the Image url to that exact https link, for example "
            "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
            "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
            "not have a public URL, add a short Text line noting the image instead. "
            "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
            "headings and emphasis. "
            "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
            "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
        ),
        include_schema=True,
        include_examples=True,
    )


# Root Coordinator / Editor-in-Chief Agent
root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=a2ui_instruction,
    code_executor=code_executor,
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
    sub_agents=[
        tech_simplifier_agent,
        human_poet_agent,
        narrative_weaver_agent,
    ],
    tools=[
        PreloadMemoryTool(),
        analyze_and_score_idea,
        send_approval_email,
        generate_cover_art,
        generate_story_video,
        analyze_story_quality,
        publish_to_medium,
        publish_to_linkedin,
        publish_to_devto,
        publish_to_instagram,
        create_genre_rich_video,
        publish_youtube_shorts,
        publish_youtube_longform,
        set_author_style_and_voice,
        search_poetry_database,
        save_article,
        list_articles,
        get_article_by_id,
        update_article_status,
        get_weather,
        get_current_time,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
