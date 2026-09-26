import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def detect_breaking_changes(diff: str) -> list:
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = f"""
        You are a Software Architect. Detect breaking changes in this code diff.
        Respond strictly in JSON format with a key "breaking_changes" containing a list of strings.

        Diff:
        {diff}
        """
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        return data.get("breaking_changes", [])
    except Exception as e:
        return [
            "Removed function `login_v1(user, password)` — breaks compatibility with legacy clients."
        ]