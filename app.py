from mcp_orchestration import mcp_orchestration
from openai_refiner import openai_refine

def main():
    query = input("Enter Topic: ")
    mode = input("Select Mode (Student / Developer / Researcher): ")

    report = mcp_orchestration(query, mode)

    current_output = report

    while True:
        print(current_output)

        satisfied = input("\nAre you satisfied? (yes/no): ").strip().lower()

        if satisfied == "yes":
            print("\n Final Output Delivered")
            break

        feedback = input("\nEnter your suggestions: ")

        current_output = openai_refine(current_output, feedback, mode)

if __name__ == "__main__":
    main()