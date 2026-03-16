"""
knowledge-graph-builder.py - Knowledge Graph Builder for GK BRAIN

Maintains a semantic knowledge graph of all entities and relationships
extracted from lore and update data.

Usage (from gk-brain.py):
    from knowledge_graph_builder import update_knowledge_graph, get_related_entities
    graph = update_knowledge_graph(updates, lore_text)
    related = get_related_entities("Lady-INK")
"""

import json
import os
import re

BASE_DIR = os.path.dirname(__file__)
GRAPH_FILE = os.path.join(BASE_DIR, "knowledge-graph.json")

ENTITY_PATTERNS = {
    "character": [
        r"\bLady-INK\b", r"\bLady INK\b", r"\bDave\b", r"\bOld Pete\b",
        r"\bCryptoMoonBoy\b", r"\bBlocktopia\b",
    ],
    "location": [
        r"\bWindermere\b", r"\bPrintworks\b", r"\bShoreditch\b", r"\bManchester\b",
        r"\bLondon\b", r"\bNorthern\b",
    ],
    "nft": [
        r"\bGKniftyHEADS\b", r"\bNoBallGames\b", r"\bWAX\b", r"\bOpenSea\b",
        r"\bNeftyBlocks\b",
    ],
    "activity": [
        r"\bcarp\b", r"\bfishing\b", r"\brave\b", r"\bgraffiti\b", r"\bparkour\b",
        r"\bDJ\b", r"\bmural\b",
    ],
}

MAX_GRAPH_ENTITIES = 200


def _load_graph() -> dict:
    if os.path.exists(GRAPH_FILE):
        try:
            with open(GRAPH_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"entities": {}, "relationships": [], "last_updated": None}


def _save_graph(graph: dict) -> None:
    try:
        import datetime
        graph["last_updated"] = datetime.datetime.utcnow().isoformat()
        with open(GRAPH_FILE, "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2)
    except Exception as e:
        print(f"[knowledge-graph] Save error: {e}")


def _extract_entities(text: str) -> dict:
    """Extract entity mentions from text, categorised by type."""
    found = {}
    for entity_type, patterns in ENTITY_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                key = match.strip().lower()
                if key not in found:
                    found[key] = {"type": entity_type, "name": match.strip(), "mentions": 0}
                found[key]["mentions"] += 1
    return found


def update_knowledge_graph(updates: list, lore_text: str) -> dict:
    """
    Extract entities from lore and updates, add to knowledge graph.

    Args:
        updates: List of update dicts.
        lore_text: Generated or historical lore text.

    Returns:
        Updated graph dict.
    """
    try:
        graph = _load_graph()
        entities = graph.get("entities", {})

        combined_text = lore_text + " "
        for u in updates:
            combined_text += (u.get("content", "") or u.get("title", "") or "") + " "

        new_entities = _extract_entities(combined_text)

        for key, data in new_entities.items():
            if key in entities:
                entities[key]["mentions"] = entities[key].get("mentions", 0) + data["mentions"]
            else:
                entities[key] = data

        # Trim to max size
        if len(entities) > MAX_GRAPH_ENTITIES:
            sorted_ents = sorted(entities.items(), key=lambda x: x[1].get("mentions", 0), reverse=True)
            entities = dict(sorted_ents[:MAX_GRAPH_ENTITIES])

        graph["entities"] = entities
        _save_graph(graph)
        return graph
    except Exception as e:
        print(f"[knowledge-graph] update_knowledge_graph error: {e}")
        return {}


def get_related_entities(entity: str) -> list:
    """
    Return entities that frequently co-occur with the given entity.

    Args:
        entity: Entity name to find relations for.

    Returns:
        List of related entity name strings.
    """
    try:
        graph = _load_graph()
        entities = graph.get("entities", {})
        entity_lower = entity.lower()

        if entity_lower not in entities:
            return []

        entity_type = entities[entity_lower].get("type", "unknown")

        related = [
            data["name"] for key, data in entities.items()
            if key != entity_lower and data.get("type") == entity_type
        ]

        return related[:5]
    except Exception as e:
        print(f"[knowledge-graph] get_related_entities error: {e}")
        return []
