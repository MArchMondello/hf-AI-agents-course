# My agents — roster

Every agent I build has **one folder** here, with the same files:

| File | What it holds |
| --- | --- |
| `PROMPT.md` | the original request, verbatim |
| `PLAN.md` | the approved plan |
| `<Agent>.ipynb` | the live diff against the template it started from, and one explanation per change |
| `EVAL.md` | the assessment: what it gets wrong, where in the code, what to try; numbers from a probe (once it has one) |

The code itself lives **only** where the agent runs (a Hugging Face Space): its git history is the record.
This repo documents it, and the notebook downloads it to compute the diff, so the docs cannot go stale.

| Agent | What it does | Live | Docs |
| --- | --- | --- | --- |
| First_agent_template | AI Agents Course Companion: answers any question, cites the [`brain/`](../brain/) notes, describes the repo and its results. A `ToolCallingAgent` (Llama 3.3 70B, 11 read-only tools); no model-written code runs, see [1.8](../brain/1.8-LL-public-agent-codeagent-is-not-a-sandbox.md) | [Space](https://huggingface.co/spaces/MArcoMondelloMBAMArch/First_Agent_Template) | [First_agent_template/](First_agent_template/) |

## How to add an agent

1. Create `my-agents/<Agent>/` with `PROMPT.md` (the request) and `PLAN.md` (the approved plan).
2. Build the agent where it runs (to change it: [`tools/deploy_space.py`](../tools/deploy_space.py), `get` → edit → `put` → `put --commit`); copy `First_agent_template.ipynb` to `<Agent>.ipynb` and change its parameters cell (`UPSTREAM`, `SPACE`, the two shas).
3. Add one row to the table above.
