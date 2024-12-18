from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from tf2.api.criteria import router as criteria_router
from tf2.api.resumes import router as resumes_router
from tf2.api.scorers import router as scorers_router

app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

app.include_router(criteria_router)
app.include_router(resumes_router)
app.include_router(scorers_router)

"""
# 对单份简历评分
curl -X POST "http://localhost:8000/scorers/技术评估/example.pdf"

# 批量评分
curl -X POST "http://localhost:8000/scorers/batch/技术评估"

# 获取详细评分结果
curl "http://localhost:8000/scorers/results/技术评估/example.pdf"

# 获取 JSON 格式的标准：
curl "http://localhost:8000/criteria/json/數據科學家評估標準"


# 创建新的评估标准：
curl -X POST "http://localhost:8000/criteria/json" \
     -H "Content-Type: application/json" \
     -d @standard.json

# 更新标准：
curl -X PUT "http://localhost:8000/criteria/json/數據科學家評估標準" \
     -H "Content-Type: application/json" \
     -d @updated_standard.json

# 列出所有标准：
curl "http://localhost:8000/criteria/list/json"

curl -X POST "http://localhost:8000/criteria/file" \
     -H "Content-Type: application/json" \
     -d '"/path/to/standard.json"'
"""

