import json
from crewai import Agent, Task, Crew
from langchain_community.chat_models import ChatLiteLLM
from dotenv import load_dotenv
import os

load_dotenv()

# llm = LLM(model="ollama/llama3.2", base_url="http://localhost:11434")

llm = ChatLiteLLM(
    model="huggingface/meta-llama/Llama-3.2-3B-Instruct:novita",
    llm_provider="huggingface",
    api_base="https://router.huggingface.co/v1",
    api_key=os.getenv("HF_API_TOKEN"),
)

extractor_agent = Agent(
    name="TeluguFestivalExtractor",
    role="An expert in Telugu festivals who verifies if user input matches the text.",
    goal="Determine if the Telugu text describes the user's given festival, and extract its story. If not, classify as 'other'.",
    backstory="You specialize in Telugu cultural analysis and understand how to validate user expectations against actual text content.",
    llm=llm,
    verbose=True,
)


def build_extraction_task(
    telugu_text: str, rituals_text: str, expected_festival: str
) -> Task:
    safe_story = telugu_text.strip().replace('"', '\\"').replace("\n", "\\n")
    safe_rituals = rituals_text.strip().replace('"', '\\"').replace("\n", "\\n")
    safe_fest = expected_festival.strip().lower()

    prompt = f"""
You are an expert in Telugu festivals.

The user claims the following text is about the festival: "{safe_fest}".

The description and rituals are provided separately. Verify if they truly describe the claimed festival.
IMPORTANT : convert only the telugu festival names to English before storing them in the JSON object.

If they match the expected festival, return:
- festival_name (in English, lowercase)
- story (from the description)
- rituals (from the rituals section)

If they do **not** match the expected festival, set:
- festival_name = "other"
- story = full description
- rituals = full rituals

Respond only in JSON format like:

[
  {{
    "festival_name": "dasara",
    "story": "This is the story...",
    "rituals": "These are the rituals..."
  }}
]
"""

    full_text = f"### Description:\n{safe_story}\n\n### Rituals:\n{safe_rituals}"
    return Task(
        description=prompt + "\n\n" + full_text,
        agent=extractor_agent,
        expected_output="Festival verification with story and rituals",
    )


def extract_festival_data(
    telugu_text: str, rituals_text: str, expected_festival: str
) -> list[dict]:
    task = build_extraction_task(telugu_text, rituals_text, expected_festival)
    crew = Crew(agents=[extractor_agent], tasks=[task], verbose=True)
    result = crew.kickoff()

    try:
        return json.loads(result.raw.strip())
    except json.JSONDecodeError:
        return [{"festival_name": "other", "story": telugu_text.strip()}]

