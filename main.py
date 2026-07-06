import os
from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS

os.environ["GROQ_API_KEY"] = "Your API key"

from agents.dungeon_master import DungeonMaster
from agents.world_shifter import WorldShifter
from agents.pattern_reader import PatternReader
from agents.thesis_report import ThesisReport

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# Initialize agents
dungeon_master = DungeonMaster()
world_shifter = WorldShifter()
pattern_reader = PatternReader()
thesis_report = ThesisReport()

# Thread-safe session storage
sessions = {}


@app.route('/')
def serve_landing():
    """Serve the landing page."""
    return send_from_directory(app.static_folder, 'Landing Page-code.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory(app.static_folder, path)


@app.route('/scenario', methods=['GET'])
def get_scenario():
    """Return the first investing scenario."""
    import uuid
    session_id = str(uuid.uuid4())
    
    current_scenario = dungeon_master.generate_scenario(company_memory={})
    
    # Create session object with all fields
    sessions[session_id] = {
        "company": {},
        "company_memory": {
            "historical_summary": "",
            "major_events": [],
            "strategic_decisions": [],
            "management_changes": [],
            "capital_allocation_history": []
        },
        "world_state": {
            "cash_position": {
                "level": "strong",
                "trend": "stable"
            },
            "debt_profile": {
                "level": "low",
                "trend": "stable"
            },
            "management": {
                "credibility": "high",
                "execution": "strong",
                "capital_allocation": "disciplined",
                "communication": "clear"
            },
            "competitive_position": {
                "market_share": "leader",
                "pricing_power": "high",
                "innovation": "strong",
                "customer_loyalty": "high"
            },
            "valuation": {
                "multiple": "reasonable",
                "market_sentiment": "neutral",
                "expectations": "moderate"
            },
            "industry": {
                "cycle": "expansion",
                "competitive_intensity": "moderate",
                "regulatory_pressure": "low"
            }
        },
        "current_scenario": current_scenario,
        "decision_history": [],
        "round_number": 1
    }
    
    return jsonify({
        "session_id": session_id,
        "scenario_id": current_scenario["scenario_id"],
        "title": current_scenario["title"],
        "story": current_scenario["story"],
        "options": current_scenario["options"],
        "company_name": "Aether Energy Systems",
        "position_size": "₹450 Crore (4.5% of Fund)",
        "investment_thesis": "Grid stabilization through micro-storage.",
        "fund_capital": "₹10,000 Cr",
        "portfolio_value": "₹10,240 Cr"
    })


@app.route('/choice', methods=['POST'])
def submit_choice():
    """Process user choice and return next scenario."""
    data = request.json
    session_id = data.get("session_id")
    scenario_id = data.get("scenario_id")
    choice = data.get("choice")
    reason = data.get("reason")
    
    # Retrieve session from thread-safe storage
    session = sessions.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    current_scenario = session["current_scenario"]
    world_state = session["world_state"]
    decision_history = session["decision_history"]
    company_memory = session["company_memory"]
    
    # Record the choice in session decision history
    session["decision_history"].append({
        "scenario_id": scenario_id,
        "choice": choice,
        "reason": reason,
        "timestamp": pattern_reader.record_choice(scenario_id, choice)["timestamp"]
    })
    
    # Evolve world and generate next scenario using WorldShifter
    session["round_number"] += 1
    round_number = session["round_number"]
    next_scenario = world_shifter.evolve_world(current_scenario, choice, round_number, world_state, decision_history, reason, company_memory)
    next_scenario["scenario_id"] = f"scenario_{round_number + 1}"
    
    # Update world state if WorldShifter returned an updated state
    if "updated_world_state" in next_scenario:
        session["world_state"] = next_scenario["updated_world_state"]
        del next_scenario["updated_world_state"]  # Don't expose to frontend
    
    # Update company memory if WorldShifter returned an updated memory
    if "updated_company_memory" in next_scenario:
        session["company_memory"] = next_scenario["updated_company_memory"]
        del next_scenario["updated_company_memory"]  # Don't expose to frontend
    
    # Update session
    session["current_scenario"] = next_scenario
    
    return jsonify({
        "scenario_id": next_scenario["scenario_id"],
        "title": next_scenario["title"],
        "story": next_scenario["story"],
        "options": next_scenario["options"],
        "company_name": "Aether Energy Systems",
        "position_size": "₹450 Crore (4.5% of Fund)",
        "investment_thesis": "Grid stabilization through micro-storage.",
        "fund_capital": "₹10,000 Cr",
        "portfolio_value": "₹10,240 Cr"
    })


@app.route('/decision-history', methods=['GET'])
def get_decision_history():
    """Return all recorded decisions for a session."""
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({"error": "session_id required"}), 400
    
    session = sessions.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify(session["decision_history"])


@app.route('/report', methods=['GET'])
def get_report():
    """Generate final investment thesis report for a session."""
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({"error": "session_id required"}), 400
    
    session = sessions.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    decision_history = session.get("decision_history", [])
    company_memory = session.get("company_memory", {})
    world_state = session.get("world_state", {})
    round_number = session.get("round_number", 1)
    
    # Generate report using ThesisReport agent
    report = thesis_report.generate_report(decision_history, company_memory, world_state, round_number)
    
    return jsonify(report)


@app.route('/test', methods=['GET'])
def test_page():
    """Temporary testing page for simulation loop."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Investment Simulation Test</title>
        <style>
            body {
                background-color: #1a1a1a;
                color: white;
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }
            h1 {
                border-bottom: 1px solid #444;
                padding-bottom: 10px;
            }
            .scenario-story {
                line-height: 1.6;
                margin: 20px 0;
            }
            .options {
                margin-top: 30px;
            }
            button {
                display: block;
                width: 100%;
                padding: 15px;
                margin: 10px 0;
                background-color: #333;
                color: white;
                border: 1px solid #555;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background-color: #444;
            }
            #loading {
                display: none;
                text-align: center;
                margin: 20px 0;
            }
            #reasonModal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.7);
                z-index: 1000;
            }
            .modal-content {
                background-color: #2a2a2a;
                margin: 15% auto;
                padding: 20px;
                border: 1px solid #444;
                width: 80%;
                max-width: 500px;
                border-radius: 5px;
            }
            .modal-content h2 {
                margin-top: 0;
            }
            .modal-content textarea {
                width: 100%;
                height: 80px;
                background-color: #333;
                color: white;
                border: 1px solid #555;
                padding: 10px;
                margin: 10px 0;
                resize: none;
                font-family: Arial, sans-serif;
            }
            .modal-buttons {
                display: flex;
                justify-content: flex-end;
                gap: 10px;
                margin-top: 10px;
            }
            .modal-buttons button {
                width: auto;
                padding: 10px 20px;
                margin: 0;
            }
        </style>
    </head>
    <body>
        <h1 id="title">Loading...</h1>
        <div id="story" class="scenario-story">Loading scenario...</div>
        <div id="loading">Loading next scenario...</div>
        <div class="options">
            <button id="optionA" onclick="showReasonModal('A')">A</button>
            <button id="optionB" onclick="showReasonModal('B')">B</button>
            <button id="optionC" onclick="showReasonModal('C')">C</button>
            <button id="optionD" onclick="showReasonModal('D')">D</button>
        </div>

        <div id="reasonModal">
            <div class="modal-content">
                <h2>Why did you choose this?</h2>
                <textarea id="reasonInput" maxlength="150" placeholder="Optional: Explain your reasoning (max 150 characters)"></textarea>
                <div class="modal-buttons">
                    <button onclick="closeModal()">Skip</button>
                    <button onclick="confirmChoice()">Continue</button>
                </div>
            </div>
        </div>

        <script>
            let currentScenario = null;
            let sessionId = null;
            let selectedChoice = null;

            async function loadScenario() {
                document.getElementById('loading').style.display = 'block';
                const response = await fetch('/scenario');
                currentScenario = await response.json();
                sessionId = currentScenario.session_id;
                displayScenario();
                document.getElementById('loading').style.display = 'none';
            }

            function displayScenario() {
                document.getElementById('title').textContent = currentScenario.title;
                document.getElementById('story').textContent = currentScenario.story;
                
                // Update button text with option descriptions
                document.getElementById('optionA').textContent = 'A. ' + currentScenario.options.A;
                document.getElementById('optionB').textContent = 'B. ' + currentScenario.options.B;
                document.getElementById('optionC').textContent = 'C. ' + currentScenario.options.C;
                document.getElementById('optionD').textContent = 'D. ' + currentScenario.options.D;
            }

            function showReasonModal(choice) {
                selectedChoice = choice;
                document.getElementById('reasonInput').value = '';
                document.getElementById('reasonModal').style.display = 'block';
            }

            function closeModal() {
                document.getElementById('reasonModal').style.display = 'none';
                selectedChoice = null;
            }

            async function confirmChoice() {
                const reason = document.getElementById('reasonInput').value.trim();
                document.getElementById('reasonModal').style.display = 'none';
                document.getElementById('loading').style.display = 'block';
                
                const response = await fetch('/choice', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        session_id: sessionId,
                        scenario_id: currentScenario.scenario_id,
                        choice: selectedChoice,
                        reason: reason || null
                    })
                });
                currentScenario = await response.json();
                displayScenario();
                document.getElementById('loading').style.display = 'none';
                selectedChoice = null;
            }

            // Load initial scenario on page load
            loadScenario();
        </script>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)
