# Persistent course records and helper contract

Use an available Python interpreter. `course_store.py` requires only the standard library. `source_evidence.py` uses PyMuPDF for PDF operations, python-pptx for PPTX indexing, and Pillow for images. Locate available bundled dependencies when supported; if a renderer/dependency is unavailable, explain the concrete limitation instead of promising a screenshot. Do not install a full Office/OCR suite merely to ingest a file.

Commands below use paths relative to the skill directory; use its actual absolute path when executing. Create JSON payload files with normal file-editing tools instead of interpolating large student text into shell commands.

```text
python scripts/course_store.py init --db /course/learning.sqlite3 --course-id chemistry-2026 --name Chemistry
python scripts/course_store.py apply --db /course/learning.sqlite3 --payload /course/update.json
python scripts/course_store.py report --db /course/learning.sqlite3
python scripts/course_store.py export --db /course/learning.sqlite3 --out /course/reports/records.json
python scripts/source_evidence.py index --source /course/book.pdf --out /course/index/book.json
python scripts/source_evidence.py render --source /course/book.pdf --unit 17 --out /course/evidence/book-p17.png
```

## Atomic payload

`apply` accepts any combination of `sources`, `topics`, and `events`, and updates the batch in one transaction. Missing references or invalid enums roll back the whole batch. Sources/events are immutable by ID; an identical retry is idempotent. Updating a source's coverage or notes is allowed if its identity fields remain unchanged. Topic label/metadata updates preserve all past events.

```json
{
  "sources": [{
    "id": "book-v1", "title": "Course textbook", "kind": "textbook",
    "path": "/course/sources/book.pdf", "sha256": "REPLACE_WITH_ACTUAL_64_HEX_HASH",
    "total_units": 120,
    "metadata": {"coverage": {"indexed_units": [1,2], "studied_units": [1], "pending_units": [2,3]}, "edition": "verified edition"}
  }],
  "topics": [{
    "id": "concept-a", "label": "Concept A",
    "metadata": {
      "aliases": [], "prerequisites": [], "classroom_priority": "unknown",
      "priority_evidence": [],
      "citations": [{"source_id": "book-v1", "unit": 1, "printed_page": "verified label if available"}]
    }
  }],
  "events": [{
    "id": "q-001", "kind": "question", "topics": ["concept-a"],
    "at": "2026-10-04T21:30:00+08:00", "result": "unverified", "independent": false,
    "data": {
      "question": "Faithful student question", "student_reasoning": null,
      "citations": [{"source_id": "book-v1", "unit": 1, "image_path": "/course/evidence/book-p1.png"}],
      "causes": [], "next_question": null
    }
  }]
}
```

The hash and date above illustrate schema, not actual user facts. Never copy them into a live record. Generate IDs for actual events and use the user's current time zone when supplying `at`. If omitted, the helper uses the host's offset-aware current time; override it if host/client contexts differ.

Source `kind`: `textbook`, `lecture`, `quiz`, `homework`, `syllabus`, `answer_key`, `other`.
Event `kind`: `question`, `homework`, `diagnosis`, `diagnostic`, `review`.
Event `result`: `unverified`, `correct`, `partial`, `incorrect`, `assisted`.
`independent` must be a JSON boolean and indicates whether the observed attempt was made without substantive help.

For a homework event, save `problem`, `attempt`, `student_reasoning`, and the grading basis in `data`. For a diagnosis event, use top-level `linked_event_id` to reference the original homework; store `causes` as objects with `label`, `status` (`suspected` or `confirmed`), and `evidence` supporting confirmed causes. Use `next_question` for a pending follow-up. Later diagnosis events for the same attempt replace the current diagnostic view, without deleting earlier evidence; carry forward still-valid causes into the latest event. Mark `diagnosis_complete: true` only when the questioning is finished or the student declined it; uncertainty can remain in either case.

For review/diagnostic attempts, store the actual response, rubric/method, assistance, and feedback; use `linked_event_id` when revisiting a particular mistake. Optional `next_review_date` records an agreed plan. Record the student event only after observing the response.

Top-level `supersedes` references an existing event that this new event corrects. Each event can be superseded once; make further corrections to the latest event in the chain. Corrected entries are excluded from active reports but remain in exports. If a corrected homework becomes correct, no unresolved diagnosis is required merely because of its historical error.

The database stores sources, topics, events, and event-topic relations with foreign keys. Structured metadata remains JSON for domain flexibility. JSON exports include all historical entries, course identity, and schema version; they can be inspected without understanding SQLite. The `report` command exposes active per-topic observations and unfinished homework diagnosis IDs; the AI still decides learning priorities from the evidence.

## Screenshots

`render` accepts a PDF physical page or an image unit (images have only unit 1). Optional `--crop x0 y0 x1 y1` uses normalized coordinates in `[0,1]`; retain all assumptions and labels. It emits the image and an adjacent `.png.json` provenance record with source path, hash, unit, and crop. Inspect the image before citing. Use a unique filename per source hash/unit/crop so evidence from different versions is not overwritten.

For native PPTX, `index` extracts slide text and notes, not visual layout. Render the deck with an available Office/LibreOffice/presentation tool to obtain screenshots. Register the original deck as the source, and keep the conversion path/hash and original slide mapping in citation metadata. Cite the slide the student saw, not an unverified converted page number.
