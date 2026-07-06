import random


class EventEngine:
    """Selects investment events based on rules, world state, and context."""
    
    EVENT_TYPES = [
        "Quarterly Earnings",
        "Capital Allocation",
        "Acquisition",
        "Governance Issue",
        "Competitor Action",
        "Promoter Selling",
        "Buyback",
        "Debt Refinancing",
        "Regulation",
        "Macro Event",
        "Product Launch",
        "Supply Chain",
        "Management Change",
        "Industry Cycle",
        "Short Seller Report"
    ]
    
    def __init__(self):
        self.previous_events = []
    
    def select_event(self, round_number, world_state=None, company_condition=None):
        """Select an event based on rules and context.
        
        Args:
            round_number: Current round number
            world_state: Current world state dict
            company_condition: Company condition dict
            
        Returns:
            Selected event type string
        """
        candidates = self._get_candidates(round_number, world_state, company_condition)
        
        # Filter out recently used events to avoid repetition
        candidates = [e for e in candidates if e not in self.previous_events[-3:]]
        
        # If no candidates after filtering, use all candidates
        if not candidates:
            candidates = self._get_candidates(round_number, world_state, company_condition)
        
        # Weighted random selection
        weights = self._get_weights(candidates, round_number, world_state)
        selected = random.choices(candidates, weights=weights, k=1)[0]
        
        self.previous_events.append(selected)
        return selected
    
    def _get_candidates(self, round_number, world_state, company_condition):
        """Get candidate events based on rules."""
        candidates = []
        
        # Round-based rules
        if round_number in [2, 3]:
            candidates.append("Quarterly Earnings")
        
        if round_number >= 8:
            candidates.extend(["Macro Event", "Competitor Action"])
        
        # World state-based rules (structured format)
        if world_state:
            cash_level = world_state.get("cash_position", {}).get("level")
            debt_level = world_state.get("debt_profile", {}).get("level")
            mgmt_credibility = world_state.get("management", {}).get("credibility")
            mgmt_capital = world_state.get("management", {}).get("capital_allocation")
            mgmt_communication = world_state.get("management", {}).get("communication")
            market_share = world_state.get("competitive_position", {}).get("market_share")
            innovation = world_state.get("competitive_position", {}).get("innovation")
            loyalty = world_state.get("competitive_position", {}).get("customer_loyalty")
            expectations = world_state.get("valuation", {}).get("expectations")
            industry_cycle = world_state.get("industry", {}).get("cycle")
            regulatory = world_state.get("industry", {}).get("regulatory_pressure")
            
            # Cash-based events
            if cash_level == "strong":
                candidates.append("Buyback")
                candidates.append("Capital Allocation")
            elif cash_level in ["weak", "moderate"]:
                candidates.append("Debt Refinancing")
            
            # Management-based events
            if mgmt_credibility in ["weak", "poor", "low"]:
                candidates.append("Governance Issue")
                candidates.append("Promoter Selling")
            
            if mgmt_communication in ["weak", "poor", "unclear", "vague"]:
                candidates.append("Governance Issue")
            
            if mgmt_capital in ["weak", "poor", "undisciplined"]:
                candidates.append("Acquisition")  # Poor acquisition risk
            
            # Competitive position-based events
            if innovation in ["strong", "excellent"]:
                candidates.append("Product Launch")
            
            if loyalty in ["weak", "poor", "declining"]:
                candidates.append("Competitor Action")
            
            if market_share == "challenger":
                candidates.append("Product Launch")
                candidates.append("Acquisition")
            
            # Valuation-based events
            if expectations in ["high", "very high", "elevated"]:
                candidates.append("Quarterly Earnings")  # Earnings disappointment risk
            
            # Industry-based events
            if industry_cycle == "recession":
                candidates.append("Supply Chain")
                candidates.append("Regulation")
            
            if regulatory in ["high", "very high", "intense"]:
                candidates.append("Regulation")
                candidates.append("Compliance Investigation")
        
        # Company condition-based rules
        if company_condition:
            if company_condition.get("growth_stage") == "mature":
                candidates.append("Industry Cycle")
            elif company_condition.get("growth_stage") == "expansion":
                candidates.append("Management Change")
        
        # Add fallback candidates if no specific rules matched
        if not candidates:
            candidates = [
                "Quarterly Earnings",
                "Capital Allocation",
                "Governance Issue",
                "Competitor Action"
            ]
        
        return list(set(candidates))  # Remove duplicates
    
    def _get_weights(self, candidates, round_number, world_state):
        """Get weights for weighted random selection."""
        weights = []
        
        for event in candidates:
            weight = 1.0
            
            # Boost weight for round-specific events
            if round_number in [2, 3] and event == "Quarterly Earnings":
                weight *= 3.0
            elif round_number >= 8 and event in ["Macro Event", "Competitor Action"]:
                weight *= 2.5
            
            # Boost weight for world state-specific events (structured format)
            if world_state:
                cash_level = world_state.get("cash_position", {}).get("level")
                mgmt_credibility = world_state.get("management", {}).get("credibility")
                mgmt_communication = world_state.get("management", {}).get("communication")
                innovation = world_state.get("competitive_position", {}).get("innovation")
                expectations = world_state.get("valuation", {}).get("expectations")
                regulatory = world_state.get("industry", {}).get("regulatory_pressure")
                
                if cash_level == "strong" and event == "Buyback":
                    weight *= 2.0
                elif mgmt_credibility in ["weak", "poor", "low"] and event == "Governance Issue":
                    weight *= 2.0
                elif mgmt_communication in ["weak", "poor", "unclear", "vague"] and event == "Governance Issue":
                    weight *= 2.0
                elif innovation in ["strong", "excellent"] and event == "Product Launch":
                    weight *= 2.0
                elif expectations in ["high", "very high", "elevated"] and event == "Quarterly Earnings":
                    weight *= 2.0
                elif regulatory in ["high", "very high", "intense"] and event == "Regulation":
                    weight *= 2.0
            
            weights.append(weight)
        
        return weights
