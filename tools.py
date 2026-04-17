from autogen_validation import autogen_pipeline
from crewai.tools import tool

@tool("autogen_modifier")
def autogen_modifier(content: str, mode: str)-> str:
    """This validates, edits and refines the content using Autogen pipeline. It improves factual correctness, grammar and structure based on the mode. """
    return autogen_pipeline(content, mode)

