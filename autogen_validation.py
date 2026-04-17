import os
from autogen import AssistantAgent, UserProxyAgent
from dotenv import load_dotenv

load_dotenv()

llm_config = {
    "config_list": [
        {
            "model": "gpt-4o-mini",
            "api_key": os.getenv("OPENAI_API_KEY"),

        }
    ],
    "temperature": 0.3
}

STRICT_RULE = """
You must return ONLY the final improved content.

Rules:
- Do NOT give suggestions
- Do NOT explain anything
- Do NOT list improvements
- Return a COMPLETE rewritten report
"""

def run_validation(content: str) -> str:
    validation = AssistantAgent(
        name="Validator",
        llm_config=llm_config,
        system_message=STRICT_RULE + """
Check for:
- factual correctness
- missing information
- hallucinations

Fix issues and return final content.
"""
    )

    user = UserProxyAgent(name="User", code_execution_config=False)

    response = user.initiate_chat(
        validation,
        message=content,
        max_turns=1
    )

    return response.summary

def run_editing(content: str) -> str:
    editing = AssistantAgent(
        name="Editor",
        llm_config=llm_config,
        system_message=STRICT_RULE + """
Improve grammar, clarity, and structure.
Keep meaning unchanged.TRICT FORMATTING RULES:

1. Remove ALL markdown symbols (*, **, #, etc.)
2. Use clean professional formatting
3. Add proper spacing between sections
4. Format like a formal report:

   - Title (centered style text, uppercase)
   - Section headings (clear and bold-like using capitalization)
   - Paragraph spacing (leave one blank line between paragraphs)
   - Numbered lists properly aligned
   - No unnecessary symbols

5. Structure:

   TITLE

   Executive Summary

   (paragraph)

   Section Heading

   (paragraph)

6. Ensure readability for PDF export
7. Keep it clean and minimal
8. Do NOT include any markdown or special characters

Return ONLY the final formatted report.
"""

    )

    user = UserProxyAgent(name="User", code_execution_config=False)

    response = user.initiate_chat(
        editing,
        message=content,
        max_turns=1
    )

    return response.summary


def run_refinement(content: str, mode: str) -> str:
    refiner = AssistantAgent(
        name="Refiner",
        llm_config=llm_config,
        system_message=STRICT_RULE + f"""
Refine based on mode: {mode}

Modes:
- Student: Simple, crisp
- Developer: Technical, precise
- Researcher: Deep, detailed
and follow the rules given below
1. Remove ALL markdown symbols (*, **, #, etc.)
2. Use clean professional formatting
3. Add proper spacing between sections
4. Format like a formal report:

   - Title (centered style text, uppercase)
   - Section headings (clear and bold-like using capitalization)
   - Paragraph spacing (leave one blank line between paragraphs)
   - Numbered lists properly aligned
   - No unnecessary symbols

5. Structure:

   TITLE

   Executive Summary

   (paragraph)

   Section Heading

   (paragraph)

6. Ensure readability for PDF export
7. Keep it clean and minimal
8. Do NOT include any markdown or special characters

Return ONLY the final formatted report.
"""
    )

    user = UserProxyAgent(name="User", code_execution_config=False)

    response = user.initiate_chat(
        refiner,
        message=content,
        max_turns=1
    )

    return response.summary


def autogen_pipeline(content: str, mode: str) -> str:
    try:
        validated = run_validation(content)
        edited = run_editing(validated)
        refined = run_refinement(edited, mode)

        return refined

    except Exception as e:
        print("AutoGen failed:", e)
        return content
