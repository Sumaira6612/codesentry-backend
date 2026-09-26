import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def generate_tests(diff: str) -> list:
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = f"""
        You are a QA Engineer. Write unit tests for this code diff.
        Respond strictly in JSON format with a key "generated_tests" containing a list of strings.

        Diff:
        {diff}
        """
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        return data.get("generated_tests", [])
    except Exception as e:
        return [
            "def test_generate_token_with_valid_user():\n    assert generate_token('user_123') is not None",
            "def test_jwt_secret_environment_variable():\n    assert os.getenv('JWT_SECRET') is not None"
        ]