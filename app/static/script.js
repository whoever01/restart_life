function showTab(tabId) {
  const views = document.querySelectorAll('.view');
  views.forEach(view => {
    view.style.display = 'none';
  });
  
  const targetView = document.getElementById(tabId + '-view');
  targetView.style.display = 'flex';
  
  const tabs = document.querySelectorAll('.tab-button');
  tabs.forEach(tab => {
    tab.classList.remove('active');
  });
  
  const activeTab = document.querySelector(`.tab-button[data-tab="${tabId}"]`);
  activeTab.classList.add('active');

  if (tabId === 'events') {
    initScrollbar();
  }
  
  if (tabId === 'social') {
    initChatList();
  }
}

async function nextYear() {
  try {
    const currentYear = parseInt(document.getElementById('current-year').textContent);
    const nextYear = currentYear + 1;
    
    // 更新所有显示年份的地方
    document.querySelectorAll('#current-year').forEach(el => {
      el.textContent = nextYear;
    });
    
    // 将之前的事件卡片折叠
    const oldEvents = document.querySelectorAll('.event-item');
    oldEvents.forEach(event => {
      const detail = event.querySelector('.event-detail');
      event.classList.add('collapsed');
      detail.style.display = 'none';
    });
    
    // 从服务器获取新事件
    const response = await fetch('/get_events', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        context: {
          ...gameData,
          // 确保包含角色相关信息
          character: gameData.character || '',
          characters: Array.isArray(gameData.characters) ? gameData.characters : (gameData.characters || '').split(',').filter(Boolean),
          // 其他必要的参数...
        } 
      })
    });
    const data = await response.json();
    
    if (data.events && data.events.length > 0) {
      const eventList = document.getElementById('event-list');
      data.events.forEach(event => {
        const eventItem = document.createElement('div');
        eventItem.className = 'event-item';
        
        eventItem.innerHTML = `
          <div class="event-header">
            <div class="event-brief">
              <span class="event-age">${event.age || 0}岁</span>
              <span class="brief-content">${event.briefDescription || ''}</span>
            </div>
          </div>
          <div class="event-detail" style="display: block;">
            <div class="event-content">${event.content}</div>
            ${event.effects ? `<div class="event-effects">
              <div class="effects-title">事件影响：</div>
              <div class="effects-content">${formatEffects(event.effects)}</div>
            </div>` : ''}
          </div>
        `;
        
        // 修改点击事件处理
        const header = eventItem.querySelector('.event-header');
        const detail = eventItem.querySelector('.event-detail');
        
        header.addEventListener('click', function() {
          if (eventItem.classList.contains('collapsed')) {
            eventItem.classList.remove('collapsed');
            detail.style.display = 'block';
          } else {
            eventItem.classList.add('collapsed');
            detail.style.display = 'none';
          }
        });
        
        eventList.appendChild(eventItem);
      });
      
      // 自动滚动到新添加的事件
      setTimeout(() => {
        eventList.scrollTo({
          top: eventList.scrollHeight,
          behavior: 'smooth'
        });
      }, 100);
    }
  } catch (error) {
    console.error('生成事件失败:', error);
    console.error('错误详情:', { gameData, currentAge, currentYear });
    alert('获取事件失败，请刷新页面重试');
    button.disabled = false;
  }
}

function showChatWindow(contact) {
  const chatWindow = document.getElementById('chat-window');
  const chatContactName = document.getElementById('chat-contact-name');
  const chatMessages = document.getElementById('chat-messages');
  
  chatContactName.textContent = contact.name;
  chatMessages.innerHTML = '';
  
  // 按年份对消息进行分组并显示
  const messagesByYear = {};
  contact.messages.forEach(msg => {
    const year = msg.year || currentYear;
    if (!messagesByYear[year]) {
      messagesByYear[year] = [];
    }
    messagesByYear[year].push(msg);
  });
  
  Object.keys(messagesByYear).sort().forEach(year => {
    // 添加年份分隔线
    const yearDivider = document.createElement('div');
    yearDivider.className = 'year-divider';
    yearDivider.innerHTML = `
      <span class="year-text">${year}</span>
      <div class="divider-line"></div>
    `;
    chatMessages.appendChild(yearDivider);
    
    // 显示该年份的消息
    messagesByYear[year].forEach(msg => {
      const messageDiv = document.createElement('div');
      messageDiv.className = `message ${msg.from}`;
      messageDiv.innerHTML = `
        <div class="message-content">
          <p>${msg.text}</p>
        </div>
      `;
      chatMessages.appendChild(messageDiv);
    });
  });
  
  // 清除未读消息计数
  contact.unread = 0;
  
  // 显示聊天窗口
  chatWindow.style.display = 'flex';
  
  // 自动滚动到底部
  chatMessages.scrollTop = chatMessages.scrollHeight;
  
  // 刷新联系人列表以更新未读计数显示
  initChatList();
}

