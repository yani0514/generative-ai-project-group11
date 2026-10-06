# Decisions

# Week 1: the stack, the first call, and what it costs

## Week 1

**Run conditions.** Everything below was produced on:

- machine: ASUS ROG Strix G16 G614JVR, Intel(R) Core(TM) i9-14900HX, 32 GB RAM
- model: qwen3:4b-instruct
- served by: Ollama, one request at a time, locally
- dates: 2026-10-02 to 2026-10-03

Every number in this file is meaningless without those four lines, so they
are stated once here and referred to rather than repeated.

### 1. Machine and model set

I am running the required plus optional model set.

The installed models are:

- `qwen3:4b-instruct`
- `nomic-embed-text`
- `qwen2.5:7b`
- `qwen3-vl:4b`

The optional models are already available locally, so no additional model setup is required before week 9.

### 2. The first call

| | |
| --- | --- |
| finish reason | `stop` |
| prompt tokens | 24 |
| completion tokens | 42 |
| elapsed | 6.26 s |

The finish reason was `stop`, meaning the model ended normally. If it had returned a truncation/length-related finish reason instead, the program should treat the output as incomplete rather than as a valid short answer.

### 3. Variance

| cell | distinct (recording) | distinct (mine) | median latency |
| --- | ---: | ---: | ---: |
| closed_short, t=0.0 | 1/12 | 1/6 | 0.07 s |
| closed_short, t=1.0 | 1/12 | 1/6 | 0.07 s |
| open_list, t=0.0 | 1/12 | 1/6 | 0.64 s |
| open_list, t=1.0 | 11/12 | 6/6 | 0.96 s |

How many distinct answers did you get? Does your machine agree with the recording?
- At temperature 0, both the `closed_short` and `open_list` prompts produced one distinct answer on my machine. This agrees with the recording.

Which cell still returns a single answer at temperature 1.0, and why that one:
- The `closed_short` cell still returned a single distinct answer at temperature 1.0. The prompt is highly constrained because it asks for the capital of Luxembourg in one word, so there is very little room for a valid alternative response.

Which cells a test asserting exact string equality would pass on, and what that tells me about testing this system:
- An exact-string equality test would pass for `closed_short, t=0.0`, `closed_short, t=1.0`, and `open_list, t=0.0` in my run. It would fail for `open_list, t=1.0`, where all 6 responses were different strings. This shows that exact string equality can work for tightly constrained outputs, but it is not reliable for open-ended generation where several differently worded answers may still be valid.


**The sentence that carries into week 10.** Exact output repetition can be relied on more for tightly constrained prompts, especially at low temperature, but it should not be assumed for open-ended generation where multiple valid outputs are possible.

### 4. The cold start

- cold call: 2.72 s
- warm call: 0.07 s
- ratio: 39.22x

What this implies for a system that uses more than one model, and what I
will do about it:

The cold call was much slower because the model had to be loaded into memory before generating the response. Switching between different models inside a single user request could therefore introduce large latency spikes if each model has to be loaded separately. I would avoid unnecessary model switching within one request and prefer keeping one model warm or routing requests to a model before starting the main processing pipeline.

### 5. Cost, estimated

A 200-case golden set, at the token cost of my long case:

| | one run | nightly for the semester |
| --- | ---: | ---: |
| small tier | 0.0335 EUR | 3.28 EUR |
| large tier | 2.4912 EUR | 244.14 EUR |

Estimates against the price list dated 2026-08-10, not
measurements. Running locally, my actual monetary cost was zero.

Which tier I would run nightly, which I would run before a release, and why
not the same one for both:

I would run the small tier nightly because it is much cheaper for repeated evaluation. I would use the large tier before a release when higher model capability may justify the additional cost. Using the large tier every night would be unnecessarily expensive for routine regression testing.

### Deferred

Nothing deferred for Week 1.


## Week 2

**Run conditions.** model: `qwen3:4b-instruct` | temperature: 0.0 | prompt version: `week02-zero-shot-v1` |
served locally | date: 2026-10-05 | scored on: my own machine

### 1. The output contract

The conventions I chose, and why:

- due_date, when the message states no date: `None` / `null`
- due_date, when the message states only a relative expression: `None` / `null`
- quote, and what "verbatim" means in my scorer: the returned quote must appear exactly as a substring of the original message. The scorer does not lowercase, remove punctuation, change whitespace, translate, or paraphrase it.
- what my scorer does with a record that failed validation: it increments the invalid-record count and counts all four fields as incorrect for that document.

