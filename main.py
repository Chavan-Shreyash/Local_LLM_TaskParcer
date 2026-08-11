import json
from datetime import datetime

import ollama


def fix_json(text: str):
    text = text.strip()

    # remove markdown
    if text.startswith("```"):
        text = text.split("```")[1]

    # try to fix missing closing brace
    if not text.endswith("}"):
        text = text + "}"

    return text
def parse_task(user_input: str):
    current_date = datetime.now().strftime("%Y-%m-%d")

    for attempt in range(2):  # retry once
        response = ollama.chat(
            model="llama3",
            messages=[
                {
                    "role": "system",
                    "content": f"""
You are an AI that extracts structured task data.

Today's date is {current_date}.
If the task is recurring, set date and time to null.
Return ONLY valid JSON.
Do NOT include explanation.
Ensure the JSON is complete and valid.

Format:
{{
  "task_type": "reminder | meeting | other",
  "description": "string",
  "date": "YYYY-MM-DD or null",
  "time": "HH:MM or null"
}}
"""
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )

        content = response['message']['content']
        print("RAW OUTPUT:", content)

        content = fix_json(content)

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            print("Retrying due to JSON error...")

    return {
        "error": "Failed after retry",
        "raw_output": content
    }


if __name__ == "__main__":
    text = "Remind me to call mom tomorrow evening"
    inputs = [
    "Remind me to call mom tomorrow evening",
    "Schedule a meeting with John next Monday at 3pm",
    "Book a flight to Delhi tomorrow",
    "Remind me to drink water every 2 hours"
]
    for text in inputs:
        result = parse_task(text)
        print(result)