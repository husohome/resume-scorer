from fastapi import APIRouter, Depends, HTTPException
from typing import List, Any, Dict
from tf2.db.schemas import Criterion
from tf2.components.criteria_manager import CriteriaManager

router = APIRouter(
    prefix="/criteria",
    tags=["criteria"]
)

# 依赖注入函数
async def get_criteria_manager():
    return CriteriaManager()

@router.post("/", response_model=Criterion)
async def create_criteria(
    criteria: Criterion,
    manager: CriteriaManager = Depends(get_criteria_manager)
):
    """创建新的评估标准"""
    return await manager.create_criteria(criteria)

@router.get("/{name}", response_model=Criterion)
async def get_criteria(
    name: str,
    manager: CriteriaManager = Depends(get_criteria_manager)
):
    """获取单个评估标准"""
    return await manager.get_criteria(name)

@router.get("/", response_model=List[Criterion])
async def list_criteria(
    skip: int = 0,
    limit: int = 10,
    manager: CriteriaManager = Depends(get_criteria_manager)
):
    """列出所有评估标准"""
    return await manager.list_criteria(skip=skip, limit=limit)

@router.put("/{name}", response_model=Criterion)
async def update_criteria(
    name: str,
    criteria: Criterion,
    manager: CriteriaManager = Depends(get_criteria_manager)
):
    """更新评估标准"""
    return await manager.update_criteria(name, criteria)

@router.delete("/{name}", response_model=bool)
async def delete_criteria(
    name: str,
    manager: CriteriaManager = Depends(get_criteria_manager)
):
    """删除评估标准"""
    return await manager.delete_criteria(name)

@router.get("/{name}/tree", response_model=dict[str, Any])
async def get_criteria_tree(
    name: str,
    manager: CriteriaManager = Depends(get_criteria_manager)
):
    """获取评估标准的树形结构"""
    return await manager.get_criteria_tree(name)

@router.post("/search", response_model=List[Criterion])
async def search_criteria(
    metadata_query: dict[str, Any],
    manager: CriteriaManager = Depends(get_criteria_manager)
):
    """通过元数据搜索评估标准"""
    return await manager.search_criteria_by_metadata(metadata_query)

@router.post("/json", response_model=Criterion)
async def create_criteria_from_json(
    json_data: Dict[str, Any],
    manager: CriteriaManager = Depends(get_criteria_manager)
):
    """从 JSON 创建新的评估标准"""
    try:
        criterion = Criterion.from_json(json_data)
        return await manager.create_criteria(criterion)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/file")
async def create_criteria_from_file(
    file_path: str,
    manager: CriteriaManager = Depends(get_criteria_manager)
):
    """从 JSON 文件创建评估标准"""
    try:
        return await manager.load_criteria_from_json(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/json/{name}")
async def get_criteria_as_json(
    name: str,
    manager: CriteriaManager = Depends(get_criteria_manager)
):
    """获取评估标准的 JSON 表示"""
    criterion = await manager.get_criteria(name)
    return criterion.to_json()

@router.put("/json/{name}")
async def update_criteria_from_json(
    name: str,
    json_data: Dict[str, Any],
    manager: CriteriaManager = Depends(get_criteria_manager)
):
    """使用 JSON 更新评估标准"""
    try:
        criterion = Criterion.from_json(json_data)
        return await manager.update_criteria(name, criterion)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list/json")
async def list_criteria_as_json(
    manager: CriteriaManager = Depends(get_criteria_manager)
):
    """列出所有评估标准的 JSON 表示"""
    criteria = await manager.list_all_criteria()
    return [c.to_json() for c in criteria]
