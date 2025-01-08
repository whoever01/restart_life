from flask import jsonify, current_app
import random

@bp.route('/random_allocate')
def random_allocate():
    # 根据配置决定使用哪种天赋生成方式
    if current_app.config['USE_AI_TALENTS']:
        return generate_ai_talents()
    else:
        return generate_local_talents()

def generate_local_talents():
    # 预定义的天赋列表
    talents = [
        "体质满值",
        "平平无奇",
        "家境满值",
        "天生丽质",
        "过目不忘",
        "富贵命",
        "运动天才",
        "艺术天赋",
        "商业头脑"
    ]
    
    # 随机选择3-4个天赋
    num_talents = random.randint(3, 4)
    selected_talents = random.sample(talents, num_talents)
    
    # 生成随机属性值
    attributes = {
        "颜值": random.randint(0, 20),
        "智力": random.randint(0, 20),
        "体质": random.randint(0, 20),
        "家境": random.randint(0, 20)
    }
    
    # 应用天赋效果
    for talent in selected_talents:
        if talent == "体质满值":
            attributes["体质"] = 20
        elif talent == "家境满值":
            attributes["家境"] = 20
        elif talent == "天生丽质":
            attributes["颜值"] = min(20, attributes["颜值"] + 5)
        # ... 其他天赋效果
    
    return jsonify({
        "attributes": attributes,
        "talents": selected_talents,
        "city": random.choice(["北京", "上海", "广州", "深圳"])
    })

def generate_ai_talents():
    try:
        response = coze_api.get_random_talents()
        # 如果没有获取到天赋，使用本地生成
        if not response:
            logger.warning("No talents received from AI, falling back to local generation")
            return generate_local_talents()
        
        # 生成随机属性值
        attributes = {
            "颜值": random.randint(0, 20),
            "智力": random.randint(0, 20),
            "体质": random.randint(0, 20),
            "家境": random.randint(0, 20)
        }
        
        # 处理每个天赋对属性的影响
        for talent in response:
            try:
                # 提取天赋效果
                effects = {}
                if '（' in talent and '）' in talent:
                    talent_name = talent.split('（')[0]
                    effect_str = talent.split('（')[1].rstrip('）')
                    
                    # 处理多个效果
                    effects_list = effect_str.split('，')
                    for effect in effects_list:
                        # 分别处理属性和数值
                        for attr in ["颜值", "智力", "体质", "家境"]:
                            if attr in effect:
                                # 提取数值（包括正负号）
                                value_str = effect.replace(attr, '').strip()
                                try:
                                    # 直接计算带符号的数值
                                    value = int(value_str)
                                    effects[attr] = value
                                except ValueError:
                                    logger.warning(f"无法解析属性值: {value_str}")
                    
                    # 应用效果到属性值
                    for attr, value in effects.items():
                        if attr in attributes:
                            attributes[attr] = max(0, min(20, attributes[attr] + value))
            except Exception as e:
                logger.error(f"Error processing talent {talent}: {e}")
                continue
        
        # 确保所有属性值在有效范围内
        for key in attributes:
            attributes[key] = max(0, min(20, attributes[key]))
        
        return jsonify({
            "attributes": attributes,
            "talents": response,
            "city": random.choice(["北京", "上海", "广州", "深圳"])
        })
            
    except Exception as e:
        logger.error(f"AI talent generation failed: {e}")
        # 如果 AI 生成失败，回退到本地生成
        return generate_local_talents() 