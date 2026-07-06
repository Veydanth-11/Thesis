import os
import json
from groq import Groq
from agents.event_engine import EventEngine


class DungeonMaster:
    """Generates investing scenarios with choices using Groq API."""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.scenario_counter = 0
        self.model = "llama-3.3-70b-versatile"
        self.event_engine = EventEngine()
    
    def generate_scenario(self, previous_scenario=None, previous_choice=None, world_state=None, round_number=1, company_memory=None):
        """Generate a new investing scenario using Groq API.
        
        Args:
            previous_scenario: Previous scenario dict (optional)
            previous_choice: User's previous choice (optional)
            world_state: Current world state dict (optional)
            round_number: Current round number (optional)
            company_memory: Company historical memory (optional)
            
        Returns:
            dict with: title, story, options (A-D), scenario_id
        """
        self.scenario_counter += 1
        scenario_id = f"scenario_{self.scenario_counter}"
        
        # Select event type for this scenario using EventEngine
        company_condition = {}  # Can be enhanced later
        event_type = self.event_engine.select_event(round_number, world_state, company_condition)
        
        # Build prompt for Groq API
        if previous_scenario and previous_choice:
            prompt = self._build_continuation_prompt(previous_scenario, previous_choice, world_state, event_type, company_memory)
        else:
            prompt = self._build_initial_prompt(world_state, event_type, company_memory)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1500,
        )
        
        content = response.choices[0].message.content
        return self._parse_response(content, scenario_id)
    
    def _get_system_prompt(self):
        return """You are a former Chief Investment Officer interviewing for a billion-dollar fund.

Your objective: discover how this person makes investment decisions under uncertainty.

This is NOT a classroom. This is an investment committee meeting.

Rules:
- Write like a real IC memo: terse, specific, information-dense
- Never explain industries or teach concepts
- Maximum 85 words for the story
- Force genuinely difficult trade-offs
- Every option must be defensible to a skeptical board
- No option is clearly "right" or "wrong"
- Ambiguity is intentional and necessary
- Assume sophisticated investor audience
- Include concrete numbers, dates, names
- Avoid generic language like "the company" or "the market"
- Use real-world specificity: "Q3 EBITDA missed by 12%", not "earnings disappointed"

The story should feel like it was written at 2am before a board meeting.

Return valid JSON only:
{
  "title": "...",
  "story": "...",
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."}
}"""
    
    def _build_initial_prompt(self, world_state=None, event_type=None, company_memory=None):
        world_state_text = ""
        if world_state:
            world_state_text = self._format_world_state_naturally(world_state)
        
        event_text = ""
        if event_type:
            event_text = f"\nEvent Type: {event_type}\nWrite the scenario around this specific event."
        
        company_history_text = ""
        if company_memory:
            company_history_text = self._format_company_memory_naturally(company_memory)
        
        return f"Generate an initial investment scenario. Create a realistic company in a specific sector (tech, healthcare, energy, finance, etc.) facing a critical decision point. The scenario should present a compelling investment opportunity with clear trade-offs.{world_state_text}{company_history_text}{event_text}"
    
    def _build_continuation_prompt(self, previous_scenario, previous_choice, world_state=None, event_type=None, company_memory=None):
        world_state_text = ""
        if world_state:
            world_state_text = self._format_world_state_naturally(world_state)
        
        event_text = ""
        if event_type:
            event_text = f"\nEvent Type: {event_type}\nWrite the scenario around this specific event."
        
        company_history_text = ""
        if company_memory:
            company_history_text = self._format_company_memory_naturally(company_memory)
        
        return f"""Continue the investment story from the previous scenario.

Previous Title: {previous_scenario['title']}
Previous Story: {previous_scenario['story']}
User's Choice: {previous_choice}{world_state_text}{company_history_text}{event_text}

Generate the next scenario in this investment journey:
- The same company and situation should continue
- New information should emerge based on the user's choice
- The stakes should evolve naturally
- Maintain narrative continuity
- Never evaluate whether the user's choice was correct
- Simply show what happens next

Return the next scenario in the same JSON format."""
    
    def _format_world_state_naturally(self, world_state):
        """Format world state as natural language summary for LLM."""
        text = "\nCurrent Business State:\n"
        
        # Cash Position
        cash = world_state.get("cash_position", {})
        if cash:
            level = cash.get("level", "unknown")
            trend = cash.get("trend", "unknown")
            text += f"Cash Position: {level} and {trend}\n"
        
        # Debt Profile
        debt = world_state.get("debt_profile", {})
        if debt:
            level = debt.get("level", "unknown")
            trend = debt.get("trend", "unknown")
            text += f"Debt Profile: {level} and {trend}\n"
        
        # Management
        mgmt = world_state.get("management", {})
        if mgmt:
            credibility = mgmt.get("credibility", "unknown")
            execution = mgmt.get("execution", "unknown")
            capital = mgmt.get("capital_allocation", "unknown")
            communication = mgmt.get("communication", "unknown")
            text += f"Management: {credibility} credibility, {execution} execution, {capital} capital allocation, {communication} communication\n"
        
        # Competitive Position
        comp = world_state.get("competitive_position", {})
        if comp:
            market_share = comp.get("market_share", "unknown")
            pricing = comp.get("pricing_power", "unknown")
            innovation = comp.get("innovation", "unknown")
            loyalty = comp.get("customer_loyalty", "unknown")
            text += f"Competitive Position: {market_share} market share, {pricing} pricing power, {innovation} innovation, {loyalty} customer loyalty\n"
        
        # Valuation
        val = world_state.get("valuation", {})
        if val:
            multiple = val.get("multiple", "unknown")
            sentiment = val.get("market_sentiment", "unknown")
            expectations = val.get("expectations", "unknown")
            text += f"Valuation: {multiple} multiple, {sentiment} market sentiment, {expectations} expectations\n"
        
        # Industry
        industry = world_state.get("industry", {})
        if industry:
            cycle = industry.get("cycle", "unknown")
            intensity = industry.get("competitive_intensity", "unknown")
            regulatory = industry.get("regulatory_pressure", "unknown")
            text += f"Industry: {cycle} cycle, {intensity} competitive intensity, {regulatory} regulatory pressure\n"
        
        return text
    
    def _format_company_memory_naturally(self, company_memory):
        """Format company memory as natural language summary for LLM."""
        text = "\nCompany History:\n"
        
        # Historical summary first
        historical_summary = company_memory.get("historical_summary", "")
        if historical_summary:
            text += f"Historical Summary:\n{historical_summary}\n\n"
        
        # Recent major events (last 5)
        major_events = company_memory.get("major_events", [])
        if major_events:
            text += "Recent Major Events:\n"
            for event in major_events[-5:]:
                round_num = event.get("round", "unknown")
                description = event.get("event", "unknown event")
                text += f"• Round {round_num}: {description}\n"
        
        # Recent strategic decisions (last 4)
        strategic_decisions = company_memory.get("strategic_decisions", [])
        if strategic_decisions:
            text += "Recent Strategic Decisions:\n"
            for decision in strategic_decisions[-4:]:
                round_num = decision.get("round", "unknown")
                description = decision.get("decision", "unknown decision")
                text += f"• Round {round_num}: {description}\n"
        
        # Recent management changes (last 3)
        mgmt_changes = company_memory.get("management_changes", [])
        if mgmt_changes:
            text += "Recent Management Changes:\n"
            for change in mgmt_changes[-3:]:
                round_num = change.get("round", "unknown")
                description = change.get("change", "unknown change")
                text += f"• Round {round_num}: {description}\n"
        
        # Recent capital allocation (last 4)
        cap_history = company_memory.get("capital_allocation_history", [])
        if cap_history:
            text += "Recent Capital Allocation:\n"
            for allocation in cap_history[-4:]:
                round_num = allocation.get("round", "unknown")
                description = allocation.get("allocation", "unknown allocation")
                text += f"• Round {round_num}: {description}\n"
        
        return text
    
    def _parse_response(self, content, scenario_id):
        """Parse JSON response from Groq with robust error handling."""
        try:
            # Try to extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Try to find JSON object boundaries
            content = content.strip()
            if content.startswith('{') and content.endswith('}'):
                # Find the matching closing brace
                brace_count = 0
                json_start = 0
                json_end = len(content)
                for i, char in enumerate(content):
                    if char == '{':
                        if brace_count == 0:
                            json_start = i
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                content = content[json_start:json_end]
            
            data = json.loads(content)
            return {
                "scenario_id": scenario_id,
                "title": data.get("title", "Investment Scenario"),
                "story": data.get("story", "Scenario description"),
                "options": data.get("options", {
                    "A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"
                })
            }
        except json.JSONDecodeError as e:
            print(f"[DungeonMaster] JSON parsing failed: {e}")
            print(f"[DungeonMaster] Raw response:\n{content}")
            raise
