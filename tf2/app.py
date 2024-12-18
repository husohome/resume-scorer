import json
import gradio as gr
from pathlib import Path
from tf2.db.schemas import Criterion
from tf2.components.resume_scorer import ResumeScorer
from tf2.components.criteria_manager import CriteriaManager
from tf2.components.resume_manager import ResumeManager

print("\n=== 啟動履歷評分系統 ===")

# 获取 tf2 包的根目录
tf2_root = Path(__file__).parent
print(f"tf2 根目录: {tf2_root}")

# 初始化管理器（使用相对于 tf2 目录的路径）
criteria_manager = CriteriaManager(str(tf2_root / "assets/criteria"))
resume_manager = ResumeManager(str(tf2_root / "assets/resumes"))
scorer = ResumeScorer(seed=42)

# Define all_resumes globally
resume_manager.set_base_folder(str(tf2_root / "assets/resumes"))
all_resumes = resume_manager.get_all_resumes()

# Add Bootstrap CSS and JavaScript
BOOTSTRAP_HTML = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
function saveCriterion(element) {
    const card = element.closest('.card');
    const textarea = card.querySelector('textarea');
    const jsonText = textarea.value;
    // Call Gradio's function
    const event = new CustomEvent('save-criterion', { detail: jsonText });
    document.dispatchEvent(event);
}

