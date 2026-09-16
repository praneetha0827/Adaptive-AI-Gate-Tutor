import json

from openai import APIConnectionError, APIError, APIStatusError, OpenAI
from pydantic import ValidationError

from app.schemas.tutor import TutorTurn


class AIProviderError(Exception):
    pass


class OpenAIProvider:
    """OpenAI-based provider for tutor and assessment agents.
    
    Uses the v1/chat/completions API with structured output (JSON mode).
    """

    def __init__(self, api_key: str, model: str, base_url: str | None = None) -> None:
        client_options: dict[str, str] = {"api_key": api_key}
        if base_url:
            client_options["base_url"] = base_url
        self.client = OpenAI(**client_options)
        self.model = model

    def generate_tutor_turn(self, context: dict[str, object], user_message: str) -> TutorTurn:
        """Generate the next tutor interaction turn.
        
        Args:
            context: Student context including curriculum, mastery, previous mistakes
            user_message: The student's message or answer
            
        Returns:
            TutorTurn: Structured tutor response (explanation, question, hint, etc.)
            
        Raises:
            AIProviderError: If API call fails or response is invalid
        """
        schema = TutorTurn.model_json_schema()
        system_prompt = (
            "You are an adaptive GATE Computer Science tutor. Your role is to teach interactively, "
            "gauge student understanding, provide hints rather than direct answers, and adapt difficulty. "
            "Use ONLY the curriculum context provided. Be concise. Return a valid JSON response."
        )
        user_prompt = f"Student context:\n{json.dumps(context, indent=2)}\n\nStudent message: {user_message}"

        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=TutorTurn,
                temperature=0.7,
                max_tokens=1000,
            )
        except (APIConnectionError, APIStatusError, APIError, ValidationError, IndexError, KeyError, TypeError) as error:
            raise AIProviderError(f"OpenAI API request failed: {error}") from error

        if not response.choices or response.choices[0].message.parsed is None:
            raise AIProviderError("OpenAI did not return structured output")

        return response.choices[0].message.parsed

