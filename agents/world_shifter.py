import os
import json
from groq import Groq
from agents.event_engine import EventEngine


class WorldShifter:
    """Evolves the world based on user choices using Groq API."""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"
        self.event_engine = EventEngine()
    
    def evolve_world(self, previous_scenario, user_choice, round_number, world_state=None, decision_history=None, latest_reason=None, company_memory=None):
        """Evolve the world state and generate next scenario based on user's choice using Groq API.
        
        Args:
            previous_scenario: Previous scenario dict
            user_choice: User's selected option (A-D)
            round_number: Current round number
            world_state: Current world state dict (optional)
            decision_history: List of previous decisions (optional)
            latest_reason: User's latest reasoning (optional)
            company_memory: Company historical memory (optional)
            
        Returns:
            dict with next scenario in same JSON format
        """
        # Select event type for this scenario using EventEngine
        company_condition = {}  # Can be enhanced later
        event_type = self.event_engine.select_event(round_number, world_state, company_condition)
        
        prompt = self._build_evolution_prompt(previous_scenario, user_choice, round_number, world_state, decision_history, latest_reason, event_type)
        
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
        next_scenario = self._parse_response(content)
        
        # Update world state based on user choice (simple logic for now)
        if world_state:
            updated_state = self._update_world_state(world_state, user_choice)
            next_scenario["updated_world_state"] = updated_state
        
        # Update company memory based on event type and choice
        if company_memory:
            updated_memory = self._update_company_memory(company_memory, round_number, event_type, user_choice)
            next_scenario["updated_company_memory"] = updated_memory
        
        return next_scenario
    
    def _update_world_state(self, world_state, user_choice):
        """Update world state based on user choice.
        
        Args:
            world_state: Current world state dict (structured format)
            user_choice: User's selected option (A-D)
            
        Returns:
            Updated world state dict
        """
        updated = world_state.copy()
        
        # Deep copy nested structures
        for key in updated:
            if isinstance(updated[key], dict):
                updated[key] = updated[key].copy()
        
        # State evolution logic based on choice (structured format)
        # Only modify fields that logically change based on the decision
        if user_choice == "A":
            # Aggressive action - may increase risk, use cash
            if updated.get("cash_position", {}).get("level") == "strong":
                updated["cash_position"]["level"] = "moderate"
                updated["cash_position"]["trend"] = "declining"
            if updated.get("debt_profile", {}).get("level") == "low":
                updated["debt_profile"]["level"] = "moderate"
                updated["debt_profile"]["trend"] = "increasing"
            # Aggressive moves may affect market sentiment
            if updated.get("valuation", {}).get("market_sentiment") == "neutral":
                updated["valuation"]["market_sentiment"] = "cautious"
        elif user_choice == "B":
            # Balanced action - minimal change
            if updated.get("management", {}).get("execution") == "strong":
                updated["management"]["execution"] = "consistent"
        elif user_choice == "C":
            # Defensive action - may preserve cash, but lose competitive edge
            if updated.get("cash_position", {}).get("level") == "moderate":
                updated["cash_position"]["level"] = "strong"
                updated["cash_position"]["trend"] = "improving"
            if updated.get("competitive_position", {}).get("market_share") == "leader":
                updated["competitive_position"]["market_share"] = "challenger"
                updated["competitive_position"]["pricing_power"] = "moderate"
            # Defensive moves may affect innovation perception
            if updated.get("competitive_position", {}).get("innovation") == "strong":
                updated["competitive_position"]["innovation"] = "moderate"
        elif user_choice == "D":
            # Alternative strategic move
            if updated.get("management", {}).get("capital_allocation") == "disciplined":
                updated["management"]["capital_allocation"] = "experimental"
        
        return updated
    
    def _update_company_memory(self, company_memory, round_number, event_type, user_choice):
        """Update company memory based on event type and user choice.
        
        Args:
            company_memory: Current company memory dict
            round_number: Current round number
            event_type: Selected event type
            user_choice: User's selected option (A-D)
            
        Returns:
            Updated company memory dict
        """
        updated = company_memory.copy()
        
        # Deep copy nested structures
        for key in updated:
            if isinstance(updated[key], list):
                updated[key] = updated[key].copy()
        
        # Add meaningful events based on event type
        if event_type == "Quarterly Earnings":
            updated["major_events"].append({
                "round": round_number,
                "event": f"Quarterly earnings reported (Choice: {user_choice})"
            })
        elif event_type == "Acquisition":
            updated["major_events"].append({
                "round": round_number,
                "event": f"Acquisition decision made (Choice: {user_choice})"
            })
            updated["strategic_decisions"].append({
                "round": round_number,
                "decision": f"{'Pursued' if user_choice in ['A', 'B'] else 'Declined'} acquisition opportunity"
            })
        elif event_type == "Management Change":
            updated["management_changes"].append({
                "round": round_number,
                "change": f"Management transition (Choice: {user_choice})"
            })
        elif event_type == "Buyback":
            updated["capital_allocation_history"].append({
                "round": round_number,
                "allocation": f"{'Share buyback initiated' if user_choice in ['A', 'B'] else 'Buyback declined'}"
            })
        elif event_type == "Debt Refinancing":
            updated["major_events"].append({
                "round": round_number,
                "event": f"Debt refinancing completed (Choice: {user_choice})"
            })
            updated["capital_allocation_history"].append({
                "round": round_number,
                "allocation": f"Debt restructuring decision"
            })
        elif event_type == "Governance Issue":
            updated["major_events"].append({
                "round": round_number,
                "event": f"Governance controversy addressed (Choice: {user_choice})"
            })
        elif event_type == "Product Launch":
            updated["major_events"].append({
                "round": round_number,
                "event": f"New product launched (Choice: {user_choice})"
            })
            updated["strategic_decisions"].append({
                "round": round_number,
                "decision": f"Product expansion strategy"
            })
        elif event_type == "Regulation":
            updated["major_events"].append({
                "round": round_number,
                "event": f"Regulatory compliance action (Choice: {user_choice})"
            })
        
        # Keep memory concise - summarize if too long
        needs_summary = False
        
        if len(updated["major_events"]) > 10:
            # Keep only last 5 major events, summarize older ones
            older_events = updated["major_events"][:-5]
            updated["major_events"] = updated["major_events"][-5:]
            needs_summary = True
        
        if len(updated["strategic_decisions"]) > 8:
            older_decisions = updated["strategic_decisions"][:-4]
            updated["strategic_decisions"] = updated["strategic_decisions"][-4:]
            needs_summary = True
        
        if len(updated["management_changes"]) > 5:
            older_changes = updated["management_changes"][:-3]
            updated["management_changes"] = updated["management_changes"][-3:]
            needs_summary = True
        
        if len(updated["capital_allocation_history"]) > 8:
            older_allocations = updated["capital_allocation_history"][:-4]
            updated["capital_allocation_history"] = updated["capital_allocation_history"][-4:]
            needs_summary = True
        
        # Generate historical summary if needed
        if needs_summary:
            # Create a temporary memory with the older events to summarize
            older_memory = company_memory.copy()
            older_memory["major_events"] = older_events if 'older_events' in locals() else []
            older_memory["strategic_decisions"] = older_decisions if 'older_decisions' in locals() else []
            older_memory["management_changes"] = older_changes if 'older_changes' in locals() else []
            older_memory["capital_allocation_history"] = older_allocations if 'older_allocations' in locals() else []
            
            new_summary = self._generate_historical_summary(older_memory)
            
            # Append to existing summary
            if updated.get("historical_summary"):
                updated["historical_summary"] = updated["historical_summary"] + " " + new_summary
            else:
                updated["historical_summary"] = new_summary
        
        return updated
    
    def _generate_historical_summary(self, company_memory):
        """Generate LLM-based historical summary of older events.
        
        Args:
            company_memory: Current company memory dict
            
        Returns:
            Summary string (max 120 words)
        """
        # Collect all events to summarize
        events_to_summarize = []
        
        for event in company_memory.get("major_events", []):
            events_to_summarize.append(f"Round {event.get('round')}: {event.get('event')}")
        
        for decision in company_memory.get("strategic_decisions", []):
            events_to_summarize.append(f"Round {decision.get('round')}: {decision.get('decision')}")
        
        for change in company_memory.get("management_changes", []):
            events_to_summarize.append(f"Round {change.get('round')}: {change.get('change')}")
        
        for allocation in company_memory.get("capital_allocation_history", []):
            events_to_summarize.append(f"Round {allocation.get('round')}: {allocation.get('allocation')}")
        
        if not events_to_summarize:
            return ""
        
        # Build prompt for LLM
        events_text = "\n".join(events_to_summarize)
        
        prompt = f"""Summarize these company events into a concise business narrative (max 120 words).

Events:
{events_text}

Focus on:
- Strategic evolution
- Management credibility
- Capital allocation patterns
- Competitive position changes

Return only the summary text, no intro or outro."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a business analyst who writes concise executive summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200,
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Ensure it's not too long
            words = summary.split()
            if len(words) > 120:
                summary = " ".join(words[:120])
            
            return summary
        except Exception as e:
            # Fallback to simple concatenation if LLM fails
            return f"Company evolved through {len(events_to_summarize)} key events including strategic decisions, management changes, and capital allocation actions."
    
    def _get_system_prompt(self):
        return """You are not continuing a story. You are moving the market forward.