function sendMessage() {
  const chatInput = document.getElementById('chat-input');
  const message = chatInput.value.trim();
  if (message) {
    const chatMessages = document.getElementById('chat-messages');
    const year = document.getElementById('current-year').textContent;
    
    // 获取当前聊天的联系人名称
    const contactName = document.getElementById('chat-contact-name').textContent;
    const currentContact = contacts.find(contact => contact.name === contactName);
    
    if (currentContact) {
      currentContact.messages.push({
        text: message,
        year: year,
        from: 'self'
      });
    }
    
    // 创建新消息元素
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message self';
    messageDiv.innerHTML = `
      <div class="message-content">
        <p>${message}</p>
      </div>
    `;
    chatMessages.appendChild(messageDiv);
    
    // 清空输入框
    chatInput.value = '';
    
    // 自动滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // 模拟对方回复
    setTimeout(() => {
      const replyText = '好的，我知道了';
      // 保存对方的回复
      if (currentContact) {
        currentContact.messages.push({
          text: replyText,
          year: year,
          from: 'other'
        });
        // 更新联系人列表中显示的最新消息
        currentContact.message = replyText;
      }
      
      const replyDiv = document.createElement('div');
      replyDiv.className = 'message other';
      replyDiv.innerHTML = `
        <div class="message-content">
          <p>${replyText}</p>
        </div>
      `;
      chatMessages.appendChild(replyDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 1000);
  }
}

function logChatClick(contactName) {
  console.log(`点击了聊天项：${contactName}`);
  showChatWindow(contactName);
}

// 修改联系人数据结构，确保包含未读消息计数
const contacts = [
  {
    name: '爸爸',
    message: '欢迎来到这个世界，我的宝贝！',
    unread: 1,
    messages: [
      { 
        text: '欢迎来到这个世界，我的宝贝！',
        year: '2025',
        from: 'other'
      }
    ]
  },
  {
    name: '妈妈',
    message: '妈妈爱你，我的小天使！',
    unread: 1,
    messages: [
      {
        text: '妈妈爱你，我的小天使！',
        year: '2025',
        from: 'other'
      }
    ]
  }
];

// 修改初始化聊天列表函数
function initChatList() {
  const chatList = document.querySelector('#social-view .chat-list');
  if (!chatList) return;
  
  chatList.innerHTML = '';

  contacts.forEach(contact => {
    const chatItem = document.createElement('div');
    chatItem.className = 'chat-item';
    chatItem.innerHTML = `
      <div class="avatar">${contact.name.charAt(0)}</div>
      <div class="chat-details">
        <div class="chat-header">
          <p class="contact-name">${contact.name}</p>
          ${contact.unread ? `<span class="unread-badge">${contact.unread}</span>` : ''}
        </div>
        <div class="message-row">
          <p class="message-preview">${contact.message}</p>
        </div>
      </div>
    `;
    chatItem.onclick = () => showChatWindow(contact);
    chatList.appendChild(chatItem);
  });
}

// 添加关闭聊天窗口函数
function closeChat() {
  const chatWindow = document.getElementById('chat-window');
  const socialView = document.getElementById('social-view');
  
  chatWindow.style.display = 'none';
  socialView.style.display = 'block';
  
  // 刷新联系人列表以更新未读消息状态
  initChatList();
}

// 在适当的地方添加更新回合数的函数
function updateRound(roundNumber) {
  document.getElementById('current-round').textContent = roundNumber;
}

// 添加滚动到顶部和底部的辅助函数
function scrollToTop() {
  const eventList = document.getElementById('event-list');
  eventList.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
}

function scrollToBottom() {
  const eventList = document.getElementById('event-list');
  eventList.scrollTo({
    top: eventList.scrollHeight,
    behavior: 'smooth'
  });
}

// 修改滚动条初始化函数
function initScrollbar() {
  const eventList = document.getElementById('event-list');
  const scrollThumb = document.querySelector('.scroll-thumb');
  const scrollTrack = document.querySelector('.scroll-track');
  
  if (!eventList || !scrollThumb || !scrollTrack) return;

  function updateScrollThumb() {
    const scrollPercentage = eventList.scrollTop / (eventList.scrollHeight - eventList.clientHeight);
    const thumbHeight = Math.max(40, (eventList.clientHeight / eventList.scrollHeight) * scrollTrack.clientHeight);
    const thumbTop = scrollPercentage * (scrollTrack.clientHeight - thumbHeight);
    
    scrollThumb.style.height = `${thumbHeight}px`;
    scrollThumb.style.top = `${thumbTop}px`;
  }

  // 移除旧的事件监听器
  eventList.removeEventListener('scroll', updateScrollThumb);
  
  // 添加新的事件监听器
  eventList.addEventListener('scroll', updateScrollThumb);
  
  // 初始化滚动条位置
  updateScrollThumb();
}

// 添加处理新消息的函数
function handleNewMessages(messages) {
  if (!messages || !messages.length) return;
  
  messages.forEach(message => {
    if (message.fromCharacter) {
      let contact = contacts.find(c => c.name === message.fromCharacter);
      if (!contact) {
        contact = {
          name: message.fromCharacter,
          messages: [],
          unread: 0
        };
        contacts.push(contact);
      }
      
      if (message.messageChain) {
        message.messageChain.forEach(msg => {
          contact.messages.push({
            text: msg.text,
            year: currentYear,
            from: 'other'
          });
          // 增加未读消息计数
          contact.unread++;
        });
        
        // 更新最新消息预览
        contact.message = message.messageChain[message.messageChain.length - 1].text;
      }
    }
  });
  
  // 刷新联系人列表
  initChatList();
}

// 添加相关的 CSS 样式
const chatStyle = document.createElement('style');
chatStyle.textContent = `
  .unread-badge {
    background-color: #ff3b30;
    color: white;
    border-radius: 50%;
    padding: 2px 6px;
    font-size: 12px;
    position: absolute;
    right: 10px;
    top: 10px;
  }
  
  .chat-item {
    position: relative;
  }
`;
document.head.appendChild(chatStyle);

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    try {
        // 安全地获取和设置元素
        const safeSetText = (id, value) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            } else {
                console.log(`Element with id '${id}' not found`);
            }
        };

        // 获取游戏数据
        let gameData;
        try {
            gameData = JSON.parse(localStorage.getItem('gameData')) || {};
        } catch (e) {
            console.error('解析游戏数据失败:', e);
            gameData = {};
        }
        
        // 更新基本信息
        safeSetText('player-name', gameData.name || '');
        safeSetText('player-gender', gameData.sex || '');
        
        // 更新属性值
        safeSetText('intelligence', String(gameData.attributes?.智力 || 10));
        safeSetText('physical', String(gameData.attributes?.体质 || 10));
        safeSetText('appearance', String(gameData.attributes?.颜值 || 10));
        safeSetText('wealth', String(gameData.attributes?.家境 || 10));
        
        // 初始化状态栏
        safeSetText('current-year', '2025');
        
        if (gameData.city || gameData.talents) {
            console.log('玩家城市:', gameData.city);
            console.log('玩家天赋:', gameData.talents);
        }

        // 初始化组件
        initScrollbar();
        initChatList();
    } catch (error) {
        console.error('初始化过程中出错:', error);
    }
});

