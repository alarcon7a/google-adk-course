# Part of agent.py --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents import SequentialAgent, ParallelAgent
from google.adk.tools import google_search
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use an efficient Gemini model. You can change it if needed.
GEMINI_MODEL = "gemini-2.5-flash"

# --- 1. Define "Specialist" Sub-Agents (that will run in parallel) ---

# Specialist 1: Flight Researcher
flight_researcher = LlmAgent(
    name="FlightResearcher",
    model=GEMINI_MODEL,
    instruction="""You are an AI Assistant specialized in travel.
Research and summarize flight options for a trip as indicated by the user.
Use the provided Google Search tool.
Summarize your key findings concisely, mentioning airlines and approximate price ranges.
Your output should be *only* the summary.
""",
    description="Researches and summarizes flight options.",
    tools=[google_search],
    # Store the result in the 'state' for the synthesizer agent to use
    output_key="flight_results"
)

# Specialist 2: Hotel Researcher
hotel_researcher = LlmAgent(
    name="HotelResearcher",
    model=GEMINI_MODEL,
    instruction="""You are an AI Assistant specialized in accommodation.
Research and summarize hotel options for the destination provided by the user.
Use the provided Google Search tool.
Summarize your key findings concisely, mentioning hotel types (e.g. luxury, boutique, budget) and popular areas.
Your output should be *only* the summary.
""",
    description="Researches and summarizes hotel options.",
    tools=[google_search],
    # Store the result in the 'state'
    output_key="hotel_results"
)

# Specialist 3: Activities Researcher
activities_researcher = LlmAgent(
    name="ActivitiesResearcher",
    model=GEMINI_MODEL,
    instruction="""You are an AI Assistant specialized in local tourism.
Research and summarize the main activities and tourist attractions to do in the destination indicated by the user.
Use the provided Google Search tool.
Summarize your key findings concisely, mentioning at least 3 popular activities.
Your output should be *only* the summary.
""",
    description="Researches and summarizes tourist activities.",
    tools=[google_search],
    # Store the result in the 'state'
    output_key="activities_results"
)

# --- 2. Create the ParallelAgent (Executes researchers concurrently) ---
# This agent orchestrates the simultaneous execution of specialists.
# Finishes once all specialists have completed their task and
# saved their results in the session 'state'.
parallel_research_agent = ParallelAgent(
    name="ParallelTravelResearchAgent",
    sub_agents=[flight_researcher, hotel_researcher, activities_researcher],
    description="Executes multiple travel research agents in parallel."
)

# --- 3. Define the Synthesizer Agent (Runs *after* the parallel agents) ---
# This agent takes the results stored in the 'state' by the parallel agents
# and consolidates them into a single structured travel proposal.
synthesizer_agent = LlmAgent(
    name="ItinerarySynthesisAgent",
    model=GEMINI_MODEL,
    instruction="""You are an AI Assistant expert in creating travel itineraries.

Your main task is to combine the following research summaries into a clear and structured travel proposal.

**Fundamental: Your complete response MUST be based *exclusively* on the information provided in the 'Input Summaries' below. DO NOT add any external knowledge, facts or details that are not present in these specific summaries.**

**Input Summaries:**

* **Flights:**
    {flight_results}

* **Accommodation:**
    {hotel_results}

* **Activities:**
    {activities_results}

**Output Format:**

## Travel Itinerary Proposal

### Flight Options
(Based on FlightResearcher findings)
[Synthesize and detail *only* the information from the provided flight summary.]

### Accommodation Options
(Based on HotelResearcher findings)
[Synthesize and detail *only* the information from the provided hotel summary.]

### Recommended Activities
(Based on ActivitiesResearcher findings)
[Synthesize and detail *only* the information from the provided activities summary.]

### Plan Conclusion
[Offer a brief final statement that connects *only* the findings presented above.]

Your output should be *only* the structured report following this format. Do not include introductory or closing phrases outside this structure.
""",
    description="Combines research agent findings into a structured travel proposal.",
    # No tools needed, as it only processes text input.
    # No output_key needed, as its direct response is the final pipeline result.
)


# --- 4. Create the SequentialAgent (Orchestrates the complete flow) ---
# This is the main agent that will be executed. First runs the ParallelAgent
# to populate the 'state', then runs the SynthesizerAgent to produce the final result.
travel_planning_pipeline = SequentialAgent(
    name="CompleteTravelPlanningPipeline",
    # First parallel research, then synthesis.
    sub_agents=[parallel_research_agent, synthesizer_agent],
    description="Coordinates parallel travel research and synthesizes the results."
)

# The `root_agent` is the entry point to execute the entire workflow.
root_agent = travel_planning_pipeline