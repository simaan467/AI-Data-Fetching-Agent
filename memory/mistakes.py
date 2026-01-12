import json
import os

#to store mistakes
MISTAKES_FILE = os.path.join(os.path.dirname(__file__), "mistakes.json")



#to load memory from file
def load_memory():
    if not os.path.exists(MISTAKES_FILE):
        return {"patterns":{}}
    with open(MISTAKES_FILE,"r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {"patterns":{}}
    return data


#to save memory to file
def save_memory(data):
    with open(MISTAKES_FILE,"w") as f:
        json.dump(data,f,indent=2)

#to record a mistake
def record_mistake(mistake_name):
    data = load_memory()

    # ensure patterns exists
    if "patterns" not in data:
        data["patterns"] = {}

    if mistake_name not in data["patterns"]:
        data["patterns"][mistake_name] = 1
    else:
        data["patterns"][mistake_name] += 1

    save_memory(data)
    print("LOGGED MISTAKE:", mistake_name)



#to get count of a specific mistake
def get_mistake_count(mistake_name):
    data = load_memory()
    return data["patterns"].get(mistake_name, 0)

#to get all mistakes
def get_all_mistakes():
    data = load_memory()
    return data["patterns"]


