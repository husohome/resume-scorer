from pathlib import Path
from typing import List, Optional, Dict
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
import filetype
from fastapi import HTTPException

class ResumeManager:
    def __init__(self, base_folder: Optional[str] = None):
        """
        初始化履歷管理器
        Args:
            base_folder: 履歷文件夾的基礎路徑
        """
        self.base_folder = Path(base_folder) if base_folder else None
        self._resumes: Dict[str, List[Document]] = {}  # Dictionary to store resumes
    
    def set_base_folder(self, folder_path: str) -> None:
        """設置基礎文件夾路徑"""
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
        """檢查文件是否為 PDF"""
        kind = filetype.guess(str(file_path))
        return kind is not None and kind.mime == 'application/pdf'
    
    def read_resume(self, file_path: str) -> List[Document]:
        """
        讀取單個履歷文件
        Args:
            file_path: PDF 文件路徑
        Returns:
            Document 列表，每個頁面一個 Document
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
            documents = loader.load()
            self._resumes[path.name] = documents  # Store the resume in memory
            return documents
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error reading PDF {file_path}: {str(e)}"
            )
    
    def get_all_resumes(self) -> Dict[str, List[Document]]:
        """返回所有存儲的履歷"""
        return self._resumes
    
    def read_all_resumes(self) -> dict[str, List[Document]]:
        """
        讀取文件夾中的所有履歷
        Returns:
            字典，鍵為文件名，值為 Document 列表
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
                # 記錄錯誤但繼續處理其他文件
                results[file_path.name] = [
                    Document(
                        page_content=f"Error reading file: {str(e.detail)}",
                        metadata={"error": True, "file_path": str(file_path)}
                    )
                ]
        return results
    
    def get_resume_metadata(self) -> List[dict]:
        """
        獲取所有履歷文件的元數據
        Returns:
            履歷元數據列表
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

    # 創建管理器並設置文件夾
    manager = ResumeManager("/path/to/resumes")

    # 讀取所有履歷
    all_resumes = manager.read_all_resumes()

    # 獲取元數據
    metadata = manager.get_resume_metadata()

    # 讀取單個履歷
    documents = manager.read_resume("/path/to/resumes/example.pdf")
