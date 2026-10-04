# Source-grounded tutoring and homework diagnosis

## Knowledge questions and worked problems

1. Identify the active course and map the question to one or more topics. Retrieve relevant textbook and lecture passages, examples, and quiz items from the index.
2. Open the original pages/slides; verify wording, notation, formulas, assumptions, and locators. Generate readable source screenshots that include needed conditions and diagram labels. If the passage continues onto another page, include both.
3. Answer directly in the course's terminology. Use a short exact quotation for the core definition or statement where useful, then explain its meaning or apply it step by step. Keep quotations separate from paraphrases and supplemental reasoning. With no supplied source, label the answer provisional and explain why a course screenshot is unavailable.
4. Attach the screenshot(s), original file locator, and printed page when verified. A screenshot of the student's problem can support interpretation of the question, but is not a substitute for the relevant knowledge passage when that passage is available.
5. Append a `question` event with the topic IDs, question or faithful summary, relevant citations, and `result: unverified` by default. Record an observed assessment outcome only when the student actually produces one. Optional follow-up checks should help learning, not obstruct a requested direct explanation.

A repeated question is a useful review signal, but may reflect curiosity or an advanced question. State this distinction in summaries. Saying "I understand" is self-report, not independent demonstrated mastery.

## Checking homework interactively

Read the problem and the student's submitted work before grading. Distinguish a verified teacher answer, an independent assistant solution, and a provisional judgment. Missing work is not a wrong answer. For calculations check assumptions, units, signs, intermediate steps, and result; for proofs check logical sufficiency; for essays check claims, evidence, rubric criteria, and structure; for code inspect reasoning, execution, and relevant tests.

Mark clearly observable errors and correct work promptly. Before exposing a full correction that would bias the diagnosis, ask a neutral question about the relevant step: what they were trying to do, why they chose that formula/claim, or what they thought a condition meant. Ask one or two focused questions per turn, listen, and adapt the next question to the answer. A long fixed diagnostic questionnaire is inappropriate.

Use these cause labels as a shared vocabulary, adding a course-specific cause if necessary:

- `missing_knowledge`: cannot recall or identify the relevant concept/rule.
- `misconception`: explicitly states an incorrect meaning or relation.
- `condition_misuse`: knows a rule but applies it outside its conditions.
- `strategy_gap`: cannot select or connect a suitable approach.
- `execution_error`: arithmetic, algebra, units, signs, transcription, or implementation mistake, with otherwise sound reasoning.
- `reading_error`: misinterprets the prompt, data, or required task.
- `expression_gap`: incomplete reasoning, unclear presentation, or insufficient evidence against the rubric.
- `unknown`: available evidence cannot establish a cause.

Multiple causes can coexist. Initially label hypotheses `suspected`. Confirm a cause only using the student's actual reasoning or a discriminating follow-up attempt; retain a short evidence quote or work locator. Do not infer a misconception from a wrong final number alone, or call an unexplained error "carelessness". A correct answer can still contain faulty reasoning.

Save the initial `homework` event with the actual attempt/result. Append `diagnosis` events linked to that event as the interaction develops, leaving the original record intact. Save unfinished diagnosis with the best next question so another chat can resume. If the student declines further questioning or wants all corrections at once, honor that preference: supply the correction and leave uncertain causes unconfirmed.

Once the cause is supported, provide a concise explanation using the relevant source screenshot, a targeted correction, and a small discriminating retry. Observe the retry before recording improvement. An assisted retry is `assisted`; it does not prove independent mastery. Give the student the chance to attempt the retry before revealing its solution, unless they request the answer.

## Correction and updates

If the student disputes an answer or corrects a record, recheck the original evidence. Append a new event with `supersedes` pointing to the mistaken event; include all intended topic links and the corrected data. Historical entries remain auditable but superseded entries do not count in active reports. Never turn an assistant grading error into a student weakness.

For record summaries use ordinary language, such as "已记录：适用条件尚需核实；下一步是解释为何能使用这个公式。" Mention logging failures plainly. Routine bookkeeping should not dominate the tutoring response.
