from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List
from langchain.schema import Document
from tf2.db.schemas import Criterion
from tf2.components.resume_scorer import ResumeScorer
from tf2.components.resume_manager import ResumeManager
from tf2.components.criteria_manager import CriteriaManager

router = APIRouter(
    prefix="/scorers",
    tags=["scorers"]
)

# 依赖注入函数
async def get_scorer():
    return ResumeScorer(seed=42)  # 使用固定种子以保持结果一致性

async def get_resume_manager():
    return ResumeManager()

async def get_criteria_manager():
    return CriteriaManager()

@router.post("/{criteria_name}/{resume_filename}")
async def score_single_resume(
    criteria_name: str,
    resume_filename: str,
    scorer: ResumeScorer = Depends(get_scorer),
    resume_manager: ResumeManager = Depends(get_resume_manager),
    criteria_manager: CriteriaManager = Depends(get_criteria_manager)
):
    """
    对单份简历进行评分
    
    Args:
        criteria_name: 评估标准名称
        resume_filename: 简历文件名
    """
    try:
        # 获取评估标准
        criterion = await criteria_manager.get_criteria(criteria_name)
        
        # 读取简历文档
        documents = resume_manager.read_resume(resume_filename)
        
        # 评分
        scored_criterion = scorer.score_resume(criterion, documents)
        
        return {
            "resume": resume_filename,
            "criteria": criteria_name,
            "scored_criterion": scored_criterion,
            "overall_score": scored_criterion.calculate_overall_score()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch/{criteria_name}")
async def score_resume_batch(
    criteria_name: str,
    scorer: ResumeScorer = Depends(get_scorer),
    resume_manager: ResumeManager = Depends(get_resume_manager),
    criteria_manager: CriteriaManager = Depends(get_criteria_manager)
):
    """
    批量评分处理
    
    Args:
        criteria_name: 评估标准名称
    """
    try:
        # 获取评估标准
        criterion = await criteria_manager.get_criteria(criteria_name)
        
        # 读取所有简历
        documents_batch = resume_manager.read_all_resumes()
        
        # 批量评分
        results = scorer.score_resume_batch(criterion, documents_batch)
        
        # ���式化返回结果
        return {
            filename: {
                "scored_criterion": scored,
                "overall_score": scored.calculate_overall_score()
            }
            for filename, scored in results.items()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{criteria_name}/{resume_filename}")
async def get_scoring_details(
    criteria_name: str,
    resume_filename: str,
    scorer: ResumeScorer = Depends(get_scorer),
    resume_manager: ResumeManager = Depends(get_resume_manager),
    criteria_manager: CriteriaManager = Depends(get_criteria_manager)
):
    """
    获取详细的评分结果
    
    Args:
        criteria_name: 评估标准名称
        resume_filename: 简历文件名
    """
    try:
        result = await score_single_resume(
            criteria_name,
            resume_filename,
            scorer,
            resume_manager,
            criteria_manager
        )
        
        # 添加更多详细信息
        scored_criterion = result["scored_criterion"]
        
        def extract_scores(criterion: Criterion) -> Dict:
            return {
                "name": criterion.name,
                "score": criterion.score,
                "content": criterion.content,
                "children": [
                    {
                        "weight": weight,
                        **extract_scores(child)
                    }
                    for weight, child in criterion.children
                ]
            }
        
        return {
            "resume": resume_filename,
            "criteria": criteria_name,
            "overall_score": result["overall_score"],
            "detailed_scores": extract_scores(scored_criterion)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
