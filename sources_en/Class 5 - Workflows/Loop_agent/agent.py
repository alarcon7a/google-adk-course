# Part of agent.py --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup

import asyncio
import os
from google.adk.agents import LoopAgent, LlmAgent, BaseAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools.tool_context import ToolContext

# --- Constants ---
GEMINI_MODEL = "gemini-2.0-flash"
# Example 3: Iterative Content Refinement

# Tool to exit the loop
def exit_loop(tool_context: ToolContext):
  """Call this function ONLY when the critique indicates no further changes are needed, signaling the iterative process should end."""
  print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
  tool_context.actions.escalate = True
  # Return empty dict as tools should typically return JSON-serializable output
  return {}

print("\n=== Example: LoopAgent ===")

# Writer agent
writer = LlmAgent(
    name="Writer",
    model="gemini-2.0-flash",
    instruction=(
        "Improve the current text based on the received critiques. "
        "If there is no previous text, generate an initial one on the given topic."
    ),
    output_key="current_text"
)

# Critic agent
critic = LlmAgent(
    name="Critic",
    model="gemini-2.5-flash",
    instruction=(
        "Review in a very detailed and critical manner the following text 'current_text' "
        "and provide constructive criticism to improve it. "
        "In the case that the text is excellent and needs no improvement, say exactly: "
        "'No further improvements required.' and call the exit_loop tool. "
        "Otherwise, provide specific suggestions to improve the text."
    ),
    tools=[exit_loop],
    output_key="critique"
)


# Refinement loop
refinement_loop = LoopAgent(
    name="RefinementLoop",
    sub_agents=[writer, critic],
    max_iterations=6  # Maximum 6 iterations
)

root_agent = refinement_loop