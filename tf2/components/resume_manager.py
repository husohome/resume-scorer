from pathlib import Path
from typing import List, Optional
from langchain.document_loaders import PyPDFLoader
from langchain.schema import Document
import magic
from fastapi import HTTPException

class ResumeManager:
    def __init__(self, base_folder: Optional[str] = None):
        """
        初始化简历管理器
        Args:
            base_folder: 简历文件夹的基础路径
        """
        self.base_folder = Path(base_folder) if base_folder else None
        self._mime = magic.Magic(mime=True)
    
    def set_base_folder(self, folder_path: str) -> None:
        """设置基础文件夹路径"""
        path = Path(folder_path)
        if not path.exists():
            raise HTTPException(
                status_code=400,
                detail=f"Folder path {folder_path} does not exist"
            )
        if not path.is_dir():
            raise HTTPException(
                status_code=400,
                detail=f"Path {folder_path} is not a directory"
            )
        self.base_folder = path
    
    def _is_pdf(self, file_path: Path) -> bool:
        """检查文件是否为 PDF"""
        mime_type = self._mime.from_file(str(file_path))
        return mime_type == 'application/pdf'
    
    def read_resume(self, file_path: str) -> List[Document]:
        """
        读取单个简历文件
        Args:
            file_path: PDF 文件路径
        Returns:
            Document 列表，每个页面一个 Document
        """
        path = Path(file_path)
        if not path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File {file_path} not found"
            )
        
        if not self._is_pdf(path):
            raise HTTPException(
                status_code=400,
                detail=f"File {file_path} is not a PDF"
            )
        
        try:
            loader = PyPDFLoader(str(path))
            return loader.load()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error reading PDF {file_path}: {str(e)}"
            )
    
    def read_all_resumes(self) -> dict[str, List[Document]]:
        """
        读取文件夹中的所有简历
        Returns:
            字典，键为文件名，值为 Document 列表
        """
        if not self.base_folder:
            raise HTTPException(
                status_code=400,
                detail="Base folder not set"
            )
        
        results = {}
        for file_path in self.base_folder.glob("*.pdf"):
            try:
                results[file_path.name] = self.read_resume(str(file_path))
            except HTTPException as e:
                # 记录错误但继续处理其他文件
                results[file_path.name] = [
                    Document(
                        page_content=f"Error reading file: {str(e.detail)}",
                        metadata={"error": True, "file_path": str(file_path)}
                    )
                ]
        return results
    
    def get_resume_metadata(self) -> List[dict]:
        """
        获取所有简历文件的元数据
        Returns:
            简历元数据列表
        """
        if not self.base_folder:
            raise HTTPException(
                status_code=400,
                detail="Base folder not set"
            )
        
        metadata = []
        for file_path in self.base_folder.glob("*.pdf"):
            if self._is_pdf(file_path):
                metadata.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "last_modified": file_path.stat().st_mtime,
                    "path": str(file_path)
                })
        return metadata

# FastAPI 路由示例：
"""
@router.post("/resumes/folder")
async def set_resume_folder(folder_path: str):
    manager = ResumeManager()
    manager.set_base_folder(folder_path)
    return {"status": "success", "folder": folder_path}

@router.get("/resumes/metadata")
async def get_resumes_metadata():
    manager = ResumeManager()
    return manager.get_resume_metadata()

@router.get("/resumes/{filename}")
async def get_resume(filename: str):
    manager = ResumeManager()
    documents = manager.read_resume(filename)
    return {
        "filename": filename,
        "pages": len(documents),
        "content": [doc.page_content for doc in documents]
    }
"""

if __name__ == "__main__":

    # 创建管理器并设置文件夹
    manager = ResumeManager("/path/to/resumes")

    # 读取所有简历
    all_resumes = manager.read_all_resumes()

    # 获取元数据
    metadata = manager.get_resume_metadata()

    # 读取单个简历
    documents = manager.read_resume("/path/to/resumes/example.pdf")
