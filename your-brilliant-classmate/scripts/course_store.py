#!/usr/bin/env python3
"""Store course evidence and learning events with atomic, auditable updates."""

import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys

SOURCE_KINDS = {"textbook", "lecture", "quiz", "homework", "syllabus", "answer_key", "other"}
EVENT_KINDS = {"question", "homework", "diagnosis", "diagnostic", "review"}
RESULTS = {"unverified", "correct", "partial", "incorrect", "assisted"}
SCHEMA = """
CREATE TABLE IF NOT EXISTS course (id TEXT PRIMARY KEY, name TEXT NOT NULL, schema_version INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS sources (id TEXT PRIMARY KEY, record TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS topics (id TEXT PRIMARY KEY, record TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY, kind TEXT NOT NULL, at TEXT NOT NULL,
    result TEXT NOT NULL, independent INTEGER NOT NULL, record TEXT NOT NULL,
    linked_event_id TEXT REFERENCES events(id),
    supersedes TEXT UNIQUE REFERENCES events(id)
);
CREATE TABLE IF NOT EXISTS event_topics (
    event_id TEXT NOT NULL REFERENCES events(id), topic_id TEXT NOT NULL REFERENCES topics(id),
    PRIMARY KEY (event_id, topic_id)
);
"""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def object_value(value, label):
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def identifier(record):
    object_value(record, "record")
    value = record.get("id")
    require(isinstance(value, str) and bool(value.strip()), "Record needs a nonempty id")
    return value


def open_db(path, readonly=False):
    require(path.is_file(), f"Database does not exist; run init first: {path}")
    conn = sqlite3.connect(path.as_uri() + ("?mode=ro" if readonly else "?mode=rw"), uri=True)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        rows = conn.execute("SELECT id, name, schema_version FROM course").fetchall()
        require(len(rows) == 1 and rows[0][2] == 1, "Unsupported or uninitialized course database")
    except Exception:
        conn.close()
        raise
    return conn


def load_records(conn, table):
    return {row[0]: json.loads(row[1]) for row in conn.execute(f"SELECT id, record FROM {table}")}


def validate_citations(value, sources):
    if isinstance(value, list):
        for item in value:
            validate_citations(item, sources)
    elif isinstance(value, dict):
        if "source_id" in value:
            require(value["source_id"] in sources, f"Unknown citation source: {value['source_id']}")
            if "unit" in value:
                unit = value["unit"]
                total = sources[value["source_id"]]["total_units"]
                require(type(unit) is int and 1 <= unit <= total, "Citation unit outside source bounds")
        for item in value.values():
            validate_citations(item, sources)


def upsert_source(conn, item):
    source_id = identifier(item)
    require(item.get("kind") in SOURCE_KINDS, "Invalid source kind")
    require(isinstance(item.get("title"), str) and item["title"].strip(), "Source needs a title")
    require(type(item.get("total_units")) is int and item["total_units"] > 0, "Source total_units must be positive")
    require(re.fullmatch(r"[0-9a-fA-F]{64}", item.get("sha256", "")) is not None, "Source needs a SHA-256 hash")
    require(isinstance(item.get("path"), str), "Source needs a file path")
    path = Path(item["path"]).expanduser().resolve()
    require(path.is_file(), f"Source file unavailable: {path}")
    with path.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    require(digest == item["sha256"].lower(), "Source hash does not match the actual file")
    item = dict(item, path=str(path), sha256=digest)
    object_value(item.get("metadata", {}), "Source metadata")
    old = conn.execute("SELECT record FROM sources WHERE id=?", (source_id,)).fetchone()
    if old:
        before = json.loads(old[0])
        for key in ("title", "kind", "path", "sha256", "total_units"):
            require(before[key] == item[key], f"Source {source_id} changed identity; use a new source ID")
    conn.execute("INSERT INTO sources VALUES (?,?) ON CONFLICT(id) DO UPDATE SET record=excluded.record", (source_id, encode(item)))


