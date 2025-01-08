import logging
from flask import jsonify, request, render_template
from app.routes import main_bp
from app.models.attributes import generate_random_attributes_and_city
from app.utils.data_loader import load_city_data
from app.models.coze_systems import CozeSystems

coze_systems = CozeSystems()

@main_bp.route('/')
def index():
    cities = load_city_data()
    return render_template('index.html', cities=cities)

@main_bp.route('/random_allocate', methods=['GET'])
def random_allocate():
    try:
        cities = load_city_data()
        # 首先尝试使用 coze天赋系统
        try:
            if current_app.config['USE_AI_TALENTS']:
                coze_talents = coze_systems.process_talents()
                if coze_talents:
                    attributes_copy, _, city = generate_random_attributes_and_city(cities)
                    return jsonify({
                        "attributes": attributes_copy,
                        "talents": coze_talents,
                        "city": city
                    })
        except Exception as e:
            logger.warning(f"AI talent generation failed: {e}, falling back to local generation")
        
        # 如果 AI 生成失败或未启用，使用本地生成
        return generate_local_talents()
        
    except Exception as e:
        logging.error(f"Error in random_allocate: {str(e)}")
        # 如果出现任何错误，也使用本地生成
        return generate_local_talents()

def generate_local_talents():
    try:
        cities = load_city_data()
        attributes_copy, selected_talents, city = generate_random_attributes_and_city(cities)
        return jsonify({
            "attributes": attributes_copy,
            "talents": selected_talents,
            "city": city
        })
    except Exception as e:
        logging.error(f"Error in local talent generation: {str(e)}")
        # 返回最基础的默认值
        return jsonify({
            "attributes": {
                "颜值": 10,
                "智力": 10,
                "体质": 10,
                "家境": 10
            },
            "talents": ["平平无奇"],
            "city": "北京"
        })

@main_bp.route('/generate_event', methods=['POST'])
def generate_event():
    try:
        context = request.json.get('context', {})
        event_data = coze_systems.process_event(context)
        if not event_data:
            raise ValueError("No event data received")
        
        return jsonify(event_data)
    except Exception as e:
        logging.error(f"Error in generate_event: {str(e)}")
        return jsonify({"error": str(e)}), 500

@main_bp.route('/get_messages', methods=['POST'])
def get_messages():
    try:
        context = request.json.get('context', {})
        messages = coze_systems.process_messages(context)
        return jsonify({"messages": messages})
    except Exception as e:
        logging.error(f"Error in get_messages: {str(e)}")
        return jsonify({"error": str(e)}), 500

@main_bp.route('/start_new_life', methods=['POST'])
def start_new_life():
    selected_city = request.json.get('city')
    attributes_copy = request.json.get('attributes')
    talents = request.json.get('talents')
    
    return jsonify({
        "message": f"开始新人生，分配结果：{attributes_copy}, 城市: {selected_city}, 天赋: {', '.join(talents)}"
    })

@main_bp.route('/game')
def game():
    return render_template('game.html') 