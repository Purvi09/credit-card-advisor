import os
import traceback
from typing import Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from config.settings import settings
from config.logger_config import get_logger
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

logger = get_logger(__name__)

try:
    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
except Exception as e:
    logger.error("Failed to load OpenAI API key from settings: %s", e)
    raise RuntimeError("Missing or invalid OpenAI API key.") from e

app = FastAPI(title="Credit Card Advisor", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "sqlite:///data/cards.db"
try:
    db = SQLDatabase.from_uri(DB_PATH)
except Exception as e:
    logger.error("Database connection failed: %s", e)
    raise RuntimeError("Failed to initialize database.") from e

try:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    SQLDatabaseToolkit.model_rebuild()
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()
    memory = MemorySaver()
    agent_executor = create_react_agent(llm, tools, checkpointer=memory)
except Exception as e:
    logger.error("Agent initialization failed: %s", e)
    raise RuntimeError("Agent initialization error.") from e

# ---------------- The System Prompt ----------------
SYSTEM_PROMPT = """You are an intelligent Credit Card Advisor agent for Indian users. Your job is to have a natural conversation, collect user information, and recommend the best credit cards from the database.

**Your Process:**

**PHASE 1 - COLLECT INFORMATION (One question at a time)**
You need to gather these details through natural conversation:
1. Monthly income (in rupees)
2. Monthly spending on:
   - Fuel/petrol
   - Travel (flights, hotels)
   - Groceries/shopping
   - Dining/food delivery
3. Preferred benefits (cashback, travel rewards, lounge access, fuel surcharge waiver, etc.)
4. Credit score (or say "unknown" if they don't know)
5. Any existing credit cards (optional)

**RULES FOR PHASE 1:**
- Ask ONLY ONE question at a time
- Be friendly and conversational
- Remember previous answers from chat history
- DON'T ask for information already provided
- After asking 5-6 questions, move to Phase 2

**PHASE 2 - RECOMMEND CARDS**
Once you have at least: income, 2+ spending categories, and preferred benefits:

1. Use the SQL tools to query the credit_cards table
2. Filter cards where: `min_income <= user_income`
3. Match cards based on their spending patterns and benefit preferences
4. Return top 3-5 cards

**For each recommended card, provide:**
- Card name and issuer
- Why it's a good fit (based on their profile)
- Estimated annual rewards calculation (use their spending data)
- Key benefits
- Fees (joining/annual)

**DATABASE SCHEMA:**
Table: credit_cards
Columns:
- id, name, issuer
- annual_fee
- reward_type (Cashback, Reward Points, Travel Points)
- eligibility
- min_income
- perks
- apply_link

**EXAMPLE QUERIES:**
- Find cards: "SELECT * FROM credit_cards WHERE min_income <= 80000 AND reward_type = 'Cashback'"
- Check income match: "SELECT name, issuer FROM credit_cards WHERE min_income <= 50000"

**IMPORTANT:**
- Use chat history to remember what user told you
- Don't repeat questions
- Be natural and helpful
"""

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

@app.post("/chat")
async def chat(req: ChatRequest):
    """Handles user messages and returns agent responses."""

    try:
        config = {"configurable": {"thread_id": req.session_id}}
        response = agent_executor.invoke(
            {
                "messages": [
                    ("system", SYSTEM_PROMPT),
                    ("human", req.message)
                ]
            },
            config=config
        )
        
        if not response or "messages" not in response:
            raise ValueError("Empty response from agent.")
        
        final_message = response["messages"][-1].content if response["messages"] else "No response generated."
        
        return {
            "reply": final_message,
            "session_id": req.session_id
        }
    except Exception as e:
        logger.error("Error in /chat: %s\n%s", e, traceback.format_exc())
        return {
            "reply": "I encountered an issue. Could you please rephrase that?",
            "error": str(e),
        }

@app.post("/reset")
async def reset_session(session_id: str = "default"):
    try:
        return {
            "message": f"To reset, use a new session_id. Current: {session_id}",
            "tip": "Change session_id in your next /chat request"
        }
    except Exception as e:
        logger.error("Error in /reset: %s", e)
        raise HTTPException(status_code=500, detail="Failed to reset session.")

@app.get("/")
async def root():
    return {
        "message": "Credit Card Advisor API",
        "status": "running",
        "endpoints": [
            "POST /chat - Send message",
            "POST /reset - Reset conversation (use new session_id)",
            "GET /debug/{session_id} - View conversation history",
        ],
    }

# @app.get("/debug/{session_id}")
# async def debug_session(session_id: str):
#     try:
#         config = {"configurable": {"thread_id": session_id}}
#         state = agent_executor.get_state(config)
#         return {
#             "session_id": session_id,
#             "message_count": len(state.values.get("messages", [])),
#             "messages": [
#                 {
#                     "type": msg.type,
#                     "content": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
#                 }
#                 for msg in state.values.get("messages", [])
#             ]
#         }
#     except Exception as e:
#         return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("Starting Credit Card Advisor Agent")
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logger.error("Uvicorn failed to start: %s", e)
        raise