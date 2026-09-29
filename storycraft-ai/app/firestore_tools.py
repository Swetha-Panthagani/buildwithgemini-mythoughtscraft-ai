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

"""Firestore backend tools for StoryCraft AI articles and drafts."""

from datetime import datetime, timezone
import re
from typing import Any, Dict, List, Optional
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-63146160a304"
COLLECTION_NAME = "storycraft_articles"

_db_client: Optional[firestore.Client] = None


def get_firestore_client() -> firestore.Client:
    """Returns a singleton Firestore client with the hardcoded project ID."""
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client(project=PROJECT_ID)
    return _db_client


def _slugify(text: str) -> str:
    """Generate a simple URL-friendly slug for document IDs."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")[:50] or "article"


def save_article(
    title: str,
    content: str,
    genre: str,
    concept: str = "",
    target_audience: str = "General audience",
    tags: Optional[List[str]] = None,
    publish_target: str = "draft",
    cover_image_prompt: str = "",
    article_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Save or update an article draft in the Firestore database.

    Args:
        title: The title of the article, poem, or story.
        content: The full written text/body of the article or poem.
        genre: The genre category, e.g., 'tech', 'poetry', 'story', or 'general'.
        concept: Brief summary of the core idea or inspiration behind the piece.
        target_audience: Target readers (e.g. 'Beginners', 'General audience').
        tags: List of descriptive tags for discovery and Medium tagging.
        publish_target: Desired publish state when uploaded to Medium ('draft' or 'public').
        cover_image_prompt: Suggested prompt or description for the cover image artwork.
        article_id: Optional custom ID. If omitted, generated from genre and title.

    Returns:
        A dictionary with the operation status, document ID, and confirmation message.
    """
    db = get_firestore_client()
    now_iso = datetime.now(timezone.utc).isoformat()

    doc_id = article_id or f"{_slugify(genre)}-{_slugify(title)}"
    doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
    existing_doc = doc_ref.get()

    doc_data: Dict[str, Any] = {
        "title": title,
        "content": content,
        "genre": genre.lower(),
        "concept": concept or title,
        "target_audience": target_audience,
        "tags": tags or [genre.capitalize(), "Writing"],
        "status": "draft",
        "publish_target": publish_target.lower() if publish_target in ["draft", "public"] else "draft",
        "medium_url": "",
        "cover_image_prompt": cover_image_prompt,
        "updated_at": now_iso,
    }

    if existing_doc.exists:
        doc_ref.update(doc_data)
        message = f"Article '{title}' (ID: {doc_id}) successfully updated in Firestore."
    else:
        doc_data["created_at"] = now_iso
        doc_ref.set(doc_data)
        message = f"Article '{title}' (ID: {doc_id}) successfully saved as a draft in Firestore."

    return {
        "status": "success",
        "article_id": doc_id,
        "message": message,
        "article": doc_data,
    }


def list_articles(
    genre: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """Retrieve articles or drafts from Firestore, optionally filtered by genre or status.

    Args:
        genre: Optional filter by genre (e.g., 'tech', 'poetry', 'story').
        status: Optional filter by status ('draft', 'ready_to_publish', 'published').
        limit: Maximum number of articles to return (default: 10).

    Returns:
        A dictionary containing the list of articles found and summary count.
    """
    db = get_firestore_client()
    query = db.collection(COLLECTION_NAME)

    if genre:
        query = query.where(filter=firestore.FieldFilter("genre", "==", genre.lower()))
    if status:
        query = query.where(filter=firestore.FieldFilter("status", "==", status.lower()))

    docs = query.limit(limit).stream()
    articles: List[Dict[str, Any]] = []

    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        # Truncate content in list view for readability
        if "content" in item and len(item["content"]) > 160:
            item["content_snippet"] = item["content"][:160] + "..."
        else:
            item["content_snippet"] = item.get("content", "")
        articles.append(item)

    return {
        "total_count": len(articles),
        "articles": articles,
    }


def get_article_by_id(article_id: str) -> Dict[str, Any]:
    """Retrieve a single article's full content and details by its ID.

    Args:
        article_id: The unique Firestore document ID of the article.

    Returns:
        The article data dictionary or an error status if not found.
    """
    db = get_firestore_client()
    doc = db.collection(COLLECTION_NAME).document(article_id).get()

    if not doc.exists:
        return {
            "status": "error",
            "message": f"Article with ID '{article_id}' not found in Firestore.",
        }

    data = doc.to_dict()
    data["id"] = doc.id
    return {
        "status": "success",
        "article": data,
    }


def update_article_status(
    article_id: str,
    status: str,
    medium_url: str = "",
) -> Dict[str, Any]:
    """Update an article's publication status and optionally record its Medium URL.

    Args:
        article_id: The unique ID of the article to update.
        status: The new status ('draft', 'ready_to_publish', 'published').
        medium_url: Optional URL of the published story on Medium.

    Returns:
        Status dictionary confirming the update.
    """
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(article_id)
    doc = doc_ref.get()

    if not doc.exists:
        return {"status": "error", "message": f"Article '{article_id}' not found."}

    update_payload: Dict[str, Any] = {
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if medium_url:
        update_payload["medium_url"] = medium_url

    doc_ref.update(update_payload)
    return {
        "status": "success",
        "article_id": article_id,
        "updated_status": status,
        "medium_url": medium_url,
        "message": f"Article '{article_id}' status updated to '{status}'.",
    }
