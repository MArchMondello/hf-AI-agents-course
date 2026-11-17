# first_agent.py — your first agent, running on local Qwen

from smolagents import CodeAgent, LiteLLMModel

# --- 1. The brain: your local model, served by Ollama ------------------
model = LiteLLMModel(
    model_id="ollama_chat/qwen2:7b",    # must match a name from `ollama list`
    api_base="http://127.0.0.1:11434",  # where Ollama listens on your machine
    num_ctx=8192,                       # context window: how much text the model "sees" at once
)

# --- 2. The agent: wraps the brain and lets it write + run Python ------
agent = CodeAgent(
    tools=[],       # no extra tools yet: the agent can still write code
    model=model,
)

# --- 3. Give it a task and print the answer ----------------------------
#result = agent.run("what are the key ingredients of pizza margherita?")
result = agent.run("What is the 10th Fibonacci number?")
print(result)

# --- 4. A second query: another task that benefits from running code ---
result2 = agent.run("How many prime numbers are there below 100, and what is their sum?")
print(result2)