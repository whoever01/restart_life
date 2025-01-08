from dotenv import load_dotenv
import os
from app import create_app
import logging

# 首先加载环境变量，这样后续的代码都能使用
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 开发者设置
USE_AI_TALENTS = os.getenv('USE_AI_TALENTS', 'false').lower() == 'true'

app = create_app()

# 将设置注入到应用配置中
app.config['USE_AI_TALENTS'] = USE_AI_TALENTS

if __name__ == '__main__':
    logger.info("Starting the application...")
    logger.info(f"Using AI talents: {USE_AI_TALENTS}")
    # 从环境变量获取调试模式设置
    debug_mode = os.getenv('DEBUG', 'true').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1', port=5000)
    logger.info("Application started successfully!") 