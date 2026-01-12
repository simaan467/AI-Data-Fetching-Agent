from memory import mistakes
from tools.api_tool import fetch_api_data
from tools.vectordb import vectorDB
from memory.mistakes import get_all_mistakes,record_mistake
from evaluation.evaluator import evaluate_run


class DataAgent:
    def __init__(self, llm):
        self.llm = llm
        self.db = vectorDB()

    #generating multiple plan with reminders from past mistakes
    def generate_plan(self, query):
        mistakes = get_all_mistakes()
        reminders = []
        if mistakes.get("skipped_chroma", 0):
            reminders.append("- Step 1 must ALWAYS be Chroma DB.")
        if mistakes.get("skipped_api", 0):
            reminders.append("- Step 2 must include API Tool.")
        if mistakes.get("wrong_sequence", 0):
            reminders.append("- Tool order must be: Chroma → API → Final Answer.")
        if mistakes.get("ignored_output", 0):
            reminders.append("- Never generate answer without using all required tools.")
        if mistakes.get("no_tool_used", 0):
            reminders.append("- Both tools are required before final answer.")

        reminder_text = "\n".join(reminders) if reminders else "No special rules."
    

        prompt = f"""
You are a planning agent that generates a 3-step plan for answering the user.

USER QUERY: "{query}"

PAST MISTAKE HISTORY:
{reminder_text}

RULES:
- You MUST output exactly 3 steps.
- Steps MUST be written as:
  1. <text>
  2. <text>
  3. <text>
- You MAY use tools (Chroma DB, API Tool).
- You MAY generate steps in any order.
- You MAY skip a tool.
- You MAY incorrectly order steps.
- You MAY incorrectly skip required tools.
- You MAY generate the final answer too early.

Using the past mistakes as hints, improve your plan over time.

Return ONLY the 3 steps.
        """

        response = self.llm.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt
        )

        return response.text

    def execute_plan(self, plan, query):
        steps = []
        mistakes = []

        plan_lines = [line.strip() for line in plan.split("\n") if line.strip()]
        if len(plan_lines) != 3:
            record_mistake("invalid_plan_format")
            return steps, {"error": "Invalid plan format"}


        # Validate exact structure
        if not plan_lines[0].lower().startswith("1. use chroma db"):
            mistakes.append("skipped_chroma")

        if not plan_lines[2].lower().startswith("3. generate final answer"):
            mistakes.append("answer_too_early")

        use_api = "api" in plan_lines[1].lower()

        #1 Chroma
        try:
            vector_data = self.db.query(query)
            steps.append("Used Chroma DB")
        except:
            vector_data = None
            mistakes.append("chroma_error")

        #API
        api_data = None
        if use_api or not vector_data:
            try:
                api_data = fetch_api_data(query)
                steps.append("Called API Tool")
            except:
                mistakes.append("api_error")

        # Generate final answer
        answer = self.combine(vector_data, api_data)
        steps.append("Generated final answer")

        # Save mistakes to memory
        for m in mistakes:
            record_mistake(m)


        return steps, answer

    

    #if both db and api data present, combine
    def combine(self, db, api):
        result = {}
        if db:
            result["matching_results"] = [doc.page_content for doc in db]
        else:
            result["matching_results"] = ["No DB data"]
        if api:
            result["api_results"] = api
        else:
            result["api_results"] = "No API data"
        return result


    def run(self, query):
        plan = self.generate_plan(query)
        steps, final_result = self.execute_plan(plan, query)
        evaluate_run(steps, final_result)

        return {
            "plan": plan,
            "steps": steps,
            "final_answer": final_result
        }
