# Postmortem

## What went wrong

Early development questions were unclear about required output. Asking which customer placed the most orders could reasonably produce only a name, while the reference expected a name and order count. Extra or missing columns caused mismatches despite reasonable SQL. Tie-breaking and ordering also needed clarification.

Our initial parser accepted plain SQL and `sql` or unlabeled Markdown fences, but not `sqlite` fences. Gemma's development run had eight parse errors and scored 2/10. Those errors did not establish that the SQL itself was wrong. The same parser served Phi4-mini and all other models; the recorded incident involved Gemma.

Models also made actual SQL mistakes: nonexistent or ambiguous columns, incorrect date filters, missing limits, and incorrect aggregations.

## How we addressed the problems

We clarified output columns, entity identity, date boundaries, ordering, and tie-breaks. Qwen improved from 4/10 to 10/10 on the revised development questions, showing the effect of clearer questions rather than changed model weights.

We extended the common parser to accept `sqlite` fences case-insensitively. It removes wrappers without repairing SQL or accepting surrounding explanations. Gemma then scored 5/10 with no parse errors. Automated checks cover accepted formats and rejected outputs.

All four models subsequently used the same prompt, parser, scorer, temperature, output limit, and unchanged 50-item test set. Accuracy was Gemma 21/50, Llama 32/50, Phi 50/50, and Qwen 47/50.

## What we learned

Different SQL queries can return the same answer. We therefore execute both the generated and reference queries and compare their returned results, rather than their SQL text. Matching on one database still does not prove equivalence on every possible dataset.

Clear questions and consistent evaluation matter as much as model selection. Questions should specify the intended result without prescribing its SQL implementation.

Local inference is not free. With the same assumed €0.20/hour, lower requests/hour means higher hardware cost/1K: Qwen cost €0.3329 versus Phi's €0.1044. Throughput and device placement matter, not size alone. Setup, maintenance, hardware resources, and developer time add operational costs excluded from this hardware-only metric.

## What we would improve next time

We would document independent reference-answer review before freezing the test set, use a consistent warm-up policy, and record execution metadata for every run. Predefining repetitions for all models would make timing comparisons stronger than repeating only one, without tuning questions after seeing final scores.
