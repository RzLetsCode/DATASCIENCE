from pydantic import BaseModel, Field
from typing import List

class Reflection(BaseModel):
    """Critique details for an answer reflection."""
    missing: str = Field(..., description="What information is missing in the answer.")
    superfluous: str = Field(..., description="What information is superfluous and could be removed.")

class AnswerQuestion(BaseModel):
    """Model for a full detailed answer, reflection, and search queries."""
    answer: str = Field(..., description="A detailed (~250 word) answer to the question.")
    search_queries: List[str] = Field(
        ..., 
        description="1-3 recommended search queries for improving the current answer."
    )
    reflection: Reflection = Field(
        ..., 
        description="Reflection and critique on the initial answer."
    )

class ReviseAnswer(AnswerQuestion):
    """Model for a revised answer, including references."""
    references: List[str] = Field(
        ...,
        description="List of citations or references supporting the revised answer."
    )
