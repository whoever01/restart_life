"""
这个文件负责生成和管理角色的基础属性系统。主要功能包括：

1. 定义基础属性：
   - 颜值、智力、体质、家境四个基本属性
   
2. 随机生成角色属性：
   - 从15点属性点中随机分配到颜值、智力、体质三个属性上
   - 每个属性最高不超过20点
   
3. 城市和家境系统：
   - 随机选择出生城市
   - 根据城市的经济情况计算角色的家境值
   
4. 天赋系统整合：
   - 从天赋池中随机选择3个天赋
   - 应用天赋效果来调整基础属性值

主要通过generate_random_attributes_and_city()函数来生成一个完整的角色属性组合。
"""


import random
from app.models.talents import generate_random_talents
from app.utils.data_loader import load_city_data

# 初始属性
attributes = {
    "颜值": 0,
    "智力": 0,
    "体质": 0,
    "家境": 0
}

def generate_random_attributes_and_city(city_data):
    available_points = 15
    attributes_copy = attributes.copy()

    # 随机分配属性点
    while available_points > 0:
        random_attr = random.choice(['颜值', '智力', '体质'])
        if attributes_copy[random_attr] < 20:
            attributes_copy[random_attr] += 1
            available_points -= 1

    # 选择天赋
    selected_talents, selected_talent_objects = generate_random_talents()
    
    # 选择城市和计算家境
    city = random.choice(city_data)
    attributes_copy['家境'] = calculate_wealth(city)

    # 应用天赋效果
    for talent in selected_talent_objects:
        talent_effect = talent["effect"]
        for key, value in talent_effect.items():
            attributes_copy[key] += value

    return attributes_copy, selected_talents, city['city']

def calculate_wealth(city):
    rand_value = random.random()
    wealth = 0
    
    if rand_value < city['wealthy_chance']:
        wealth = 5
    elif rand_value < city['wealthy_chance'] + city['poor_chance']:
        wealth = -3
    elif rand_value < city['wealthy_chance'] + city['poor_chance'] + city['normal_chance']:
        wealth = 0
    elif rand_value < city['wealthy_chance'] + city['poor_chance'] + city['normal_chance'] + city['very_poor_chance']:
        wealth = -5
    else:
        wealth = 10
        
    return wealth 