"""
ChatBot - Массовая рассылка в онлайн чаты v2.1 ИСПРАВЛЕННАЯ
ИСПРАВЛЕНИЯ: Улучшенная работа с iframe, контекстом и задержками
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import queue
from datetime import datetime
import json
import os
import sys
import glob
import requests
import zipfile
import shutil
import pandas as pd
import time
import logging
import random
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ============================================================================
# АНТИДЕТЕКТ - User Agent Rotator
# ============================================================================

class UserAgentRotator:
    """Ротация User-Agent для имитации разных пользователей"""
    
    USER_AGENTS = [
        # Windows Chrome (различные версии)
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        
        # Windows Firefox
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
        
        # Windows Edge
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        
        # MacOS Chrome
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        
        # MacOS Safari
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
        
        # MacOS Firefox
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
        
        # Linux Chrome
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        
        # Linux Firefox
        'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
        
        # Windows 11 Chrome
        'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        
        # Android Chrome (мобильные)
        'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
    ]
    
    def __init__(self):
        self.used_agents = deque(maxlen=5)  # Последние 5 использованных
    
    def get_random(self):
        """Получить случайный User-Agent (исключая недавно использованные)"""
        available = [ua for ua in self.USER_AGENTS if ua not in self.used_agents]
        
        if not available:
            available = self.USER_AGENTS
        
        agent = random.choice(available)
        self.used_agents.append(agent)
        
        return agent


# ============================================================================
# АНТИДЕТЕКТ - Менеджер
# ============================================================================

class AntidetectManager:
    """Управление всеми антидетект функциями"""
    
    def __init__(self, fast_mode=True):
        self.fast_mode = fast_mode
        self.ua_rotator = UserAgentRotator()
    
    def random_delay(self, min_sec=1, max_sec=3):
        """Случайная задержка между действиями"""
        if self.fast_mode:
            delay = random.uniform(min_sec * 0.7, max_sec * 0.7)  # ИСПРАВЛЕНО: было 0.5
        else:
            delay = random.uniform(min_sec, max_sec)
        
        time.sleep(delay)
    
    def human_typing(self, element, text, typing_speed='normal'):
        """Имитация человеческого ввода текста"""
        if typing_speed == 'fast' or self.fast_mode:
            # Быстрый ввод (для быстрого режима)
            element.send_keys(text)
        else:
            # Медленный человеческий ввод
            for i, char in enumerate(text):
                element.send_keys(char)
                
                # Базовая задержка
                base_delay = random.uniform(0.05, 0.15)
                
                # Иногда делаем паузы (как будто человек думает)
                if random.random() < 0.1:
                    base_delay += random.uniform(0.3, 0.8)
                
                # После пробела чуть быстрее
                if char == ' ':
                    base_delay *= 0.7
                
                # Перед заглавными буквами небольшая пауза
                if i < len(text) - 1 and text[i+1].isupper():
                    base_delay += random.uniform(0.1, 0.2)
                
                time.sleep(base_delay)
    
    def random_mouse_movement(self, driver, element):
        """Случайное движение мыши перед кликом"""
        try:
            actions = ActionChains(driver)
            
            # Случайное смещение от центра элемента
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            
            # Медленное движение к элементу
            actions.move_to_element_with_offset(element, offset_x, offset_y)
            actions.pause(random.uniform(0.1, 0.3))
            actions.perform()
            
        except Exception as e:
            pass  # Не критично если не получилось
    
    def random_scroll(self, driver):
        """Случайная прокрутка страницы (имитация чтения)"""
        try:
            # Прокрутка вниз
            scroll_distance = random.randint(300, 800)
            driver.execute_script(f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});")
            time.sleep(random.uniform(0.5, 1.5))
            
            # Иногда прокручиваем немного обратно
            if random.random() < 0.3:
                back_distance = scroll_distance // random.randint(2, 4)
                driver.execute_script(f"window.scrollBy({{top: -{back_distance}, behavior: 'smooth'}});")
                time.sleep(random.uniform(0.3, 0.7))
        except:
            pass
    
    def add_noise_to_fingerprint(self, driver):
        """Добавление шума в browser fingerprint"""
        try:
            # Защита от WebGL fingerprinting
            driver.execute_script("""
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter.apply(this, arguments);
                };
            """)
            
            # Защита от Canvas fingerprinting
            driver.execute_script("""
                const toBlob = HTMLCanvasElement.prototype.toBlob;
                const toDataURL = HTMLCanvasElement.prototype.toDataURL;
                const getImageData = CanvasRenderingContext2D.prototype.getImageData;
                
                var noisify = function(canvas, context) {
                    const shift = {
                        'r': Math.floor(Math.random() * 10) - 5,
                        'g': Math.floor(Math.random() * 10) - 5,
                        'b': Math.floor(Math.random() * 10) - 5,
                        'a': Math.floor(Math.random() * 10) - 5
                    };
                    
                    const width = canvas.width;
                    const height = canvas.height;
                    const imageData = getImageData.apply(context, [0, 0, width, height]);
                    
                    for (let i = 0; i < imageData.data.length; i += 4) {
                        imageData.data[i + 0] += shift.r;
                        imageData.data[i + 1] += shift.g;
                        imageData.data[i + 2] += shift.b;
                        imageData.data[i + 3] += shift.a;
                    }
                    
                    context.putImageData(imageData, 0, 0);
                };
            """)
            
            # Защита от Audio fingerprinting
            driver.execute_script("""
                const audioContext = AudioContext.prototype.constructor;
                AudioContext.prototype.constructor = function() {
                    const context = new audioContext(arguments);
                    const getChannelData = AudioBuffer.prototype.getChannelData;
                    AudioBuffer.prototype.getChannelData = function() {
                        const float32Array = getChannelData.apply(this, arguments);
                        for (let i = 0; i < float32Array.length; i++) {
                            float32Array[i] += Math.random() * 0.0000001;
                        }
                        return float32Array;
                    };
                    return context;
                };
            """)
            
        except Exception as e:
            pass  # Не критично


# ============================================================================
# ПРОКСИ МЕНЕДЖЕР
# ============================================================================

class ProxyManager:
    """Управление прокси-серверами с ротацией"""
    
    def __init__(self, proxy_file=None):
        self.proxies = []
        self.current_index = 0
        self.failed_proxies = set()
        
        if proxy_file and os.path.exists(proxy_file):
            self.load_proxies(proxy_file)
    
    def load_proxies(self, filename):
        """Загрузка списка прокси из файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Пропускаем пустые строки и комментарии
                    if not line or line.startswith('#'):
                        continue
                    
                    # Убираем протокол если есть
                    if line.startswith('http://') or line.startswith('https://'):
                        line = line.split('://', 1)[1]
                    
                    self.proxies.append(line)
            
            print(f"✓ Загружено {len(self.proxies)} прокси")
            
        except Exception as e:
            print(f"✗ Ошибка загрузки прокси: {e}")
    
    def get_next_proxy(self):
        """Получить следующий прокси из списка"""
        if not self.proxies:
            return None
        
        # Пытаемся найти рабочий прокси
        attempts = 0
        max_attempts = len(self.proxies)
        
        while attempts < max_attempts:
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            # Пропускаем failed прокси
            if proxy not in self.failed_proxies:
                return proxy
            
            attempts += 1
        
        # Если все прокси failed - сбрасываем список и начинаем заново
        if attempts >= max_attempts:
            print("⚠ Все прокси были помечены как неработающие. Сброс списка...")
            self.failed_proxies.clear()
            return self.proxies[0] if self.proxies else None
        
        return None
    
    def mark_as_failed(self, proxy):
        """Отметить прокси как неработающий"""
        self.failed_proxies.add(proxy)
        print(f"✗ Прокси помечен как неработающий: {proxy}")
    
    def format_for_selenium(self, proxy):
        """Формат прокси для Selenium"""
        parts = proxy.split(':')
        
        if len(parts) == 2:
            return f'http://{proxy}'
        elif len(parts) == 4:
            ip, port, username, password = parts
            return f'http://{username}:{password}@{ip}:{port}'
        
        return None


# ============================================================================
# CHATBOT - ИСПРАВЛЕННАЯ ВЕРСИЯ v2.1
# ============================================================================

