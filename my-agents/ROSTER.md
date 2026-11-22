# My agents — roster

Every agent I build has **one folder** here, with the same three files:

| File | What it holds |
| --- | --- |
| `PROMPT.md` | the original request, verbatim |
| `PLAN.md` | the approved plan |
| `<Agent>.ipynb` | the live diff against the template it started from, and one explanation per change |

The code itself lives **only** where the agent runs (a Hugging Face Space): its git history is the record.
This repo documents it, and the notebook downloads it to compute the diff, so the docs cannot go stale.

| Agent | What it does | Live | Docs |
| --- | --- | --- | --- |
| First_agent_template | Repo guide: answers any question; cites Marco's [`brain/`](../brain/) notes. A `ToolCallingAgent` (Llama 3.3 70B, 8 read-only tools, no model-written code runs: [why](../brain/1.8-LL-public-agent-codeagent-is-not-a-sandbox.md)) | [Space](https://huggingface.co/spaces/MArcoMondelloMBAMArch/First_Agent_Template) | [First_agent_template/](First_agent_template/) |

## How to add an agent

1. Create `my-agents/<Agent>/` with `PROMPT.md` (the request) and `PLAN.md` (the approved plan).
2. Build the agent where it runs; copy `First_agent_template.ipynb` to `<Agent>.ipynb` and change its parameters cell (`UPSTREAM`, `SPACE`, the two shas).
3. Add one row to the table above.
