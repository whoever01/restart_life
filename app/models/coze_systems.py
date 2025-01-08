"""
这个模块负责处理来自 Coze 平台的各个系统数据，主要功能包括：

1. 天赋系统：
   - 解析天赋数据
   - 计算天赋效果

2. 事件系统：
   - 处理事件内容
   - 计算事件效果
   - 管理角色关系

3. 微信系统：
   - 处理消息链
   - 管理消息效果
   - 处理角色状态
"""

from app.utils.coze_api import CozeAPI
import logging

logger = logging.getLogger(__name__)

class CozeSystems:
    def __init__(self):
        self.api = CozeAPI()
        
    def process_talents(self):
        """处理天赋系统返回的数据"""
        talents = self.api.get_random_talents()
        # 解析天赋效果，转换为属性变化
        processed_talents = []
        for talent in talents:
            name, effect = self._parse_talent_string(talent)
            processed_talents.append({
                "name": name,
                "effect": effect
            })
        return processed_talents
    
    def process_event(self, context=None):
        """
        处理事件系统返回的数据
        
        参数：
        context: dict, 包含角色状态和历史信息
        """
        if not context:
            return []
        
        # 确保属性值正确转换
        if 'attributes' in context:
            attrs = context['attributes']
            context.update({
                'appearance': attrs.get('颜值', ''),
                'intelligence': attrs.get('智力', ''),
                'physical': attrs.get('体质', ''),
                'wealth': attrs.get('家境', '')
            })
        
        events = self.api.generate_event(context)
        return events
    
    def process_messages(self, context=None):
        """
        处理微信系统返回的数据
        
        参数：
        context: dict, 包含角色状态和历史消息
        """
        if not context:
            return []
        
        # 确保属性值正确转换
        if 'attributes' in context:
            attrs = context['attributes']
            context.update({
                'appearance': attrs.get('颜值', ''),
                'intelligence': attrs.get('智力', ''),
                'physical': attrs.get('体质', ''),
                'wealth': attrs.get('家境', '')
            })
        
        messages = self.api.get_wechat_messages(context)
        if messages:
            logger.info(f"Generated messages: {messages}")
        return messages
    
    def _parse_talent_string(self, talent_str):
        """解析天赋字符串，提取名称和效果"""
        # 示例："明眸皓齿（颜值+3）" -> ("明眸皓齿", {"颜值": 3})
        name = talent_str.split('（')[0]
        effect_str = talent_str.split('（')[1].rstrip('）')
        
        # 解析效果
        effect = {}
        if '+' in effect_str:
            attr, value = effect_str.split('+')
            effect[attr] = int(value)
        elif '-' in effect_str:
            attr, value = effect_str.split('-')
            effect[attr] = -int(value)
            
        return name, effect 