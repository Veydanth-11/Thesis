from datetime import datetime


class PatternReader:
    """Records user choices for pattern analysis (in-memory only)."""
    
    def __init__(self):
        self.session_records = []
    
    def record_choice(self, scenario_id, user_choice):
        """Record a user's choice.
        
        Args:
            scenario_id: ID of the scenario
            user_choice: User's selected option (A-D)
            
        Returns:
            dict with recorded data
        """
        record = {
            "scenario_id": scenario_id,
            "user_choice": user_choice,
            "timestamp": datetime.now().isoformat()
        }
        
        self.session_records.append(record)
        return record
    
    def get_session_records(self):
        """Get all records from current session."""
        return self.session_records
