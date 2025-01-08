"""
这个文件负责生成和管理角色的天赋系统。主要功能包括：

1. 天赋数据加载：
   - 从外部数据文件中加载所有可用的天赋信息
   - 每个天赋包含名称和对应的属性效果

2. 随机天赋生成：
   - 从天赋池中随机选择3个天赋
   - 返回天赋名称列表和完整的天赋对象列表

该模块与属性系统紧密配合，通过天赋效果来调整角色的基础属性值。
"""

import random
from app.utils.data_loader import load_talent_data

# 使用data_loader加载天赋数据
talent_pool = load_talent_data()

def generate_random_talents():
    selected_talents = random.sample(talent_pool, 3)
    return [talent["name"] for talent in selected_talents], selected_talents 