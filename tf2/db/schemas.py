from pydantic import BaseModel
from typing_extensions import Self
from typing import Any, Dict
from sqlalchemy import Column, String, Float, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.ext.declarative import declared_attr

class Base(DeclarativeBase):
    pass

# 关联表用于处理 criteria 之间的父子关系
criteria_association = Table(
    'criteria_association',
    Base.metadata,
    Column('parent_id', String, ForeignKey('criteria.name'), primary_key=True),
    Column('child_id', String, ForeignKey('criteria.name'), primary_key=True),
    Column('weight', Float, nullable=False)
)

class CriterionORM(Base):
    """SQLAlchemy 的 Criterion 模型"""
    __tablename__ = 'criteria'

    name = Column(String, primary_key=True)
    content = Column(String, nullable=False)
    scale = Column(String, nullable=False)
    score = Column(Float, nullable=True)
    metadata = Column(JSON, nullable=False, default=dict)

    # 自引用关系
    children = relationship(
        'CriterionORM',
        secondary=criteria_association,
        primaryjoin=name == criteria_association.c.parent_id,
        secondaryjoin=name == criteria_association.c.child_id,
        backref='parents'
    )

    def to_pydantic(self) -> "Criterion":
        """转换为 Pydantic 模���"""
        children_with_weights = []
        for child in self.children:
            # 获取权重
            weight = next(
                row.weight for row in criteria_association.select()
                .where(criteria_association.c.parent_id == self.name)
                .where(criteria_association.c.child_id == child.name)
                .execute()
            )
            children_with_weights.append((weight, child.to_pydantic()))
        
        return Criterion(
            name=self.name,
            content=self.content,
            scale=self.scale,
            score=self.score,
            children=children_with_weights,
            metadata=self.metadata
        )

    @classmethod
    def from_pydantic(cls, criterion: "Criterion") -> "CriterionORM":
        """从 Pydantic 模型创建"""
        orm_criterion = cls(
            name=criterion.name,
            content=criterion.content,
            scale=criterion.scale,
            score=criterion.score,
            metadata=criterion.metadata
        )
        
        # 递归处理子标准
        for weight, child in criterion.children:
            child_orm = cls.from_pydantic(child)
            orm_criterion.children.append(child_orm)
            # 需要单独设置权重
            criteria_association.insert().values(
                parent_id=orm_criterion.name,
                child_id=child_orm.name,
                weight=weight
            )
        
        return orm_criterion

class Criterion(BaseModel):
    """Pydantic 模型保持不变"""
    name: str = ""
    content: str
    scale: str = "0.0 to 1.0"
    score: float | None = None
    children: list[tuple[float, Self]] = []
    metadata: dict[str, Any] = {}

    def to_orm(self) -> CriterionORM:
        """便捷方法：转换为 ORM 模型"""
        return CriterionORM.from_pydantic(self)

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
            metadata=json_data.get("metadata", {})
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
            "metadata": self.metadata
        }

    