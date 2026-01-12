# agent/llm_client.py
"""
LLM client wrapper – currently uses Groq, but easy to swap (OpenAI, Anthropic, local, etc.).
"""

from typing import List, Dict
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    """Encapsulates LLM calls with configuration and safety checks."""

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set in .env")

        self.client = Groq(api_key=api_key)
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 800,
    ) -> str:
        """
        Call the LLM and return the content.

        Args:
            messages: Chat history in ChatML format
            temperature: Controls randomness (lower = more deterministic)
            max_tokens: Max output length

        Returns:
            Cleaned string response
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()