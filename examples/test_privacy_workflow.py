import sys
import os
import json
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.workflows.main_graph import app, ts

def main():
    if ts is None:
        print("请按要求安装 tenseal后再运行: pip install tenseal")
        return

    # 从模拟数据读取
    mock_data_path = os.path.join(os.path.dirname(__file__), 'crisis_mock_data.json')
    all_data = []
    try:
        if os.path.exists(mock_data_path):
            with open(mock_data_path, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
    except Exception as e:
        print(f"读取数据失败: {e}")

    if not all_data:
        print("未检测到模拟数据，将使用备用单条测试数据")
        all_data = [{
            "student_id": "test_stu_001",
            "raw_data": {
                "academic_data": {"gpa": 1.2, "failed_courses": 3},
                "financial_data": {"monthly_living_expenses": 500, "has_heavy_debt": True},
                "psychological_data": {"stress_index": 85, "sleep_quality_score": 3}
            }
        }]

    print(f"可用测试数据条数: {len(all_data)}")
    
    # 支持从命令行参数获取或手动输入
    if len(sys.argv) > 1:
        try:
            num_to_process = int(sys.argv[1])
        except ValueError:
            num_to_process = 1
    else:
        try:
            val = input(f"请输入要处理的数据条数 (1-{len(all_data)}, 默认 1): ").strip()
            num_to_process = int(val) if val else 1
        except EOFError:
            num_to_process = 1
        except ValueError:
            num_to_process = 1

    num_to_process = max(1, min(num_to_process, len(all_data)))
    print(f"🚀 正在启动工作流，准备处理 {num_to_process} 条数据...\n")

    for i in range(num_to_process):
        test_stu = all_data[i]
        student_id = test_stu["student_id"]
        raw_data = test_stu["raw_data"]

        initial_state = {
            "student_id": student_id,
            "raw_data": raw_data
        }
        
        print(f"--- [进度 {i+1}/{num_to_process}] 正在评估学生: {student_id} ---")
        print(f"原始数据快照: {json.dumps(raw_data, ensure_ascii=False)}")
        
        results = app.invoke(initial_state)
        
        print(f"最终预警判定: {'❗警报触发❗' if results.get('final_alert') else '✅安全'}")
        
        # 仅在处理少量数据或最后一条时显示密文，避免刷屏
        if num_to_process <= 2 or i == num_to_process - 1:
            print(f"[加密状态验证]")
            print(f"学术密文(部分): {results.get('enc_academic_b64', '')[:20]}...")
            print(f"财务密文(部分): {results.get('enc_financial_b64', '')[:20]}...")
            print(f"总分密文(部分): {results.get('enc_total_b64', '')[:20]}...")
        
        print("-" * 50)

    print("\n✅ 所有评估任务已完成。")

if __name__ == "__main__":
    main()
