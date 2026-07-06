# Thesis
### An AI-Powered Investment Psychology Simulator

> Information is no longer the edge. Decision-making is.

Thesis is an AI-powered investment committee simulator that evaluates **how investors think under uncertainty**, rather than whether they arrive at the "correct" answer.

Instead of measuring returns, Thesis analyzes conviction, adaptability, risk discipline, reasoning, and behavioral consistency across a sequence of evolving investment scenarios.

---

## The Problem

Modern AI can summarize earnings calls, generate DCF models, and produce both bull and bear cases for almost any company.

But after all the analysis is complete, one decision still remains.

That decision belongs to the investor.

Current investing platforms evaluate outcomes.
Thesis evaluates the decision-making process.

---

## What Thesis Does

You assume the role of a Chief Investment Officer managing institutional capital.

Across 20 sequential investment committee decisions:

- Companies evolve
- Markets change
- Management teams change
- Competitors react
- Macroeconomic conditions shift
- New information continuously emerges

There are **no correct answers.**

Only consequences.

At the end of the simulation, Thesis generates an institutional-style behavioral assessment describing your investment philosophy.

---

## Key Features

- AI-generated investment scenarios
- Dynamic world evolution
- Persistent company memory
- Behavioral pattern recognition
- Institutional-quality Investment Thesis Report
- Modern responsive frontend
- End-to-end simulation experience

---

## Tech Stack

### Backend
- Python
- Flask
- Groq LLM API

### Frontend
- HTML
- Tailwind CSS
- Vanilla JavaScript

### AI Components

- DungeonMaster
- WorldShifter
- PatternReader
- EventEngine
- ThesisReport

---

## Project Structure

```
Thesis/
│
├── agents/
│   ├── dungeon_master.py
│   ├── world_shifter.py
│   ├── pattern_reader.py
│   ├── event_engine.py
│   └── thesis_report.py
│
├── frontend/
├── data/
├── main.py
└── requirements.txt
```

---

## Running the Project

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Thesis.git
cd Thesis
```

Install dependencies

```bash
pip install -r requirements.txt
```

Set your Groq API key

Windows

```cmd
set GROQ_API_KEY=YOUR_API_KEY
```

Linux / macOS

```bash
export GROQ_API_KEY=YOUR_API_KEY
```

Run the application

```bash
python main.py
```

Open

```
http://127.0.0.1:5000
```

---

## Simulation Flow

Landing Page

↓

Investment Scenario

↓

Decision Selection

↓

Investment Reasoning

↓

World Evolution

↓

Next Committee Meeting

↓

Final Investment Thesis Report

---

## Future Improvements

- Multi-player investment committee mode
- Portfolio performance visualization
- Multiple investment styles
- Historical market simulations
- Custom company creation
- Enhanced behavioral analytics

---

## Inspiration

Thesis was built around one central idea:

> In a world where AI can generate every argument, the real competitive advantage is understanding **how you make decisions when no answer is certain.**

---

## Authors

Veydanth Bajaj

Capstone Project | Kaggle Hackathon 2026
