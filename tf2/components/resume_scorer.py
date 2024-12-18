from typing import Optional
import random
from tf2.db.schemas import Criterion
from langchain.schema import Document

class ResumeScorer:
    def __init__(self, seed: Optional[int] = None):
        """
        初始化简历评分器
        Args:
            seed: 随机数种子，用于生成可重复的随机分数
        """
        if seed is not None:
            random.seed(seed)
    
    def _generate_random_score(self) -> float:
        """生成0到1之间的随机分数"""
        return round(random.uniform(0.0, 1.0), 2)
    
    def _fill_criterion_scores(self, criterion: Criterion) -> Criterion:
        """递归地为标准及其子标准填充随机分数"""
        # 为当前标准生成随机分数
        criterion.score = self._generate_random_score()
        
        # 递归处理所有子标准
        scored_children = []
        for weight, child in criterion.children:
            scored_child = self._fill_criterion_scores(child)
            scored_children.append((weight, scored_child))
        
        criterion.children = scored_children
        return criterion
    
    def score_resume(
        self, 
        criterion: Criterion,
        documents: list[Document]
    ) -> Criterion:
        """
        为简历生成评分（模拟版本）
        
        Args:
            criterion: 评估标准对象
            documents: 简历文档（这里不会实际使用，但保持接口一致性）
        
        Returns:
            填充了分数的评估标准对象
        """
        return self._fill_criterion_scores(criterion)
    
    def score_resume_batch(
        self,
        criterion: Criterion,
        documents_batch: dict[str, list[Document]]
    ) -> dict[str, Criterion]:
        """
        批量为多份简历生成评分
        
        Args:
            criterion: 评估标准对象
            documents_batch: 简历文档批次，键为文件名
        
        Returns:
            文件名到评分结果的映射
        """
        results = {}
        for filename, docs in documents_batch.items():
            # 为每个简历创建标准的深拷贝，避免共享状态
            criterion_copy = Criterion(
                name=criterion.name,
                content=criterion.content,
                scale=criterion.scale,
                children=criterion.children.copy(),
                metadata=criterion.metadata.copy()
            )
            results[filename] = self.score_resume(criterion_copy, docs)
        return results

# 使用示例：
"""
# 创建评分器
scorer = ResumeScorer(seed=42)  # 使用固定种子以获得可重复的结果

# 创建评估标准
criterion = Criterion(
    name="总评",
    content="总体评估",
    scale="0.0 to 1.0",
    children=[
        (0.6, Criterion(
            name="技术能力",
            content="技术相关能力评估",
            scale="0.0 to 1.0",
            children=[]
        )),
        (0.4, Criterion(
            name="软技能",
            content="沟通和团队协作能力",
            scale="0.0 to 1.0",
            children=[]
        ))
    ]
)

# 为单份简历评分
scored_criterion = scorer.score_resume(criterion, [])
print(f"总分：{scored_criterion.calculate_overall_score()}")

# 批量评分
documents_batch = {
    "resume1.pdf": [],
    "resume2.pdf": []
}
results = scorer.score_resume_batch(criterion, documents_batch)
for filename, scored in results.items():
    print(f"{filename}: {scored.calculate_overall_score()}")
"""
