"""
这个文件是项目的数据加载工具模块，主要负责：

1. 数据文件读取：
   - 从CSV文件中读取城市和天赋数据
   - 处理文件编码和格式转换
   
2. 数据格式化：
   - 将CSV数据转换为程序可用的字典格式
   - 处理特殊字段（如天赋效果的字符串转字典）
   
3. 环境配置：
   - 使用环境变量来配置数据文件路径
   - 提供默认路径作为备选方案

主要函数：
- load_city_data(): 加载城市数据，包含各种经济水平的概率
- load_talent_data(): 加载天赋数据，包含天赋名称和属性效果
"""

import csv
import ast
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def load_city_data():
    """
    加载城市数据文件，读取每个城市的经济概率分布。
    
    返回值：
    list: 包含城市信息的字典列表，每个字典包含：
        - city: 城市名称
        - wealthy_chance: 出现土豪的概率
        - poor_chance: 出现穷人的概率
        - normal_chance: 普通人的概率
        - very_poor_chance: 特别穷的概率
        - very_wealthy_chance: 特别富有的概率
    """
    city_data = []
    city_data_path = os.getenv('CITY_DATA_PATH', 'app/data/city_data.csv')
    
    with open(city_data_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            city_data.append({
                'city': row['城市名称'],
                'wealthy_chance': float(row['出现土豪几率']),
                'poor_chance': float(row['出现穷鬼几率']),
                'normal_chance': float(row['正常几率']),
                'very_poor_chance': float(row['特别穷几率']),
                'very_wealthy_chance': float(row['特别富贵的几率'])
            })
    return city_data

def load_talent_data():
    """
    加载天赋数据文件，读取天赋名称和对应效果。
    
    返回值：
    list: 包含天赋信息的字典列表，每个字典包含：
        - name: 天赋名称
        - effect: 天赋效果（字典格式，表示对各属性的影响）
    """
    talents = []
    talents_data_path = os.getenv('TALENTS_DATA_PATH', 'app/data/talents.csv')
    
    with open(talents_data_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['name']
            effect = ast.literal_eval(row['effect'])  # 将字符串格式的效果转换为字典
            talents.append({"name": name, "effect": effect})
    return talents 