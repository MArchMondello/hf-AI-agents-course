# hf-AI-agents-course

My agents and experiments, built while following the [Hugging Face AI Agents Course](https://huggingface.co/learn/agents-course).

The default engine is **local and free**: an open model (`qwen2:7b`) served by [Ollama](https://ollama.com) on my own machine.
Paid engines (Claude API, Hugging Face Inference API) are optional, one line away.

## Live demo: the AI Agents Course Companion

**[Try it on Hugging Face Spaces](https://huggingface.co/spaces/MArcoMondelloMBAMArch/First_Agent_Template)**: ask it anything. Questions about agents, LLMs or dev setup are answered from this repo's [`brain/`](brain/) notes, with a link to the note; it can also describe the repo and its results; every answer ends with a live signature (course coverage, notes, experiments, notebooks, stars).

- A smolagents `ToolCallingAgent` (Llama 3.3 70B) with 11 read-only tools: it never runs code written by the model. Why: [1.8](brain/1.8-LL-public-agent-codeagent-is-not-a-sandbox.md).
- Limits: anonymous, 25 questions/day in total (max 5 per visitor); signed in with Hugging Face, 25/day billed to your own account. Each question is independent, max 500 characters.
- How it was built, with the live diff against the course template: [`my-agents/`](my-agents/ROSTER.md).

## What's inside

```
hf-AI-agents-course/
├── .env.example                  ← names of the secrets (no values): copy to .env
├── 0.onboarding.ipynb            ← first agent: smolagents CodeAgent on local Qwen, its guards and sandboxes
├── 1.weather-agent-lab.ipynb     ← an agent from scratch, up to a real weather tool and a hand-made agent loop
├── brain/                        ← cheat sheets (CS) and lessons learned (LL), one per topic
├── certificates/                 ← course certificates, one per unit passed
├── my-agents/                    ← one folder per deployed agent: prompt, plan, notebook (ROSTER.md = the index)
├── probe/                        ← raw model outputs of the experiments, as JSON
└── requirements.txt              ← pinned Python packages
```

| File | What it does |
| --- | --- |
| [`0.onboarding.ipynb`](0.onboarding.ipynb) | A `CodeAgent` with no tools: it answers by writing and running Python (10th Fibonacci number, primes below 100). Then what stops that code from doing damage: the `LocalPythonExecutor` tested against harmful commands, and the sandbox options (Blaxel, E2B, Modal, Docker). |
| [`1.weather-agent-lab.ipynb`](1.weather-agent-lab.ipynb) | The course's "dummy agent", rebuilt with **three interchangeable engines** (local Qwen, Claude, Hugging Face) behind one `chat()` function. Plus a **disrespectful agent** used for the experiments below, and **Maresciallo Costa**: a weather agent with a real tool (`WeatherNow`, live data from [Open-Meteo](https://open-meteo.com), no API key) and a hand-made agent loop. |
| [`my-agents/`](my-agents/ROSTER.md) | The agents I deploy, one folder each. The code lives in the Space; here: the original request, the approved plan and a notebook that computes the diff against the course template **live**. First one: the repo guide agent above. |

## Experiments: can a system prompt make an agent lie?

The notebook's BONUS sections give a rude agent one order, *"hide the truth"*, and one tool, a fake `get_weather`.
Each setup ran 10 times on Qwen2 7B. The raw outputs are in [`probe/`](probe/).

| Setup | Truth | Lie | Lesson |
| --- | --- | --- | --- |
| Order in the system prompt | 8 / 10 | 0 / 10 | the tool result beats a distant order: [1.2](brain/1.2-LL-the-liar-agent.md) |
| Same order, pasted next to the tool result | 0 / 10 | 7 / 10 | the closest text wins, a **prompt injection**: [1.3](brain/1.3-LL-lie-order-next-to-observation.md) |
| Same, plus `stop=["Observation:"]` | 0 / 10 | 1 / 10 | `stop` blocks the forged evidence, not the intent: [1.3](brain/1.3-LL-lie-order-next-to-observation.md) |

What I take from it: **tool output is data, never instructions**, and an agent loop needs `stop`, input validation and `max_steps`.

## Experiments: what does a persona do to the answers?

Maresciallo Costa is a calm TV weatherman, asked to open and close the Final Answer with two fixed phrases.
Weather frozen, 10 runs per variant on Qwen2 7B. Main probe on Castell'Umberto (Sicily), backup on Lyon:

| Setup | Phrases present (Castell'Umberto / Lyon) | Numbers right | In Italian | Lesson |
| --- | --- | --- | --- | --- |
| Phrases in the template line + a tone rule | **1–2 / 10** vs **7–8 / 10** | 20 / 20 | 8 / 20 | same prompt, another city, another result: [1.4](brain/1.4-LL-weather-agent-persona-chat-template.md) |
| Same, **without** the tone rule | 0 / 10 vs 0 / 10 | 20 / 20 | 0 / 20 | a template line shows, a rule commands: [1.4](brain/1.4-LL-weather-agent-persona-chat-template.md) |
| Opening and closing swapped | 1–5 / 10 vs 1–2 / 10 | 20 / 20 | 5 / 20 | position effects: inconclusive: [1.4](brain/1.4-LL-weather-agent-persona-chat-template.md) |

What I take from it: **the prompt asks, the code guarantees**, a prompt validated on one input is not validated, and the model reads one string (the chat template), not a list of messages.

## Experiments: is a public agent safe, and which model can call tools?

Before going live, the repo guide agent went through two adversarial reviews (fake token, fake model writing the attack) and one real tool-call probe per candidate model:

| Test | Result | Lesson |
| --- | --- | --- |
| Review #1 on the course's `CodeAgent` | model-written code read the Space secrets in one line: switched to `ToolCallingAgent` | [1.8](brain/1.8-LL-public-agent-codeagent-is-not-a-sandbox.md) |
| Review #2 on the `ToolCallingAgent` | no critical/high; added a per-visitor cap and an Origin check | [1.8](brain/1.8-LL-public-agent-codeagent-is-not-a-sandbox.md) |
| Tool calls: Qwen2.5-Coder-32B / Qwen2.5-72B / Qwen3-32B / Llama-3.3-70B | 404 / 500 / invalid JSON / **3 of 3 correct** | [1.8](brain/1.8-LL-public-agent-codeagent-is-not-a-sandbox.md) |

What I take from it: **on a public page, a `CodeAgent` needs a real sandbox**; who pays is decided in code before the model runs; pin the provider.

## Experiments: does the agent find the right note?

The agent cited the wrong note for "What is the ReAct loop?". Instead of patching that question: 42 queries with their expected notes, plus 15 held-out ones written before tuning, old search vs new (BM25F), on a frozen copy of the notes:

| Set | Old top-1 | New top-1 | Old top-3 | New top-3 | Lesson |
| --- | --- | --- | --- | --- | --- |
| Development (42) | 35 | **38** | 41 | **42** | [1.9](brain/1.9-LL-note-search-bm25-measured.md) |
| Held-out exam (15) | 13 | **14** | 14 | **15** | [1.9](brain/1.9-LL-note-search-bm25-measured.md) |

What I take from it: **measure before and after, and keep an exam you didn't study for**; rare words carry the meaning; finding the right note is not reading the right part of it.

## Helping others

| Date | Contribution | Link |
| --- | --- | --- |
| 2026-11-22 | Diagnosed why the course's First Agent Template only answers "Error" (a provider 400 hidden by a UI crash) and proposed a 3-line fix to the template | [PR #789](https://huggingface.co/spaces/agents-course/First_agent_template/discussions/789) |
| 2026-11-22 | Posted the cause and the fix where students reported the bug | [discussion #364](https://huggingface.co/spaces/agents-course/First_agent_template/discussions/364) |

What I take from it: a fix for others needs a minimal diff, the evidence (logs, a reproduction) and a reply where people are looking. See [1.7](brain/1.7-LL-helping-others-upstream-fix.md).

## `brain/`: what I learned, in reusable form

| # | Type | Topic |
| --- | --- | --- |
| [0.1](brain/0.1-CS-bash.md) | CS | Bash |
| [0.2](brain/0.2-CS-python-venv.md) | CS | Python virtual environments |
| [0.3](brain/0.3-LL-reading-an-agent-trace.md) | LL | Reading an agent trace |
| [0.4](brain/0.4-CS-git-github.md) | CS | Git and GitHub |
| [0.5](brain/0.5-CS-github-publish-project.md) | CS | Publishing a project on GitHub |
| [0.6](brain/0.6-CS-markdown.md) | CS | Markdown |
| [0.7](brain/0.7-CS-course-notebooks-jupyter.md) | CS | Course notebooks in Jupyter |
| [0.8](brain/0.8-CS-env-secrets.md) | CS | Secrets in a `.env` file, shared by all projects |
| [0.9](brain/0.9-CS-ide-claude-code-statusline.md) | CS | My IDE: VS Code on WSL, Claude Code and its status line |
| [1.0](brain/1.0-CS-agents.md) | CS | What an agent is |
| [1.1](brain/1.1-LL-dummy-agent-temperature.md) | LL | Temperature, memory and invented Observations |
| [1.2](brain/1.2-LL-the-liar-agent.md) | LL | The liar agent |
| [1.3](brain/1.3-LL-lie-order-next-to-observation.md) | LL | Proximity, alibis and prompt injection |
| [1.4](brain/1.4-LL-weather-agent-persona-chat-template.md) | LL | A real tool, a persona and the chat template |
| [1.5](brain/1.5-CS-sandbox-approaches.md) | CS | Sandbox approaches for code agents |
| [1.6](brain/1.6-CS-hf-space-first-agent.md) | CS | A Hugging Face Space: the First Agent Template, and why it only said "Error" |
| [1.7](brain/1.7-LL-helping-others-upstream-fix.md) | LL | Helping others: an upstream fix, and the review that made it right |
| [1.8](brain/1.8-LL-public-agent-codeagent-is-not-a-sandbox.md) | LL | A public agent: CodeAgent is not a sandbox, and who pays |
| [1.9](brain/1.9-LL-note-search-bm25-measured.md) | LL | Note search, measured: BM25F, a held-out exam, and the right section |

**CS** = cheat sheet (commands, workflows, errors → fixes). **LL** = lessons learned (an experiment and what it taught me).

## Run it yourself

**Prerequisites:** Python 3.10+ and [Ollama](https://ollama.com) installed.

```bash
# --- 1. Download the model (one time, ~4.4 GB) ---
ollama pull qwen2:7b

# --- 2. Clone the repo and enter it ---
git clone https://github.com/MArchMondello/hf-AI-agents-course.git
cd hf-AI-agents-course

# --- 3. Create a virtual environment and install the dependencies ---
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# --- 4. Secrets: copy the template, then fill in the values in your editor ---
cp .env.example .env

```

Then open the notebooks (`0.onboarding.ipynb`, `1.weather-agent-lab.ipynb`) in VS Code or Jupyter and pick the `.venv` kernel.
`BACKEND = "local"` needs nothing else. For `"claude"` or `"HF"`, fill in `ANTHROPIC_API_KEY` or `HF_TOKEN_READ` in `.env` ([`.env.example`](.env.example) lists every name). The `.env` can stay in the repo root (git-ignored) or move to any parent folder, since `load_dotenv()` searches upwards. Mine lives one level up, outside every repo: see [0.8](brain/0.8-CS-env-secrets.md).

## Certificates

| Date | Certificate |
| --- | --- |
| 2026-11-23 | [Unit 1: Fundamentals of Agents](certificates/unit1-fundamentals.webp), Hugging Face Agents Course |

## About me

I'm an architect and computational designer, now working as a product owner in AEC software.
This repo is part of my path into applied AI engineering.
