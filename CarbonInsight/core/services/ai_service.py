import logging
import os

from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)

def generate_ai_response(instructions:str, _input:str, model:str = "gpt-4o") -> str:
    api_key = os.environ.get("OPENAI_API_KEY", None)
    if api_key is None:
        logger.error("OpenAI API key is not set.")
        return "AI services are currently unavailable due to a missing API key."

    client = OpenAI(api_key=api_key)

    try:
        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=_input,
        )
        return response.output_text
    except OpenAIError as e:
        # Handle all OpenAI API errors
        logger.error(f"OpenAI API error: {e}")
        return "We are unable to process your request at the moment. Please try again later."
