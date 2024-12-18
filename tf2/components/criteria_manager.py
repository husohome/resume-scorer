from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from tf2.db.schemas import Criterion
import json
from pathlib import Path
import shutil

class CriteriaManager:
    def __init__(self, criteria_folder: str = "./assets/criteria"):
        """
        初始化评估标准管理器
        Args:
            criteria_folder: 评估标准 JSON 文件所在文件夹
        """
        self.criteria_folder = Path(criteria_folder)
        self._ensure_folder_exists()
        self._criteria_store: Dict[str, Criterion] = {}
        self._criteria_file_map: Dict[str, Path] = {}  # 添加名称到文件路径的映射
        self._load_all_criteria()
    
    def _ensure_folder_exists(self) -> None:
        """确保标准文件夹存在"""
        self.criteria_folder.mkdir(parents=True, exist_ok=True)
    
    def _get_json_path(self, name: str) -> Path:
        """获取标准文件的完整路径"""
        return self.criteria_folder / f"{name}.json"
    
    def _load_all_criteria(self) -> None:
        """加载所有评估标准"""
        try:
            # 清空当前��储
            self._criteria_store.clear()
            self._criteria_file_map.clear()  # 清空映射
            
            # 加载所有 JSON 文件
            for json_file in self.criteria_folder.glob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        json_data = json.load(f)
                        criterion = Criterion.from_json(json_data)
                        self._criteria_store[criterion.name] = criterion
                        self._criteria_file_map[criterion.name] = json_file  # 记录文件路径
                except Exception as e:
                    print(f"Error loading {json_file}: {str(e)}")
        except Exception as e:
            print(f"Error loading criteria: {str(e)}")
    
    def _save_criterion_to_file(self, criterion: Criterion) -> None:
        """将单个标准保存到文件"""
        json_path = self._get_json_path(criterion.name)
        json_data = criterion.to_json()
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
    
    def create_criteria(self, criteria: Criterion) -> Criterion:
        """
        创建新的评估标准
        Args:
            criteria: 评估标准对象
        Returns:
            创建的评估标准
        Raises:
            HTTPException: 如果标准已存在或创建失败
        """
        json_path = self._get_json_path(criteria.name)
        if json_path.exists():
            raise HTTPException(
                status_code=400,
                detail=f"Criteria with name {criteria.name} already exists"
            )
        
        try:
            # 保存到文件
            self._save_criterion_to_file(criteria)
            # 更新内存中的存储
            self._criteria_store[criteria.name] = criteria
            return criteria
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create criteria: {str(e)}"
            )
    
    def get_criteria(self, name: str) -> Criterion:
        """
        获取单个评估标准
        Args:
            name: 标准名称
        Returns:
            评估标准对象
        Raises:
            HTTPException: 如果标准不存在
        """
        if name not in self._criteria_store:
            raise HTTPException(
                status_code=404,
                detail=f"Criteria {name} not found"
            )
        return self._criteria_store[name]
    
    def get_criteria_file_path(self, name: str) -> Path:
        """
        获取评估标准对应的文件路径
        Args:
            name: 标准名称
        Returns:
            文件路径
        Raises:
            HTTPException: 如果标准不存在
        """
        if name not in self._criteria_file_map:
            raise HTTPException(
                status_code=404,
                detail=f"Criteria {name} not found"
            )
        return self._criteria_file_map[name]
    
    def list_criteria(self, skip: int = 0, limit: int = 10) -> List[Criterion]:
        """
        列出所有评估标准
        Args:
            skip: 跳过的数量
            limit: 返回的最大数量
        Returns:
            评估标准列表
        """
        # 重新加载以确保最新
        self._load_all_criteria()
        return list(self._criteria_store.values())[skip:skip + limit]
    
    def update_criteria(self, name: str, criteria: Criterion) -> Criterion:
        """
        更新评估标准
        Args:
            name: 要更新的标准名称
            criteria: 新的标准对象
        Returns:
            更新后的标准
        Raises:
            HTTPException: 如果标准不存在或更新失败
        """
        if name not in self._criteria_store:
            raise HTTPException(
                status_code=404,
                detail=f"Criteria {name} not found"
            )
        
        try:
            # 获取正确的文件路径
            json_path = self.get_criteria_file_path(name)
            
            # 如果名称改变，需要删除旧文件
            if name != criteria.name:
                json_path.unlink()
                json_path = self._get_json_path(criteria.name)  # 更新路径
            
            # 保存新文件
            self._save_criterion_to_file(criteria)
            
            # 更新内存存储
            if name != criteria.name:
                del self._criteria_store[name]
                del self._criteria_file_map[name]
            self._criteria_store[criteria.name] = criteria
            self._criteria_file_map[criteria.name] = json_path
            
            return criteria
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update criteria: {str(e)}"
            )
    
    def delete_criteria(self, name: str) -> bool:
        """
        删除评估标准
        Args:
            name: 要删除的标准名称
        Returns:
            是否删除成功
        Raises:
            HTTPException: 如果标准不存在或删除失败
        """
        json_path = self._get_json_path(name)
        if not json_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Criteria {name} not found"
            )
        
        try:
            # 删除文件
            json_path.unlink()
            # 从内存中移除
            del self._criteria_store[name]
            return True
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete criteria: {str(e)}"
            )
    
    def search_criteria_by_metadata(
        self, metadata_query: Dict[str, Any]
    ) -> List[Criterion]:
        """
        通过元数据搜索评估标准
        Args:
            metadata_query: 元数据查询条件
        Returns:
            匹配的标准列表
        """
        # 重新加载以确保最新
        self._load_all_criteria()
        
        results = []
        for criteria in self._criteria_store.values():
            matches = all(
                criteria.meta_info.get(key) == value 
                for key, value in metadata_query.items()
            )
            if matches:
                results.append(criteria)
        return results
    
    def get_criteria_tree(self, name: str) -> Dict[str, Any]:
        """
        获取评估标准的树形结构
        Args:
            name: 标准名称
        Returns:
            树形结构的字典表示
        """
        criteria = self.get_criteria(name)
        
        def build_tree(criterion: Criterion) -> Dict[str, Any]:
            return {
                "name": criterion.name,
                "content": criterion.content,
                "scale": criterion.scale,
                "meta_info": criterion.meta_info,
                "children": [
                    {
                        "weight": weight,
                        **build_tree(child)
                    }
                    for weight, child in criterion.children
                ]
            }
        
        return build_tree(criteria)
    
    def backup_criteria(self, backup_folder: str) -> bool:
        """
        备份所有评估标准
        Args:
            backup_folder: 备份文件夹路径
        Returns:
            是否备份成功
        """
        try:
            backup_path = Path(backup_folder)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # 复制所有文件到备份文件夹
            for json_file in self.criteria_folder.glob("*.json"):
                shutil.copy2(json_file, backup_path)
            
            return True
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to backup criteria: {str(e)}"
            )
    
    def restore_criteria(self, backup_folder: str) -> bool:
        """
        从备份恢复评估标准
        Args:
            backup_folder: 备份文件夹路径
        Returns:
            是否恢复成功
        """
        try:
            backup_path = Path(backup_folder)
            if not backup_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"Backup folder {backup_folder} not found"
                )
            
            # 清空当前文件夹
            for json_file in self.criteria_folder.glob("*.json"):
                json_file.unlink()
            
            # 复制备份文件到当前文件夹
            for json_file in backup_path.glob("*.json"):
                shutil.copy2(json_file, self.criteria_folder)
            
            # 重新加载所有标准
            self._load_all_criteria()
            
            return True
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to restore criteria: {str(e)}"
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