class ChatBot:
    """
    ChatBot ИСПРАВЛЕННАЯ ВЕРСИЯ v2.1
    Улучшения: контекст iframe, задержки, обработка ошибок
    """
    
    # ПОЛНЫЕ селекторы для ВСЕХ поддерживаемых чатов
    CHAT_SELECTORS = {
        'jivochat': {
            'button': [
                # Кастомные теги JivoChat
                {'type': 'css', 'value': 'jdiv[id*="jivo"]'},
                {'type': 'xpath', 'value': '//jdiv[contains(@id, "jivo")]'},
                {'type': 'xpath', 'value': '//jdiv[contains(@class, "label")]'},
                {'type': 'xpath', 'value': '//jdiv[@class and contains(@class, "label")]'},
                {'type': 'css', 'value': 'jdiv'},
                {'type': 'xpath', 'value': '//jdiv'},
                
                # Контейнеры
                {'type': 'css', 'value': 'div[id*="jivo"]'},
                {'type': 'xpath', 'value': '//div[contains(@id, "jivo")]'},
                
                # iframe
                {'type': 'css', 'value': 'iframe[id*="jivo"]'},
                {'type': 'xpath', 'value': '//iframe[contains(@id, "jivo")]'},
            ],
            'input': [
                # Специфичные классы
                {'type': 'css', 'value': 'textarea.inputField__nHBvS'},
                {'type': 'xpath', 'value': '//textarea[contains(@class, "inputField")]'},
                
                # По placeholder
                {'type': 'xpath', 'value': '//textarea[contains(@placeholder, "Введите")]'},
                {'type': 'xpath', 'value': '//textarea[@placeholder="Введите сообщение"]'},
                {'type': 'xpath', 'value': '//textarea[contains(@placeholder, "сообщение")]'},
                {'type': 'xpath', 'value': '//textarea[contains(@placeholder, "message")]'},
                
                # В контексте jdiv
                {'type': 'xpath', 'value': '//jdiv//textarea'},
                
                # Общие
                {'type': 'css', 'value': 'textarea'},
            ],
            'send': [
                {'type': 'xpath', 'value': '//jdiv[contains(@class, "sendButton") and not(contains(@class, "disabled"))]'},
                {'type': 'css', 'value': '.sendButton__ZfXlc'},
                {'type': 'xpath', 'value': '//jdiv[contains(@class, "sendButton")]'},
            ],
            'iframe': ['jivo'],
            'markers': ['jivo', 'jdiv'],
            'js_api': 'window.jivo_api && window.jivo_api.open()'
        },
        
        'bitrix24': {
            'button': [
                {'type': 'css', 'value': '.b24-widget-button-wrapper'},
                {'type': 'css', 'value': '.b24-widget-button-inner-item'},
                {'type': 'css', 'value': '.b24-widget-button-position-bottom-right'},
                {'type': 'xpath', 'value': '//div[contains(@class, "b24-widget-button")]'},
                {'type': 'css', 'value': '#bx-online-consultant'},
                {'type': 'xpath', 'value': '//div[@id="bx-online-consultant"]'},
            ],
            'input': [
                {'type': 'css', 'value': 'textarea[name="im-message"]'},
                {'type': 'css', 'value': '.bx-messenger-textarea'},
                {'type': 'xpath', 'value': '//textarea[contains(@class, "b24-form-control")]'},
                {'type': 'xpath', 'value': '//textarea[contains(@placeholder, "Введите сообщение")]'},
                {'type': 'css', 'value': '.b24-form-control-string textarea'},
            ],
            'send': [
                {'type': 'css', 'value': '.b24-widget-button-send'},
                {'type': 'xpath', 'value': '//button[contains(@class, "b24") and contains(@class, "send")]'},
                {'type': 'css', 'value': 'button[class*="b24"][class*="send"]'},
            ],
            'iframe': ['b24', 'bitrix'],
            'markers': ['b24', 'bitrix', 'bx-messenger'],
            'js_api': 'window.BX && window.BX.LiveChat && BX.LiveChat.openWidget()'
        },
        
        'amocrm': {
            'button': [
                # Основная кнопка
                {'type': 'css', 'value': '.amo-button.amo-button--main'},
                {'type': 'css', 'value': '#amobutton'},
                {'type': 'css', 'value': '.amo-button'},
                {'type': 'xpath', 'value': '//div[contains(@class, "amo-button")]'},
                {'type': 'xpath', 'value': '//div[@id="amobutton"]'},
                {'type': 'css', 'value': '.amo-button-holder'},
            ],
            'input': [
                # В iframe
                {'type': 'css', 'value': 'textarea[placeholder*="Введите"]'},
                {'type': 'css', 'value': 'textarea[placeholder*="сообщение"]'},
                {'type': 'css', 'value': 'textarea[name="message"]'},
                {'type': 'css', 'value': 'input[type="text"]'},
                {'type': 'xpath', 'value': '//textarea'},
                {'type': 'xpath', 'value': '//input[@type="text"]'},
            ],
            'send': [
                {'type': 'css', 'value': 'button[type="submit"]'},
                {'type': 'xpath', 'value': '//button[contains(text(), "Отправить")]'},
                {'type': 'xpath', 'value': '//button[contains(@class, "send")]'},
            ],
            'iframe': ['amo-livechat-iframe', 'amocrm', 'gso.amocrm'],
            'markers': ['amo-button', 'amo-livechat', 'amocrm'],
            'js_api': None
        },
        
        'intercom': {
            'button': [
                {'type': 'css', 'value': '.intercom-launcher'},
                {'type': 'css', 'value': '.intercom-launcher-button'},
                {'type': 'css', 'value': '#intercom-container .intercom-launcher'},
                {'type': 'xpath', 'value': '//div[contains(@class, "intercom-launcher")]'},
            ],
            'input': [
                {'type': 'css', 'value': '.intercom-composer-input'},
                {'type': 'css', 'value': '.intercom-composer textarea'},
                {'type': 'xpath', 'value': '//textarea[contains(@class, "intercom")]'},
            ],
            'send': [
                {'type': 'css', 'value': '.intercom-composer-send-button'},
                {'type': 'xpath', 'value': '//button[contains(@class, "intercom") and contains(@class, "send")]'},
            ],
            'iframe': ['intercom'],
            'markers': ['intercom'],
            'js_api': 'window.Intercom && window.Intercom("show")'
        },
        
        'tawk': {
            'button': [
                {'type': 'css', 'value': '#tawkchat-chat-bubble'},
                {'type': 'css', 'value': '.tawk-button'},
                {'type': 'css', 'value': '.tawk-min-container'},
                {'type': 'xpath', 'value': '//div[contains(@class, "tawk")]'},
                {'type': 'xpath', 'value': '//div[@id="tawkchat-chat-bubble"]'},
            ],
            'input': [
                {'type': 'css', 'value': 'textarea[placeholder*="Enter"]'},
                {'type': 'css', 'value': 'textarea.tawk-textarea'},
                {'type': 'xpath', 'value': '//textarea[contains(@class, "tawk")]'},
            ],
            'send': [
                {'type': 'css', 'value': 'button[type="submit"]'},
                {'type': 'xpath', 'value': '//button[@type="submit"]'},
            ],
            'iframe': ['tawk'],
            'markers': ['tawk'],
            'js_api': 'window.Tawk_API && window.Tawk_API.maximize()'
        },
        
        'drift': {
            'button': [
                {'type': 'css', 'value': '#drift-widget'},
                {'type': 'css', 'value': '.drift-frame-chat'},
                {'type': 'css', 'value': '#drift-widget-container'},
                {'type': 'xpath', 'value': '//div[@id="drift-widget"]'},
            ],
            'input': [
                {'type': 'css', 'value': '#drift-widget-input'},
                {'type': 'css', 'value': 'textarea.drift-input'},
                {'type': 'xpath', 'value': '//textarea[contains(@class, "drift")]'},
            ],
            'send': [
                {'type': 'css', 'value': '.drift-widget-controller-send'},
                {'type': 'xpath', 'value': '//button[contains(@class, "drift") and contains(@class, "send")]'},
            ],
            'iframe': ['drift'],
            'markers': ['drift'],
            'js_api': 'window.drift && drift.api.openChat()'
        },
        
        'crisp': {
            'button': [
                {'type': 'css', 'value': '.crisp-client'},
                {'type': 'css', 'value': 'div[data-crisp-hide]'},
                {'type': 'xpath', 'value': '//div[contains(@class, "crisp")]'},
            ],
            'input': [
                {'type': 'css', 'value': 'textarea.crisp-input'},
                {'type': 'xpath', 'value': '//textarea[contains(@class, "crisp")]'},
            ],
            'send': [
                {'type': 'css', 'value': 'button[type="submit"]'},
            ],
            'iframe': ['crisp'],
            'markers': ['crisp'],
            'js_api': 'window.$crisp && $crisp.push(["do", "chat:open"])'
        },
        
        'livechat': {
            'button': [
                {'type': 'css', 'value': '#chat-widget-container'},
                {'type': 'css', 'value': '.lc-button'},
                {'type': 'css', 'value': '#livechat-compact-view'},
                {'type': 'xpath', 'value': '//div[@id="chat-widget-container"]'},
            ],
            'input': [
                {'type': 'css', 'value': 'textarea[name="message"]'},
                {'type': 'xpath', 'value': '//textarea[@name="message"]'},
            ],
            'send': [
                {'type': 'css', 'value': 'button[type="submit"]'},
            ],
            'iframe': ['livechat'],
            'markers': ['livechat', 'lc-'],
            'js_api': None
        },
        
        'carrotquest': {
            'button': [
                {'type': 'css', 'value': '#carrotquest-messenger-collapsed'},
                {'type': 'css', 'value': '.carrotquest-messenger-button'},
                {'type': 'xpath', 'value': '//div[contains(@class, "carrotquest")]'},
                {'type': 'xpath', 'value': '//div[@id="carrotquest-messenger-collapsed"]'},
            ],
            'input': [
                {'type': 'css', 'value': 'textarea[placeholder*="Введите"]'},
                {'type': 'css', 'value': 'textarea.carrotquest-input'},
                {'type': 'xpath', 'value': '//textarea[contains(@class, "carrotquest")]'},
            ],
            'send': [
                {'type': 'css', 'value': 'button[type="submit"]'},
                {'type': 'xpath', 'value': '//button[contains(text(), "Отправить")]'},
            ],
            'iframe': ['carrotquest'],
            'markers': ['carrotquest'],
            'js_api': 'window.carrotquest && carrotquest.open()'
        },
        
        'chatra': {
            'button': [
                {'type': 'css', 'value': '#chatra'},
                {'type': 'css', 'value': '.chatra--expanded'},
                {'type': 'xpath', 'value': '//div[@id="chatra"]'},
                {'type': 'xpath', 'value': '//div[contains(@class, "chatra")]'},
            ],
            'input': [
                {'type': 'css', 'value': 'textarea[placeholder*="Type"]'},
                {'type': 'css', 'value': 'textarea.chatra__input'},
                {'type': 'xpath', 'value': '//textarea[contains(@class, "chatra")]'},
            ],
            'send': [
                {'type': 'css', 'value': 'button.chatra__send-button'},
                {'type': 'xpath', 'value': '//button[contains(@class, "chatra") and contains(@class, "send")]'},
            ],
            'iframe': ['chatra'],
            'markers': ['chatra'],
            'js_api': 'window.Chatra && Chatra("openChat")'
        },
        
        'livetex': {
            'button': [
                {'type': 'css', 'value': '#liveTexWebButton'},
                {'type': 'css', 'value': '.livetex-button'},
                {'type': 'xpath', 'value': '//div[contains(@class, "livetex")]'},
                {'type': 'xpath', 'value': '//div[@id="liveTexWebButton"]'},
            ],
            'input': [
                {'type': 'css', 'value': 'textarea[name="text"]'},
                {'type': 'css', 'value': 'textarea.livetex-input'},
                {'type': 'xpath', 'value': '//textarea[contains(@class, "livetex")]'},
            ],
            'send': [
                {'type': 'css', 'value': 'input[type="submit"]'},
                {'type': 'xpath', 'value': '//input[@type="submit"]'},
            ],
            'iframe': ['livetex'],
            'markers': ['livetex'],
            'js_api': None
        },
        
        'freshchat': {
            'button': [
                {'type': 'css', 'value': '#fc_frame'},
                {'type': 'css', 'value': '.fc-widget-button'},
                {'type': 'xpath', 'value': '//div[@id="fc_frame"]'},
            ],
            'input': [
                {'type': 'css', 'value': 'textarea[placeholder*="Type"]'},
                {'type': 'xpath', 'value': '//textarea'},
            ],
            'send': [
                {'type': 'css', 'value': 'button[type="submit"]'},
            ],
            'iframe': ['freshchat', 'fc_frame'],
            'markers': ['freshchat', 'fc-widget'],
            'js_api': 'window.fcWidget && fcWidget.open()'
        },
        
        'envybox': {
            'button': [
                {'type': 'css', 'value': '.envybox-button'},
                {'type': 'xpath', 'value': '//div[contains(@class, "envybox")]'},
            ],
            'input': [
                {'type': 'css', 'value': 'textarea[name="message"]'},
                {'type': 'xpath', 'value': '//textarea'},
            ],
            'send': [
                {'type': 'css', 'value': 'button[type="submit"]'},
            ],
            'iframe': ['envybox'],
            'markers': ['envybox'],
            'js_api': None
        },
        
        'redhelper': {
            'button': [
                {'type': 'css', 'value': '#redhelper-button'},
                {'type': 'css', 'value': '.redhelper-widget'},
                {'type': 'xpath', 'value': '//div[contains(@class, "redhelper")]'},
            ],
            'input': [
                {'type': 'css', 'value': 'textarea[name="message"]'},
                {'type': 'xpath', 'value': '//textarea'},
            ],
            'send': [
                {'type': 'css', 'value': 'button[type="submit"]'},
            ],
            'iframe': ['redhelper'],
            'markers': ['redhelper'],
            'js_api': None
        },
        
        'dashly': {
            'button': [
                {'type': 'css', 'value': '.dashly-widget'},
                {'type': 'xpath', 'value': '//div[contains(@class, "dashly")]'},
            ],
            'input': [
                {'type': 'css', 'value': 'textarea[placeholder*="Введите"]'},
                {'type': 'xpath', 'value': '//textarea'},
            ],
            'send': [
                {'type': 'css', 'value': 'button[type="submit"]'},
            ],
            'iframe': ['dashly'],
            'markers': ['dashly'],
            'js_api': 'window.dashly && dashly.open()'
        }
    }
    
    def __init__(self, session_folder, thread_id=0, headless=False, timeout=10, 
                 fast_mode=True, use_antidetect=True, proxy=None, log_callback=None):
        """
        Инициализация бота
        """
        
        self.thread_id = thread_id
        self.timeout = timeout
        self.session_folder = session_folder
        self.screenshots_folder = os.path.join(session_folder, 'screenshots')
        self.detected_chat_type = None
        self.fast_mode = fast_mode
        self.current_iframe = None
        self.in_iframe_context = False  # НОВОЕ: отслеживание контекста
        self.max_attempts = 3
        self.log_callback = log_callback
        self.proxy = proxy
        
        # Антидетект
        self.use_antidetect = use_antidetect
        self.antidetect = AntidetectManager(fast_mode) if use_antidetect else None
        
        # ИСПРАВЛЕНО: Увеличены задержки для надежности
        if fast_mode:
            self.delay_page_load = 4  # было 3
            self.delay_after_open_chat = 3  # было 2
            self.delay_before_send = 0.8  # было 0.5
            self.delay_after_send = 2  # было 1.5
            self.typing_delay = 0.01
        else:
            self.delay_page_load = 5  # было 4
            self.delay_after_open_chat = 4  # было 3
            self.delay_before_send = 1.5  # было 1
            self.delay_after_send = 3  # было 2
            self.typing_delay = 0.03
        
        os.makedirs(self.screenshots_folder, exist_ok=True)
        
        self.setup_logging()
        self.driver = self._init_driver(headless)
        
    def log(self, message, level="INFO"):
        """Логирование с указанием потока"""
        prefixed_message = f"[Thread-{self.thread_id}] {message}"
        
        if self.log_callback:
            self.log_callback(prefixed_message, level)
        
        if level == "INFO":
            self.logger.info(prefixed_message)
        elif level == "ERROR":
            self.logger.error(prefixed_message)
        elif level == "WARNING":
            self.logger.warning(prefixed_message)
        elif level == "DEBUG":
            self.logger.debug(prefixed_message)
    
    def setup_logging(self):
        """Настройка логирования в файл"""
        log_file = os.path.join(self.session_folder, f'thread_{self.thread_id}.log')
        self.logger = logging.getLogger(f'ChatBot_{self.thread_id}_{id(self)}')
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()
        
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        self.logger.propagate = False
    
    def _find_chromedriver(self):
        """Поиск chromedriver.exe в стандартных путях"""
        search_paths = [
            os.path.join(os.getcwd(), 'chromedriver.exe'),
            os.path.join(os.getcwd(), 'chromedriver', 'chromedriver.exe'),
            os.path.join(os.path.expanduser("~"), ".wdm", "drivers", "chromedriver", "win64", "**", "chromedriver.exe"),
        ]
        
        for path in search_paths:
            if '**' not in path:
                if os.path.exists(path) and os.path.isfile(path) and os.path.getsize(path) > 1000000:
                    return path
            else:
                found = glob.glob(path, recursive=True)
                for f in found:
                    if os.path.isfile(f) and os.path.getsize(f) > 1000000:
                        return f
        return None
    
    def _download_chromedriver(self):
        """Автоматическое скачивание ChromeDriver"""
        try:
            self.log("Скачивание ChromeDriver...")
            version = "131.0.6778.85"
            driver_dir = os.path.join(os.getcwd(), 'chromedriver')
            os.makedirs(driver_dir, exist_ok=True)
            
            download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/win64/chromedriver-win64.zip"
            
            zip_path = os.path.join(driver_dir, 'chromedriver.zip')
            response = requests.get(download_url, timeout=60)
            
            if response.status_code == 200:
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(driver_dir)
                
                for root, dirs, files in os.walk(driver_dir):
                    for file in files:
                        if file == 'chromedriver.exe':
                            src = os.path.join(root, file)
                            dst = os.path.join(driver_dir, 'chromedriver.exe')
                            if src != dst:
                                shutil.copy2(src, dst)
                            try:
                                os.remove(zip_path)
                            except:
                                pass
                            self.log("✓ ChromeDriver скачан")
                            return dst
            return None
        except Exception as e:
            self.log(f"Ошибка загрузки ChromeDriver: {e}", "ERROR")
            return None
    
    def _init_driver(self, headless):
        """ИСПРАВЛЕНО: Инициализация WebDriver с отключением GPU в headless"""
        self.log("Инициализация WebDriver с антидетектом...")
        
        options = Options()
        
        if headless:
            options.add_argument('--headless=new')
            # ИСПРАВЛЕНО: Отключаем GPU в headless для избежания ошибок
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
        
        # Базовые настройки
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        
        # Антидетект: отключение GCM и синхронизации
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-translate')
        options.add_argument('--disable-features=TranslateUI')
        
        # ИСПРАВЛЕНО: Подавление логов GPU
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--log-level=3')  # Только критические ошибки
        
        # АНТИДЕТЕКТ: Случайный User-Agent
        if self.use_antidetect:
            user_agent = self.antidetect.ua_rotator.get_random()
            options.add_argument(f'user-agent={user_agent}')
            self.log(f"User-Agent: {user_agent[:60]}...")
        else:
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # АНТИДЕТЕКТ: Случайный размер окна
        if self.use_antidetect:
            width = random.randint(1366, 1920)
            height = random.randint(768, 1080)
            options.add_argument(f'--window-size={width},{height}')
        else:
            options.add_argument('--window-size=1920,1080')
        
        # Прокси
        if self.proxy:
            proxy_formatted = self.proxy
            # Убираем протокол если есть
            if not proxy_formatted.startswith('http'):
                proxy_formatted = f'http://{proxy_formatted}'
            
            options.add_argument(f'--proxy-server={proxy_formatted}')
            self.log(f"Прокси: {self.proxy}")
        
        # Отключение автоматизации
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # АНТИДЕТЕКТ: Языки и локаль
        if self.use_antidetect:
            languages = [
                'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'en-US,en;q=0.9,ru;q=0.8',
                'ru;q=0.9,en;q=0.8'
            ]
            options.add_argument(f'--lang={random.choice(languages)}')
        
        # Настройки загрузки страницы
        options.page_load_strategy = 'eager'
        
        # Поиск ChromeDriver
        driver_path = self._find_chromedriver()
        if not driver_path:
            driver_path = self._download_chromedriver()
        
        if not driver_path:
            raise Exception("ChromeDriver не найден!")
        
        service = Service(
            executable_path=driver_path,
            log_path='NUL' if sys.platform == 'win32' else '/dev/null'
        )
        
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(20)
        driver.implicitly_wait(0)
        
        # АНТИДЕТЕКТ: Скрытие WebDriver и изменение fingerprint
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                // Скрываем webdriver
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                
                // Добавляем плагины
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Языки
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['ru-RU', 'ru', 'en-US', 'en']
                });
                
                // Chrome runtime
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                // Permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            '''
        })
        
        # АНТИДЕТЕКТ: Fingerprint noise
        if self.use_antidetect:
            self.antidetect.add_noise_to_fingerprint(driver)
        
        self.log("✓ WebDriver запущен с антидетектом")
        return driver
    
    # НОВЫЙ МЕТОД: Безопасное переключение в основной контекст
    def switch_to_default_content(self):
        """Безопасное переключение в основной контекст"""
        try:
            self.driver.switch_to.default_content()
            self.in_iframe_context = False
            self.current_iframe = None
            self.log("✓ Переключено в основной контекст", "DEBUG")
        except Exception as e:
            self.log(f"Ошибка переключения в основной контекст: {e}", "DEBUG")
    
    # НОВЫЙ МЕТОД: Безопасное переключение в iframe
    def switch_to_iframe(self, iframe):
        """Безопасное переключение в iframe"""
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(iframe)
            self.in_iframe_context = True
            self.current_iframe = iframe
            self.log("✓ Переключено в iframe", "DEBUG")
            return True
        except Exception as e:
            self.log(f"Ошибка переключения в iframe: {e}", "DEBUG")
            self.in_iframe_context = False
            return False
    
    def open_website(self, url):
        """Открытие сайта с имитацией человека"""
        try:
            self.log(f"→ Открытие: {url}")
            
            # Сброс контекста
            self.switch_to_default_content()
            
            # АНТИДЕТЕКТ: Случайная задержка перед открытием
            if self.use_antidetect:
                self.antidetect.random_delay(0.5, 1.5)
            
            self.driver.get(url)
            
            # Ожидание загрузки
            time.sleep(self.delay_page_load)
            
            # АНТИДЕТЕКТ: Имитация чтения страницы
            if self.use_antidetect:
                self.antidetect.random_scroll(self.driver)
                self.antidetect.random_delay(1, 2)
            
            self.log("✓ Загружено")
            return True
            
        except Exception as e:
            self.log(f"✗ Ошибка открытия: {e}", "ERROR")
            return False
    
    def is_element_visible(self, element):
        """Проверка видимости элемента"""
        try:
            if not element.is_displayed():
                return False
            
            size = element.size
            if size['width'] <= 0 or size['height'] <= 0:
                return False
            
            # Проверка opacity
            try:
                opacity = self.driver.execute_script("return window.getComputedStyle(arguments[0]).opacity;", element)
                if opacity == '0':
                    return False
            except:
                pass
            
            # Проверка visibility
            try:
                visibility = self.driver.execute_script("return window.getComputedStyle(arguments[0]).visibility;", element)
                if visibility == 'hidden':
                    return False
            except:
                pass
            
            return True
        except:
            return False
    
    def is_chat_element(self, element):
        """ИСПРАВЛЕНО: Более мягкая проверка принадлежности к чату"""
        try:
            # Для amoCRM - не проверяем вообще
            if self.detected_chat_type == 'amocrm':
                return True
            
            # Для других - проверяем только антимаркеры
            parent_html = self.driver.execute_script("""
                var element = arguments[0];
                var parent = element;
                var html = '';
                for(var i = 0; i < 6; i++) {
                    if(!parent) break;
                    html += (parent.outerHTML || '').substring(0, 500);
                    parent = parent.parentElement;
                }
                return html.toLowerCase();
            """, element)
            
            # Только антимаркеры
            anti_markers = [
                'comment', 'комментар',
                'search', 'поиск',
                'subscribe', 'подпис',
                'newsletter', 'рассылка',
                'contact-form',
                'review', 'отзыв',
                'login', 'вход', 'signin',
                'register', 'регистр', 'signup',
            ]
            
            has_anti_marker = any(marker in parent_html for marker in anti_markers)
            
            # Если есть антимаркер - точно НЕ чат
            if has_anti_marker:
                return False
            
            # Иначе считаем что это чат
            return True
            
        except Exception as e:
            self.log(f"Ошибка проверки элемента: {e}", "DEBUG")
            return True  # ИСПРАВЛЕНО: по умолчанию считаем что это чат
    
    def detect_chat_type(self):
        """Определение типа чата на странице"""
        self.log("→ Поиск чата на странице...")
        
        # Сброс контекста
        self.switch_to_default_content()
        
        # Прокрутка для активации lazy-loaded виджетов
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
        except:
            pass
        
        # Проверяем все известные чаты
        for chat_name, selectors in self.CHAT_SELECTORS.items():
            # Проверяем первые 3 селектора кнопок
            for selector in selectors['button'][:3]:
                try:
                    by_type = By.CSS_SELECTOR if selector['type'] == 'css' else By.XPATH
                    elements = self.driver.find_elements(by_type, selector['value'])
                    
                    for element in elements:
                        if self.is_element_visible(element):
                            self.detected_chat_type = chat_name
                            self.log(f"✓ Обнаружен: {chat_name.upper()}")
                            return chat_name
                except Exception as e:
                    self.log(f"Ошибка селектора {selector['value']}: {e}", "DEBUG")
                    continue
        
        # Проверка iframe
        chat_type = self._detect_chat_in_iframes()
        if chat_type:
            return chat_type
        
        # Универсальный поиск
        if self._find_generic_chat():
            self.detected_chat_type = 'generic'
            self.log("✓ Обнаружен: GENERIC CHAT")
            return 'generic'
        
        self.log("✗ Чат не найден", "WARNING")
        return None
    
    def _detect_chat_in_iframes(self):
        """Поиск чатов внутри iframe"""
        try:
            # Возвращаемся в основной контекст
            self.switch_to_default_content()
            
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            self.log(f"→ Проверка {len(iframes)} iframe...", "DEBUG")
            
            for i, iframe in enumerate(iframes[:15]):  # Проверяем максимум 15 iframe
                try:
                    # Получаем атрибуты iframe
                    iframe_src = (iframe.get_attribute('src') or '').lower()
                    iframe_id = (iframe.get_attribute('id') or '').lower()
                    iframe_class = (iframe.get_attribute('class') or '').lower()
                    iframe_name = (iframe.get_attribute('name') or '').lower()
                    iframe_title = (iframe.get_attribute('title') or '').lower()
                    
                    iframe_attrs = iframe_src + iframe_id + iframe_class + iframe_name + iframe_title
                    
                    # Проверяем каждый тип чата
                    for chat_name, config in self.CHAT_SELECTORS.items():
                        iframe_markers = config.get('iframe', [])
                        
                        if any(marker in iframe_attrs for marker in iframe_markers):
                            self.log(f"✓ Найден {chat_name.upper()} в iframe #{i}")
                            self.current_iframe = iframe
                            self.detected_chat_type = chat_name
                            return chat_name
                            
                except Exception as e:
                    self.log(f"Ошибка проверки iframe #{i}: {e}", "DEBUG")
                    continue
                    
        except Exception as e:
            self.log(f"Ошибка при проверке iframe: {e}", "DEBUG")
        finally:
            # Всегда возвращаемся в основной контекст
            self.switch_to_default_content()
        
        return None
    
    def _find_generic_chat(self):
        """Универсальный поиск чата"""
        generic_selectors = [
            {'type': 'xpath', 'value': '//div[contains(@class, "chat") or contains(@id, "chat")]'},
            {'type': 'css', 'value': '[class*="chat-widget"]'},
            {'type': 'css', 'value': '[id*="chat-widget"]'},
            {'type': 'css', 'value': '[class*="messenger"]'},
            {'type': 'css', 'value': '[class*="widget"]'},
        ]
        
        for selector in generic_selectors:
            try:
                by_type = By.CSS_SELECTOR if selector['type'] == 'css' else By.XPATH
                elements = self.driver.find_elements(by_type, selector['value'])
                
                for element in elements:
                    if self.is_element_visible(element) and self.is_chat_element(element):
                        return True
            except:
                continue
        
        return False
    
    def try_click_element(self, element, description="элемент"):
        """Множественные попытки клика по элементу с антидетектом"""
        
        # АНТИДЕТЕКТ: Движение мыши перед кликом
        if self.use_antidetect:
            self.antidetect.random_mouse_movement(self.driver, element)
            self.antidetect.random_delay(0.2, 0.5)
        
        click_methods = [
            # Метод 1: Обычный клик
            lambda el: el.click(),
            
            # Метод 2: JavaScript клик
            lambda el: self.driver.execute_script("arguments[0].click();", el),
            
            # Метод 3: ActionChains
            lambda el: ActionChains(self.driver).move_to_element(el).click().perform(),
            
            # Метод 4: JS с фокусом
            lambda el: self.driver.execute_script("arguments[0].focus(); arguments[0].click();", el),
            
            # Метод 5: ActionChains с паузой
            lambda el: ActionChains(self.driver).move_to_element(el).pause(0.5).click().perform(),
        ]
        
        for i, method in enumerate(click_methods, 1):
            try:
                method(element)
                self.log(f"✓ Клик: {description} (метод #{i})")
                
                # АНТИДЕТЕКТ: Задержка после клика
                if self.use_antidetect:
                    self.antidetect.random_delay(0.3, 0.7)
                
                return True
            except Exception as e:
                self.log(f"  Метод клика #{i} не сработал: {e}", "DEBUG")
                continue
        
        self.log(f"✗ Не удалось кликнуть по {description}", "WARNING")
        return False
    
    def wait_for_chat_open(self, chat_type, timeout=10):
        """ИСПРАВЛЕНО: Улучшенное ожидание открытия чата с явным контекстом"""
        self.log(f"→ Ожидание полного открытия чата (до {timeout}с)...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 1. Проверяем основной контекст
            self.switch_to_default_content()
            
            if chat_type in self.CHAT_SELECTORS:
                for selector in self.CHAT_SELECTORS[chat_type]['input'][:2]:
                    try:
                        by_type = By.CSS_SELECTOR if selector['type'] == 'css' else By.XPATH
                        element = self.driver.find_element(by_type, selector['value'])
                        
                        if self.is_element_visible(element):
                            self.log(f"✓ Чат открылся в основном контексте!")
                            return True
                    except:
                        continue
            
            # 2. Проверяем все iframe
            try:
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    try:
                        if self.switch_to_iframe(iframe):
                            time.sleep(0.5)  # НОВОЕ: небольшая задержка после переключения
                            
                            if chat_type in self.CHAT_SELECTORS:
                                for selector in self.CHAT_SELECTORS[chat_type]['input'][:2]:
                                    try:
                                        by_type = By.CSS_SELECTOR if selector['type'] == 'css' else By.XPATH
                                        element = self.driver.find_element(by_type, selector['value'])
                                        
                                        if self.is_element_visible(element):
                                            self.log(f"✓ Чат открылся в iframe! Контекст сохранен")
                                            # НЕ переключаемся обратно - остаемся в iframe!
                                            return True
                                    except:
                                        continue
                            
                            # Если не нашли - возвращаемся
                            self.switch_to_default_content()
                    except:
                        self.switch_to_default_content()
                        continue
            except:
                pass
            
            time.sleep(0.5)
        
        self.log(f"⚠ Чат не открылся за {timeout}с", "WARNING")
        self.switch_to_default_content()
        return False
    
    def open_jivochat_special(self):
        """ИСПРАВЛЕНО: Улучшенное открытие JivoChat с сохранением контекста"""
        self.log("→ Специальное открытие JivoChat...")
        
        # Возвращаемся в основной контекст
        self.switch_to_default_content()
        
        # Метод 1: JavaScript API
        try:
            result = self.driver.execute_script("""
                try {
                    if (typeof window.jivo_api !== 'undefined') {
                        window.jivo_api.open();
                        return 'api_open';
                    }
                } catch(e) {}
                return 'no_api';
            """)
            
            if 'api_open' in str(result):
                self.log("  ✓ Использован JS API")
                time.sleep(self.delay_after_open_chat)  # ИСПРАВЛЕНО: используем переменную
                if self.wait_for_chat_open('jivochat', timeout=5):
                    return True
        except:
            pass
        
        # Метод 2: Клик по всем jdiv элементам
        try:
            jdivs = self.driver.find_elements(By.TAG_NAME, 'jdiv')
            self.log(f"  Найдено jdiv элементов: {len(jdivs)}")
            
            for i, jdiv in enumerate(jdivs):
                if self.is_element_visible(jdiv):
                    if self.try_click_element(jdiv, f"jdiv #{i}"):
                        time.sleep(self.delay_after_open_chat)  # ИСПРАВЛЕНО
                        
                        # Проверяем открытие
                        if self.wait_for_chat_open('jivochat', timeout=5):
                            return True
        except:
            pass
        
        return False
    
    def open_amocrm_special(self):
        """ИСПРАВЛЕНО: Улучшенное открытие amoCRM с сохранением контекста"""
        self.log("→ Специальное открытие amoCRM...")
        
        # Возвращаемся в основной контекст
        self.switch_to_default_content()
        
        # Сначала ищем iframe
        self.log("  → Поиск iframe amoCRM...")
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            self.log(f"  Найдено iframe всего: {len(iframes)}")
            
            for idx, iframe in enumerate(iframes):
                try:
                    name = iframe.get_attribute('name') or ''
                    src = iframe.get_attribute('src') or ''
                    
                    self.log(f"    iframe #{idx}: name='{name[:30]}', src='{src[:50]}'", "DEBUG")
                    
                    if 'amo-livechat' in name or 'amocrm' in src or 'livechat' in src:
                        self.log(f"  ✓✓✓ Найден iframe amoCRM")
                        
                        # Переключаемся и сохраняем контекст
                        if self.switch_to_iframe(iframe):
                            time.sleep(2)  # Ждем загрузки
                            
                            # Проверяем наличие полей
                            all_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'textarea, input[type="text"], input:not([type])')
                            self.log(f"  В iframe найдено полей ввода: {len(all_inputs)}")
                            
                            if all_inputs:
                                # Остаемся в iframe!
                                self.log("  ✓ iframe с полями найден, контекст сохранен")
                                return True
                            else:
                                self.switch_to_default_content()
                except Exception as e:
                    self.log(f"  Ошибка проверки iframe #{idx}: {e}", "DEBUG")
                    self.switch_to_default_content()
                    continue
        except Exception as e:
            self.log(f"  Ошибка поиска iframe: {e}", "DEBUG")
        
        # Если iframe не нашли, пробуем кликнуть по кнопке
        self.switch_to_default_content()
        self.log("  → Поиск и клик по кнопке amoCRM...")
        
        try:
            button_selectors = [
                (By.CSS_SELECTOR, '.amo-button.amo-button--main'),
                (By.ID, 'amobutton'),
                (By.CSS_SELECTOR, '.amo-button'),
                (By.XPATH, '//div[contains(@class, "amo-button")]'),
            ]
            
            for by_type, selector_value in button_selectors:
                try:
                    elements = self.driver.find_elements(by_type, selector_value)
                    
                    for element in elements:
                        if self.is_element_visible(element):
                            self.log(f"  ✓ Найдена кнопка")
                            
                            if self.try_click_element(element, "amoCRM button"):
                                self.log("  Ждем появления iframe после клика...")
                                time.sleep(self.delay_after_open_chat + 1)  # ИСПРАВЛЕНО: +1 секунда
                                
                                # Ищем iframe снова
                                iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
                                for iframe in iframes:
                                    name = iframe.get_attribute('name') or ''
                                    src = iframe.get_attribute('src') or ''
                                    
                                    if 'amo-livechat' in name or 'amocrm' in src or 'livechat' in src:
                                        self.log(f"  ✓✓✓ После клика появился iframe")
                                        
                                        if self.switch_to_iframe(iframe):
                                            time.sleep(2)
                                            
                                            test_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'textarea, input')
                                            self.log(f"  В iframe после клика найдено полей: {len(test_inputs)}")
                                            
                                            if test_inputs:
                                                return True
                                            else:
                                                self.switch_to_default_content()
                except Exception as e:
                    self.log(f"  Ошибка с селектором: {e}", "DEBUG")
                    self.switch_to_default_content()
                    continue
        except Exception as e:
            self.log(f"  Ошибка поиска кнопки: {e}", "DEBUG")
        
        self.switch_to_default_content()
        return False
    
    def open_chat(self):
        """ИСПРАВЛЕНО: Открытие чата с явным сохранением контекста"""
        self.log("→ Открытие чата...")
        
        # Определяем тип чата
        chat_type = self.detect_chat_type()
        
        if not chat_type:
            self.log("✗ Чат не найден на странице", "ERROR")
            return False
        
        # Проверка - может чат уже открыт?
        self.log("→ Проверка, открыт ли чат...")
        if self.wait_for_chat_open(chat_type, timeout=3):
            self.log("✓ Чат уже открыт!")
            # Контекст уже сохранен в wait_for_chat_open
            return True
        
        # Возвращаемся в основной контекст
        self.switch_to_default_content()
        
        # СПЕЦИАЛЬНАЯ ОБРАБОТКА
        if chat_type == 'jivochat':
            if self.open_jivochat_special():
                self.log("✓ JivoChat открыт специальным методом")
                # Контекст уже сохранен
                return True
        
        if chat_type == 'amocrm':
            if self.open_amocrm_special():
                self.log("✓ amoCRM открыт специальным методом")
                # Контекст уже сохранен
                return True
        
        # Стандартное открытие
        for attempt in range(1, self.max_attempts + 1):
            self.log(f"→ Попытка #{attempt}/{self.max_attempts}...")
            
            # Возвращаемся в основной контекст
            self.switch_to_default_content()
            
            button = None
            
            # Поиск кнопки
            if chat_type in self.CHAT_SELECTORS:
                for selector in self.CHAT_SELECTORS[chat_type]['button']:
                    try:
                        by_type = By.CSS_SELECTOR if selector['type'] == 'css' else By.XPATH
                        elements = self.driver.find_elements(by_type, selector['value'])
                        
                        for el in elements:
                            if self.is_element_visible(el):
                                button = el
                                self.log(f"  ✓ Найдена кнопка")
                                break
                        
                        if button:
                            break
                    except:
                        continue
            
            if button:
                if self.try_click_element(button, "кнопка чата"):
                    time.sleep(self.delay_after_open_chat)  # ИСПРАВЛЕНО: используем переменную
                    
                    # Проверяем открытие
                    if self.wait_for_chat_open(chat_type, timeout=8):
                        self.log("✓ Чат успешно открыт!")
                        # Контекст уже сохранен в wait_for_chat_open
                        return True
                    else:
                        self.log(f"⚠ Попытка #{attempt}: чат не открылся", "WARNING")
            
            if attempt < self.max_attempts:
                time.sleep(2)
        
        # JS API (последняя попытка)
        self.switch_to_default_content()
        if self._force_open_chat_js(chat_type):
            time.sleep(self.delay_after_open_chat)
            if self.wait_for_chat_open(chat_type, timeout=8):
                return True
        
        self.log("✗ Не удалось открыть чат", "ERROR")
        self.switch_to_default_content()
        return False
    
    def _force_open_chat_js(self, chat_type):
        """Принудительное открытие через JavaScript API"""
        if chat_type not in self.CHAT_SELECTORS:
            return False
        
        js_api = self.CHAT_SELECTORS[chat_type].get('js_api')
        if not js_api:
            return False
        
        try:
            self.log(f"→ Попытка открытия через JS API ({chat_type})...")
            result = self.driver.execute_script(f"""
                try {{
                    {js_api};
                    return true;
                }} catch(e) {{
                    return false;
                }}
            """)
            
            if result:
                self.log(f"✓ Открыто через JS API")
                return True
        except Exception as e:
            self.log(f"JS API ошибка: {e}", "DEBUG")
        
        return False
    
    def find_input_field(self):
        """ИСПРАВЛЕНО v3: Поиск поля ввода БЕЗ переключения контекста"""
        self.log("→ Поиск поля ввода...")
        self.log(f"  Текущий контекст: {'iframe' if self.in_iframe_context else 'основной'}", "DEBUG")
        
        # ВАЖНО: НЕ переключаем контекст! Используем тот, что установлен
        
        # ОТЛАДКА: Выводим все поля
        try:
            all_textareas = self.driver.find_elements(By.CSS_SELECTOR, 'textarea')
            all_inputs_text = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
            all_inputs_any = self.driver.find_elements(By.CSS_SELECTOR, 'input:not([type="hidden"]):not([type="submit"]):not([type="button"])')
            
            self.log(f"  📊 ОТЛАДКА: textarea={len(all_textareas)}, input[text]={len(all_inputs_text)}, input[any]={len(all_inputs_any)}")
            
            # Подробно о первых 5
            all_fields = all_textareas + all_inputs_text + all_inputs_any
            for i, field in enumerate(all_fields[:5]):
                try:
                    visible = self.is_element_visible(field)
                    placeholder = field.get_attribute('placeholder') or ''
                    field_class = field.get_attribute('class') or ''
                    field_name = field.get_attribute('name') or ''
                    
                    self.log(f"    Поле #{i}: {field.tag_name}, visible={visible}, placeholder='{placeholder[:25]}', name='{field_name[:20]}', class='{field_class[:30]}'", "DEBUG")
                except Exception as e:
                    self.log(f"    Ошибка проверки поля #{i}: {e}", "DEBUG")
        except Exception as e:
            self.log(f"  Ошибка отладки: {e}", "DEBUG")
        
        # 1. ПОИСК ПО СПЕЦИФИЧНЫМ СЕЛЕКТОРАМ (в текущем контексте)
        if self.detected_chat_type and self.detected_chat_type in self.CHAT_SELECTORS:
            self.log(f"  → Специфичный поиск для {self.detected_chat_type} в текущем контексте...")
            
            for i, selector in enumerate(self.CHAT_SELECTORS[self.detected_chat_type]['input']):
                try:
                    by_type = By.CSS_SELECTOR if selector['type'] == 'css' else By.XPATH
                    elements = self.driver.find_elements(by_type, selector['value'])
                    
                    if elements:
                        self.log(f"    Селектор #{i}: найдено {len(elements)}", "DEBUG")
                    
                    for element in elements:
                        if self.is_element_visible(element):
                            # Для amoCRM - берем первое видимое
                            if self.detected_chat_type == 'amocrm':
                                self.log(f"✓✓✓ НАЙДЕНО поле ввода amoCRM!")
                                return element
                            
                            # Для остальных - проверяем принадлежность чату
                            if self.is_chat_element(element):
                                self.log(f"✓✓✓ НАЙДЕНО поле ввода ({self.detected_chat_type})!")
                                return element
                except Exception as e:
                    self.log(f"    Ошибка селектора #{i}: {e}", "DEBUG")
        
        # 2. УНИВЕРСАЛЬНЫЙ ПОИСК (в текущем контексте)
        self.log("  → Универсальный поиск в текущем контексте...")
        
        # Для amoCRM - берем ЛЮБОЕ видимое поле ввода
        if self.detected_chat_type == 'amocrm':
            self.log("  → amoCRM: поиск ЛЮБОГО видимого поля ввода...")
            try:
                priority_selectors = [
                    'textarea',
                    'input[type="text"]',
                    'input:not([type="hidden"]):not([type="submit"]):not([type="button"])',
                ]
                
                for sel in priority_selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, sel)
                    self.log(f"    {sel}: найдено {len(elements)}", "DEBUG")
                    
                    for element in elements:
                        if self.is_element_visible(element):
                            self.log(f"✓✓✓ НАЙДЕНО видимое поле (amoCRM): {sel}")
                            return element
            except Exception as e:
                self.log(f"  Ошибка универсального поиска amoCRM: {e}", "DEBUG")
        else:
            # Для остальных - стандартный поиск
            generic_selectors = [
                {'type': 'css', 'value': 'textarea'},
                {'type': 'css', 'value': 'input[type="text"]'},
                {'type': 'xpath', 'value': '//textarea[contains(@placeholder, "message") or contains(@placeholder, "Message") or contains(@placeholder, "Введите")]'},
            ]
            
            for selector in generic_selectors:
                try:
                    by_type = By.CSS_SELECTOR if selector['type'] == 'css' else By.XPATH
                    elements = self.driver.find_elements(by_type, selector['value'])
                    
                    for element in elements:
                        if not self.is_element_visible(element):
                            continue
                        
                        if not self.is_chat_element(element):
                            continue
                        
                        size = element.size
                        if size['height'] > 200:
                            continue
                        
                        self.log(f"✓✓✓ НАЙДЕНО поле (универсальный поиск)!")
                        return element
                except:
                    continue
        
        # 3. ПОИСК В ДРУГИХ КОНТЕКСТАХ (если еще не в iframe)
        if not self.in_iframe_context:
            self.log("  → Поиск во всех iframe...")
            try:
                self.switch_to_default_content()
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                self.log(f"  Найдено iframe для проверки: {len(iframes)}")
                
                for i, iframe in enumerate(iframes[:15]):
                    try:
                        if self.switch_to_iframe(iframe):
                            time.sleep(0.5)  # НОВОЕ: небольшая задержка
                            
                            # Ищем textarea
                            textareas = self.driver.find_elements(By.CSS_SELECTOR, 'textarea')
                            inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], input:not([type])')
                            
                            all_inputs = textareas + inputs
                            
                            if all_inputs:
                                self.log(f"    iframe #{i}: найдено полей {len(all_inputs)}")
                            
                            for inp in all_inputs:
                                if self.is_element_visible(inp):
                                    self.log(f"✓✓✓ НАЙДЕНО поле в iframe #{i}!")
                                    # Остаемся в iframe!
                                    return inp
                            
                            self.switch_to_default_content()
                    except:
                        self.switch_to_default_content()
                        continue
            except Exception as e:
                self.log(f"  Ошибка поиска в iframe: {e}", "DEBUG")
        
        # НЕ НАЙДЕНО
        self.log("✗✗✗ ПОЛЕ ВВОДА НЕ НАЙДЕНО", "ERROR")
        
        # Делаем отладочный скриншот
        try:
            debug_path = os.path.join(self.screenshots_folder, f'DEBUG_no_input_t{self.thread_id}.png')
            self.driver.save_screenshot(debug_path)
            self.log(f"✓ Отладочный скриншот: DEBUG_no_input_t{self.thread_id}.png")
        except:
            pass
        
        return None
    
    def send_message(self, url, message):
        """ИСПРАВЛЕНО: Отправка с сохранением контекста iframe"""
        start_time = time.time()
        result = {
            'url': url,
            'status': 'error',
            'chat_type': None,
            'message': message,
            'screenshot': None,
            'error': None,
            'duration': 0,
            'thread_id': self.thread_id
        }
        
        try:
            self.log("="*70)
            self.log(f"Сайт: {url}")
            self.log("="*70)
            
            self.detected_chat_type = None
            self.current_iframe = None
            self.in_iframe_context = False
            
            # Сброс контекста
            self.switch_to_default_content()
            
            # 1. Открытие сайта
            if not self.open_website(url):
                result['error'] = 'Не удалось открыть сайт'
                return result
            
            # Скриншот после загрузки
            self.take_screenshot(url, 'step1_loaded')
            
            # 2. Открытие чата (контекст сохраняется автоматически)
            if not self.open_chat():
                result['error'] = 'Чат не открывается'
                self.take_screenshot(url, 'error_chat_not_open')
                return result
            
            # Скриншот после открытия чата
            self.take_screenshot(url, 'step2_chat_opened')
            self.log(f"  Контекст после открытия чата: {'iframe' if self.in_iframe_context else 'основной'}", "DEBUG")
            
            # 3. Поиск поля ввода (БЕЗ переключения контекста!)
            input_field = self.find_input_field()
            if not input_field:
                result['error'] = 'Поле ввода не найдено'
                self.take_screenshot(url, 'error_no_input')
                
                # Дополнительная отладка
                self.log("=== ОТЛАДОЧНАЯ ИНФОРМАЦИЯ ===", "ERROR")
                self.log(f"Тип чата: {self.detected_chat_type}", "ERROR")
                self.log(f"В iframe: {self.in_iframe_context}", "ERROR")
                self.log("=" * 30, "ERROR")
                
                return result
            
            # Скриншот с найденным полем
            self.take_screenshot(url, 'step3_input_found')
            
            # 4. Проверка элемента (кроме amoCRM)
            if self.detected_chat_type != 'amocrm':
                if not self.is_chat_element(input_field):
                    result['error'] = 'Найденное поле не является чатом'
                    self.take_screenshot(url, 'error_not_chat')
                    return result
            
            self.log("→ Ввод сообщения...")
            
            # 5. Клик и активация поля
            try:
                self.try_click_element(input_field, "поле ввода")
            except:
                try:
                    input_field.click()
                except:
                    pass
            
            # АНТИДЕТЕКТ: Задержка
            if self.use_antidetect:
                self.antidetect.random_delay(0.3, 0.7)
            else:
                time.sleep(0.5)
            
            # 6. Очистка
            try:
                input_field.clear()
            except:
                pass
            
            time.sleep(0.3)
            
            # 7. Ввод текста
            try:
                if self.use_antidetect:
                    self.antidetect.human_typing(input_field, message, 'normal' if not self.fast_mode else 'fast')
                else:
                    if self.fast_mode and len(message) > 20:
                        input_field.send_keys(message)
                    else:
                        for char in message:
                            input_field.send_keys(char)
                            time.sleep(self.typing_delay)
                
                self.log("✓ Текст введен")
            except Exception as e:
                self.log(f"✗ Ошибка ввода текста: {e}", "ERROR")
                result['error'] = f'Ошибка ввода текста: {e}'
                self.take_screenshot(url, 'error_typing')
                return result
            
            # Скриншот с введенным текстом
            self.take_screenshot(url, 'step4_text_entered')
            
            # ИСПРАВЛЕНО: Увеличенная задержка перед отправкой
            if self.use_antidetect:
                self.antidetect.random_delay(0.8, 1.5)  # было 0.5, 1.2
            else:
                time.sleep(self.delay_before_send)
            
            # 8. Отправка
            sent = False
            
            # Пробуем найти кнопку (в текущем контексте!)
            if self.detected_chat_type and self.detected_chat_type in self.CHAT_SELECTORS:
                for selector in self.CHAT_SELECTORS[self.detected_chat_type]['send']:
                    try:
                        by_type = By.CSS_SELECTOR if selector['type'] == 'css' else By.XPATH
                        send_button = self.driver.find_element(by_type, selector['value'])
                        
                        if self.is_element_visible(send_button):
                            if self.try_click_element(send_button, "кнопка отправки"):
                                sent = True
                                self.log("✓ Кнопка отправки нажата")
                                break
                    except:
                        continue
            
            # Enter если не нашли кнопку
            if not sent:
                try:
                    input_field.send_keys(Keys.RETURN)
                    self.log("✓ Отправлено (Enter)")
                except Exception as e:
                    self.log(f"✗ Ошибка отправки Enter: {e}", "ERROR")
                    result['error'] = f'Ошибка отправки: {e}'
                    return result
            
            # ИСПРАВЛЕНО: Увеличенная задержка после отправки
            if self.use_antidetect:
                self.antidetect.random_delay(2, 3)  # было 1.5, 2.5
            else:
                time.sleep(self.delay_after_send)
            
            # 9. Скриншот успеха
            screenshot_path = self.take_screenshot(url, 'success')
            
            result['status'] = 'success'
            result['chat_type'] = self.detected_chat_type
            result['screenshot'] = screenshot_path
            
            self.log("="*70)
            self.log("✓✓✓ УСПЕШНО ОТПРАВЛЕНО ✓✓✓")
            self.log("="*70)
            
        except Exception as e:
            self.log(f"✗ КРИТИЧЕСКАЯ ОШИБКА: {e}", "ERROR")
            result['error'] = str(e)
            self.take_screenshot(url, 'error_exception')
            
            import traceback
            self.log(traceback.format_exc(), "ERROR")
            
        finally:
            # Возврат из iframe
            self.switch_to_default_content()
            
            result['duration'] = round(time.time() - start_time, 2)
            self.log(f"Время: {result['duration']}с\n")
            
        return result
             
    def take_screenshot(self, url, status='screenshot'):
        """Создание скриншота"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.replace('www.', '').replace('.', '_')
            timestamp = datetime.now().strftime('%H%M%S')
            filename = f"t{self.thread_id}_{domain}_{status}_{timestamp}.png"
            filepath = os.path.join(self.screenshots_folder, filename)
            
            self.driver.save_screenshot(filepath)
            self.log(f"✓ Скриншот: {filename}", "DEBUG")
            return filepath
        except Exception as e:
            self.log(f"Ошибка скриншота: {e}", "ERROR")
            return None
        
    def close(self):
        """Закрытие браузера"""
        try:
            self.driver.quit()
            self.log("✓ Браузер закрыт")
        except:
            pass


# ============================================================================
# МУЛЬТИПОТОЧНАЯ РАССЫЛКА
# ============================================================================

class MultiThreadMailer:
    """
    Менеджер мультипоточной рассылки с антидетектом
    """
    
    def __init__(self, max_workers=3, use_antidetect=True, proxy_manager=None):
        """
        Args:
            max_workers: Максимальное количество потоков
            use_antidetect: Использовать антидетект
            proxy_manager: Менеджер прокси
        """
        self.max_workers = max_workers
        self.use_antidetect = use_antidetect
        self.proxy_manager = proxy_manager
        self.active_threads = {}
        self.stop_event = threading.Event()
    
    def run_parallel_mailing(self, urls, message, settings, log_callback=None, progress_callback=None):
        """
        Параллельная обработка списка URL
        
        Args:
            urls: Список URL
            message: Сообщение для отправки
            settings: Настройки (session_folder, headless, fast_mode)
            log_callback: Функция для логирования
            progress_callback: Функция для обновления прогресса
            
        Returns:
            list: Список результатов
        """
        
        session_folder = settings['session_folder']
        results = []
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            
            # Создаем задачи для каждого URL
            for i, url in enumerate(urls):
                if self.stop_event.is_set():
                    break
                
                # Получаем прокси для потока (если есть)
                proxy = None
                if self.proxy_manager and self.proxy_manager.proxies:
                    proxy = self.proxy_manager.get_next_proxy()
                
                # Создаем задачу
                future = executor.submit(
                    self.process_single_url,
                    url, message, settings, i, proxy, log_callback
                )
                
                futures[future] = {'url': url, 'index': i}
            
            # Собираем результаты по мере выполнения
            for future in as_completed(futures):
                if self.stop_event.is_set():
                    break
                
                url_data = futures[future]
                
                try:
                    result = future.result(timeout=120)  # Таймаут 2 минуты на один URL
                    results.append(result)
                    
                    completed += 1
                    
                    # Обновляем прогресс
                    if progress_callback:
                        progress_callback(completed, len(urls))
                    
                except Exception as e:
                    # Ошибка выполнения задачи
                    results.append({
                        'url': url_data['url'],
                        'status': 'error',
                        'error': f'Thread execution error: {str(e)}',
                        'thread_id': url_data['index']
                    })
                    
                    if log_callback:
                        log_callback(f"[Thread-{url_data['index']}] КРИТИЧЕСКАЯ ОШИБКА: {e}", "ERROR")
        
        return results
    
    def process_single_url(self, url, message, settings, thread_id, proxy, log_callback):
        """
        Обработка одного URL в отдельном потоке
        
        Args:
            url: URL сайта
            message: Сообщение
            settings: Настройки
            thread_id: ID потока
            proxy: Прокси
            log_callback: Функция логирования
            
        Returns:
            dict: Результат обработки
        """
        
        bot = None
        
        try:
            # Создаем отдельный экземпляр бота для потока
            bot = ChatBot(
                session_folder=settings['session_folder'],
                thread_id=thread_id,
                headless=settings.get('headless', False),
                timeout=10,
                fast_mode=settings.get('fast_mode', True),
                use_antidetect=self.use_antidetect,
                proxy=proxy,
                log_callback=log_callback
            )
            
            # Отправляем сообщение
            result = bot.send_message(url, message)
            
            return result
            
        except Exception as e:
            return {
                'url': url,
                'status': 'error',
                'error': str(e),
                'thread_id': thread_id,
                'duration': 0
            }
        finally:
            # Закрываем браузер
            if bot:
                bot.close()
    
    def stop(self):
        """Остановка всех потоков"""
        self.stop_event.set()


# ============================================================================
# MAILING MANAGER
# ============================================================================

class MailingManager:
    """Менеджер рассылок (создание сессий, загрузка URL, отчеты)"""
    
    def __init__(self):
        self.base_folder = 'mailings'
        os.makedirs(self.base_folder, exist_ok=True)
        
    def create_session(self):
        """Создать новую сессию рассылки"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        session_folder = os.path.join(self.base_folder, f'session_{timestamp}')
        os.makedirs(session_folder, exist_ok=True)
        return session_folder
        
    def load_urls_from_file(self, filepath):
        """Загрузить URL из файла (Excel/CSV/TXT)"""
        urls = []
        
        try:
            ext = os.path.splitext(filepath)[1].lower()
            
            if ext in ['.xlsx', '.xls']:
                df = pd.read_excel(filepath)
                url_columns = [col for col in df.columns if 'url' in col.lower() or 'site' in col.lower() or 'link' in col.lower()]
                if url_columns:
                    urls = df[url_columns[0]].dropna().tolist()
                else:
                    urls = df.iloc[:, 0].dropna().tolist()
                    
            elif ext == '.csv':
                df = pd.read_csv(filepath)
                url_columns = [col for col in df.columns if 'url' in col.lower() or 'site' in col.lower()]
                if url_columns:
                    urls = df[url_columns[0]].dropna().tolist()
                else:
                    urls = df.iloc[:, 0].dropna().tolist()
                    
            elif ext == '.txt':
                with open(filepath, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip()]
                    
            # Фильтруем только валидные URL
            urls = [url for url in urls if isinstance(url, str) and url.startswith('http')]
            
            return urls
            
        except Exception as e:
            print(f"Ошибка загрузки файла: {e}")
            return []
            
    def save_report(self, session_folder, results):
        """Сохранить отчет о рассылке (JSON + TXT)"""
        
        # JSON отчет
        report_json = os.path.join(session_folder, 'report.json')
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total': len(results),
            'success': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] == 'error']),
            'results': results
        }
        
        with open(report_json, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4, ensure_ascii=False)
            
        # TXT отчет
        report_txt = os.path.join(session_folder, 'report.txt')
        with open(report_txt, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("ОТЧЕТ О РАССЫЛКЕ (v2.1 ИСПРАВЛЕННАЯ)\n")
            f.write("="*70 + "\n\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Всего сайтов: {summary['total']}\n")
            f.write(f"Успешно отправлено: {summary['success']}\n")
            f.write(f"Ошибок: {summary['failed']}\n")
            f.write(f"Успешность: {round(summary['success']/summary['total']*100, 1) if summary['total'] > 0 else 0}%\n\n")
            f.write("="*70 + "\n")
            f.write("ДЕТАЛИ:\n")
            f.write("="*70 + "\n\n")
            
            for i, r in enumerate(results, 1):
                f.write(f"{i}. {r['url']}\n")
                f.write(f"   Поток: Thread-{r.get('thread_id', '?')}\n")
                f.write(f"   Статус: {'✓ Успех' if r['status'] == 'success' else '✗ Ошибка'}\n")
                if r.get('chat_type'):
                    f.write(f"   Тип чата: {r['chat_type'].upper()}\n")
                if r.get('error'):
                    f.write(f"   Ошибка: {r['error']}\n")
                f.write(f"   Время выполнения: {r.get('duration', 0)}с\n")
                if r.get('screenshot'):
                    f.write(f"   Скриншот: {os.path.basename(r['screenshot'])}\n")
                f.write("\n")
        
        print(f"\n✓ Отчет сохранен: {report_txt}")

# ============================================================================
# GUI - ПОЛНАЯ ВЕРСИЯ v2.1 ИСПРАВЛЕННАЯ
# ============================================================================

class ChatBotGUI:
    """
    Графический интерфейс для ChatBot v2.1
    ИСПРАВЛЕННАЯ ВЕРСИЯ
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("ChatBot v2.1 - Мультипоточность + Антидетект (ИСПРАВЛЕННАЯ)")
        self.root.geometry("1050x850")
        self.root.resizable(True, True)
        
        # Переменные
        self.urls = []
        self.is_running = False
        self.manager = MailingManager()
        self.log_queue = queue.Queue()
        self.multi_mailer = None
        self.proxy_manager = None
        
        # Настройка стилей
        self.setup_styles()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Запуск проверки очереди логов
        self.check_log_queue()
    
    def setup_styles(self):
        """Настройка стилей ttk"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Стиль для кнопки запуска
        style.configure('Accent.TButton', 
                       font=('Arial', 10, 'bold'),
                       foreground='#2196F3')
        
        # Стиль для кнопки остановки
        style.configure('Stop.TButton', 
                       font=('Arial', 10, 'bold'),
                       foreground='#f44336')
    
    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        
        # ========== ВЕРХНЯЯ ПАНЕЛЬ (Заголовок) ==========
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(top_frame, 
                                text="ChatBot v2.1 - Мультипоточность + Антидетект (ИСПРАВЛЕННАЯ)", 
                                font=('Arial', 15, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(top_frame, 
                                   text="Поддержка 15+ чатов | Параллельная обработка | Антидетект защита | Исправлены ошибки контекста", 
                                   font=('Arial', 9), 
                                   foreground='gray')
        subtitle_label.pack()
        
        # ========== NOTEBOOK (Вкладки) ==========
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ========== ВКЛАДКА 1: НАСТРОЙКИ ==========
        settings_frame = ttk.Frame(notebook, padding=10)
        notebook.add(settings_frame, text="📝 Настройки")
        
        # --- Фрейм для списка URL ---
        url_frame = ttk.LabelFrame(settings_frame, text="Сайты для рассылки", padding=10)
        url_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Кнопки управления URL
        url_buttons = ttk.Frame(url_frame)
        url_buttons.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(url_buttons, text="➕ Добавить URL", 
                  command=self.add_url).pack(side=tk.LEFT, padx=2)
        ttk.Button(url_buttons, text="📁 Загрузить из файла", 
                  command=self.load_from_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(url_buttons, text="🗑 Очистить список", 
                  command=self.clear_urls).pack(side=tk.LEFT, padx=2)
        ttk.Button(url_buttons, text="❌ Удалить выбранный", 
                  command=self.delete_selected_url).pack(side=tk.LEFT, padx=2)
        
        # Счетчик URL
        self.url_count_label = ttk.Label(url_buttons, text="URL: 0", font=('Arial', 9, 'bold'))
        self.url_count_label.pack(side=tk.RIGHT, padx=5)
        
        # Список URL (с полосой прокрутки)
        url_list_frame = ttk.Frame(url_frame)
        url_list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(url_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.url_listbox = tk.Listbox(url_list_frame, 
                                       yscrollcommand=scrollbar.set, 
                                       height=6,
                                       font=('Consolas', 9))
        self.url_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.url_listbox.yview)
        
        # --- Фрейм для сообщения ---
        msg_frame = ttk.LabelFrame(settings_frame, text="Сообщение для отправки", padding=10)
        msg_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.message_text = scrolledtext.ScrolledText(msg_frame, 
                                                       height=4, 
                                                       wrap=tk.WORD,
                                                       font=('Arial', 10))
        self.message_text.pack(fill=tk.BOTH, expand=True)
        
        # Счетчик символов
        msg_info_frame = ttk.Frame(msg_frame)
        msg_info_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.char_count_label = ttk.Label(msg_info_frame, text="Символов: 0", 
                                          font=('Arial', 8), foreground='gray')
        self.char_count_label.pack(side=tk.RIGHT)
        
        self.message_text.bind('<KeyRelease>', self.update_char_count)
        
        # --- Фрейм для параметров ---
        options_frame = ttk.LabelFrame(settings_frame, text="Параметры рассылки", padding=10)
        options_frame.pack(fill=tk.X)
        
        # Две колонки для параметров
        col1 = ttk.Frame(options_frame)
        col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        col2 = ttk.Frame(options_frame)
        col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        # Колонка 1: Основные параметры
        self.fast_mode_var = tk.BooleanVar(value=True)
        self.headless_var = tk.BooleanVar(value=False)
        self.antidetect_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(col1, text="⚡ Быстрый режим", 
                       variable=self.fast_mode_var).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(col1, text="🔇 Фоновый режим (без GUI браузера)", 
                       variable=self.headless_var).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(col1, text="🛡️ Антидетект (рекомендуется)", 
                       variable=self.antidetect_var).pack(anchor=tk.W, pady=2)
        
        # Колонка 2: Потоки и прокси
        ttk.Label(col2, text="Количество потоков (1-10):").pack(anchor=tk.W)
        
        self.threads_var = tk.IntVar(value=3)
        threads_frame = ttk.Frame(col2)
        threads_frame.pack(fill=tk.X, pady=(0, 10))
        
        threads_spinbox = ttk.Spinbox(threads_frame, from_=1, to=10, 
                                      textvariable=self.threads_var, width=10)
        threads_spinbox.pack(side=tk.LEFT)
        
        ttk.Label(threads_frame, text="(рекомендуется 3-5)", 
                 font=('Arial', 8), foreground='gray').pack(side=tk.LEFT, padx=(5, 0))
        
        # Прокси
        proxy_frame = ttk.Frame(col2)
        proxy_frame.pack(fill=tk.X)
        
        ttk.Button(proxy_frame, text="📡 Загрузить прокси", 
                  command=self.load_proxies).pack(side=tk.LEFT)
        
        self.proxy_count_label = ttk.Label(proxy_frame, text="Прокси: 0", 
                                           font=('Arial', 8))
        self.proxy_count_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # ========== ВКЛАДКА 2: ПРОГРЕСС РАССЫЛКИ ==========
        progress_frame = ttk.Frame(notebook, padding=10)
        notebook.add(progress_frame, text="📊 Прогресс рассылки")
        
        # --- Статистика ---
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_label = ttk.Label(stats_frame, 
                                      text="Готов к запуску", 
                                      font=('Arial', 12, 'bold'))
        self.stats_label.pack()
        
        self.progress_label = ttk.Label(stats_frame, 
                                        text="", 
                                        font=('Arial', 9))
        self.progress_label.pack()
        
        # --- Прогресс-бар ---
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                            mode='determinate',
                                            length=300)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Процент выполнения
        self.percent_label = ttk.Label(progress_frame, 
                                       text="0%", 
                                       font=('Arial', 10, 'bold'))
        self.percent_label.pack()
        
        # --- Фрейм для логов ---
        log_frame = ttk.LabelFrame(progress_frame, text="Логи выполнения (мультипоточные)", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Кнопки управления логами
        log_buttons = ttk.Frame(log_frame)
        log_buttons.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(log_buttons, text="🗑 Очистить логи", 
                  command=self.clear_logs).pack(side=tk.LEFT, padx=2)
        ttk.Button(log_buttons, text="💾 Сохранить логи", 
                  command=self.save_logs).pack(side=tk.LEFT, padx=2)
        
        # Текстовое поле для логов
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                   height=20, 
                                                   state='disabled', 
                                                   bg='#1e1e1e', 
                                                   fg='#00ff00', 
                                                   font=('Consolas', 9),
                                                   wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # ========== ВКЛАДКА 3: О ПРОГРАММЕ ==========
        about_frame = ttk.Frame(notebook, padding=20)
        notebook.add(about_frame, text="ℹ️ О программе")
        
        about_text = """
ChatBot v2.1 - ИСПРАВЛЕННАЯ ВЕРСИЯ

🔧 ИСПРАВЛЕНИЯ В ВЕРСИИ 2.1:
• Исправлены ошибки GPU в headless режиме
• Улучшена работа с iframe (явное отслеживание контекста)
• Устранена потеря контекста при переключении между iframe
• Увеличены задержки для более надежной работы
• Улучшена обработка amoCRM и JivoChat
• Добавлено подавление GPU логов
• Исправлено дублирование переключения контекста
• Более мягкая проверка принадлежности элементов к чату

🚀 ОСНОВНЫЕ ВОЗМОЖНОСТИ:
• Параллельная обработка до 10 сайтов одновременно
• Поддержка 15+ популярных онлайн чатов
• Массовая рассылка с детальными отчетами
• Импорт URL из Excel, CSV, TXT файлов
• Скриншоты всех отправленных сообщений

🛡️ АНТИДЕТЕКТ ЗАЩИТА:
• Ротация User-Agent (25+ различных браузеров)
• Случайные задержки между действиями
• Имитация человеческого ввода текста
• Случайные движения мыши перед кликом
• Защита от WebGL/Canvas fingerprinting
• Скрытие признаков автоматизации

🎯 ПОДДЕРЖИВАЕМЫЕ ЧАТЫ:
• JivoChat - популярный русский чат ✓ УЛУЧШЕНО
• Bitrix24 - CRM система с чатом
• amoCRM - CRM с онлайн консультантом ✓ УЛУЧШЕНО
• Intercom - международный чат
• Tawk.to - бесплатный чат
• Drift - маркетинговый чат
• Crisp - современный чат
• LiveChat - профессиональный чат
• Carrot Quest - русский чат
• Chatra - простой чат
• LiveTex - корпоративный чат
• FreshChat - от FreshWorks
• Envybox - виджет обратного звонка
• RedHelper - помощник продаж
• Dashly - маркетинговая платформа

⚡ ПРОИЗВОДИТЕЛЬНОСТЬ:
• В 3-5 раз быстрее однопоточной версии
• Оптимизированное использование ресурсов
• Автоматическое восстановление после ошибок
• Поддержка прокси-серверов для масштабирования

📊 ОТЧЕТНОСТЬ:
• Детальные логи по каждому потоку
• Скриншоты всех отправок (успех/ошибка)
• JSON и TXT отчеты
• Статистика успешности по типам чатов
• История всех рассылок

🔌 ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ:
• Поддержка HTTP/HTTPS прокси
• Ротация прокси между потоками
• Импорт URL из различных форматов
• Сохранение конфигурации
• Автоматическая загрузка ChromeDriver

💡 РЕКОМЕНДАЦИИ:
• Используйте 3-5 потоков для оптимальной работы
• Включайте антидетект для массовых рассылок (100+ сайтов)
• Используйте прокси при большом объеме
• Проверяйте URL перед рассылкой
• Сохраняйте отчеты для анализа
• В headless режиме GPU отключен автоматически

⚙️ СИСТЕМНЫЕ ТРЕБОВАНИЯ:
• Windows 10/11 (64-bit)
• Google Chrome (устанавливается автоматически)
• Интернет-соединение
• 4 GB RAM (рекомендуется 8 GB для 5+ потоков)

📋 ФОРМАТ ФАЙЛОВ ДЛЯ ИМПОРТА:
• Excel (.xlsx, .xls) - колонка с именем "url" или "site"
• CSV (.csv) - первая колонка или колонка "url"
• Text (.txt) - один URL на строку

🔧 ФОРМАТ ПРОКСИ:
• ip:port
• ip:port:username:password

🐛 ИЗВЕСТНЫЕ ОГРАНИЧЕНИЯ:
• GPU ошибки в логах в headless режиме (не критично, GPU отключен)
• Некоторые сайты могут требовать дополнительных задержек

Версия: 2.1 (Fixed - Multithread + Antidetect)
Автор: ChatBot Development Team
Дата исправления: 31.10.2024
Лицензия: Commercial
        """
        
        about_scroll = scrolledtext.ScrolledText(about_frame, 
                                                 wrap=tk.WORD,
                                                 font=('Arial', 9))
        about_scroll.pack(fill=tk.BOTH, expand=True)
        about_scroll.insert('1.0', about_text)
        about_scroll.config(state='disabled')
        
        # ========== НИЖНЯЯ ПАНЕЛЬ (Кнопки управления) ==========
        bottom_frame = ttk.Frame(self.root, padding=10)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Левая часть - кнопки запуска/остановки
        left_buttons = ttk.Frame(bottom_frame)
        left_buttons.pack(side=tk.LEFT)
        
        self.start_button = ttk.Button(left_buttons, 
                                       text="▶ НАЧАТЬ РАССЫЛКУ", 
                                       command=self.start_mailing, 
                                       style='Accent.TButton',
                                       width=20)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(left_buttons, 
                                      text="⏹ ОСТАНОВИТЬ", 
                                      command=self.stop_mailing, 
                                      style='Stop.TButton',
                                      state='disabled',
                                      width=15)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Правая часть - дополнительные кнопки
        right_buttons = ttk.Frame(bottom_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(right_buttons, 
                  text="📂 Открыть папку с отчетами", 
                  command=self.open_reports_folder).pack(side=tk.RIGHT, padx=5)
    
    # ========== ФУНКЦИИ УПРАВЛЕНИЯ URL ==========
    
    def update_char_count(self, event=None):
        """Обновление счетчика символов в сообщении"""
        text = self.message_text.get("1.0", tk.END).strip()
        count = len(text)
        self.char_count_label.config(text=f"Символов: {count}")
    
    def update_url_count(self):
        """Обновление счетчика URL"""
        count = len(self.urls)
        self.url_count_label.config(text=f"URL: {count}")
    
    def add_url(self):
        """Добавление URL через диалоговое окно"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить URL")
        dialog.geometry("500x180")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, 
                 text="Введите URL сайта:", 
                 font=('Arial', 10)).pack(pady=10)
        
        url_entry = ttk.Entry(dialog, width=60, font=('Arial', 10))
        url_entry.pack(pady=5, padx=20)
        url_entry.focus()
        
        info_label = ttk.Label(dialog, 
                              text="URL должен начинаться с http:// или https://", 
                              font=('Arial', 8), 
                              foreground='gray')
        info_label.pack()
        
        def add():
            url = url_entry.get().strip()
            if url and url.startswith('http'):
                self.urls.append(url)
                self.url_listbox.insert(tk.END, url)
                self.update_url_count()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", 
                                    "Введите корректный URL\n(должен начинаться с http:// или https://)")
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Добавить", command=add, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)
        
        url_entry.bind('<Return>', lambda e: add())
    
    def delete_selected_url(self):
        """Удаление выбранного URL из списка"""
        selection = self.url_listbox.curselection()
        if selection:
            index = selection[0]
            self.url_listbox.delete(index)
            del self.urls[index]
            self.update_url_count()
        else:
            messagebox.showinfo("Информация", "Выберите URL для удаления из списка")
    
    def load_from_file(self):
        """Загрузка URL из файла"""
        filepath = filedialog.askopenfilename(
            title="Выберите файл со списком URL",
            filetypes=[
                ("Excel файлы", "*.xlsx *.xls"),
                ("CSV файлы", "*.csv"),
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*")
            ]
        )
        
        if filepath:
            urls = self.manager.load_urls_from_file(filepath)
            if urls:
                self.urls.extend(urls)
                for url in urls:
                    self.url_listbox.insert(tk.END, url)
                self.update_url_count()
                messagebox.showinfo("Успех", f"Загружено {len(urls)} URL из файла")
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить URL из файла")
    
    def clear_urls(self):
        """Очистка всего списка URL"""
        if self.urls and messagebox.askyesno("Подтверждение", "Очистить весь список URL?"):
            self.urls.clear()
            self.url_listbox.delete(0, tk.END)
            self.update_url_count()
    
    def load_proxies(self):
        """Загрузка прокси из файла"""
        filepath = filedialog.askopenfilename(
            title="Выберите файл с прокси",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filepath:
            self.proxy_manager = ProxyManager(filepath)
            count = len(self.proxy_manager.proxies)
            self.proxy_count_label.config(text=f"Прокси: {count}")
            messagebox.showinfo("Успех", f"Загружено {count} прокси\n\nФормат поддерживаемых прокси:\n- ip:port\n- ip:port:user:pass")
    
    # ========== ФУНКЦИИ УПРАВЛЕНИЯ ЛОГАМИ ==========
    
    def clear_logs(self):
        """Очистка логов"""
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state='disabled')
    
    def save_logs(self):
        """Сохранение логов в файл"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"chatbot_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filepath:
            try:
                logs = self.log_text.get("1.0", tk.END)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(logs)
                messagebox.showinfo("Успех", f"Логи сохранены в:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить логи:\n{e}")
    
    def log_message(self, message, level="INFO"):
        """Добавление сообщения в очередь логов"""
        self.log_queue.put((message, level))
    
    def check_log_queue(self):
        """Проверка очереди логов и обновление GUI"""
        try:
            while True:
                message, level = self.log_queue.get_nowait()
                
                self.log_text.config(state='normal')
                
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                # Настройка цветов для разных уровней
                if level == "ERROR":
                    tag = 'error'
                    self.log_text.tag_config('error', foreground='#ff4444')
                elif level == "WARNING":
                    tag = 'warning'
                    self.log_text.tag_config('warning', foreground='#ffaa00')
                elif level == "DEBUG":
                    tag = 'debug'
                    self.log_text.tag_config('debug', foreground='#888888')
                else:
                    tag = 'info'
                    self.log_text.tag_config('info', foreground='#00ff00')
                
                self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
                self.log_text.see(tk.END)
                self.log_text.config(state='disabled')
                
        except queue.Empty:
            pass
        
        # Повторная проверка через 100мс
        self.root.after(100, self.check_log_queue)
    
    # ========== ФУНКЦИИ УПРАВЛЕНИЯ РАССЫЛКОЙ ==========
    
    def start_mailing(self):
        """Запуск рассылки"""
        # Проверки
        if not self.urls:
            messagebox.showerror("Ошибка", "Добавьте хотя бы один URL для рассылки!")
            return
        
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showerror("Ошибка", "Введите сообщение для отправки!")
            return
        
        # Подтверждение
        confirm_text = f"""Начать рассылку?

Параметры:
• Сайтов: {len(self.urls)}
• Потоков: {self.threads_var.get()}
• Быстрый режим: {'Да' if self.fast_mode_var.get() else 'Нет'}
• Антидетект: {'Да' if self.antidetect_var.get() else 'Нет'}
• Фоновый режим: {'Да' if self.headless_var.get() else 'Нет'}
• Прокси: {len(self.proxy_manager.proxies) if self.proxy_manager else 0}

ВНИМАНИЕ: В фоновом режиме GPU будет отключен автоматически.

Продолжить?"""
        
        if not messagebox.askyesno("Подтверждение", confirm_text):
            return
        
        # Блокировка интерфейса
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        # Сброс прогресса
        self.progress_bar['value'] = 0
        self.percent_label.config(text="0%")
        
        # Очистка логов
        self.clear_logs()
        
        # Запуск в отдельном потоке
        thread = threading.Thread(target=self.run_mailing, 
                                 args=(message,), 
                                 daemon=True)
        thread.start()
    
    def stop_mailing(self):
        """Остановка рассылки"""
        if messagebox.askyesno("Подтверждение", "Остановить выполнение рассылки?"):
            self.is_running = False
            if self.multi_mailer:
                self.multi_mailer.stop()
            self.log_message("⚠ Остановка рассылки пользователем...", "WARNING")
    
    def run_mailing(self, message):
        """Основной процесс рассылки (выполняется в отдельном потоке)"""
        session_folder = self.manager.create_session()
        
        self.log_message("="*70)
        self.log_message("НАЧАЛО РАССЫЛКИ v2.1 (ИСПРАВЛЕННАЯ ВЕРСИЯ)")
        self.log_message("="*70)
        self.log_message(f"Сессия: {os.path.basename(session_folder)}")
        self.log_message(f"Сайтов: {len(self.urls)}")
        self.log_message(f"Потоков: {self.threads_var.get()}")
        self.log_message(f"Быстрый режим: {'Включен' if self.fast_mode_var.get() else 'Выключен'}")
        self.log_message(f"Антидетект: {'Включен' if self.antidetect_var.get() else 'Выключен'}")
        self.log_message(f"Фоновый режим: {'Включен (GPU отключен)' if self.headless_var.get() else 'Выключен'}")
        if self.proxy_manager:
            self.log_message(f"Прокси: {len(self.proxy_manager.proxies)} шт.")
        self.log_message("="*70)
        
        results = []
        
        try:
            # Создаем мультипоточный обработчик
            self.multi_mailer = MultiThreadMailer(
                max_workers=self.threads_var.get(),
                use_antidetect=self.antidetect_var.get(),
                proxy_manager=self.proxy_manager
            )
            
            settings = {
                'session_folder': session_folder,
                'headless': self.headless_var.get(),
                'fast_mode': self.fast_mode_var.get(),
            }
            
            def progress_callback(completed, total):
                """Обновление прогресса"""
                progress = (completed / total) * 100
                self.progress_bar['value'] = progress
                self.percent_label.config(text=f"{int(progress)}%")
                self.stats_label.config(text=f"Обработано {completed} из {total}")
            
            # Запуск параллельной обработки
            results = self.multi_mailer.run_parallel_mailing(
                self.urls, message, settings,
                log_callback=self.log_message,
                progress_callback=progress_callback
            )
            
        except Exception as e:
            self.log_message(f"КРИТИЧЕСКАЯ ОШИБКА: {e}", "ERROR")
            import traceback
            self.log_message(traceback.format_exc(), "ERROR")
        finally:
            # Сохранение отчета
            self.manager.save_report(session_folder, results)
            
            # Финальная статистика
            success_count = len([r for r in results if r['status'] == 'success'])
            failed_count = len(results) - success_count
            total_time = sum(r.get('duration', 0) for r in results)
            
            self.log_message("")
            self.log_message("="*70)
            self.log_message("РАССЫЛКА ЗАВЕРШЕНА")
            self.log_message("="*70)
            self.log_message(f"Обработано: {len(results)} из {len(self.urls)}")
            self.log_message(f"Успешно: {success_count}")
            self.log_message(f"Ошибок: {failed_count}")
            self.log_message(f"Успешность: {round(success_count/len(results)*100, 1) if results else 0}%")
            self.log_message(f"Общее время: {round(total_time, 1)}с")
            self.log_message(f"Среднее время на сайт: {round(total_time/len(results), 1) if results else 0}с")
            self.log_message(f"Папка с отчетами: {session_folder}")
            self.log_message("="*70)
            
            # Обновление GUI
            self.progress_bar['value'] = 100
            self.percent_label.config(text="100%")
            self.stats_label.config(text=f"Завершено: {success_count}/{len(results)} успешно")
            self.progress_label.config(text="")
            
            # Разблокировка интерфейса
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.is_running = False
            
            # Уведомление
            messagebox.showinfo("Рассылка завершена", 
                              f"Рассылка успешно завершена!\n\n"
                              f"Обработано: {len(results)}\n"
                              f"Успешно: {success_count}\n"
                              f"Ошибок: {failed_count}\n"
                              f"Успешность: {round(success_count/len(results)*100, 1) if results else 0}%\n\n"
                              f"Отчеты сохранены в:\n{session_folder}")
    
    def open_reports_folder(self):
        """Открытие папки с отчетами"""
        folder = os.path.abspath(self.manager.base_folder)
        if os.path.exists(folder):
            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                os.system(f'open "{folder}"')
            else:
                os.system(f'xdg-open "{folder}"')
        else:
            messagebox.showinfo("Информация", 
                              "Папка с отчетами пока пуста.\n"
                              "Запустите хотя бы одну рассылку.")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Главная функция - запуск приложения"""
    
    # Настройка кодировки для Windows
    if sys.platform == 'win32':
        try:
            os.system('chcp 65001 >nul 2>&1')
        except:
            pass
    
    # Создание и запуск GUI
    root = tk.Tk()
    app = ChatBotGUI(root)
    
    # Обработка закрытия окна
    def on_closing():
        if app.is_running:
            if messagebox.askyesno("Подтверждение", 
                                  "Рассылка выполняется.\n"
                                  "Вы уверены, что хотите выйти?"):
                app.is_running = False
                if app.multi_mailer:
                    app.multi_mailer.stop()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Запуск главного цикла
    root.mainloop()


if __name__ == "__main__":
    main()