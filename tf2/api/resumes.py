# tf2/api/resumes.py
from fastapi import APIRouter, Depends
from typing import List, Dict
from langchain.schema import Document
from tf2.components.resume_manager import ResumeManager

router = APIRouter(
    prefix="/resumes",
    tags=["resumes"]
)

# 依赖注入函数
async def get_resume_manager():
    return ResumeManager()  # 实际使用时可能需要配置基础路径

@router.post("/folder")
async def set_resume_folder(
    folder_path: str,
    manager: ResumeManager = Depends(get_resume_manager)
):
    """设置简历文件夹路径"""
    manager.set_base_folder(folder_path)
    return {"status": "success", "folder": folder_path}

@router.get("/metadata")
async def get_resumes_metadata(
    manager: ResumeManager = Depends(get_resume_manager)
):
    """获取所有简历的元数据"""
    return manager.get_resume_metadata()

@router.get("/{filename}")
async def get_resume(
    filename: str,
    manager: ResumeManager = Depends(get_resume_manager)
):
    """获取单个简历的内容"""
    documents = manager.read_resume(filename)
    return {
        "filename": filename,
        "pages": len(documents),
        "content": [doc.page_content for doc in documents],
        "metadata": [doc.metadata for doc in documents]
    }

@router.get("/")
async def read_all_resumes(
    manager: ResumeManager = Depends(get_resume_manager)
):
    """读取所有简历"""
    resumes = manager.read_all_resumes()
    return {
        filename: {
            "pages": len(docs),
            "content": [doc.page_content for doc in docs],
            "metadata": [doc.metadata for doc in docs]
        }
        for filename, docs in resumes.items()
    }
    

"""
curl -X POST "http://localhost:8000/resumes/folder" -d '"path/to/resumes"'

# 获取所有简历元数据
curl "http://localhost:8000/resumes/metadata"

# 读取特定简历
curl "http://localhost:8000/resumes/example.pdf"

# 读取所有简历
curl "http://localhost:8000/resumes/"
"""