// 添加 CSS 样式
const style = document.createElement('style');
style.textContent = `
    /* 玩家信息卡片样式 */
    .player-info {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        color: #333;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 15px;
    }

    .info-column {
        position: relative;
        padding: 10px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .info-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        background: white;
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid #eee;
    }

    .info-item:last-child {
        margin-bottom: 0;
    }

    .info-icon {
        font-size: 18px;
        color: #666;
    }

    .info-value {
        font-size: 16px;
        font-weight: 500;
        color: #333;
    }

    .stat-info {
        flex: 1;
    }

    .stat-label {
        font-size: 14px;
        color: #666;
        margin-bottom: 4px;
    }

    .stat-value {
        font-size: 18px;
        font-weight: 500;
        color: #333;
    }

    /* 事件卡片样式 */
    .event-item {
        margin-bottom: 15px;
        border-radius: 8px;
        overflow: hidden;
        background: #fff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .event-header {
        padding: 12px 16px;
        background: #e8f4f8;
        cursor: pointer;
    }

    .event-brief {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .event-age {
        font-weight: bold;
        color: #2c3e50;
        padding: 2px 8px;
        background: #fff;
        border-radius: 4px;
    }

    .brief-content {
        color: #2c3e50;
        flex: 1;
    }

    .event-detail {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 16px;
        background: #fff;
    }

    .event-content {
        color: #2c3e50;
        line-height: 1.6;
        padding: 8px 0;
        border-bottom: 1px solid #eee;
    }

    .event-effects {
        margin-top: 8px;
        padding: 8px 12px;
        background: #f8f9fa;
        border-radius: 6px;
    }

    .effects-title {
        color: #666;
        font-size: 14px;
        margin-bottom: 4px;
    }

    .effects-content {
        color: #2c3e50;
        font-size: 14px;
    }

    .event-item.collapsed .event-detail {
        display: none;
    }
`;
document.head.appendChild(style);

// 添加格式化效果的函数
function formatEffects(effects) {
  const effectTexts = [];
  for (const [key, value] of Object.entries(effects)) {
    let effectText = '';
    const sign = value > 0 ? '+' : '';
    switch(key) {
      case 'intelligence':
        effectText = `智力${sign}${value}`;
        break;
      case 'physical':
        effectText = `体质${sign}${value}`;
        break;
      case 'appearance':
        effectText = `颜值${sign}${value}`;
        break;
      case 'wealth':
        effectText = `家境${sign}${value}`;
        break;
    }
    if (effectText) {
      effectTexts.push(effectText);
    }
  }
  return effectTexts.join('  ');
}