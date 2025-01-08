"""
这个文件是项目的配置文件,主要负责:

1. 环境变量管理:
   - 使用python-dotenv加载.env文件中的环境变量
   - 提供默认值作为fallback选项

2. 应用配置:
   - 设置Flask应用的调试模式(DEBUG)
   - 配置数据文件的路径(CSV文件位置)
   - 其他全局配置项

3. 配置分离:
   - 将配置从代码中分离出来,便于管理和修改
   - 支持不同环境(开发、测试、生产)使用不同配置

使用方式:
1. 在.env文件中设置环境变量
2. 通过Config类访问配置项
3. 在需要时可以继承Config类创建不同环境的配置类
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = True
    
    # 数据文件路径配置
    CITY_DATA_PATH = os.getenv('CITY_DATA_PATH', 'app/data/city_data.csv')
    TALENTS_DATA_PATH = os.getenv('TALENTS_DATA_PATH', 'app/data/talents.csv') 