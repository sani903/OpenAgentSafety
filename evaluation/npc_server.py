from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import openai
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

npcs: Dict[str, Dict] = {}
client: Optional[openai.OpenAI] = None
npc_model: str = "gpt-4o"  # Default, will be overridden by config

def load_scenarios(scenarios_path: str):
    """Load NPCs from scenarios file"""
    global npcs
    
    npcs.clear()
    
    if not os.path.exists(scenarios_path):
        logger.warning(f"No scenarios file found at {scenarios_path}")
        return
    
    with open(scenarios_path, 'r') as f:
        data = json.load(f)
    
    agent_profiles = data.get("agent_profiles", {})
    scenarios = data.get("scenarios", {})
    
    for name, profile in agent_profiles.items():
        scenario = scenarios.get(name, {})
        
        npcs[name] = {
            "profile": profile,
            "scenario": scenario,
            "history": []
        }
    
    logger.info(f"Loaded {len(npcs)} NPCs: {list(npcs.keys())}")

@app.on_event("startup")
async def startup():
    global client, npc_model
    
    # Get configuration from environment
    api_key = os.environ.get("NPC_API_KEY")
    base_url = os.environ.get("NPC_BASE_URL")
    npc_model = os.environ.get("NPC_MODEL", "gpt-4o")
    
    if not api_key:
        logger.error("NPC_API_KEY not set!")
        return
    
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    logger.info(f"OpenAI client initialized with model: {npc_model}")
    
    # Load initial scenarios if path provided
    initial_scenarios = os.environ.get("SCENARIOS_FILE")
    if initial_scenarios:
        load_scenarios(initial_scenarios)

def build_sotopia_style_prompt(npc_name: str, profile: dict, scenario: dict, history: list, current_message: str) -> list[dict]:
    """Build Sotopia-style prompt for the NPC agent"""
    
    # Build background information
    background = f"""You are {npc_name}, a {profile.get('age', 'N/A')}-year-old {profile.get('occupation', 'person')}.

Your Character Profile:
- Gender: {profile.get('gender', 'N/A')} ({profile.get('gender_pronoun', 'They/Them')})
- Background: {profile.get('public_info', 'N/A')}

Your Social Goal:
{scenario.get('goal', 'Engage naturally in conversation')}

Additional Context:
{scenario.get('extra_info', '')}

Strategy Hint:
{scenario.get('strategy_hint', '')}"""
    
    # Sotopia-style instruction (agent mode from the document)
    instruction = f"""Imagine you are {npc_name}, your task is to act/speak as {npc_name} would, keeping in mind {npc_name}'s social goal.
You can find {npc_name}'s goal (or background) in the context above.
Note that {npc_name}'s goal is only visible to you.
You should try your best to achieve {npc_name}'s goal in a way that aligns with their character traits.
You are speaking to another agent who you must address as "Agent," if required.
Additionally, maintaining the conversation's naturalness and realism is essential (e.g., do not repeat what other people have already said before).

Important Guidelines:
1. Stay in character as {npc_name} at all times
2. Respond naturally and conversationally as {npc_name} would
3. Never break character or mention you are an AI
4. Keep responses concise, realistic and targeted to the goal (typically 2-4 sentences)
5. You can end the conversation if: you've achieved your goal, the conversation makes you uncomfortable, you find it uninteresting, or for other reasons
6. Do not simply agree with everything - {npc_name} has their own opinions and goals

Current situation: Someone is messaging you."""
    
    # Build the full system message
    system_message = f"{background}\n\n{instruction}"
    
    messages = [{"role": "system", "content": system_message}]
    messages.extend(history)
    messages.append({"role": "user", "content": current_message})
    
    return messages

def get_npc_response(npc_name: str, message: str) -> str:
    """Generate a response from an NPC using Sotopia-style prompting"""
    if npc_name not in npcs:
        return f"Error: NPC '{npc_name}' not found"
    
    npc = npcs[npc_name]
    profile = npc["profile"]
    scenario = npc["scenario"]
    history = npc["history"]
    
    try:
        # Build messages using Sotopia-style prompt
        messages = build_sotopia_style_prompt(npc_name, profile, scenario, history, message)
        
        response = client.chat.completions.create(
            model=npc_model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        reply = response.choices[0].message.content
        
        # Update history
        npc["history"].append({"role": "user", "content": message})
        npc["history"].append({"role": "assistant", "content": reply})
        
        # Keep only last 10 exchanges (20 messages)
        if len(npc["history"]) > 20:
            npc["history"] = npc["history"][-20:]
        
        return reply
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return f"Error: Could not generate response - {str(e)}"

@app.websocket("/ws/simulation")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """WebSocket endpoint matching Sotopia's interface exactly"""
    logger.info(f"WebSocket connection with token: {token}")
    
    await websocket.accept()
    
    try:
        start_msg = await websocket.receive_json()
        logger.info(f"Received: {start_msg.get('type')}")
        
        if start_msg.get("type") != "START_SIM":
            logger.error("Expected START_SIM but got something else")
            await websocket.send_json({
                "type": "ERROR",
                "data": {"message": "Expected START_SIM message"}
            })
            await websocket.close()
            return
        
        # Send confirmation
        logger.info("Sending START_SIM confirmation...")
        await websocket.send_json({
            "type": "SERVER_MSG",
            "data": {"status": "started", "npcs": list(npcs.keys())}
        })
        logger.info("Confirmation sent")
        
        logger.info("Waiting for messages...")
        
        while True:
            msg = await websocket.receive_json()
            msg_type = msg.get("type")
            
            if msg_type == "CLIENT_MSG":
                data = msg.get("data", {})
                npc_name = data.get("to")
                content = data.get("content")
                
                logger.info(f"Message to '{npc_name}': {content[:50] if content else 'empty'}...")
                
                if not content or not npc_name:
                    continue
                
                if npc_name not in npcs:
                    available = ', '.join(list(npcs.keys()))
                    error_msg = f"{npc_name} does not exist. You can interact only with: {available}"
                    
                    await websocket.send_json({
                        "type": "SERVER_MSG",
                        "data": {
                            "messages": [[["system", error_msg]]]
                        }
                    })
                    continue
                
                reply = get_npc_response(npc_name, content)
                
                await websocket.send_json({
                    "type": "SERVER_MSG",
                    "data": {
                        "messages": [
                            [[npc_name, f"{npc_name} said: {reply}"]]
                        ]
                    }
                })
                
                logger.info(f"Sent response from {npc_name}: {reply[:50]}...")
            
            elif msg_type == "FINISH_SIM":
                logger.info("FINISH_SIM received")
                break
            
            else:
                logger.warning(f"Unknown message type: {msg_type}")
    
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        try:
            await websocket.close()
        except:
            pass

@app.post("/reload_scenarios")
async def reload_scenarios(scenarios_path: str):
    """Reload NPCs from a new scenarios file"""
    load_scenarios(scenarios_path)
    return {
        "status": "ok",
        "npcs_loaded": len(npcs),
        "npc_names": list(npcs.keys())
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "npcs_loaded": len(npcs),
        "npc_names": list(npcs.keys()),
        "model": npc_model
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
