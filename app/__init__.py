from flask import Flask
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    """配置日志系统"""
    # 确保logs目录存在
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 配置应用日志
    app_logger = logging.getLogger('app')
    app_logger.setLevel(logging.DEBUG)
    app_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10
    )
    app_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    app_logger.addHandler(app_handler)
    
    # 配置API日志
    api_logger = logging.getLogger('api')
    api_logger.setLevel(logging.DEBUG)
    api_handler = RotatingFileHandler(
        'logs/api.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10
    )
    api_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))
    api_logger.addHandler(api_handler)

def create_app():
    # 设置日志
    setup_logging()
    logger = logging.getLogger('app')
    
    logger.info("Creating Flask application...")
    app = Flask(__name__,
        template_folder='templates',
        static_folder='static'
    )
    
    logger.info("Registering blueprints...")
    # 注册蓝图
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    logger.info("Application created successfully!")
    return app 