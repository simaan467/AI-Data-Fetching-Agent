from memory.mistakes import record_mistake

#if agent doent attain chroma
def evaluate_run(steps,final_result):
    if any("Selected tool: chroma" in s for s in steps):
        if not any("Used Chroma DB" in s for s in steps):
            record_mistake("skipped_chroma")

    #if agent selected api but never actually called it
    if any("selected_tool:api" in s for s in steps):
        if not any("Called API" in s for s in steps):
            record_mistake("skipped_api")

    #if answer produced without any tools
    used_tools = (
        any("Used Chroma DB" in s for s in steps) or
        any("Called API" in s for s in steps)
    )
    if not used_tools:
        record_mistake("no_tool_used")

    #if final result is empty
    if final_result is None or final_result == "":
        record_mistake("empty_answer")

    #wrong order
    if any("Called API" in s for s in steps) and \
        any("Used Chroma Db" in s for s in steps):

        api_index = steps.index("Called API") if "Called API" in steps else 999
        db_index = steps.index("Used Chroma DB") if "Used Chroma DB" in steps else -1

        if api_index < db_index:
            record_mistake("wrong_sequence")

    # If the tool output was ignored (beginner check)
    if any("Got API result:" in s for s in steps) and \
       "Generated answer" in steps[-1] and \
       "Used tool output" not in " ".join(steps):
        record_mistake("ignored_output")

    return True


