from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import os
from agents import ParserAgent, CalculatorAgent, CoachAgent

app = FastAPI(title="Smart Nutritional Analyst")

# Initialize Agents
parser_agent = ParserAgent()
calculator_agent = CalculatorAgent()
coach_agent = CoachAgent()

# Serve static files
# Ensure the directories exist
os.makedirs("src", exist_ok=True)
app.mount("/src", StaticFiles(directory="src"), name="src")
app.mount("/data", StaticFiles(directory="data"), name="data")

class AnalysisRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return FileResponse("index.html")

@app.post("/analyze")
async def analyze_meal(request: AnalysisRequest):
    # Step 1: Parse
    parsed_items = await parser_agent.parse(request.text)
    
    # Step 2: Calculate
    calc_results = calculator_agent.calculate(parsed_items)
    
    # Step 3: Coach
    feedback = coach_agent.generate_feedback(calc_results["total"])
    
    return {
        "parsed_items": parsed_items,
        "total": calc_results["total"],
        "detailed_results": calc_results["detailed_results"],
        "feedback": feedback
    }

if __name__ == "__main__":
    import uvicorn
    # Use PORT environment variable if available (for cloud deployment like Render)
    # Default to 8000 for local development
    port = int(os.getenv("PORT", 8000))
    
    # Use 0.0.0.0 for cloud, but 127.0.0.1 is usually safer for local dev
    # However, 0.0.0.0 works everywhere.
    host = "0.0.0.0"
    
    print(f"--- Launching Smart Nutritional Analyst ---")
    print(f"Local Access: http://127.0.0.1:{port}")
    if os.getenv("PORT"):
        print(f"Cloud Mode detected (Port {port})")
    
    uvicorn.run(app, host=host, port=port)
