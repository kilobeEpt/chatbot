# -*- coding: utf-8 -*-

CHAT_SELECTORS_META = {
    "version": "2025-12-15",
    "owner": "chatbot_v2v2",
}

# NOTE: This dataset is intentionally kept as plain Python for easy edits.
CHAT_SELECTORS = {
    'jivochat': {
        'button': [
            {'type': 'css', 'value': 'jdiv[id*="jivo"]'},
            {'type': 'xpath', 'value': '//jdiv[contains(@id, "jivo")]'},
            {'type': 'xpath', 'value': '//jdiv[contains(@class, "label")]'},
            {'type': 'xpath', 'value': '//jdiv[@class and contains(@class, "label")]'},
            {'type': 'css', 'value': 'jdiv'},
            {'type': 'xpath', 'value': '//jdiv'},
            {'type': 'css', 'value': 'div[id*="jivo"]'},
            {'type': 'xpath', 'value': '//div[contains(@id, "jivo")]'},
            {'type': 'css', 'value': 'iframe[id*="jivo"]'},
            {'type': 'xpath', 'value': '//iframe[contains(@id, "jivo")]'},
        ],
        'input': [
            {'type': 'css', 'value': 'textarea.inputField__nHBvS'},
            {'type': 'xpath', 'value': '//textarea[contains(@class, "inputField")]'},
            {'type': 'xpath', 'value': '//textarea[contains(@placeholder, "Введите")]'},
            {'type': 'xpath', 'value': '//textarea[@placeholder="Введите сообщение"]'},
            {'type': 'xpath', 'value': '//textarea[contains(@placeholder, "сообщение")]'},
            {'type': 'xpath', 'value': '//textarea[contains(@placeholder, "message")]'},
            {'type': 'xpath', 'value': '//jdiv//textarea'},
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
            {'type': 'css', 'value': '.amo-button.amo-button--main'},
            {'type': 'css', 'value': '#amobutton'},
            {'type': 'css', 'value': '.amo-button'},
            {'type': 'xpath', 'value': '//div[contains(@class, "amo-button")]'},
            {'type': 'xpath', 'value': '//div[@id="amobutton"]'},
            {'type': 'css', 'value': '.amo-button-holder'},
        ],
        'input': [
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
    },

    # Newly added datasets
    'zendesk': {
        'meta': {'owner': 'community', 'version': '2025-12-15'},
        'button': [
            {'type': 'css', 'value': '.zEWidget-launcher'},
            {'type': 'css', 'value': '.zEWidget-launcher--active'},
            {'type': 'css', 'value': 'iframe[id*="zopim"]'},
            {'type': 'css', 'value': 'iframe[src*="zendesk"], iframe[src*="zopim"]'},
            {'type': 'xpath', 'value': '//iframe[contains(@id, "zopim") or contains(@src, "zendesk") or contains(@src, "zopim")]'},
        ],
        'input': [
            {'type': 'css', 'value': 'textarea'},
            {'type': 'xpath', 'value': '//textarea'},
        ],
        'send': [
            {'type': 'css', 'value': 'button[type="submit"]'},
            {'type': 'xpath', 'value': '//button[@type="submit" or contains(., "Send") or contains(., "Отправить")]'},
        ],
        'iframe': ['zopim', 'zendesk'],
        'markers': ['zopim', 'zendesk', 'zEWidget'],
        'js_api': 'window.zE && zE("webWidget", "open")'
    },

    'helpcrunch': {
        'meta': {'owner': 'community', 'version': '2025-12-15'},
        'button': [
            {'type': 'css', 'value': '.helpcrunch-widget'},
            {'type': 'css', 'value': '.helpcrunch-launcher'},
            {'type': 'css', 'value': 'iframe[src*="helpcrunch"]'},
            {'type': 'xpath', 'value': '//iframe[contains(@src, "helpcrunch")]'},
        ],
        'input': [
            {'type': 'css', 'value': 'textarea'},
            {'type': 'xpath', 'value': '//textarea'},
        ],
        'send': [
            {'type': 'css', 'value': 'button[type="submit"]'},
            {'type': 'xpath', 'value': '//button[@type="submit" or contains(., "Send") or contains(., "Отправить")]'},
        ],
        'iframe': ['helpcrunch'],
        'markers': ['helpcrunch'],
        'js_api': 'window.HelpCrunch && HelpCrunch("open")'
    },
}
