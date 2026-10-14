import os
import requests


OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def get_ai_response(prompt):
    """
    Send a prompt to OpenRouter and return the AI response.
    """

    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    model = os.getenv("OPENROUTER_MODEL", "").strip()

    if not api_key or not model:
        return {
            "success": False,
            "message": (
                "OpenRouter is not configured. Add your API key "
                "and model name to the .env file."
            ),
        }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are SkillSync AI, a career and skill-development "
                    "assistant for college students. Give practical, "
                    "realistic, structured advice. Never claim to have "
                    "verified a student's skills or guaranteed employment. "
                    "Clearly distinguish recommendations from facts."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.4,
    }

    try:
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )

        response.raise_for_status()
        result = response.json()

        answer = result["choices"][0]["message"]["content"]

        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("The AI returned an empty response.")

        return {
            "success": True,
            "message": answer.strip(),
        }

    except requests.Timeout:
        return {
            "success": False,
            "message": (
                "The AI request timed out. Please try again."
            ),
        }

    except requests.HTTPError as error:
        status_code = (
            error.response.status_code
            if error.response is not None
            else None
        )

        if status_code == 401:
            message = "OpenRouter rejected the API key. Check your .env file."
        elif status_code == 402:
            message = "OpenRouter reports insufficient credits for this request."
        elif status_code == 429:
            message = "OpenRouter rate limit reached. Please try again later."
        else:
            message = (
                "OpenRouter could not complete the request. "
                "Check your model name, account, and API configuration."
            )

        return {
            "success": False,
            "message": message,
        }

    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError):
        return {
            "success": False,
            "message": (
                "Unable to get a valid AI response. "
                "Check your connection and OpenRouter configuration."
            ),
        }