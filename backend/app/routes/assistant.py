"""AI Climate Assistant API routes."""
from fastapi import APIRouter
from app.schemas.schemas import AssistantRequest, AssistantResponse
from app.services.ai_assistant_service import ai_assistant

router = APIRouter()


@router.post("/chat", response_model=AssistantResponse)
async def chat(req: AssistantRequest):
    """Send a message to the AI Climate Assistant."""
    result = await ai_assistant.chat(
        message=req.message,
        session_id=req.session_id,
        context=req.context,
    )
    return AssistantResponse(**result)


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """Get conversation history for a session."""
    history = await ai_assistant.get_session_history(session_id)
    return {"session_id": session_id, "messages": history}


@router.get("/suggestions")
async def get_suggestions():
    """Get suggested questions for the AI assistant."""
    return {
        "suggestions": [
            "Why is rainfall expected to decrease in Rajasthan?",
            "Which states are at highest flood risk this week?",
            "Explain the temperature anomaly in Maharashtra",
            "What is the drought status in Tamil Nadu?",
            "How accurate are the rainfall predictions for Kerala?",
            "What are the heatwave risks for Delhi this month?",
            "Compare monsoon patterns between Assam and Gujarat",
            "What happens if temperature increases by 2°C across India?",
        ]
    }
