from agent import DataAgent
from google import genai


def load_llm():
    client = genai.Client(api_key="GEMINI_API_KEY")
    return client


def run_tests(agent, query, runs=3):
    for i in range(runs):
        print("\n" + "=" * 60)
        print(f" RUN {i+1} ")
        print("=" * 60)

        result = agent.run(query)

        print("\n PLAN :-\n", result["plan"])
        print("\nSTEPS :")
        for s in result["steps"]:
            print("*", s)

        print("\n FINAL ANSWER :-")
        print(result["final_answer"])
        print("\n")


if __name__ == "__main__":
    llm = load_llm()
    agent = DataAgent(llm)

    user_query = input("Ask me something: ")
    run_tests(agent, user_query, runs=3)
