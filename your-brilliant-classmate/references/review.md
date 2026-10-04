# Personalized final-exam review

## Start from saved evidence

Load course metadata, topic priorities, source coverage, and active learning events. Confirm exam date/scope and available time only if needed and not already known. Preserve user-specified exam formats. Explicit teacher scope takes precedence over an inferred topic-frequency ranking.

Build a report that distinguishes:

- confirmed mistakes and their supported causes;
- unresolved questions or incomplete diagnoses;
- improvement demonstrated by later independent attempts;
- topics with only assisted success or self-report;
- important topics with no assessment evidence;
- unprocessed material and source-access gaps.

Use `course_store.py report` for event counts and pending diagnoses; then interpret the actual evidence. Its counts are descriptive, not a mastery score. Repeated questions alone cannot label a topic weak. Preserve the history: one later error can reopen a topic, and one immediate success is weak evidence of stable retention.

## Prioritize transparently

Prioritize within the exam scope using classroom importance, severity and recurrence of confirmed difficulties, prerequisite impact, whether later independent attempts resolved them, and time available. Label priority reasons in the saved report with linked event/source evidence. Avoid numerical confidence or mastery percentages without a validated measurement method.

High-priority but untested topics need short diagnostics, not automatic remediation. Low-frequency topics still deserve coverage when in scope. Maintain a coverage checklist so personalization does not become endless repetition of the same wrong questions.

## Review material and interaction

Create a practical plan fitting the time available, plus a topic-based weakness sheet. For each selected topic include the original source locator/screenshot when teaching it, the student's actual past confusion, a concise correction, and suitable retrieval or transfer practice. Keep quotes short and mark newly generated questions as assistant-created. Do not invent past mistakes, quiz scores, dates, or teacher exam predictions.

Choose practice suited to the course: explanations, diagrams, derivations, calculations, proofs, experimental decisions, coding, language production, or rubric-based argumentation. Use an altered context or delayed check to distinguish memorizing a past answer from understanding. For an interactive self-test, show questions before answers; for a requested printable answer key, separate questions and solutions.

Append each observed `review` attempt, including independence, topic links, result, reasoning, citations, and follow-up date if agreed. Revisit recurring causes with targeted practice, then broaden to mixed tasks and previously untested material. Treat repeated independent success across different tasks and occasions as stronger evidence than a single immediate retry.

## Deliverables and persistence

Save the review plan and readable knowledge/weakness report under the course's `reports/`, linking to the database-backed event IDs and source locators. Export an inspectable JSON snapshot with `course_store.py export` if useful. Keep source paths usable; do not export records to external services without a user request.

Dates stored in the database are suggested study dates, not background reminders. Do not claim the skill will wake up, monitor, or schedule notifications by itself. If no history exists, start from course coverage and a diagnostic; state that the plan is based on course materials rather than personal performance.
