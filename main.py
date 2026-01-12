from agent import DataAgent
from dotenv import load_dotenv
from google import genai
import os


def load_llm():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("API key not loaded. Check your .env file location and format.")

    client = genai.Client(api_key=api_key)
    return client

#iterating multiple test runs
def run_tests(agent, query, runs=3):
    for i in range(runs):
        print("\n" + "~~" * 30)
        print(f" RUN {i+1} ")
        print("~~" * 30)

        result = agent.run(query)

        print("\n PLAN :-\n", result["plan"])
        print("\nSTEPS :")
        for s in result["steps"]:
            print("*", s)

        print("\n FINAL ANSWER :-")
        print(result["final_answer"])
        print("\n")

# Main execution
if __name__ == "__main__":
    llm = load_llm()
    agent = DataAgent(llm)

    user_query = input("Ask me something: ")
    run_tests(agent, user_query, runs=3)