def add_event(conn, item, sources, topic_ids):
    event_id = identifier(item)
    require(item.get("kind") in EVENT_KINDS, "Invalid event kind")
    item = dict(item)
    old = conn.execute("SELECT record FROM events WHERE id=?", (event_id,)).fetchone()
    if "at" not in item:
        item["at"] = json.loads(old[0])["at"] if old else datetime.now().astimezone().isoformat()
    timestamp = datetime.fromisoformat(item["at"])
    require(timestamp.utcoffset() is not None, "Event timestamp must include a time-zone offset")
    require(item.get("result", "unverified") in RESULTS, "Invalid event result")
    item.setdefault("result", "unverified")
    item.setdefault("independent", False)
    require(type(item["independent"]) is bool, "independent must be a boolean")
    topics = item.get("topics")
    require(isinstance(topics, list) and topics and all(isinstance(t, str) for t in topics), "Event needs topic IDs")
    require(len(topics) == len(set(topics)) and set(topics) <= topic_ids, "Duplicate or unknown event topic")
    data = object_value(item.get("data", {}), "Event data")
    item.setdefault("data", {})
    causes = data.get("causes", [])
    require(isinstance(causes, list), "causes must be an array")
    for cause in causes:
        object_value(cause, "Cause")
        require(isinstance(cause.get("label"), str) and cause["label"].strip(), "Cause needs a label")
        require(cause.get("status") in {"suspected", "confirmed"}, "Invalid cause status")
        if cause["status"] == "confirmed":
            require(bool(cause.get("evidence")), "Confirmed cause needs actual supporting evidence")
    if "diagnosis_complete" in data:
        require(type(data["diagnosis_complete"]) is bool, "diagnosis_complete must be a boolean")
    for key in ("linked_event_id", "supersedes"):
        target = item.get(key)
        if target is not None:
            require(isinstance(target, str) and target != event_id, f"Invalid {key}")
            row = conn.execute("SELECT kind FROM events WHERE id=?", (target,)).fetchone()
            require(row is not None, f"Unknown {key}: {target}; place parent event earlier in the batch")
            if item["kind"] == "diagnosis" and key == "linked_event_id":
                require(row[0] == "homework", "Diagnosis must link to homework")
    if item["kind"] == "diagnosis":
        require(bool(item.get("linked_event_id")), "Diagnosis needs linked_event_id")
    validate_citations(data, sources)
    serialized = encode(item)
    if old:
        require(old[0] == serialized, f"Event {event_id} already exists with different data; append a correction")
        return
    conn.execute(
        "INSERT INTO events VALUES (?,?,?,?,?,?,?,?)",
        (event_id, item["kind"], item["at"], item["result"], int(item["independent"]), serialized,
         item.get("linked_event_id"), item.get("supersedes")),
    )
    conn.executemany("INSERT INTO event_topics VALUES (?,?)", [(event_id, t) for t in topics])


def apply(conn, payload):
    object_value(payload, "Payload")
    require(set(payload) <= {"sources", "topics", "events"}, "Unknown payload section")
    for key in ("sources", "topics", "events"):
        require(isinstance(payload.get(key, []), list), f"{key} must be an array")
    with conn:
        for item in payload.get("sources", []):
            upsert_source(conn, item)
        sources = load_records(conn, "sources")
        for item in payload.get("topics", []):
            topic_id = identifier(item)
            require(isinstance(item.get("label"), str) and item["label"].strip(), "Topic needs a label")
            object_value(item.get("metadata", {}), "Topic metadata")
            conn.execute("INSERT INTO topics VALUES (?,?) ON CONFLICT(id) DO UPDATE SET record=excluded.record", (topic_id, encode(item)))
        topics = load_records(conn, "topics")
        for item in topics.values():
            metadata = item.get("metadata", {})
            prerequisites = metadata.get("prerequisites", [])
            require(isinstance(prerequisites, list) and all(isinstance(p, str) and p in topics and p != item["id"] for p in prerequisites), "Unknown or self-referential prerequisite")
            if "classroom_priority" in metadata:
                require(metadata["classroom_priority"] in {"high", "medium", "low", "unknown"}, "Invalid classroom priority")
            validate_citations(metadata, sources)
        for item in payload.get("events", []):
            add_event(conn, item, sources, set(topics))


