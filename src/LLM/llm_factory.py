
from groq import Groq
from src.config import TEMPERATURE, GROQ_API_KEY, ONLINE_AI_ENDPOINT


class LLM:

    llm: Groq

    def __init__(self, local: bool = False):
        """Initialize the LLM client."""
        self._create_llm(local)

    def get_llm(self) -> Groq:
        return self.llm

    def _create_llm(self, local: bool) -> Groq:
        """
        Create and configure the LLM client based on the specified mode.
        Handles the actual initialization of the LLM client. It currently supports Groq's API for cloud-based inference
        and provides a placeholder for future local model support.

        Args:
            local (bool): Flag indicating whether to use a local model.
                - False: Initialize Groq client with cloud API
                - True: Placeholder for local model initialization (not yet implemented)

        Raises:
            ValueError: If the Groq API key is not set or invalid.
            Exception: If there's an error connecting to the Groq API.
        """
        if not local:
            try:
                self.llm: Groq = Groq(
                    api_key=GROQ_API_KEY,
                    base_url=ONLINE_AI_ENDPOINT,
                )
            except ValueError as e:
                print(f"Error connecting to Groq API: {e}")
                raise e

        # TODO: Add support for local models
        # elif local:
        #     from openai import OpenAI
        #     self.llm = OpenAI(
        #         base_url="http://localhost:1234/v1",
        #         api_key="not-needed"
        #     )

        return self.llm