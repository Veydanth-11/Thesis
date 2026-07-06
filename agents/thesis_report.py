import os
from groq import Groq


class ThesisReport:
    """Generates investment thesis reports based on simulation data."""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"
    
    def generate_report(self, decision_history, company_memory, world_state, round_number):
        """Generate investment thesis report.
        
        Args:
            decision_history: List of user decisions with reasons
            company_memory: Company historical memory
            world_state: Current world state
            round_number: Total rounds completed
            
        Returns:
            dict with report sections
        """
        if not self.client:
            return self._fallback_report(decision_history, round_number)
        
        # Build context for LLM
        context = self._build_report_context(decision_history, company_memory, world_state, round_number)
        
        # Generate report sections
        report = {
            "executive_summary": self._generate_section("executive_summary", context),
            "investment_philosophy": self._generate_section("investment_philosophy", context),
            "behavioral_patterns": self._generate_section("behavioral_patterns", context),
            "strengths": self._generate_section("strengths", context),
            "blind_spots": self._generate_section("blind_spots", context),
            "contradictions": self._generate_section("contradictions", context),
            "decision_evolution": self._generate_section("decision_evolution", context),
            "recommendations": self._generate_section("recommendations", context)
        }
        
        return report
    
    def _build_report_context(self, decision_history, company_memory, world_state, round_number):
        """Build context string for report generation."""
        context = f"SIMULATION COMPLETED: {round_number} rounds\n\n"
        
        # Decision history
        context += "DECISION HISTORY:\n"
        for i, decision in enumerate(decision_history, 1):
            choice = decision.get("choice", "unknown")
            reason = decision.get("reason", "no reason provided")
            context += f"Round {i}: Choice {choice}. Reasoning: {reason}\n"
        
        # Company memory
        context += "\nCOMPANY HISTORY:\n"
        historical_summary = company_memory.get("historical_summary", "")
        if historical_summary:
            context += f"Historical Summary: {historical_summary}\n"
        
        major_events = company_memory.get("major_events", [])
        if major_events:
            context += "Major Events:\n"
            for event in major_events[-5:]:
                context += f"  - Round {event.get('round')}: {event.get('event')}\n"
        
        strategic_decisions = company_memory.get("strategic_decisions", [])
        if strategic_decisions:
            context += "Strategic Decisions:\n"
            for decision in strategic_decisions[-4:]:
                context += f"  - Round {decision.get('round')}: {decision.get('decision')}\n"
        
        # World state
        context += "\nFINAL BUSINESS STATE:\n"
        cash = world_state.get("cash_position", {})
        if cash:
            context += f"Cash Position: {cash.get('level')} ({cash.get('trend')})\n"
        
        mgmt = world_state.get("management", {})
        if mgmt:
            context += f"Management: {mgmt.get('credibility')} credibility, {mgmt.get('execution')} execution\n"
        
        competitive = world_state.get("competitive_position", {})
        if competitive:
            context += f"Competitive Position: {competitive.get('market_share')} share, {competitive.get('innovation')} innovation\n"
        
        return context
    
    def _generate_section(self, section, context):
        """Generate a specific report section using LLM."""
        prompts = {
            "executive_summary": f"""Write a 3-4 sentence executive summary of this investment decision-maker's performance.

Context:
{context}

Focus on: overall decision quality, consistency, and key takeaways.
Tone: Professional, objective, investment firm assessment.
No scores, no ratings, no personality test language.""",
            
            "investment_philosophy": f"""Analyze the investment philosophy demonstrated through these decisions.

Context:
{context}

What patterns reveal their underlying philosophy?
How do they approach risk vs reward?
How do they balance short-term vs long-term?
What principles (if any) seem to guide their choices?

Tone: Analytical, evidence-based.
No generic labels like "conservative" or "aggressive" without evidence.""",
            
            "behavioral_patterns": f"""Identify behavioral patterns in decision-making.

Context:
{context}

Look for:
- Recurring tendencies under pressure
- How they respond to new information
- Risk appetite across different contexts
- Decision speed vs deliberation
- Consistency vs adaptability

Provide specific examples from the decisions.
Tone: Observational, not judgmental.""",
            
            "strengths": f"""Identify genuine strengths in their investment approach.

Context:
{context}

Focus on evidence-based strengths:
- Where did they demonstrate good judgment?
- What patterns suggest capability?
- Where did reasoning show sophistication?

Only include strengths supported by actual decisions.
Avoid generic praise.
Tone: Professional, specific.""",
            
            "blind_spots": f"""Identify blind spots or areas for improvement.

Context:
{context}

Look for:
- Systematic biases in their choices
- Areas where reasoning was weak
- Patterns of missing key considerations
- Situations where they struggled

Be specific and evidence-based.
Avoid harsh language - this is professional feedback.
Tone: Constructive, analytical.""",
            
            "contradictions": f"""Identify contradictions in their approach.

Context:
{context}

Where did their actions contradict their stated reasoning?
Where did they act inconsistently across similar situations?
What tensions between philosophy and practice emerged?

Contradictions are normal in investing - identify them objectively.
Tone: Observational, not critical.""",
            
            "decision_evolution": f"""Analyze how their decision-making evolved over time.

Context:
{context}

Did they learn and adapt?
Did patterns change as rounds progressed?
Did they become more or less consistent?
How did they respond to outcomes (even when ambiguous)?

Focus on evolution, not just final state.
Tone: Developmental, longitudinal.""",
            
            "recommendations": f"""Provide practical, specific recommendations for improvement.

Context:
{context}

Based on the patterns, blind spots, and contradictions identified:
- What would help them make better decisions?
- What should they be more aware of?
- What processes or frameworks might help?

Make recommendations actionable and specific.
Avoid generic advice like "be more disciplined."
Tone: Professional, coaching-oriented."""
        }
        
        prompt = prompts.get(section, "")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior investment analyst writing internal assessments for a billion-dollar fund. Your reports are evidence-based, specific, and professional. Avoid generic language, scores, or personality-test labels."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400,
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Unable to generate {section} due to error."
    
    def _fallback_report(self, decision_history, round_number):
        """Fallback report if Groq API unavailable."""
        return {
            "executive_summary": f"Completed {round_number} investment decisions. Analysis unavailable due to API limitations.",
            "investment_philosophy": "Unable to analyze without API access.",
            "behavioral_patterns": "Unable to analyze without API access.",
            "strengths": "Unable to analyze without API access.",
            "blind_spots": "Unable to analyze without API access.",
            "contradictions": "Unable to analyze without API access.",
            "decision_evolution": "Unable to analyze without API access.",
            "recommendations": "Unable to provide recommendations without API access."
        }
