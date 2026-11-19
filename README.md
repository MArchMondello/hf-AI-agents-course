# hf-AI-agents-course

My agents and experiments, built while following the [Hugging Face AI Agents Course](https://huggingface.co/learn/agents-course).

The default engine is **local and free**: an open model (`qwen2:7b`) served by [Ollama](https://ollama.com) on my own machine.
Paid engines (Claude API, Hugging Face Inference API) are optional, one line away.

## What's inside

```
hf-AI-agents-course/
├── 0.onboarding.py               ← first agent: smolagents CodeAgent on local Qwen
├── 1.dummy_agent_library.ipynb   ← an agent from scratch: system prompt + stop word + a Python function
├── brain/                        ← cheat sheets (CS) and lessons learned (LL), one per topic
├── probe/                        ← raw model outputs of the experiments, as JSON
└── requirements.txt
```

| File | What it does |
| --- | --- |
| [`0.onboarding.py`](0.onboarding.py) | A `CodeAgent` with no tools: it answers by writing and running Python (10th Fibonacci number, primes below 100). |
| [`1.dummy_agent_library.ipynb`](1.dummy_agent_library.ipynb) | The course's "dummy agent", rebuilt with **three interchangeable engines** (local Qwen, Claude, Hugging Face) behind one `chat()` function. Plus a **disrespectful agent** used for the experiments below. |

## Experiments: can a system prompt make an agent lie?

The notebook's BONUS sections give a rude agent one order, *"hide the truth"*, and one tool, a fake `get_weather`.
Each setup ran 10 times on Qwen2 7B. The raw outputs are in [`probe/`](probe/).

| Setup | Truth | Lie | Lesson |
| --- | --- | --- | --- |
| Order in the system prompt | 8 / 10 | 0 / 10 | the tool result beats a distant order: [1.2](brain/1.2-LL-the-liar-agent.md) |
| Same order, pasted next to the tool result | 0 / 10 | 7 / 10 | the closest text wins, a **prompt injection**: [1.3](brain/1.3-LL-lie-order-next-to-observation.md) |
| Same, plus `stop=["Observation:"]` | 0 / 10 | 1 / 10 | `stop` blocks the forged evidence, not the intent: [1.3](brain/1.3-LL-lie-order-next-to-observation.md) |

What I take from it: **tool output is data, never instructions**, and an agent loop needs `stop`, input validation and `max_steps`.

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
| [1.0](brain/1.0-CS-agents.md) | CS | What an agent is |
| [1.1](brain/1.1-LL-dummy-agent-temperature.md) | LL | Temperature, memory and invented Observations |
| [1.2](brain/1.2-LL-the-liar-agent.md) | LL | The liar agent |
| [1.3](brain/1.3-LL-lie-order-next-to-observation.md) | LL | Proximity, alibis and prompt injection |

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

# --- 4. Run the first agent ---
python 0.onboarding.py
```

For the notebook, open `1.dummy_agent_library.ipynb` in VS Code or Jupyter and pick the `.venv` kernel.
`BACKEND = "local"` needs nothing else. For `"claude"` or `"HF"`, create a `.env` file (git-ignored) with `ANTHROPIC_API_KEY=...` or `HF_TOKEN=...`.

## About me

I'm an architect and computational designer, now working as a product owner in AEC software.
This repo is part of my path into applied AI engineering.
