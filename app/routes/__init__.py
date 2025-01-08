from flask import Blueprint

main_bp = Blueprint('main', __name__)

from app.routes import main  # 导入路由处理模块 