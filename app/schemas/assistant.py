from typing import Any, Literal

from pydantic import BaseModel, Field


class AssistantMessage(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(..., description="Message role")
    content: str = Field(..., description="Message content")


class AssistantChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Current user message")
    history: list[AssistantMessage] = Field(default_factory=list, description="Chat history")
    context: dict[str, Any] | None = Field(default=None, description="UI/runtime context")
    use_runtime_snapshot: bool = Field(default=True, description="Attach runtime stats")


class AssistantChatResponse(BaseModel):
    answer: str = Field(..., description="Assistant answer")
    suggestions: list[str] = Field(default_factory=list, description="Suggested follow-up prompts")
    model: str = Field(..., description="Model used")
    provider_style: str = Field(..., description="Provider API style")
    context_used: dict[str, Any] = Field(default_factory=dict, description="Context actually used")


class AssistantCapabilityResponse(BaseModel):
    llm_enabled: bool
    llm_configured: bool
    provider_style: str
    model: str
    features: list[str]
