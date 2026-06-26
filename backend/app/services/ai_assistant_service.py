"""
AI Assistant Service — Mock LLM-backed climate Q&A.
Designed to be replaced by a real LLM (Gemini, GPT-4, etc.) without API changes.
"""
import random
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

import structlog

from app.services.mock_data_service import MockDataService

logger = structlog.get_logger()

# Knowledge base for mock intelligent responses
RESPONSE_TEMPLATES = {
    "rainfall": [
        "Based on IMD data and our LSTM model analysis, {state} is experiencing {condition} rainfall patterns. "
        "The monsoon influence factor for this region is currently {monsoon_pct}% above climatological normal. "
        "AI confidence in the 7-day forecast is {confidence}%.",
        "Our Digital Twin analysis indicates {state}'s rainfall is {delta} mm/day from the seasonal mean. "
        "The precipitation model shows {trend} trend over the next 5 days.",
    ],
    "temperature": [
        "The Digital Twin for {state} shows a current temperature anomaly of {anomaly}°C relative to the 30-year IMD baseline. "
        "INSAT Land Surface Temperature data confirms surface warming patterns. "
        "Heatwave probability for the next 72 hours: {heatwave_pct}%.",
        "Temperature analysis for {state} indicates {trend} trend. "
        "Our ConvLSTM spatial model projects temperatures of {temp_max}°C maximum over the forecast horizon.",
    ],
    "flood": [
        "Flood risk assessment for {state}: Current flood probability index is {flood_risk}. "
        "This is computed from: rainfall intensity ({rainfall} mm/day), soil moisture saturation, "
        "and topographic runoff coefficients derived from INSAT/Cartosat data. "
        "We recommend immediate monitoring of the {rivers} river basins.",
        "The Digital Twin detects elevated flood risk in {state}. "
        "Simulating +30% rainfall scenario would increase flood probability to {scenario_risk}.",
    ],
    "drought": [
        "Drought index for {state} is {drought_idx} (0=no drought, 1=extreme drought). "
        "The standardized precipitation index (SPI) over the past 30 days is {spi}. "
        "Crop stress probability: {crop_stress}%. Agriculture advisory issued.",
        "Our AI model has detected below-normal rainfall in {state} for the past {days} days. "
        "Soil moisture deficit: {moisture_deficit} mm. Drought watch in effect.",
    ],
    "general": [
        "ClimateTwin India is currently monitoring {regions} regions across India using IMD, INSAT, and MOSDAC data. "
        "The AI Prediction Engine is running LSTM and Random Forest models with {accuracy}% accuracy on temperature forecasts.",
        "The Digital Twin has processed {observations} climate observations in the last 24 hours. "
        "Current system status: {active_models} AI models active, {alerts} climate alerts active.",
        "India's climate today: Average temperature {temp}°C, Average rainfall {rainfall} mm/day. "
        "Active extreme weather events: {events}. The monsoon is currently {monsoon_status}.",
    ],
}

SUGGESTED_ACTIONS = {
    "rainfall": [
        "View rainfall heatmap on the GIS Map",
        "Run +30% rainfall simulation",
        "Check flood risk for downstream districts",
        "Download IMD rainfall dataset",
    ],
    "temperature": [
        "View temperature trends in Analytics",
        "Run +2°C warming simulation",
        "Check heatwave probability map",
        "Compare with historical temperatures",
    ],
    "flood": [
        "Open Flood Risk layer on map",
        "Simulate extreme rainfall scenario",
        "View historical flood events",
        "Set up flood alert for this region",
    ],
    "drought": [
        "View drought index heatmap",
        "Simulate rainfall deficit scenario",
        "Check crop stress indicators",
        "Download soil moisture data",
    ],
}


