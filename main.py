import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request

from models import ScoringRequest, ScoringResult
import mock_data
from criteria import get_preset_criteria
from scoring_api import score_resume

app = FastAPI(title="Resume Scoring System")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "criteria": get_preset_criteria()}
    )

@app.get("/resumes", response_class=HTMLResponse)
async def list_resumes(request: Request):
    resumes = mock_data.get_mock_resumes()
    return templates.TemplateResponse(
        "resume_list.html",
        {"request": request, "resumes": resumes}
    )

@app.post("/api/score", response_model=ScoringResult)
async def score(request: ScoringRequest):
    # Get resume data
    resume = mock_data.get_resume_by_id(request.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Get criteria
    preset_criteria = get_preset_criteria().get(request.criteria_id)
    if not preset_criteria:
        raise HTTPException(status_code=404, detail="Criteria not found")
    
    criteria = preset_criteria['root_criterion']
    
    # Update weights if provided (TODO: implement weight updates)
    
    # Get scoring results
    results = score_resume(resume['non_personal'], criteria)
    return ScoringResult(**results)

@app.get("/scoring/{resume_id}", response_class=HTMLResponse)
async def scoring_result(request: Request, resume_id: str):
    resume = mock_data.get_resume_by_id(resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return templates.TemplateResponse(
        "scoring_result.html",
        {"request": request, "resume": resume, "criteria": get_preset_criteria()}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
