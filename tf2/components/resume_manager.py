from pathlib import Path
from typing import List, Optional, Dict
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
import filetype
from fastapi import HTTPException
from tf2.db.schemas import TFResume
import datetime

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
    
    def _convert_to_tf_resume(self, documents: List[Document], file_path: Path) -> TFResume:
        """將 Document 列表轉換為 TFResume 對象"""
        # 合併所有頁面的內容
        full_content = "\n".join(doc.page_content for doc in documents)
        
        # 簡單的個人信息提取（這裡可以根據需要改進）
        # 假設前500個字符包含個人信息
        personal_info = full_content[:500]
        remaining_content = full_content[500:]
        
        return TFResume(
            personal_info=personal_info,
            content=remaining_content,
            meta_info={
                "file_path": str(file_path),
                "file_type": "application/pdf",
                "page_count": len(documents),
                "last_modified": datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
            }
        )
    
    def read_resume(self, file_path: str) -> TFResume:
        """
        讀取單個履歷文件
        Args:
            file_path: PDF 文件路徑
        Returns:
            TFResume 對象
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
            self._resumes[path.name] = documents  # Store the raw documents in memory
            return self._convert_to_tf_resume(documents, path)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error reading PDF {file_path}: {str(e)}"
            )

    def get_all_resumes(self) -> Dict[str, TFResume]:
        """返回所有存儲的履歷（測試用假資料）"""
        return {
            "resume1.pdf": TFResume(
                personal_info="王小明\n0912-345-678\nxiaoming@email.com\n台北市信義區信義路100號",
                content="工作經歷：\n2018-2022 軟體工程師\n專案經驗：開發企業內部系統\n技能：Python, Java, SQL",
                meta_info={
                    "file_path": "/fake/path/resume1.pdf",
                    "file_type": "application/pdf", 
                    "page_count": 2,
                    "last_modified": datetime.datetime(2023, 1, 1)
                }
            ),
            "resume2.pdf": TFResume(
                personal_info="李大華\n0923-456-789\ndahua@email.com\n新北市板橋區中山路200號",
                content="工作經歷：\n2015-2023 系統分析師\n專案經驗：金融系統開發\n技能：C#, .NET, Azure",
                meta_info={
                    "file_path": "/fake/path/resume2.pdf",
                    "file_type": "application/pdf",
                    "page_count": 3,
                    "last_modified": datetime.datetime(2023, 2, 1)
                }
            ),
            "resume3.pdf": TFResume(
                personal_info="張美玲\n0934-567-890\nmeiling@email.com\n台中市西區民生路300號",
                content="工作經歷：\n2019-2023 前端工程師\n專案經驗：電商網站開發\n技能：JavaScript, React, Vue",
                meta_info={
                    "file_path": "/fake/path/resume3.pdf",
                    "file_type": "application/pdf",
                    "page_count": 1,
                    "last_modified": datetime.datetime(2023, 3, 1)
                }
            )
        }
    
    def read_all_resumes(self) -> Dict[str, TFResume]:
        """
        讀取文件夾中的所有履歷
        Returns:
            字典，鍵為文件名，值為 TFResume 對象
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
                results[file_path.name] = TFResume(
                    personal_info="Error reading file",
                    content=str(e.detail),
                    meta_info={
                        "error": True,
                        "file_path": str(file_path)
                    }
                )
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