class AIAssistantService:
    """
    Climate AI Assistant.

    Currently uses intelligent mock responses calibrated to real climate data.
    Swap `_generate_response` to call a real LLM API when ready.
    """

    def __init__(self):
        self._sessions: Dict[str, List[Dict]] = {}

    def _detect_intent(self, message: str) -> str:
        """Simple keyword-based intent detection."""
        message_lower = message.lower()
        if any(w in message_lower for w in ["rain", "monsoon", "precipitation", "flood", "water"]):
            if "flood" in message_lower:
                return "flood"
            return "rainfall"
        elif any(w in message_lower for w in ["temperature", "heat", "warm", "cold", "celsius"]):
            return "temperature"
        elif any(w in message_lower for w in ["drought", "dry", "soil", "crop", "agriculture"]):
            return "drought"
        return "general"

    def _extract_state(self, message: str) -> Optional[str]:
        """Extract mentioned Indian state from message."""
        from app.services.mock_data_service import INDIA_STATES
        message_lower = message.lower()
        for state in INDIA_STATES:
            if state["name"].lower() in message_lower:
                return state["name"]
        return None

    def _generate_response(self, message: str, context: Optional[Dict]) -> Dict:
        """
        Generate an intelligent response.
        SWAP THIS METHOD to call a real LLM (Gemini, GPT-4, Claude) in production.
        """
        intent = self._detect_intent(message)
        state = self._extract_state(message) or "India"

        # Get real mock data for context
        regions = MockDataService.get_all_current_states()
        target_region = next(
            (r for r in regions if r["region_name"] == state),
            regions[0] if regions else {}
        )

        templates = RESPONSE_TEMPLATES.get(intent, RESPONSE_TEMPLATES["general"])
        template = random.choice(templates)

        # Fill template with real-ish data
        response_text = template.format(
            state=state,
            condition="above-normal" if (target_region.get("rainfall", 0) > 3) else "below-normal",
            monsoon_pct=random.randint(85, 140),
            confidence=random.randint(78, 94),
            delta=round((target_region.get("rainfall", 2.5) - 2.5), 1),
            trend="increasing" if random.random() > 0.5 else "decreasing",
            anomaly=round(target_region.get("temperature_anomaly", 0), 1),
            heatwave_pct=int(target_region.get("heatwave_probability", 0) * 100),
            temp_max=round(target_region.get("temperature_max", 35), 1),
            rainfall=round(target_region.get("rainfall", 3), 1),
            flood_risk=round(target_region.get("flood_risk", 0.2), 2),
            rivers="Krishna, Godavari" if state in ["Andhra Pradesh", "Telangana"] else "Ganges, Brahmaputra",
            scenario_risk=round(min(1.0, target_region.get("flood_risk", 0.2) * 1.8), 2),
            drought_idx=round(target_region.get("drought_index", 0.3), 2),
            spi=round(random.gauss(-0.5, 1.0), 2),
            crop_stress=int(random.uniform(20, 70)),
            days=random.randint(15, 45),
            moisture_deficit=random.randint(20, 80),
            regions=30,
            accuracy=random.randint(82, 94),
            observations=random.randint(8000, 15000),
            active_models=4,
            alerts=random.randint(2, 8),
            temp=round(sum(r.get("temperature_mean", 25) for r in regions) / len(regions), 1),
            events=random.randint(1, 5),
            monsoon_status="active" if datetime.now().month in range(6, 10) else "inactive",
        )

        return {
            "response": response_text,
            "intent": intent,
            "state": state,
            "suggested_actions": SUGGESTED_ACTIONS.get(intent, SUGGESTED_ACTIONS["rainfall"]),
            "sources": ["IMD", "INSAT-3D", "MOSDAC", "ClimateTwin AI"],
            "confidence": round(random.uniform(0.78, 0.96), 2),
        }

    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None,
    ) -> Dict:
        """Process a user message and return AI assistant response."""
        if not session_id:
            session_id = str(uuid.uuid4())

        # Store message in session
        if session_id not in self._sessions:
            self._sessions[session_id] = []

        self._sessions[session_id].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Generate response
        generated = self._generate_response(message, context)

        assistant_msg = {
            "role": "assistant",
            "content": generated["response"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._sessions[session_id].append(assistant_msg)

        logger.info("AI assistant responded", session_id=session_id, intent=generated["intent"])

        return {
            "response": generated["response"],
            "session_id": session_id,
            "sources": generated["sources"],
            "confidence": generated["confidence"],
            "suggested_actions": generated["suggested_actions"],
        }

    async def get_session_history(self, session_id: str) -> List[Dict]:
        return self._sessions.get(session_id, [])


# Singleton
ai_assistant = AIAssistantService()
