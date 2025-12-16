"""AI service for generating summaries using Groq API."""

from groq import AsyncGroq
from fastapi import HTTPException, status

from app.core.config import settings


class AIService:
    """Service for AI-powered operations using Groq."""

    def __init__(self) -> None:
        """Initialize the AI service with Groq client."""
        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY not set in environment variables"
            )

        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    async def generate_summary(self, content: str) -> str:
        """
        Generate a summary for the given content.

        Args:
            content: The text content to summarize

        Returns:
            The generated summary

        Raises:
            HTTPException: If summary generation fails
        """
        try:
            prompt = f"""Provide a concise and engaging summary of the following book content
in approximately 100 words. Focus on the main themes, plot, and key points:

{content}

Summary:"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional book reviewer and summarizer. "
                        "Create engaging, accurate, and concise summaries.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.7,
            )

            summary = response.choices[0].message.content.strip()
            return summary

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate summary: {str(e)}",
            )


# Global AI service instance
ai_service = AIService()
