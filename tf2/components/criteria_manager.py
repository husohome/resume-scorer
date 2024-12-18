from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from tf2.db.schemas import Criterion
import json
from pathlib import Path

class CriteriaManager:
    def __init__(self, criteria_folder: str = "./assets/criteria"):
        """
        初始化评估标准管理器
        Args:
            criteria_folder: 评估标准 JSON 文件所在文件夹
        """
        self._criteria_store: Dict[str, Criterion] = {}
        self.criteria_folder = Path(criteria_folder)
        self._load_default_criteria()
    
    def _load_default_criteria(self) -> None:
        """加载默认的评估标准"""
        try:
            if not self.criteria_folder.exists():
                return
            
            # 加载所有 JSON 文件
            for json_file in self.criteria_folder.glob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        json_data = json.load(f)
                        criterion = Criterion.from_json(json_data)
                        self._criteria_store[criterion.name] = criterion
                except Exception as e:
                    print(f"Error loading {json_file}: {str(e)}")
        except Exception as e:
            print(f"Error loading default criteria: {str(e)}")
    
    def load_criteria_from_json(self, json_path: str) -> Criterion:
        """
        从 JSON 文件加载评估标准
        Args:
            json_path: JSON 文件路径
        Returns:
            加载的评估标准
        """
        try:
            path = Path(json_path)
            if not path.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"JSON file {json_path} not found"
                )
            
            with open(path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                criterion = Criterion.from_json(json_data)
                self._criteria_store[criterion.name] = criterion
                return criterion
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON format: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error loading criteria: {str(e)}"
            )
    
    async def create_criteria(self, criteria: Criterion) -> Criterion:
        """创建新的评估标准"""
        if criteria.name in self._criteria_store:
            raise HTTPException(
                status_code=400, 
                detail=f"Criteria with name {criteria.name} already exists"
            )
        
        self._criteria_store[criteria.name] = criteria
        return criteria
    
    async def get_criteria(self, name: str) -> Criterion:
        """获取单个评估标准"""
        if name not in self._criteria_store:
            raise HTTPException(
                status_code=404, 
                detail=f"Criteria {name} not found"
            )
        return self._criteria_store[name]
    
    async def list_criteria(self, skip: int = 0, limit: int = 10) -> List[Criterion]:
        """列出所有评估标准"""
        return list(self._criteria_store.values())[skip:skip + limit]
    
    async def update_criteria(self, name: str, criteria: Criterion) -> Criterion:
        """更新评估标准"""
        if name not in self._criteria_store:
            raise HTTPException(
                status_code=404, 
                detail=f"Criteria {name} not found"
            )
        
        self._criteria_store[name] = criteria
        return criteria
    
    async def delete_criteria(self, name: str) -> bool:
        """删除评估标准"""
        if name not in self._criteria_store:
            raise HTTPException(
                status_code=404, 
                detail=f"Criteria {name} not found"
            )
        
        del self._criteria_store[name]
        return True
    
    async def search_criteria_by_metadata(
        self, metadata_query: Dict[str, Any]
    ) -> List[Criterion]:
        """通过元数据搜索评估标准"""
        results = []
        for criteria in self._criteria_store.values():
            matches = all(
                criteria.metadata.get(key) == value 
                for key, value in metadata_query.items()
            )
            if matches:
                results.append(criteria)
        return results
    
    async def get_criteria_tree(self, name: str) -> Dict[str, Any]:
        """获取评估标准的树形结构"""
        criteria = await self.get_criteria(name)
        
        def build_tree(criterion: Criterion) -> Dict[str, Any]:
            return {
                "name": criterion.name,
                "content": criterion.content,
                "scale": criterion.scale,
                "metadata": criterion.metadata,
                "children": [
                    {
                        "weight": weight,
                        **build_tree(child)
                    }
                    for weight, child in criterion.children
                ]
            }
        
        return build_tree(criteria)
    
    async def save_criteria_to_json(self, name: str, file_path: str) -> bool:
        """
        将评估标准保存为 JSON 文件
        Args:
            name: 标准名称
            file_path: 保存路径
        Returns:
            是否保存成功
        """
        try:
            criterion = await self.get_criteria(name)
            json_data = criterion.to_json()
            
            path = Path(file_path)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error saving criteria: {str(e)}"
            )

# 使用示例：
"""
# 创建管理器（会自动加载默认标准）
manager = CriteriaManager()

# 从特定 JSON 文件加载标准
criterion = manager.load_criteria_from_json("path/to/custom_criteria.json")

# 获取已加载的标准
standard_criterion = await manager.get_criteria("數據科學家評估標準")

# 获取树形结构
tree = await manager.get_criteria_tree("數據科學家評估標準")
"""
