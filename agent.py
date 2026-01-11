from tools.api_tool import fetch_api_data
from tools.vectordb import vectorDB
from memory.mistakes import get_all_mistakes
from evaluation.evaluator import evaluate_run


class DataAgent:
    def __init__(self, llm):
        self.llm = llm
        self.db = vectorDB()

    #generating multiple plan with reminders from past mistakes
    def generate_plan(self, query):
        past_mistakes = get_all_mistakes()

        reminders = []
        if past_mistakes.get("skipped_chroma", 0) > 0:
            reminders.append("Always query Chroma DB first")
        if past_mistakes.get("skipped_api", 0) > 0:
            reminders.append("If data incomplete, call API")
        if past_mistakes.get("wrong_sequence", 0) > 0:
            reminders.append("Do not call API before Chroma")
        if past_mistakes.get("no_tool_used", 0) > 0:
            reminders.append("At least one tool must be used")
        if past_mistakes.get("ignored_output", 0) > 0:
            reminders.append("Always use tool outputs to answer")

        reminder_text = "\n".join(reminders) if reminders else "No special rules"

        prompt = f"""
You are a planning agent. Your output must follow STRICT rules.

USER QUERY: "{query}"

PAST MISTAKE REMINDERS:
{reminder_text}

REQUIRED OUTPUT FORMAT:
Return EXACTLY 3 lines, like:
1. <first step>
2. <second step>
3. <third step>

RULES:
-YOU MUST include "1.", "2.", and "3." at the start of each step.
-If you do not follow this format EXACTLY, the system will fail.
- Each step must be a single short sentence.
- STEP 1 MUST always be: "Use Chroma DB".
- STEP 2 MAY be: "Use API Tool" ONLY if necessary.
- STEP 3 MUST always be: "Generate final answer".
- You MUST NOT use markdown, tables, formatting, lists, bullets, or extra text.
- You MUST NOT explain anything.
- Do NOT repeat any tool.
- Do NOT add extra lines.

ONLY return the 3 steps.
"""


        # to get response from GenAI
        response = self.llm.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt
        )

        plan = response.text
        return plan

    def execute_plan(self, plan, query):
        api_data = None
        vector_data = None
        answer = None
        steps = []
        plan_lines = [line.strip() for line in plan.split("\n") if line.strip()]

        for line in plan_lines:
            lower = line.lower()
            # First step to be chroma
            if lower.startswith("1."):
                steps.append("Selected tool: chroma")
                try:
                    vector_data = self.db.query(query)
                    steps.append("Used Chroma DB")
                except:
                    steps.append("Chroma DB error")
                continue
            # second step to be api
            if lower.startswith("2.") and "api" in lower:
                steps.append("selected_tool:api")
                try:
                    api_data = fetch_api_data(query)
                    steps.append("Called API")
                except:
                    steps.append("API error")
                continue

            if lower.startswith("3."):
                steps.append("Generated answer")
                answer = self.combine(vector_data, api_data)
                continue

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