This matters because silently skipping invalid records would make the reported score look better when the model produces outputs that cannot even be validated.

### 2. Zero-shot, per field

| field | correct | of |
| --- | ---: | ---: |
| category | 8 | 10 |
| urgency | 10 | 10 |
| due_date | 9 | 10 |
| quote | 10 | 10 |
| invalid records | 0 | 10 |

My prediction, written before block 3: examples will help most on `due_date` and category classification
because those were the fields where the zero-shot baseline made mistakes.

### 3. Few-shot

Examples chosen, and the job each one does:

| example | why it is in the block | field it should move |
| --- | --- | --- |
| EX-02 | Shows a French facilities request with no explicit due date and helps distinguish facilities from access | category / due_date |
| EX-03 | Shows a German hardware request with an explicit calendar date | category / due_date |
| EX-01 | Gives a clear access example to separate access from hardware and facilities | category |
| EX-04 | Demonstrates an informational request with no explicit due date | urgency / due_date |

| field | zero-shot | few-shot | move |
| --- | ---: | ---: | ---: |
| category | 8/10 | 8/10 | +0 |
| urgency | 10/10 | 10/10 | +0 |
| due_date | 9/10 | 10/10 | +1 |
| quote | 10/10 | 9/10 | -1 |

### 4. What got worse

The `quote` field got worse, decreasing from 10/10 in the zero-shot run to 9/10 in the few-shot run.

Looking at the individual failures:
- `REQ-01` was fixed. In the zero-shot run, the model incorrectly extracted `2023-10-27` as a due date even though the expected value was `None`. In the few-shot run, this error disappeared.

- `REQ-04` did not improve. It was still classified as `access` instead of `facilities`.

- `REQ-08` changed shape rather than being fixed. In the zero-shot run it was classified as `access` instead of `hardware`; in the few-shot run it was classified as `facilities` instead of `hardware`.

- A new error appeared on `REQ-05`: the returned quote was not a verbatim substring of the source document.

So the few-shot examples fixed the due-date error, but they did not improve the overall category score because one category error stayed the same and another only changed to a different and still wrong label. They also introduced a new quote error.

### 5. What the examples cost

- extra input tokens per call: 295
- per thousand calls: 295000
- estimated euros per thousand calls on the small tier: 0.059 EUR, against the
  price list dated 2026-08-10. Estimate, not a measurement.

### 6. Ship it or not

For now, I would ship the zero-shot variant rather than the few-shot variant.

The few-shot version improved `due_date` from 9/10 to 10/10, but `quote` dropped from 10/10 to 9/10. The category score stayed at 8/10, and the failure lines show that `REQ-08` only changed from one wrong category to another wrong category.

The few-shot prompt also adds 295 input tokens per call, so it adds extra input-token cost without showing a clear overall accuracy improvement.

With only ten records, this is not enough evidence to conclude that few-shot is better. I would change my mind if the few-shot version kept the due-date improvement, recovered the quote accuracy, and showed better category accuracy on a larger evaluation set.

### Sensitivity variant

Variant assigned: `role`. What I changed: I prepended the sentence `You are a senior service desk analyst.` to the existing few-shot system prompt and changed nothing else. 

What moved:

| field | baseline | role | move |
| --- | ---: | ---: | ---: |
| category | 8/10 | 9/10 | +1 |
| urgency | 10/10 | 10/10 | +0 |
| due_date | 10/10 | 10/10 | +0 |
| quote | 9/10 | 9/10 | +0 |

The role variant improved category by one case. No other field moved.

The language-level field-error counts were:

- English: 1 error with the baseline, 0 with the role variant
- French: 2 errors with both variants
- German: 0 errors with both variants

This shows that even a small prompt change can move a measured result. However, one corrected case out of only ten documents is not enough evidence to claim that adding a role generally improves classification.

### The gold set

Ten cases written to `artifacts/goldset.json`, tagged by language.

One thing my scorer cannot currently detect:

For the `quote` field, the scorer only checks whether the returned text appears verbatim in the original message. It does not check whether the selected quote actually supports the predicted urgency.

### Deferred

Nothing deferred for Week 2.

## Week 3

**Run conditions.** classifier model: `qwen3:4b-instruct` | answering model: `qwen3:4b-instruct` |
temperature: 0.0 | served locally | date: 2026-10-05 to 2026-10-06 | scored on: my own machine

### 1. The five route definitions

