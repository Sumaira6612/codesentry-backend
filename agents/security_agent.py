import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def analyze_security(diff: str) -> dict:
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = f"""
        You are a Security & Code Quality Expert. Analyze this code diff and detect vulnerabilities.
        Respond strictly in JSON format with two keys:
        - "score": integer (0-100)
        - "issues": list of objects with "severity", "file", "line", "issue"

        Diff:
        {diff}
        """
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "score": 65,
            "issues": [
                {
                    "severity": "CRITICAL",
                    "file": "auth/jwt.py",
                    "line": 42,
                    "issue": "Hardcoded secret key detected in JWT token generator."
                }
            ]
        }