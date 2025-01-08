"""
这个模块负责维护parameters参数
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取配置，如果没有则使用默认值
INITIAL_AGE = int(os.getenv('GAME_INITIAL_AGE', 14))
INITIAL_STATS = int(os.getenv('GAME_INITIAL_STATS', 10))
DEFAULT_CITY = os.getenv('GAME_DEFAULT_CITY', '北京')
MAX_HISTORY = int(os.getenv('GAME_MAX_HISTORY', 30))
MAX_STATS = int(os.getenv('GAME_MAX_STATS', 20))

class GameState:
    def __init__(self):
        # 基础属性
        self.name = "新玩家"
        self.sex = "男"
        self.age = str(INITIAL_AGE)
        self.appearance = str(INITIAL_STATS)
        self.intelligence = str(INITIAL_STATS)
        self.physical = str(INITIAL_STATS)
        self.wealth = str(INITIAL_STATS)
        self.city = DEFAULT_CITY
        
        # 游戏进程相关
        self.character = ""  # 当前对话的角色
        self.characters = set()  # 已解锁的角色集合
        self.talents = []    # 天赋列表
        self.events = []     # 事件历史
        self.messages = []   # 消息历史
        
        self.max_history = MAX_HISTORY  # 历史记录最大保留数量
        self.max_stats = MAX_STATS      # 属性最大值

    def update_state(self, **kwargs):
        """更新游戏状态"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == 'character':
                    # 当前对话角色
                    self.character = str(value) if value else ""
                elif key == 'characters':
                    # 处理角色列表
                    if isinstance(value, str):
                        # 如果是字符串，按逗号分割并过滤空值
                        new_chars = {x.strip() for x in value.split(',') if x.strip()}
                        self.characters.update(new_chars)
                    elif isinstance(value, (list, set)):
                        # 如果是列表或集合，直接更新
                        self.characters.update(value)
                    elif isinstance(value, dict):
                        # 如果是字典（来自角色效果），提取角色名称
                        if 'name' in value:
                            self.characters.add(value['name'])
                elif key == 'talents' and isinstance(value, list):
                    self.talents = value
                elif key == 'events' and isinstance(value, str):
                    self.events.append(value)
                    if len(self.events) > self.max_history:
                        self.events = self.events[-self.max_history:]
                elif key == 'messages' and isinstance(value, str):
                    self.messages.append(value)
                    if len(self.messages) > self.max_history:
                        self.messages = self.messages[-self.max_history:]
                elif key in ['appearance', 'intelligence', 'physical', 'wealth']:
                    # 确保属性值在合理范围内
                    try:
                        value = max(0, min(self.max_stats, int(value)))
                        setattr(self, key, str(value))
                    except ValueError:
                        pass  # 如果转换失败，保持原值不变
                else:
                    setattr(self, key, value)

    def add_event(self, event):
        """添加新事件到历史记录"""
        if not event:
            return
            
        # 移除可能存在的年龄前缀
        age_prefix = f"{self.age}岁："
        if event.startswith(age_prefix):
            event = event[len(age_prefix):]
        
        # 替换事件内容中的年龄引用
        event = event.replace(f"{int(self.age)-1} 岁", f"{self.age}岁")
        event = event.replace(f"{int(self.age)-1}岁", f"{self.age}岁")
        
        # 添加到事件列表
        self.events.append(event)
        if len(self.events) > self.max_history:
            self.events = self.events[-self.max_history:]

    def add_message(self, message):
        """添加新消息到历史记录"""
        if not message:
            return
            
        # 统一消息格式：{年龄}岁 {发送者}: [{内容}] [{时间}]
        if not message.startswith(f"{self.age}岁"):
            if '[' in message and ']' in message:
                # 如果已有消息格式，只添加年龄
                message = f"{self.age}岁 {message}"
            else:
                # 完全格式化消息
                message = f"{self.age}岁 {message.split(':')[0]}: [{message.split(':')[1].strip()}] [当天]"
            
        self.messages.append(message)
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

    def add_character(self, character_name, relationship=None):
        """添加新角色"""
        if character_name:
            self.characters.add(character_name)

    def remove_character(self, character_name):
        """移除角色（禁用）"""
        if character_name in self.characters:
            self.characters.remove(character_name)

    def get_parameters(self):
        """获取当前游戏状态的参数"""
        event_history = []
        message_history = []
        
        # 添加事件历史，过滤掉空事件
        for event in self.events:
            if event.strip():  # 只添加非空事件
                # 确保年龄引用正确
                event_text = event
                if not event_text.startswith(f"{self.age}岁："):
                    event_text = f"{self.age}岁：{event_text}"
                event_history.append(event_text)
        
        # 添加消息历史，确保包含时间和年龄信息
        for message in self.messages:
            if message.strip():  # 只添加非空消息
                # 确保消息格式：{年龄}岁 {发送者}: [{内容}] [{时间}]
                parts = message.split(' ', 1)  # 分割年龄和其他部分
                if not parts[0].endswith('岁'):
                    message = f"{self.age}岁 {message}"
                message_history.append(message)
        
        return {
            "name": self.name,
            "sex": self.sex,
            "age": self.age,
            "appearance": self.appearance,
            "intelligence": self.intelligence,
            "physical": self.physical,
            "wealth": self.wealth,
            "city": self.city,
            "character": self.character,
            "characters": ",".join(sorted(self.characters)) if self.characters else "",
            "talents": self.talents,
            "events": "；".join(filter(None, event_history)) if event_history else "",  # 过滤空字符串
            "messages": "；".join(filter(None, message_history)) if message_history else ""  # 过滤空字符串
        }

    def reset(self):
        """重置游戏状态"""
        self.__init__() 