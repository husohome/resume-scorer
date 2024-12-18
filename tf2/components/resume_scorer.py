from typing import Optional
import random
from tf2.db.schemas import Criterion
from langchain.schema import Document

class ResumeScorer:
    def __init__(self, seed: Optional[int] = None):
        """
        初始化履歷評分器
        Args:
            seed: 隨機數種子，用於生成可重複的隨機分數
        """
        if seed is not None:
            random.seed(seed)
    
    def _generate_random_score(self) -> float:
        """生成0到1之間的隨機分數"""
        return round(random.uniform(0.0, 1.0), 2)
    
    def _fill_criterion_scores(self, criterion: Criterion) -> Criterion:
        """遞歸地為標準及其子標準填充隨機分數"""
        # 為當前標準生成隨機分數
        criterion.score = self._generate_random_score()
        
        # 遞歸處理所有子標準
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
        為履歷生成評分（模擬版本）
        
        Args:
            criterion: 評估標準對象
            documents: 履歷文檔（這裡不會實際使用，但保持接口一致性）
        
        Returns:
            填充了分數的評估標準對象
        """
        return self._fill_criterion_scores(criterion)
    
    def score_resume_batch(
        self,
        criterion: Criterion,
        documents_batch: dict[str, list[Document]]
    ) -> dict[str, Criterion]:
        """
        批量為多份履歷生成評分
        
        Args:
            criterion: 評估標準對象
            documents_batch: 履歷文檔批次，鍵為文件名
        
        Returns:
            文件名到評分結果的映射
        """
        results = {}
        for filename, docs in documents_batch.items():
            # 為每個履歷創建標準的深拷貝，避免共享狀態
            criterion_copy = Criterion(
                name=criterion.name,
                content=criterion.content,
                scale=criterion.scale,
                children=criterion.children.copy(),
                meta_info=criterion.meta_info.copy() if criterion.meta_info else {}
            )
            results[filename] = self.score_resume(criterion_copy, docs)
        return results

# 使用示例：
"""
# 創建評分器
scorer = ResumeScorer(seed=42)  # 使用固定子以獲得可重複的結果

# 創建評估標準
criterion = Criterion(
    name="總評",
    content="總體評估",
    scale="0.0 to 1.0",
    children=[
        (0.6, Criterion(
            name="技術能力",
            content="技術相關能力評估",
            scale="0.0 to 1.0",
            children=[]
        )),
        (0.4, Criterion(
            name="軟技能",
            content="溝通和團隊協作能力",
            scale="0.0 to 1.0",
            children=[]
        ))
    ]
)

# 為單份履歷評分
scored_criterion = scorer.score_resume(criterion, [])
print(f"總分：{scored_criterion.calculate_overall_score()}")

# 批量評分
documents_batch = {
    "resume1.pdf": [],
    "resume2.pdf": []
}
results = scorer.score_resume_batch(criterion, documents_batch)
for filename, scored in results.items():
    print(f"{filename}: {scored.calculate_overall_score()}")
"""
