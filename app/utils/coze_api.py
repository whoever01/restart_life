"""
这个模块负责与 Coze 平台的 API 交互，主要功能包括：

1. API 连接管理：
   - 初始化 Coze 客户端
   - 处理认证和基础配置

2. 系统调用接口：
   - 天赋系统 API
   - 事件系统 API
   - 微信系统 API

3. 响应数据处理：
   - 解析 API 返回的 JSON 数据
   - 转换为程序可用的数据结构
"""

import os
import json
import requests
import logging
from app.models.game_state import GameState  # 导入 GameState 类

# 获取API日志记录器
logger = logging.getLogger('api')

class CozeAPI:
    def __init__(self):
        self.token = os.getenv('COZE_API_TOKEN')
        self.base_url = "https://api.coze.cn"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # 从环境变量获取 workflow IDs
        self.workflow_ids = {
            'talent': os.getenv('COZE_TALENT_WORKFLOW_ID'),
            'event': os.getenv('COZE_EVENT_WORKFLOW_ID'),
            'wechat': os.getenv('COZE_WECHAT_WORKFLOW_ID')
        }
        
        # 验证所有必需的 workflow IDs 都存在
        missing_ids = [k for k, v in self.workflow_ids.items() if not v]
        if missing_ids:
            raise ValueError(f"Missing workflow IDs in environment variables: {missing_ids}")
            
        # 初始化游戏状态
        self.game_state = GameState()

    def _make_request(self, workflow_id, parameters):
        """发送请求到 Coze API"""
        url = 'https://api.coze.cn/v1/workflow/run'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        data = {
            'workflow_id': workflow_id,
            'parameters': parameters
        }
        
        logger.info(f"Making request to {url}")
        logger.debug(f"Request data: {json.dumps(data, ensure_ascii=False)}")
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            logger.info(f"Response status: {response.status_code}")
            logger.debug(f"Response content: {response.text}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            logger.error(f"Response content: {getattr(e.response, 'text', 'No response text')}")
            raise

    def get_random_talents(self):
        """获取随机天赋"""
        try:
            response = self._make_request(self.workflow_ids['talent'], self.game_state.get_parameters())
            if not response:
                logger.error("Empty response from API")
                return []
            
            # 尝试从响应中提取数据
            try:
                if isinstance(response, str):
                    # 如果响应是字符串，直接解析
                    data = json.loads(response)
                else:
                    # 如果响应是字典，获取 data 字段
                    data = response.get('data', '')
                    if isinstance(data, str):
                        data = json.loads(data)
                    
                # 提取 output 字段
                if isinstance(data, dict) and 'output' in data:
                    output = data['output']
                    # 如果 output 是字符串，需要再次解析
                    if isinstance(output, str):
                        talents = json.loads(output)
                    else:
                        talents = output
                        
                    logger.info(f"Successfully got talents: {talents}")
                    return talents
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
            except Exception as e:
                logger.error(f"Error processing response: {e}")
            
            # 如果处理失败，返回空列表
            return []
            
        except Exception as e:
            logger.error(f"Error processing talents: {str(e)}")
            raise

    def generate_event(self, context=None):
        """生成随机事件"""
        try:
            if context:
                # 确保角色信息正确处理
                if 'characterEffects' in context:
                    char_effects = context['characterEffects']
                    if char_effects.get('character'):
                        char_name = char_effects['character'].get('name', '')
                        if char_name:
                            # 更新角色列表
                            if not context.get('characters'):
                                context['characters'] = []
                            if char_name not in context['characters']:
                                context['characters'].append(char_name)
                
                self.game_state.update_state(**context)
            
            response = self._make_request(self.workflow_ids['event'], self.game_state.get_parameters())
            if not response:
                logger.error("Empty response from API")
                raise Exception("Empty response from API")
            
            # 尝试从响应中提取数据
            try:
                if isinstance(response, str):
                    data = json.loads(response)
                else:
                    data = response.get('data', '')
                    if isinstance(data, str):
                        data = json.loads(data)
                    
                # 提取 output 字段并解析
                if isinstance(data, dict) and 'output' in data:
                    output = data['output']
                    if isinstance(output, str):
                        event_data = json.loads(output)
                    else:
                        event_data = output
                    
                    if isinstance(event_data, dict) and 'events' in event_data:
                        events = event_data['events']
                        if events and len(events) > 0:
                            event = events[0]
                            
                            # 处理角色效果
                            if 'characterEffects' in event:
                                char_effects = event['characterEffects']
                                if char_effects.get('character'):
                                    char_name = char_effects['character'].get('name', '')
                                    if char_name:
                                        self.game_state.characters.add(char_name)
                            
                            # 记录事件内容
                            if 'content' in event:
                                self.game_state.add_event(event['content'])
                            
                            # 构建新的事件结构
                            result = {
                                'briefDescription': event.get('briefDescription', ''),  # 新增简短描述
                                'content': event.get('content', ''),  # 详细内容
                                'effects': event.get('effects', {}),  # 事件效果
                                'age': self.game_state.age,  # 添加年龄
                                'triggers': event.get('triggers', {})  # 保留triggers
                            }
                            
                            # 如果有角色效果，也添加到结果中
                            if 'characterEffects' in event:
                                result['characterEffects'] = event['characterEffects']
                            
                            return result
                            
                    logger.error(f"Invalid event data format: {data}")
                    raise Exception("Invalid event data format")
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                raise
            except Exception as e:
                logger.error(f"Error processing event data: {e}")
                raise
            
        except Exception as e:
            logger.error(f"Error generating event: {str(e)}")
            raise

    def get_wechat_messages(self, context=None):
        """获取微信消息"""
        try:
            if context:
                self.game_state.update_state(**context)
            response = self._make_request(self.workflow_ids['wechat'], self.game_state.get_parameters())
            if not response:
                logger.error("Empty response from API")
                return []
            
            # 尝试从响应中提取数据
            try:
                if isinstance(response, str):
                    data = json.loads(response)
                else:
                    data = response.get('data', '')
                    if isinstance(data, str):
                        data = json.loads(data)
                        
                # 提取 output 字段并解析
                if isinstance(data, dict) and 'output' in data:
                    output = data['output']
                    if isinstance(output, str):
                        messages_data = json.loads(output)
                    else:
                        messages_data = output
                        
                    if isinstance(messages_data, dict) and 'messages' in messages_data:
                        messages = messages_data['messages']
                        # 记录消息到游戏状态
                        for msg in messages:
                            if msg.get('messageChain'):
                                for chain_msg in msg['messageChain']:
                                    # 使用统一的消息格式
                                    formatted_message = (
                                        f"{self.game_state.age}岁 "
                                        f"{msg['fromCharacter']}: "
                                        f"[{chain_msg['text']}]"
                                    )
                                    self.game_state.add_message(formatted_message)
                        return messages
                        
                logger.error(f"Invalid message data format: {data}")
                return []
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return []
            except Exception as e:
                logger.error(f"Error processing message data: {e}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            return [] 