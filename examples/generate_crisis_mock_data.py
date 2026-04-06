import json
import random

def generate_crisis_warning_data(num_records=100, output_file="crisis_mock_data.json"):

    last_names = ["张", "王", "李", "赵", "陈", "刘", "杨", "黄", "吴", "周", "徐", "孙", "马", "朱", "胡", "林", "郭", "何", "高", "罗"]
    middle_names = ["", "", "", "伟", "建", "宇", "浩", "博", "思", "子", "云", "佳", "晓", "秀", "玉", "秋", "梦", "文", "明", "志", "德", "泽", "嘉", "欣", "晨"]
    first_names = ["强", "芳", "娜", "敏", "静", "磊", "洋", "艳", "勇", "杰", "娟", "涛", "超", "明", "红", "霞", "飞", "鹏", "华", "平", "宇", "琪", "萱", "豪", "林"]
    
    majors = ["人工智能", "数据科学", "计算机科学与技术", "化学", "物理学", "统计学"]
    
    data = []
    
    for i in range(num_records):
        student_id = f"2026{str(i).zfill(4)}"
        
        name = random.choice(last_names) + random.choice(middle_names) + random.choice(first_names)
        
        major = random.choice(majors)
        
        # 决定该名学生的整体风险等级分布
        # 80% 安全样本，15% 中风险样本，5% 高危样本（用于触发 final_alert = True）
        risk_level = random.choices(["safe", "medium", "high"], weights=[0.80, 0.15, 0.05], k=1)[0]
        
        if risk_level == "safe":
            # 学业安全：GPA高，无挂科
            gpa = round(random.uniform(3.0, 4.3), 2)
            failed_courses = 0
            # 财务安全：月生活费充裕，无大额欠款
            monthly_living_expenses = random.randint(2000, 5000)
            has_heavy_debt = False
            # 心理安全：压力指数低 (0-100)，睡眠质量好 (1-10)
            stress_score = random.randint(10, 40)
            sleep_quality = random.randint(7, 10)
            
        elif risk_level == "medium":
            gpa = round(random.uniform(2.0, 3.2), 2)
            failed_courses = random.randint(0, 2)
            monthly_living_expenses = random.randint(1000, 2500)
            has_heavy_debt = random.choice([True, False])
            stress_score = random.randint(40, 70)
            sleep_quality = random.randint(5, 7)
            
        else: # "high" 风险样本
            # 复合型高危，用于测试同态加权求和后是否能突破 75 分预警线
            gpa = round(random.uniform(1.0, 2.0), 2)
            failed_courses = random.randint(3, 6)
            monthly_living_expenses = random.randint(500, 1200) # 经济窘迫
            has_heavy_debt = True
            stress_score = random.randint(75, 95) # 极度焦虑
            sleep_quality = random.randint(2, 4)  # 严重失眠

        student = {
            "student_id": student_id,
            "raw_data": {
                "name": name,
                "major": major,
                "academic_data": {
                    "gpa": gpa,
                    "failed_courses": failed_courses
                },
                "financial_data": {
                    "monthly_living_expenses": monthly_living_expenses,
                    "has_heavy_debt": has_heavy_debt
                },
                "psychological_data": {
                    "stress_index": stress_score,
                    "sleep_quality_score": sleep_quality
                }
            }
        }
        
        data.append(student)

    # 写入本地 JSON 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"✅ 成功生成 {num_records} 条带有风险梯度分布的测试数据，已保存至 {output_file}")
    print("💡 提示：其中约 5% 为高危复合样本，请重点验证系统对这些样本的解密预警准确性。")

if __name__ == "__main__":
    generate_crisis_warning_data(num_records=50, output_file="crisis_mock_data.json")