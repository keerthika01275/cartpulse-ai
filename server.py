# server.py
"""
CartPulse AI - FastAPI WebSocket Server
Track 1: Agentic Commerce & Autonomous Negotiation Concierge
"""

import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Load Environment
env_file = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_file, override=True)

# Import Multi-Agent Graph & Catalogs from core
from core import PRODUCT_CATALOG, ACCESSORY_CATALOG, run_cartpulse_agent

app = FastAPI(
    title="CartPulse AI - Autonomous Agentic Commerce",
    description="Real-time event-driven agentic commerce concierge with deterministic bounded pricing, prompt injection defense, and 1-click checkout.",
    version="2.1.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "CartPulse AI Multi-Agent Commerce Engine",
        "version": "2.1.0",
        "theme": "Apple/Stripe Inspired Light Theme",
        "sub_agents": [
            "SentryRouter",
            "SecurityGuardrail",
            "CatalogSpecAgent",
            "ComparisonAgent",
            "PriceHesitationAgent",
            "PriceTrendForecaster",
            "CrossSellAgent",
            "BoundedPricingAgent",
            "CheckoutAgent"
        ]
    }

@app.get("/api/products")
async def get_products():
    """Returns the full catalog of 5 core products with price history and down-sell alternatives."""
    return JSONResponse(content=list(PRODUCT_CATALOG.values()))

@app.get("/api/accessories")
async def get_accessories():
    """Returns cross-sell accessory catalog with bundle pricing."""
    return JSONResponse(content=list(ACCESSORY_CATALOG.values()))

@app.websocket("/ws/telemetry")
async def telemetry_stream(websocket: WebSocket):
    """
    Asynchronous, non-blocking telemetry stream handling client heuristics,
    intent classification, real-time negotiation, and checkout minting.
    """
    await websocket.accept()
    client_ip = websocket.client.host if websocket.client else "unknown"
    print(f"[CartPulse AI] Client connected: {client_ip}")
    
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except Exception:
                await websocket.send_json({
                    "status": "ERROR",
                    "reply": "Invalid JSON format received.",
                    "active_agent": "SENTRY_ROUTER"
                })
                continue
            
            event_type = data.get("event", "USER_CHAT")
            user_msg = data.get("user_message", "")
            cart_items = data.get("cart_items", [])
            churn_risk = float(data.get("risk_score", 0.5))

            print(f"[CartPulse AI] Event: {event_type} | Risk: {churn_risk:.2f} | Message: {user_msg[:50]}")

            # Run Multi-Agent Graph in thread pool to keep event loop 100% non-blocking
            agent_response = await asyncio.to_thread(
                run_cartpulse_agent,
                event_type=event_type,
                user_message=user_msg,
                cart_items=cart_items,
                churn_risk=churn_risk
            )

            await websocket.send_json(agent_response)

    except WebSocketDisconnect:
        print(f"[CartPulse AI] WebSocket disconnected for client {client_ip}.")
    except Exception as e:
        print(f"[CartPulse AI ERROR] WebSocket exception: {e}")
        try:
            await websocket.send_json({
                "status": "ERROR",
                "active_agent": "ERROR_HANDLER",
                "reply": "An unexpected error occurred in the agentic pipeline. Please try again.",
                "trace": {"error": str(e)}
            })
        except Exception:
            pass

@app.get("/")
async def get_frontend():
    """Serves the polished single-page application."""
    index_path = Path(__file__).resolve().parent / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>CartPulse AI - index.html not found</h1>", status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)