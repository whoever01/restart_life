import csv
import random

# 假设这些是中国的一些地级市（此处仅为示例，实际城市数量要更多）
cities = [
    "北京", "上海", "广州", "深圳", "天津", "重庆", "成都", "杭州", "武汉", "南京", 
    "西安", "青岛", "大连", "沈阳", "郑州", "济南", "苏州", "合肥", "长沙", "厦门", 
    "哈尔滨", "昆明", "石家庄", "长春", "无锡", "佛山", "南昌", "烟台", "泉州", 
    "绍兴", "南宁", "福州", "唐山", "温州", "东莞", "临沂", "邯郸", "威海", "常州",
    "珠海", "温州", "珠海", "洛阳", "兰州", "赣州", "银川", "唐山", "桂林", "马鞍山"
]

# 贫富差距区间
# 假设一线和部分二线城市富裕，而其他城市则贫富差距较大
def assign_probabilities(city):
    if city in ["北京", "上海", "深圳", "广州", "杭州", "南京", "武汉"]:
        # 特别富贵的几率高
        return (0.35, 0.05, 0.40, 0.10, 0.10)  # 土豪、富贵、正常、特别穷、特别富贵的概率
    elif city in ["成都", "重庆", "青岛", "大连", "沈阳", "郑州"]:
        # 富贵几率较高
        return (0.25, 0.08, 0.45, 0.12, 0.10)
    elif city in ["福州", "长春", "哈尔滨", "昆明", "石家庄"]:
        # 中等城市，贫富差距较为明显
        return (0.18, 0.12, 0.50, 0.15, 0.05)
    else:
        # 其他较小城市，贫富差距较大
        return (0.10, 0.20, 0.50, 0.18, 0.02)

# 写入 CSV 文件
with open('china_cities_finance_all.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # 写入表头
    writer.writerow(["城市名称", "出现土豪几率", "出现穷鬼几率", "正常几率", "特别穷几率", "特别富贵的几率"])
    
    # 遍历所有城市并为其分配概率
    for city in cities:
        probabilities = assign_probabilities(city)
        writer.writerow([city] + list(probabilities))

print("CSV 文件已生成：china_cities_finance_all.csv")
