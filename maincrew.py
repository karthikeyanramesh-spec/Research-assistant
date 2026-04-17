import warnings
from autogen_validation import autogen_pipeline
from crew import Reportwriter

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run_crew(state: dict) -> str:
    query = state.get("query")
    mode = state.get("mode")

    inputs = {"query": query, "mode": mode}

    try:
        report = Reportwriter()
        result = report.crew().kickoff(inputs=inputs)

        raw_output = result.raw
        final_output = autogen_pipeline(raw_output, mode)

        return final_output 

    except Exception as e:
        raise Exception(f"an error occurred: {e}")