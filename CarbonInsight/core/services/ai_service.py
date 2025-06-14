import logging
import os

from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)

def generate_ai_response(instructions:str, _input:str, model:str = "gpt-4o") -> str:
    """
    Sends a request to the OpenAI API and returns the response.

    Args:
        instructions (str): The instructions to send to the OpenAI API.
        _input (str): The input to send to the OpenAI API.
        model (str): Specifies the model of openai to use.
    Returns:
        The response from the OpenAI API or error message.
    """

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
