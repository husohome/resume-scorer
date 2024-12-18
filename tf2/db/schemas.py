from pydantic import BaseModel, ConfigDict
from typing import Any, Dict, List, Tuple, ForwardRef
import datetime

# 创建一个 ForwardRef 来处理自引用
CriterionRef = ForwardRef('Criterion')
class Criterion(BaseModel):
    """Pydantic 模型"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = ""
    content: str
    scale: str = "0.0 to 1.0"
    score: float | None = None
    children: List[Tuple[float, CriterionRef]] = []
    meta_info: Dict[str, Any] = {}

    def calculate_overall_score(self) -> float | None:
        """计算当前标准及其所有子标准的加权总分。
        如果某个必要的分数缺失，返回 None。

        Returns:
            float | None: 计算得出的加权总分，或在缺少必要分数时返回 None
        """
        # 如果当前标准有直接分数，且没有子标准，直接返回
        if not self.children:
            return self.score
            
        # 计算所有子标准的加权分数
        weighted_sum = 0.0
        total_weight = 0.0
        
        for weight, child in self.children:
            # 获取子标准分数（可能需要递归计算）
            child_score = child.score if child.score is not None else child.calculate_overall_score()
            
            # 如果任何子标准没有分数且无法计算，返回 None
            if child_score is None:
                return None
                
            total_weight += weight
            weighted_sum += weight * child_score
            
        # 避免除以零
        if total_weight == 0:
            return self.score
            
        # 返回加权平均分
        return weighted_sum / total_weight

    @classmethod
    def from_json(cls, json_data: dict) -> "Criterion":
        """从 JSON 数据创建 Criterion 对象"""
        children = []
        for child_data in json_data.get("children", []):
            weight = child_data["weight"]
            child = cls.from_json(child_data["criterion"])
            children.append((weight, child))
        
        return cls(
            name=json_data.get("name", ""),
            content=json_data["content"],
            scale=json_data.get("scale", "0.0 to 1.0"),
            score=json_data.get("score"),
            children=children,
            meta_info=json_data.get("meta_info", {})
        )

    def to_json(self) -> Dict[str, Any]:
        """转换为 JSON 格式"""
        return {
            "name": self.name,
            "content": self.content,
            "scale": self.scale,
            "score": self.score,
            "children": [
                {
                    "weight": weight,
                    "criterion": child.to_json()
                }
                for weight, child in self.children
            ],
            "meta_info": self.meta_info
        }

# 更新 ForwardRef
Criterion.model_rebuild()

class TFResume(BaseModel):
    """履歷模型"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    personal_info: str
    content: str # this is content without personal info
    meta_info: Dict[str, Any] = {}

class ResumeScoring(BaseModel):
    """履歷評分記錄"""
    resume: TFResume
    criterion: Criterion  # criterion itself has scores
    timing: datetime.datetime
