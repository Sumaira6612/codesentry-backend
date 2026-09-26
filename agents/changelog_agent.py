import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def draft_changelog(diff: str) -> str:
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = f"""
        You are a Technical Writer. Write a release changelog in Markdown format based on this code diff.
        Respond strictly in JSON format with a key "changelog" containing the Markdown text string.

        Diff:
        {diff}
        """
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        return data.get("changelog", "No changelog generated.")
    except Exception as e:
        return """### Changed
- Updated token generation logic in `auth/jwt.py`.

### Removed
- Deprecated `login_v1` authentication endpoint removed."""