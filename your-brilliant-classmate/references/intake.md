# Course-material intake

## Inventory and source identity

Register textbooks, lecture decks, quizzes, homework, syllabi, teacher comments, and answer keys with distinct IDs. Record title, kind, original path, SHA-256, lecture/date where known, and unit count. Do not infer an edition or teaching date from unreliable metadata. A changed hash is a new version, not a silent replacement of an already cited source.

Inspect actual formats: a misleading `.doc` can be XML; a PDF can be scanned; `.ppt` requires a compatible reader or conversion rather than a `.pptx` parser. Use available format-specific tools. Preserve formulas, diagrams, tables, speaker notes when available, and page/slide boundaries. OCR is searchable assistance, not authoritative transcription of equations.

Use `source_evidence.py index --source ... --out ...` for PDF, PPTX, and image indexes. It preserves one-based unit numbers and hashes but does not OCR or mark anything as studied. For other formats use an appropriate extractor and keep the same provenance convention. Check page images for equations or suspect extraction. Track at least `indexed_units`, `visually_checked_units`, `studied_units`, and `pending_units` in source metadata. Do not equate machine text extraction with reading.

For a large textbook, first inspect its contents and sample pages, create chapter ranges, and index it. Study uploaded lectures/quizzes and currently requested topics in detail, then continue relevant chapter coverage as useful. Report the actual coverage and remaining chapters. Never claim the entire book has been learned from a contents page or a few samples. Reuse verified maps on later turns, checking the current file hash when necessary.

## Knowledge map

Assign stable topic IDs meaningful within the course, such as `thermo-first-law` or `essay-evidence`. Record labels, aliases, parent topics, prerequisite relationships, source locators, and classroom-priority evidence. Match new questions to existing topic IDs before creating synonyms as duplicate topics.

Map each quiz item to concepts, required skills, source units, and available answer/rubric. A quiz's presence is evidence of teaching emphasis; a student's performance on it is separate evidence of mastery. Never invent a teacher key. For open responses, use the supplied rubric, or label an assistant-created rubric as provisional.

## Infer classroom priorities with traceable evidence

Useful signals include explicit exam scope, the teacher's emphasis marks, repeated coverage across lectures, representative in-class examples, assignments, quizzes, and prerequisite importance. Prefer explicit scope over repetition. Count distinct assessments or lectures, not duplicate uploads or many slides illustrating the same idea. Absence from quizzes is not proof that a topic will not be examined.

Store priority as `high`, `medium`, `low`, or `unknown`, with specific source locators and the reason. Distinguish explicit teacher priority from an assistant inference. Keep topic importance separate from student mastery. Avoid confident exam predictions based on frequency alone.

After intake, provide a concise course/topic map, supported classroom priorities, coverage limitations, and useful next learning options. Save the map under `reports/` and the durable topic/source metadata in the database. Attach actual evidence for substantive claims about content or teacher emphasis. Do not generate a full textbook-length set of notes unless requested.

## Source conflicts and missing files

Resolve differing notation using the course's stated conventions. Preserve conflicting passages in the index and cite both when it matters. If an older file has moved, ask for its new location or use an identical hash-verified durable copy. A screenshot from an older edition cannot silently substantiate a newer edition. Keep malformed or unrenderable sources registered as pending rather than dropping them from coverage.