| route | definition, one sentence, in terms of what the help desk must do |
| --- | --- |
| request | The sender wants the help desk to take a concrete action, provide a service, or solve a specific problem. |
| info | The sender wants factual information or an explanation about a commune service, without asking for an action to be taken. |
| status | The sender wants an update on the progress or current state of a previously submitted request, case, or issue. |
| complaint | The sender wants the help desk to acknowledge dissatisfaction with a commune service, handling, delay, or outcome. |
| other | The sender's message does not require a service action, factual answer, status update, or complaint handling, and should be handled as a general or uncategorized message. |

My convention for the four ambiguous queries:

I kept the convention used in `queries.py`: unresolved problems combined with dissatisfaction are treated as `complaint`; chasing an existing report without dissatisfaction is `status`; and when a message asks a procedural question while also reporting a fault, the required action takes priority and the route is `request`.

Do my definitions match the ones in `queries.py`? Yes, they follow the same general routing convention, although the wording is my own.

### 2. The policy layer

Before choosing a threshold, the confidence values I saw were: min 0.00,
max 1.00, 4 distinct values across 24 queries.

- confidence floor: 0.00, because the incorrect predictions were still reported with very high confidence, while `Q-22` was correctly classified as `other` with confidence 0.00. A positive threshold would reject a correct case without catching the high-confidence misroutes.
- evidence check: if the evidence span is not present verbatim in the original message, I route to the safe default, because fabricated evidence makes the decision difficult to audit.
- safe default: `info`, because that specialist only answers and does not create a ticket or escalate a case, so an incorrect fallback is easier to undo.

How often each check fired: below_threshold 0, evidence_not_verbatim 0,
invalid_decision 0.

The confidence threshold fired zero times. The distribution shows that this is because the model's self-reported confidence was not a useful signal for separating correct and incorrect routes, rather than because every high-confidence classification was correct.

### 3. Route accuracy

| route | correct | of |
| --- | ---: | ---: |
| request | 5 | 7 |
| info | 5 | 5 |
| status | 4 | 4 |
| complaint | 4 | 4 |
| other | 2 | 4 |

Overall 20/24. Excluding the four ambiguous: 17/20.

Confusion pairs, with direction:

| gold | applied | count |
| --- | --- | ---: |
| request | complaint | 2 |
| other | info | 1 |
| other | request | 1 |

The routes carrying most of the errors are `request` and `other`. The fix is a definition, because the confusion pairs suggest that the boundaries between these routes and the neighbouring routes are not clear enough.

### 4. What routing cost

- monolith: 6326 tokens over 24 queries
- router: 12692 tokens over 24 queries
- the classifying call alone: 7927 tokens, which is 62 per cent of the routed total

I did not record a prediction for that share before measuring it.

The 62 per cent share surprised me because the routing call is only deciding which specialist should handle the message, but it consumed most of the routed system's tokens. This happens because the classifier prompt includes all five route definitions on every call, while the selected specialist only carries the instructions for its own route.

### 5. What routing bought

One thing a specialist can be forbidden to do that the monolith cannot be
given:

The `status` specialist can be forbidden to invent the current state, completion date, or history of an existing case, because it only handles status queries. Giving the same restriction to the monolith would also affect other message types where different behavior is needed.

Would I ship the router: not yet. 
Evidence: it routed 20/24 queries correctly, or 17/20 when the four ambiguous cases are excluded, but the routing call alone used 62 per cent of the routed system's tokens. 
What would change my mind: a larger evaluation set showing that the specialist restrictions provide a clear reliability or safety benefit that justifies the extra routing cost.

### 6. Stretch variant

Variant assigned: model - `qwen2.5:7b`. 

My prediction: the larger `qwen2.5:7b` model will route more accurately because it has greater capacity, but it may use more memory and may not provide more useful confidence values.

Result:
- `qwen3:4b-instruct`: 21/24 correct, 17/20 excluding ambiguous cases, evidence verbatim 24/24, confidence range 0.00 to 1.00 with 3 distinct values, resident memory 3.9 GB.
- `qwen2.5:7b`: 18/24 correct, 16/20 excluding ambiguous cases, evidence verbatim 22/24, confidence range 0.95 to 1.00 with 2 distinct values, resident memory 5.0 GB.

The smaller `qwen3:4b-instruct` model performed better on routing accuracy and evidence copying while also using less resident memory. This shows that the larger model is not automatically better for a narrow classification task, so model choice should be based on measured task performance rather than model size alone.

### The gold set

`artifacts/goldset.json` now holds 34 cases: 10 from week 2 and 24 added
today, with the four ambiguous ones tagged.

### Deferred

Nothing deferred for Week 3.