import os
import requests

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def get_ai_response(prompt):
    """
    Send a prompt to OpenRouter and return a structured result.
    Reads credentials from environment variables.
    """

    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    model = os.getenv("OPENROUTER_MODEL", "").strip()

    if not api_key:
        return {
            "success": False,
            "message": (
                "AI configuration error: OPENROUTER_API_KEY "
                "is missing from the deployment environment."
            ),
        }

    if not model:
        return {
            "success": False,
            "message": (
                "AI configuration error: OPENROUTER_MODEL "
                "is missing from the deployment environment."
            ),
        }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv(
            "APP_URL",
            "http://localhost:5000",
        ),
        "X-Title": "SkillSync AI",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are SkillSync AI, a career and skill-development "
                    "assistant for college students. Provide personalized, "
                    "practical, structured guidance. Distinguish reported "
                    "skills from inferred skill gaps. Never claim skills "
                    "were objectively tested or guarantee employment."
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
            timeout=(10, 90),
        )

        if response.status_code == 401:
            return {
                "success": False,
                "message": (
                    "OpenRouter authentication failed. Check the "
                    "OPENROUTER_API_KEY environment variable on Render."
                ),
            }

        if response.status_code == 402:
            return {
                "success": False,
                "message": (
                    "OpenRouter reports insufficient credits or "
                    "available usage for this request."
                ),
            }

        if response.status_code == 403:
            return {
                "success": False,
                "message": (
                    "OpenRouter denied the request. Check model access "
                    "and account restrictions."
                ),
            }

        if response.status_code == 404:
            return {
                "success": False,
                "message": (
                    "The configured OpenRouter model was not found. "
                    "Check OPENROUTER_MODEL in Render Environment."
                ),
            }

        if response.status_code == 429:
            return {
                "success": False,
                "message": (
                    "OpenRouter rate limit reached. Please wait and "
                    "try again, or check your model's usage limits."
                ),
            }

        response.raise_for_status()
        data = response.json()

        choices = data.get("choices", [])

        if not choices:
            return {
                "success": False,
                "message": (
                    "OpenRouter returned no AI response. Check the "
                    "selected model and try again."
                ),
            }

        answer = choices[0].get("message", {}).get("content", "")

        # Some models may return content as a list of text blocks.
        if isinstance(answer, list):
            answer = "\n".join(
                item.get("text", "")
                for item in answer
                if isinstance(item, dict)
                and item.get("type") == "text"
            )

        if not isinstance(answer, str) or not answer.strip():
            return {
                "success": False,
                "message": (
                    "The AI returned an empty response. Please try again."
                ),
            }

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
        status = (
            error.response.status_code
            if error.response is not None
            else "unknown"
        )

        # Do not expose the API key or raw response body to users.
        return {
            "success": False,
            "message": (
                f"OpenRouter returned HTTP {status}. "
                "Check the deployment logs and model configuration."
            ),
        }

    except (requests.RequestException, ValueError, TypeError):
        return {
            "success": False,
            "message": (
                "Unable to connect to OpenRouter or read its response. "
                "Check the network and deployment logs."
            ),
        }