This is an investment committee meeting, not a narrative.

After every decision:
- Advance time naturally (weeks/months, not years)
- Reveal ONE specific new fact that changes the calculus
- The fact should be ambiguous - it could support OR challenge the previous choice
- Never reveal whether the previous decision was "right" or "wrong"
- Never create certainty or closure
- Consequences should be subtle, delayed, and mixed
- Real investing: good decisions can have bad outcomes, bad decisions can have good outcomes
- Use concrete specifics: "Q4 revenue $23.1M vs guidance $25M", not "revenue missed"
- Maximum 85 words
- Never restart the company or reset the narrative

The user should feel uncertainty, not validation or regret.

Return valid JSON only:
{
  "title": "...",
  "story": "...",
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."}
}"""
    
    def _build_evolution_prompt(self, previous_scenario, user_choice, round_number, world_state=None, decision_history=None, latest_reason=None, event_type=None):
        world_state_text = ""
        if world_state:
            world_state_text = self._format_world_state_naturally(world_state)
        
        history_text = ""
        if decision_history and len(decision_history) > 0:
            history_text = "\nDecision History:\n"
            for i, record in enumerate(decision_history, 1):
                history_text += f"Round {i}\n"
                history_text += f"Choice: {record['choice']}\n"
                if record.get('reason'):
                    history_text += f"Reason: {record['reason']}\n"
                history_text += "\n"
        
        reason_text = ""
        if latest_reason:
            reason_text = f"\nLatest Reasoning: {latest_reason}"
        
        event_text = ""
        if event_type:
            event_text = f"\nEvent Type: {event_type}\nWrite the scenario around this specific event."
        
        return f"""Advance to round {round_number + 1}.

Previous: {previous_scenario['title']}
Choice: {user_choice}{world_state_text}{history_text}{reason_text}{event_text}

Use the decision history to generate dilemmas that challenge the user's demonstrated investment style. Do not evaluate the user. Do not mention the history in the output. Use it only internally to guide scenario generation.

Reveal ONE new fact. Challenge the reasoning. Never reveal if the choice was right.

Return valid JSON only:
{
  "title": "...",
  "story": "...",
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."}
}"""
    
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
    
    def _parse_response(self, content):
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
                "title": data.get("title", "Investment Scenario"),
                "story": data.get("story", "Scenario description"),
                "options": data.get("options", {
                    "A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"
                })
            }
        except json.JSONDecodeError as e:
            print(f"[WorldShifter] JSON parsing failed: {e}")
            print(f"[WorldShifter] Raw response:\n{content}")
            raise