def snapshot(conn):
    row = conn.execute("SELECT id, name, schema_version FROM course").fetchone()
    events = [json.loads(r[0]) for r in conn.execute("SELECT record FROM events ORDER BY rowid")]
    events.sort(key=lambda event: datetime.fromisoformat(event["at"]))
    return {"course": dict(zip(("id", "name", "schema_version"), row)),
            "sources": list(load_records(conn, "sources").values()),
            "topics": list(load_records(conn, "topics").values()),
            "events": events}


def report(conn):
    state = snapshot(conn)
    superseded = {e["supersedes"] for e in state["events"] if e.get("supersedes")}
    active = [e for e in state["events"] if e["id"] not in superseded
              and not (e["kind"] == "diagnosis" and e.get("linked_event_id") in superseded)]
    latest_diagnosis = {e["linked_event_id"]: e for e in active if e["kind"] == "diagnosis"}
    pending = []
    for event in active:
        if event["kind"] == "homework" and event["result"] in {"incorrect", "partial"}:
            diagnosis = latest_diagnosis.get(event["id"])
            if not diagnosis or not diagnosis["data"].get("diagnosis_complete", False):
                pending.append({"event_id": event["id"], "next_question": diagnosis["data"].get("next_question") if diagnosis else None})
    topic_reports = []
    for topic in state["topics"]:
        events = [e for e in active if topic["id"] in e["topics"]]
        attempts = [e for e in events if e["kind"] != "diagnosis" and e["result"] != "unverified"]
        topic_reports.append({"topic": topic, "event_ids": [e["id"] for e in events],
                              "question_count": sum(e["kind"] == "question" for e in events),
                              "observed_results": dict(Counter(e["result"] for e in attempts)),
                              "independent_correct": sum(e["result"] == "correct" and e["independent"] for e in attempts),
                              "latest_observed_attempt": attempts[-1] if attempts else None})
    return {"course": state["course"], "sources": state["sources"], "topics": topic_reports,
            "pending_homework_diagnoses": pending,
            "note": "Descriptive observations only; question frequency is not a mastery score."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "apply", "report", "export"):
        part = sub.add_parser(command)
        part.add_argument("--db", required=True, type=Path)
        if command == "init":
            part.add_argument("--course-id", required=True)
            part.add_argument("--name", required=True)
        elif command == "apply":
            part.add_argument("--payload", required=True, type=Path)
        elif command == "export":
            part.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    path = args.db.expanduser().resolve()
    if args.command == "init":
        require(bool(args.course_id.strip()) and bool(args.name.strip()), "Course ID and name cannot be empty")
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path)
        try:
            conn.executescript(SCHEMA)
            with conn:
                existing = conn.execute("SELECT id FROM course").fetchall()
                require(not existing or existing == [(args.course_id,)], "Database belongs to a different course")
                conn.execute("INSERT OR IGNORE INTO course VALUES (?,?,1)", (args.course_id, args.name))
            print(encode({"database": str(path), "course_id": args.course_id}))
        finally:
            conn.close()
        return
    conn = open_db(path, readonly=args.command in {"report", "export"})
    try:
        if args.command == "apply":
            apply(conn, json.loads(args.payload.read_text(encoding="utf-8-sig")))
            print(encode({"saved": True, "database": str(path)}))
        elif args.command == "report":
            print(encode(report(conn)))
        else:
            destination = args.out.expanduser().resolve()
            require(destination != path, "Export cannot overwrite the database")
            require(all(destination != Path(source["path"]) for source in load_records(conn, "sources").values()),
                    "Export cannot overwrite a registered source")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(snapshot(conn), ensure_ascii=False, indent=2), encoding="utf-8")
            print(encode({"export": str(destination)}))
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError, KeyError, OSError, sqlite3.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
