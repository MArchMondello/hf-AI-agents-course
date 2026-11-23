# EVAL — AI Agents Course Companion

*The agent's assessment: what it gets wrong, where in the code that comes from, and what to try next. Every claim points to evidence: the quiz session of 23 Nov 2026 (the anecdote) and [probe 1.10](../../brain/1.10-CS-evals-measuring-an-agent.md) (the numbers). This is a working file: when the agent changes, re-run the probe and add a line to the log at the bottom.*

| | |
| --- | --- |
| Agent | [Space](https://huggingface.co/spaces/MArcoMondelloMBAMArch/First_Agent_Template) @ `03d5d79` · `ToolCallingAgent` · Llama 3.3 70B (Novita) · temperature 0.5 · max 4 steps |
| Notes it reads | this repo's `brain/` @ `34ddd1a` (frozen for the probe) |
| How to re-measure | [the notebook](First_agent_template.ipynb), section 5: parameters → collect (spends credit) → measure (free) |

## 1. Scorecard (baseline A, 23 Nov 2026)

| Behaviour | Public set | Private set (quiz) | Target |
| --- | --- | --- | --- |
| One note answers → cites the right note | 15/18 | 14/21 | all, except search misses we know |
| No note answers → says so, without a `Source:` | **0/18** | **0/9** | most |
| No note answers → cites a note as if it answered | **11/18** | **9/9** | 0 |
| Needs two notes → opens both | **0/6** | — | most |
| Cites a note it never opened | 5/42 | 0/30 | 0 |
| Cites a note that doesn't exist | 1/42 | 0/30 | 0 |
| Errors / crashes | 0/42 | 0/30 | 0 |
| Cost per question | ~11,500 input tokens, ~8 s | ~10,500, ~8 s | about the same |

Tried and **not adopted**: B (one sentence in the prompt: "if the notes don't answer, say so and don't cite them"): clean answers 0 → 3/18, still 0/9 on the quiz. C (the search says how many keywords each note contains): no change beyond noise, maybe worse on the quiz (right note 14 → 12/21).

## 2. Findings

Each finding: what it does · the evidence · where it comes from in the code (Space @ `03d5d79`) · what to try · how to see if it worked.

### F1. It cites notes that don't answer the question (false source) — the most serious

- **What:** outside the notes, the answer is usually built from the closest note and signed with it. Sometimes it bends the note to fit: the KV cache (a memory inside the model) becomes "the weather tool's HTTP cache" from 1.4; LangGraph "passes state through a closed loop" from 1.0. When it does notice the gap it says so, **and cites the note anyway**.
- **Evidence:** quiz session (Q1, Q3, Q7: special tokens, design rules, ReAct); probe 1.10: 11/18 "as if it answered", 6/18 "says so but cites", 9/9 on the quiz; KV cache and LangGraph 9/9 bent.
- **Where it comes from:**
  - `tools/repo_core.py` lines 336–337: `find_brain_note` returns the top 3 notes as soon as **one** keyword matches (`if s > 0`). The model can't tell a strong match from a weak one;
  - `tools/final_answer.py` lines 8–10: the answer's own description says *"If a repo tool gave you information… end with 'Source: …'"*. Any tool output counts as "information", so a citation is always demanded. It competes with any "don't cite" rule (variant B);
  - `prompts.yaml` line 4: no instruction for "the note doesn't answer".
- **What to try (code first, the prompt didn't work):**
  1. `read_brain_note` adds one line: *"Words of your question not found in this note: kv, langgraph"* (the rare words, as the search already ranks them). The drawing says what it doesn't cover;
  2. the citation rule in `final_answer.py` becomes: cite only the note whose text you used.
- **How to see it:** probe 1.10, outside the notes: "says so, no source" up, "cites as if it answered" down; covered: right note not down.

### F2. It never reads two notes (no cross-reference)

- **What:** one search, one read, answer. When a note is out of date and a newer note corrects it, the agent can't know.
- **Evidence:** probe 1.10: **0 of 216** runs opened two notes. Asked which model the Space uses, it read 1.6 (the course template, Qwen) and never 1.8 (today's model, Llama): "Qwen2.5-Coder-32B", 9/9, wrong.
- **Where it comes from:**
  - `prompts.yaml` line 4 prescribes the path: *"find_brain_note, then read_brain_note"*, once;
  - `app.py` line 169: `max_steps=4` → search + read + answer = 3 steps: room for one more read at most;
  - `tools/repo_core.py` line 514: one read returns at most 2,500 characters, so the links to other notes often fall outside it; and nothing tells the model that notes link to each other.
- **What to try:** `read_brain_note` ends with *"Linked notes: 1.7, 1.8"* (the links found in the note); the prompt: *"if the note points to another note for the details, read it too"*; `max_steps` 4 → 6 (about +4,000 input tokens per question that uses it).
- **How to see it:** probe 1.10, two-note questions: "read both notes" up; X2 answers "Llama".

### F3. The search misses when the question uses other words

- **What:** "Where can the .env file live…" → 0.2 (Python venv) instead of 0.8 (secrets), and the answer is wrong ("in the project folder"). A quiz question on designing tools → 1.8 (sandboxes) instead of 1.4 (*"the LLM only sees its name, arguments and docstring"*).
- **Evidence:** probe 1.10: C3 wrong 9/9, quiz Q8 wrong 9/9, in every variant (it's the search, not the model).
- **Where it comes from:** BM25F matches words, not meanings ([1.9](../../brain/1.9-LL-note-search-bm25-measured.md)).
- **What to try:** add these two queries to the search bench (`tests/search_eval.py` in the Space), then synonyms or embeddings (1.9, next probes).
- **How to see it:** the 1.9 bench (free, no model), then probe 1.10 covered.

### F4. It cites notes it never opened, once one that doesn't exist

- **What:** the search shows a one-line preview of 3 notes; the agent sometimes cites one of them without reading it. Once it invented a note, `0.0-LL-tokenization-subwords`, with a link that looks real.
- **Evidence:** probe 1.10: 5/42 baseline runs cite an unopened note (X2 cites 1.9 from its preview); 1/42 invents one.
- **Where it comes from:** nothing checks the `Source:` against the notes that exist and the notes that were read; the link pattern is easy to imitate.
- **What to try (code, deterministic):** before returning, `final_answer` checks every cited note name: it must exist and must have been opened in this run; otherwise the citation is removed or marked.
- **How to see it:** the two counters in the measure cell go to 0.

### F5. It says more than the note says

- **What:** "ReAct… enables the model to learn and adapt" — the model's weights don't change; what it "learns" lives in the context of one run.
- **Evidence:** quiz Q7; probe 1.10 private Q7, 9/9.
- **Where it comes from:** `prompts.yaml` line 4: *"nothing that is not in the tool output"* applies only to questions about Marco, not to answers from the notes.
- **What to try:** extend that sentence to every answer that cites a note.
- **How to see it:** read by hand (the meter can't judge "says more than the note").

### F6. Format: literal `\n`, and an answer cut after a backslash

- **What:** lists arrive with `\n` written out; once in a while the answer stops after `…provided by a tool: \`.
- **Evidence:** quiz Q3 and Q5; probe 1.10: `\n` in 4/9 runs of the list question, the cut answer 2/3 in A.
- **Where it comes from:** the model writes the line breaks as escapes inside the tool-call JSON.
- **What to try (code):** `FinalAnswerTool.forward` (`tools/final_answer.py` lines 14–15) turns `\n` into real line breaks and refuses an answer that ends with a backslash or is shorter than a sentence, so the agent gets one more step.
- **How to see it:** the `\n` counter; the cut answer gone from Q5.

### F7. What works (keep it)

- When one note answers and the search finds it, the answer is faithful and cites it: 15/18 public, Q2/Q9/Q10 3/3 in every variant.
- 0 errors in 216 runs; ~8–10 s and ~11,000 input tokens per question.
- Very consistent: the 3 runs of a question almost always agree, so one more question teaches more than one more run.

## 3. Backlog, in order of value per effort

| # | Change | Fixes | Kind | Effort |
| --- | --- | --- | --- | --- |
| 1 | `final_answer` checks the citations: the note exists and was opened | F4, part of F1 | code | small |
| 2 | `read_brain_note` lists the question's rare words missing from the note | F1 | code | small |
| 3 | `final_answer`: real line breaks, refuse a cut answer | F6 | code | small |
| 4 | `read_brain_note` lists linked notes + prompt "follow the link" + `max_steps` 6 | F2 | code + prompt | medium (cost per question up) |
| 5 | "nothing not in the tool output" for every cited answer | F5 | prompt | small, measured by hand |
| 6 | the search bench gets the C3 and Q8 queries; then synonyms or embeddings | F3 | search | medium |

After each change: re-run probe 1.10 (~2.4 M input tokens), compare with the scorecard above, add a line to the log.

## 4. Log

| Date | Space | What changed | Result |
| --- | --- | --- | --- |
| 2026-11-23 | `03d5d79` | baseline measured; variants B (prompt sentence) and C (match strength) tried, not adopted | scorecard above; [1.10](../../brain/1.10-CS-evals-measuring-an-agent.md) |