function getSelectedResumes() {
    const checkboxes = document.querySelectorAll('.resume-checkbox:checked');
    return Array.from(checkboxes).map(cb => cb.dataset.name);
}
</script>
"""

def create_criterion_card(criterion):
    return f"""
    <div class="card mb-3">
        <div class="card-body">
            <h5 class="card-title">{criterion.name}</h5>
            <div class="form-group">
                <label>編輯標準</label>
                <textarea class="form-control" rows="10">{json.dumps(criterion.to_json(), ensure_ascii=False, indent=2)}</textarea>
            </div>
            <button class="btn btn-primary mt-2" onclick="saveCriterion(this)">儲存</button>
        </div>
    </div>
    """

def create_resume_card(name, docs, checked=False):
    return f"""
    <div class="card mb-2">
        <div class="card-body">
            <div class="form-check">
                <input class="form-check-input resume-checkbox" type="checkbox" data-name="{name}" {'checked' if checked else ''}>
                <label class="form-check-label">
                    <h5 class="card-title mb-0">{name}</h5>
                    <p class="card-text">頁數: {len(docs)}</p>
                </label>
            </div>
        </div>
    </div>
    """

def load_criteria_list():
    """獲取所有評分標準列表"""
    try:
        criteria_list = criteria_manager.list_criteria(skip=0, limit=100)
        names = [criterion.name for criterion in criteria_list]
        print(f"找到的評分標準: {names}")
        return names
    except Exception as e:
        print(f"載入評分標準時出錯: {str(e)}")
        return []

def get_criterion_details(name: str) -> tuple[gr.update, gr.update]:
    """
    獲取評分標準訊息
    Returns:
        tuple: (樹形顯示文本更新, JSON文本更新)
    """
    if not name:
        return (
            gr.update(value="請選擇一個評分標準"),
            gr.update(value="")
        )
        
    try:
        print(f"\n獲取標準詳情: {name}")
        criterion = criteria_manager.get_criteria(name)
        print(f"成功獲取標準: {criterion.name}")
        
        # 獲取 JSON 表示
        json_data = criterion.to_json()
        json_text = json.dumps(json_data, ensure_ascii=False, indent=2)
        
        # 獲取樹形結構
        tree = criteria_manager.get_criteria_tree(name)
        print(f"獲取到樹形結構: {tree}")
        
        def format_tree(node, level=0):
            indent = "  " * level
            result = [f"{indent}● {node['name']}"]
            result.append(f"{indent}  說明: {node['content']}")
            if node.get('meta_info'):
                result.append(f"{indent}  元信息: {node['meta_info']}")
            
            for child in node.get('children', []):
                weight = child['weight']
                result.append(f"{indent}  ├─ 權重: {weight}")
                child_node = {k: v for k, v in child.items() if k != 'weight'}
                result.extend(format_tree(child_node, level + 1))
            
            return result
        
        formatted = format_tree(tree)
        tree_text = "\n".join(formatted)
        print(f"格式化結果預覽:\n{tree_text[:200]}...")  # 只打印前200個字符作為預覽
        
        return (
            gr.update(value=tree_text),
            gr.update(value=json_text)
        )
        
    except Exception as e:
        error_msg = f"獲取標準詳情失敗: {str(e)}"
        print(f"錯誤: {error_msg}")
        return (
            gr.update(value=error_msg),
            gr.update(value="")
        )

def update_criterion_json(name: str, json_text: str) -> gr.update:
    """更新評分標準"""
    try:
        print(f"\n更新標準: {name}")
        print(f"更新內容: {json_text[:200]}...")  # 只打印前200個字符作為預覽
        
        json_data = json.loads(json_text)
        criterion = Criterion.from_json(json_data)
        criteria_manager.update_criteria(name, criterion)
        print(f"成功更新標準: {name}")
        return gr.update(value=f"成功更新標準: {name}")
    except Exception as e:
        error_msg = f"更新失敗: {str(e)}"
        print(f"錯誤: {error_msg}")
        return gr.update(value=error_msg)

def get_resume_list() -> list:
    """獲取履歷列表"""
    try:
        metadata_list = resume_manager.get_resume_metadata()
        return [
            f"{meta['filename']} ({meta['size'] / 1024:.1f} KB)"
            for meta in metadata_list
        ]
    except Exception as e:
        print(f"獲取履歷列表失敗: {str(e)}")
        return []

def update_resume_list() -> gr.update:
    """更新履歷列表的下拉菜單"""
    try:
        choices = get_resume_list()
        return gr.update(choices=choices)
    except Exception as e:
        return gr.update(choices=[f"獲取履歷列表失敗: {str(e)}"])

def score_selected_resumes(selected_resumes: list) -> str:
    """對選擇的履歷進行評分"""
    try:
        # 使用第一個評分標準
        criteria_list = criteria_manager.list_criteria()
        if not criteria_list:
            return "沒有可用的評分標準"
        criterion = criteria_list[0]  # Get the first criterion directly
        
        # 讀取選擇的履歷
        resumes = {name: all_resumes[name] for name in selected_resumes}
        
        # 批量評分
        results = scorer.score_resume_batch(criterion, resumes)
        
        # 格式化輸出
        output = ["評分結果：\n"]
        for filename, scored_criterion in results.items():
            overall_score = scored_criterion.calculate_overall_score()
            output.append(f"{filename}: {overall_score:.2f}")
            
            def format_details(crit, level=1):
                indent = "  " * level
                output.append(f"{indent}{crit.name}: {crit.score:.2f}")
                for _, child in crit.children:
                    format_details(child, level + 1)
            
            format_details(scored_criterion)
            output.append("")  # 添加空行分隔
        
        return "\n".join(output)
    except Exception as e:
        print(f"Error details: {str(e)}")  # Add debug print
        import traceback
        print(f"Traceback: {traceback.format_exc()}")  # Add traceback
        return f"評分失敗: {str(e)}"

def refresh_criteria():
    """刷新評分標準列表"""
    try:
        choices = load_criteria_list()
        return (
            gr.update(choices=choices, value=choices[0] if choices else None),
            gr.update(choices=choices, value=choices[0] if choices else None)
        )
    except Exception as e:
        print(f"刷新鈕出錯: {str(e)}")
        return (
            gr.update(choices=[], value=None),
            gr.update(choices=[], value=None)
        )

def handle_file_upload(files) -> str:
    """處理文件上傳"""
    if not files:
        return "請上傳至少一個文件。"
    
    try:
        # Set the base folder to assets/resumes
        resume_manager.set_base_folder(str(tf2_root / "assets/resumes"))
        
        for file in files:
            # Access the file content directly as a string
            file_content = file  # Since NamedString behaves like a string
            
            # Use the 'name' attribute to get the file name
            file_path = resume_manager.base_folder / file.name
            with open(file_path, "wb") as f:
                f.write(file_content.encode())  # Encode the string to bytes for writing
        return f"成功上傳 {len(files)} 個���件。"
    except Exception as e:
        return f"文件上傳失敗: {str(e)}"

def handle_scoring(selected_resumes: list) -> gr.update:
    """處理評分並更新顯示"""
    try:
        # 進行評分
        result = score_selected_resumes(selected_resumes)
        
        # 更新UI
        return gr.update(value=result)
    except Exception as e:
        return gr.update(value=f"評分失敗: {str(e)}")

# 創建 Gradio 界面
with gr.Blocks(title="履歷評分系統") as demo:
    gr.Markdown("# 履歷評分系統")
    
    # 評分標準區域
    gr.Markdown("## 評分標準")
    with gr.Row():
        for criterion in criteria_manager.list_criteria():
            with gr.Accordion(label=criterion.name, open=False):
                json_editor = gr.Code(
                    value=json.dumps(criterion.to_json(), ensure_ascii=False, indent=2),
                    language="json",
                    interactive=True,
                    label="編輯標準"
                )
                save_btn = gr.Button("儲存")
                save_status = gr.Textbox(label="儲存狀態", interactive=False)
                
                def save_criterion(json_text):
                    try:
                        json_data = json.loads(json_text)
                        criterion = Criterion.from_json(json_data)
                        criteria_manager.update_criteria(criterion.name, criterion)
                        return gr.update(value="儲存成功")
                    except Exception as e:
                        return gr.update(value=f"儲存失敗: {str(e)}")
                
                save_btn.click(
                    fn=save_criterion,
                    inputs=[json_editor],
                    outputs=[save_status]
                )
    
    # 履歷管理與評分區域
    gr.Markdown("## 履歷管理與評分")
    with gr.Row():
        upload_file = gr.File(
            label="上傳新履歷",
            file_types=[".pdf"],
            file_count="multiple"
        )
        score_btn = gr.Button("開始評分")
        
    with gr.Row():
        # build me some test all resumes
        all_resumes = {'Jane': 'resume 1', 'John': 'resume 2', 'Jack': 'resume 3'}
        resume_checkboxes = gr.CheckboxGroup(
            choices=[f"{name} ({len(docs)} pages)" for name, docs in all_resumes.items()],
            label="選擇要評分的履歷",
            interactive=True
        )

    # 評分結果顯示
    score_status = gr.Textbox(label="評分結果", interactive=False)

    def handle_upload(files):
        """處理文件上傳並更��履歷列表"""
        try:
            # 上傳文件
            upload_result = handle_file_upload(files)
            
            # 重新載入履歷列表
            global all_resumes
            all_resumes = resume_manager.get_all_resumes()
            
            # 更新選項列表
            choices = [f"{name} ({len(docs)} pages)" for name, docs in all_resumes.items()]
            
            # 更新UI
            return [
                gr.update(value="上傳成功"),
                gr.update(choices=choices)
            ]
        except Exception as e:
            return [
                gr.update(value=f"上傳失敗: {str(e)}"),
                gr.update()
            ]

    def handle_scoring(selected_resumes):
        """處理評分並更新顯示"""
        try:
            # 從選擇的字符串中提取文件名
            selected_names = [name.split(" (")[0] for name in selected_resumes]
            
            # 進行評分
            result = score_selected_resumes(selected_names)
            
            # 更新UI
            return gr.update(value=result)
        except Exception as e:
            return gr.update(value=f"評分失敗: {str(e)}")

    # 綁定事件
    upload_file.upload(
        fn=handle_upload,
        inputs=[upload_file],
        outputs=[score_status, resume_checkboxes]
    )

    score_btn.click(
        fn=handle_scoring,
        inputs=[resume_checkboxes],
        outputs=[score_status]
    )

if __name__ == "__main__":
    print("\n啟動 Gradio 介面...")
    demo.launch() 