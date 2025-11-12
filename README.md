# 💳 Credit Card Advisor (AI Agent)

An intelligent **Credit Card Recommendation System** powered by **FastAPI**, **LangChain**, **LangGraph**, and **Streamlit**.

This project includes:
- **Backend (FastAPI + LangChain Agent)** — handles conversation, reasoning, and database querying  
- **Frontend (Streamlit)** — provides an interactive chat UI for users  
- **SQLite database** — stores credit card details (loaded from JSON)


## Demo
> [Watch the demo video here](https://drive.google.com/file/d/1aAOBp5Vd3d3mpWRhoisnl1bgMLdUc_hz/view?usp=sharing)


## Project Structure
CREDIT_CARD_ADVISOR/  
│  
├── backend/  
│ ├── config/  
│ │ ├── app.log  
│ │ ├── logger_config.py  
│ │ └── settings.py  
│ │   
│ ├── data/  
│ │ ├── creditCards.json  
│ │ ├── init_db.py  
│ │ └── cards.db  
│ │  
│ ├── main.py # FastAPI + LangChain agent  
│ ├── requirements.txt  
│ └── venv/  
│ └── .env  
│  
├── frontend/  
│ ├── app.py # Streamlit UI  
│ ├── requirements.txt  
│ └── venv/  
│  
└── README.md  

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/credit-card-advisor.git
cd credit-card-advisor
```

### 2. Backend Setup
Create and Activate Virtual Environment

```bash
cd backend
python -m venv venv # for windows
venv\Scripts\activate
pip install -r requirements.txt

#Create a .env file inside the backend/ folder:
OPENAI_API_KEY=your_openai_api_key

python data/init_db.py
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Backend will run at:
http://localhost:8000

### 3. Frontend Setup
Create and Activate Virtual Environment

```bash
cd ../frontend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Frontend will run at:
http://localhost:8501

## Agent Flow
### Architecture Overview

The Credit Card Advisor Agent follows a structured two-phase flow:

### PHASE 1 — Collect User Info

Ask one question at a time and Collects:

1. Monthly income
2. Spending categories (fuel, travel, groceries, dining)
3. Preferred benefits
4. Credit score (optional)
5. Existing cards (optional)

Uses LangGraph MemorySaver to remember previous answers.

### PHASE 2 — Recommend Cards

1. Executes SQL queries via LangChain tools:
```bash
SELECT * FROM credit_cards WHERE min_income <= {user_income};
```
2. Matches spending and benefit preferences

3. Returns 3–5 best matching cards with:
    1. Card name & issuer
    2. Why it’s a good fit
    3. Key benefits
    4. Annual fee
    5. Apply link

## Prompt Design

The system prompt (in main.py) defines the AI’s personality.  
It include:
1. Step-by-step instruction for clear understanding of model
2. Criteria to select best card for user.
3. Example (few-shot)

It ensures:  
1. Human-like, friendly conversation  
2. SQL-based data querying  
3. Context retention between messages  
4. Step-by-step interaction (not a single response)  

## Author

Kritika Agrawal  
Junior Software Developer @ Q3 Technologies  
B.Tech, NIT Kurukshetra (Production & Industrial Engineering, 2024)  