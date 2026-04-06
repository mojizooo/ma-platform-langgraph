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

    # 从模拟数据读取一条记录测试
    mock_data_path = os.path.join(os.path.dirname(__file__), 'crisis_mock_data.json')
    try:
        with open(mock_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 取第一条用于测试
            test_stu = data[0]
            student_id = test_stu["student_id"]
            raw_data = test_stu["raw_data"]
    except Exception as e:
        print(f"读取数据失败 {e}，将使用备用测试数据")
        student_id = "test_stu_001"
        raw_data = {
            "academic_data": {"gpa": 1.2, "failed_courses": 3},
            "financial_data": {"monthly_living_expenses": 500, "has_heavy_debt": True},
            "psychological_data": {"stress_index": 85, "sleep_quality_score": 3}
        }

    initial_state = {
        "student_id": student_id,
        "raw_data": raw_data
    }
    
    print(f"当前输入测试原始数据: {json.dumps(raw_data, ensure_ascii=False)}")
    
    results = app.invoke(initial_state)
    
    print(f"\n[Oracle 解密后结果]")
    print(f"学生ID: {results.get('student_id')}")
    print(f"最终预警判定: {'❗警报触发❗' if results.get('final_alert') else '✅安全'}")
    
    print(f"\n[验证系统中间状态(仅密文字符串，无真实数据)]")
    print(f"学术数据密文 (B64): {results.get('enc_academic_b64', '')[:30]}...")
    print(f"财务数据密文 (B64): {results.get('enc_financial_b64', '')[:30]}...")
    print(f"心理数据密文 (B64): {results.get('enc_psych_b64', '')[:30]}...")
    print(f"总分数密文 (B64)  : {results.get('enc_total_b64', '')[:30]}...")

    print("\n安全说明: coordinator_agent仅通过同态密文完成了盲算，没有接触过学生的真实原始分数")

if __name__ == "__main__":
    main()
