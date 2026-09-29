#!/usr/bin/env python3
"""Seed script for Firestore articles/drafts collection."""

from datetime import datetime, timezone
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-63146160a304"
COLLECTION_NAME = "storycraft_articles"

SEEDED_ARTICLES = [
    {
        "id": "tech-quantum-computing",
        "title": "Quantum Computing Explained Using a Coin Flip",
        "genre": "tech",
        "concept": "Demystifying quantum superposition and entanglement for everyday readers.",
        "content": (
            "Imagine a standard coin sitting on a table. It is either Heads or Tails—just like a standard computer bit "
            "is 0 or 1. Now imagine that coin spinning furiously across the floor. While it spins, is it Heads or Tails? "
            "It is a whirlwind of both possibilities at once. That spinning coin is a quantum qubit in superposition!"
        ),
        "target_audience": "General audience / Beginners",
        "tags": ["Technology", "QuantumComputing", "ExplainLikeImFive", "Science"],
        "status": "draft",
        "publish_target": "draft",
        "medium_url": "",
        "cover_image_prompt": "A glowing holographic coin spinning through a cosmic library of binary numbers, digital art, vibrant teal and gold lighting.",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": "poetry-rain-on-pavement",
        "title": "Petrichor at Dawn",
        "genre": "poetry",
        "concept": "The quiet memory of childhood summer storms on warm asphalt.",
        "content": (
            "The street remembers heat like old skin.\n"
            "First drops fall heavy, gray silver coins\n"
            "bursting against cracked slate.\n\n"
            "Steam whispers upward—\n"
            "the ancient earth breathing out\n"
            "everything it held through the dry afternoon."
        ),
        "target_audience": "Poetry lovers / Reflective readers",
        "tags": ["Poetry", "Life", "Rain", "Memories"],
        "status": "draft",
        "publish_target": "public",
        "medium_url": "",
        "cover_image_prompt": "Raindrops creating rippling reflections on a city asphalt street at twilight, warm streetlamp reflections, cinematic photography.",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": "story-train-conductor-pocketwatch",
        "title": "The Last Midnight Express",
        "genre": "story",
        "concept": "A retired train conductor on his final night run carrying a forgotten passenger.",
        "content": (
            "Arthur tapped the brass casing of his pocket watch. Thirty-eight years of timetables, "
            "and tonight the rails felt unusually gentle. Across car four, a young woman sat with an unopened violin case, "
            "staring at the passing shadows of pine forests. 'Next stop isn't on the map, Arthur murmured to himself with a soft smile."
        ),
        "target_audience": "Fiction & narrative lovers",
        "tags": ["Fiction", "ShortStory", "LifeLessons", "Travel"],
        "status": "ready_to_publish",
        "publish_target": "draft",
        "medium_url": "",
        "cover_image_prompt": "A vintage passenger train speeding under starry mountain skies at midnight, warm amber window glows, moody impressionist painting style.",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
]


def seed():
    print(f"Connecting to Firestore using project ID: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection(COLLECTION_NAME)

    for item in SEEDED_ARTICLES:
        doc_id = item["id"]
        data = {k: v for k, v in item.items() if k != "id"}
        collection.document(doc_id).set(data)
        print(f"✓ Seeded document: {doc_id} -> '{item['title']}' ({item['genre']})")

    print(f"\nSuccessfully seeded {len(SEEDED_ARTICLES)} items to collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    seed()
