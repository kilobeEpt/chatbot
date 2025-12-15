"""
CAPTCHA Solver Module
Handles automated CAPTCHA solving via 2captcha API (reCAPTCHA v2/v3, hCaptcha)
"""

import requests
import time
import logging
from typing import Optional, Dict, Any
from enum import Enum


class CaptchaType(Enum):
    """Supported CAPTCHA types"""
    RECAPTCHA_V2 = "recaptcha_v2"
    RECAPTCHA_V3 = "recaptcha_v3"
    HCAPTCHA = "hcaptcha"
    CLOUDFLARE = "cloudflare"


class CaptchaSolverError(Exception):
    """Base exception for CAPTCHA solver errors"""
    pass


class CaptchaSolver:
    """
    2Captcha API wrapper for solving CAPTCHA challenges
    Supports: reCAPTCHA v2, reCAPTCHA v3, hCaptcha
    """

    API_SUBMIT_URL = "http://2captcha.com/api/upload"
    API_RESULT_URL = "http://2captcha.com/api/res.php"
    
    # Error codes from 2captcha
    ERROR_CODES = {
        'ERROR_CAPTCHA_UNSOLVABLE': 'Невозможно решить CAPTCHA',
        'ERROR_NO_SLOT_AVAILABLE': 'Нет свободных слотов',
        'ERROR_ZERO_BALANCE': 'Нулевой баланс аккаунта',
        'ERROR_IP_BANNED': 'IP заблокирован',
        'ERROR_IP_TEMPORARY_BANNED': 'IP временно заблокирован',
        'ERROR_CAPTCHA_ID_DOES_NOT_EXIST': 'ID CAPTCHA не существует',
        'ERROR_AUTHENTICATION_FAILED': 'Ошибка аутентификации',
    }

    def __init__(self, api_key: str, timeout: int = 180, verbose: bool = False):
        """
        Initialize CAPTCHA solver
        
        Args:
            api_key: 2captcha API key
            timeout: Timeout for solving (seconds, default 180)
            verbose: Enable detailed logging
        """
        if not api_key or not isinstance(api_key, str):
            raise CaptchaSolverError("Invalid API key provided")
        
        self.api_key = api_key
        self.timeout = timeout
        self.verbose = verbose
        self.logger = logging.getLogger('CaptchaSolver')
        
        if verbose:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def detect_captcha(self, page_source: str, page_url: str) -> Optional[Dict[str, Any]]:
        """
        Detect CAPTCHA presence in page source
        
        Returns:
            Dict with 'type', 'sitekey', 'action', or None if no CAPTCHA detected
        """
        captcha_info = None

        # Check for reCAPTCHA v2/v3
        if 'recaptcha' in page_source.lower():
            if 'data-sitekey' in page_source:
                import re
                match = re.search(r'data-sitekey=["\']([a-zA-Z0-9_-]+)["\']', page_source)
                if match:
                    sitekey = match.group(1)
                    captcha_info = {
                        'type': CaptchaType.RECAPTCHA_V2.value,
                        'sitekey': sitekey,
                        'page_url': page_url
                    }
                    
                    # Check if v3
                    if 'grecaptcha.execute' in page_source:
                        captcha_info['type'] = CaptchaType.RECAPTCHA_V3.value
                        import re
                        action_match = re.search(r"grecaptcha\.execute\(['\"]([^'\"]+)['\"]", page_source)
                        if action_match:
                            captcha_info['action'] = action_match.group(1)
            
            # Check for iframe-based reCAPTCHA
            if not captcha_info and 'iframe' in page_source and 'recaptcha' in page_source.lower():
                import re
                iframe_match = re.search(r'src=["\']([^"\']*recaptcha[^"\']*)["\']', page_source.lower())
                if iframe_match:
                    url = iframe_match.group(1)
                    if 'k=' in url:
                        match = re.search(r'k=([a-zA-Z0-9_-]+)', url)
                        if match:
                            sitekey = match.group(1)
                            captcha_info = {
                                'type': CaptchaType.RECAPTCHA_V2.value,
                                'sitekey': sitekey,
                                'page_url': page_url
                            }

        # Check for hCaptcha
        elif 'hcaptcha' in page_source.lower():
            import re
            match = re.search(r'data-sitekey=["\']([a-zA-Z0-9_-]+)["\']', page_source)
            if match:
                sitekey = match.group(1)
                captcha_info = {
                    'type': CaptchaType.HCAPTCHA.value,
                    'sitekey': sitekey,
                    'page_url': page_url
                }

        # Check for Cloudflare Turnstile
        elif 'turnstile' in page_source.lower():
            import re
            match = re.search(r'data-sitekey=["\']([a-zA-Z0-9_-]+)["\']', page_source)
            if match:
                sitekey = match.group(1)
                captcha_info = {
                    'type': CaptchaType.CLOUDFLARE.value,
                    'sitekey': sitekey,
                    'page_url': page_url
                }

        if captcha_info:
            self.logger.info(f"CAPTCHA detected: {captcha_info['type']} (sitekey: {captcha_info['sitekey'][:10]}...)")

        return captcha_info

    def solve(self, captcha_info: Dict[str, Any], proxy: Optional[str] = None) -> Optional[str]:
        """
        Submit CAPTCHA to 2captcha and poll for solution
        
        Args:
            captcha_info: Dict with 'type', 'sitekey', 'page_url' (and 'action' for v3)
            proxy: Optional proxy in format 'http://ip:port' or 'http://user:pass@ip:port'
        
        Returns:
            Solved token string or None if failed
        """
        try:
            # Submit CAPTCHA
            captcha_id = self._submit(captcha_info, proxy)
            if not captcha_id:
                return None

            self.logger.info(f"CAPTCHA submitted (ID: {captcha_id})")

            # Poll for result with exponential backoff
            token = self._poll_result(captcha_id)
            if token:
                self.logger.info(f"CAPTCHA solved successfully (token length: {len(token)})")
                return token
            else:
                self.logger.error("Failed to retrieve CAPTCHA solution")
                return None

        except CaptchaSolverError as e:
            self.logger.error(f"CAPTCHA solver error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in solve(): {e}", exc_info=True)
            return None

    def _submit(self, captcha_info: Dict[str, Any], proxy: Optional[str] = None) -> Optional[str]:
        """
        Submit CAPTCHA to 2captcha API
        
        Returns:
            CAPTCHA ID or None if failed
        """
        try:
            captcha_type = captcha_info.get('type', CaptchaType.RECAPTCHA_V2.value)
            sitekey = captcha_info.get('sitekey')
            page_url = captcha_info.get('page_url')
            
            if not sitekey or not page_url:
                raise CaptchaSolverError("Missing sitekey or page_url")

            # Map captcha type to 2captcha method
            if captcha_type == CaptchaType.RECAPTCHA_V2.value:
                method = 'userrecaptcha'
            elif captcha_type == CaptchaType.RECAPTCHA_V3.value:
                method = 'userrecaptcha'
            elif captcha_type == CaptchaType.HCAPTCHA.value:
                method = 'hcaptcha'
            elif captcha_type == CaptchaType.CLOUDFLARE.value:
                method = 'turnstile'
            else:
                raise CaptchaSolverError(f"Unsupported captcha type: {captcha_type}")

            # Build request parameters
            data = {
                'key': self.api_key,
                'method': method,
                'googlekey': sitekey,
                'pageurl': page_url,
                'json': 1
            }

            # reCAPTCHA v3 specific parameters
            if captcha_type == CaptchaType.RECAPTCHA_V3.value:
                data['version'] = 'v3'
                if 'action' in captcha_info:
                    data['action'] = captcha_info['action']
                data['min_score'] = '0.3'

            # hCaptcha and Cloudflare specific parameters
            if captcha_type == CaptchaType.HCAPTCHA.value:
                data.pop('googlekey', None)
                data['sitekey'] = sitekey
            elif captcha_type == CaptchaType.CLOUDFLARE.value:
                data.pop('googlekey', None)
                data['sitekey'] = sitekey

            # Build request with proxy support
            proxies = None
            if proxy:
                proxies = {'http': proxy, 'https': proxy}

            self.logger.debug(f"Submitting to 2captcha: method={method}, sitekey={sitekey[:10]}...")
            
            response = requests.post(
                self.API_SUBMIT_URL,
                data=data,
                timeout=30,
                proxies=proxies
            )
            
            if response.status_code != 200:
                raise CaptchaSolverError(f"HTTP error: {response.status_code}")

            result = response.json()
            
            if result.get('status') != 1:
                error_msg = result.get('request', 'Unknown error')
                if error_msg in self.ERROR_CODES:
                    error_msg = self.ERROR_CODES[error_msg]
                raise CaptchaSolverError(f"Submit failed: {error_msg}")

            captcha_id = result.get('captcha')
            if not captcha_id:
                raise CaptchaSolverError("No captcha ID in response")

            return str(captcha_id)

        except requests.RequestException as e:
            raise CaptchaSolverError(f"Request failed: {e}")
        except Exception as e:
            raise CaptchaSolverError(f"Submit error: {e}")

    def _poll_result(self, captcha_id: str, proxy: Optional[str] = None) -> Optional[str]:
        """
        Poll 2captcha API for solution with exponential backoff
        
        Returns:
            Solution token or None if failed/timeout
        """
        start_time = time.time()
        wait_time = 2  # Start with 2 seconds
        max_wait = 10  # Max wait between polls
        
        params = {
            'key': self.api_key,
            'action': 'get',
            'captcha': captcha_id,
            'json': 1
        }

        proxies = None
        if proxy:
            proxies = {'http': proxy, 'https': proxy}

        while time.time() - start_time < self.timeout:
            try:
                time.sleep(wait_time)
                
                response = requests.get(
                    self.API_RESULT_URL,
                    params=params,
                    timeout=30,
                    proxies=proxies
                )
                
                if response.status_code != 200:
                    self.logger.warning(f"Poll HTTP error: {response.status_code}")
                    wait_time = min(wait_time + 1, max_wait)
                    continue

                result = response.json()
                
                if result.get('status') != 1:
                    request_result = result.get('request')
                    
                    # Still processing
                    if request_result == 'CAPCHA_NOT_READY':
                        self.logger.debug("CAPTCHA not ready, polling again...")
                        # Exponential backoff
                        wait_time = min(wait_time + 1, max_wait)
                        continue
                    
                    # Error
                    error_msg = request_result
                    if error_msg in self.ERROR_CODES:
                        error_msg = self.ERROR_CODES[error_msg]
                    
                    raise CaptchaSolverError(f"Solution poll error: {error_msg}")

                token = result.get('request')
                if token and token != 'CAPCHA_NOT_READY':
                    elapsed = time.time() - start_time
                    self.logger.info(f"Solution obtained in {elapsed:.1f}s")
                    return token
                
                wait_time = min(wait_time + 1, max_wait)

            except requests.RequestException as e:
                self.logger.warning(f"Poll request error: {e}, retrying...")
                wait_time = min(wait_time + 1, max_wait)
                continue
            except CaptchaSolverError as e:
                self.logger.error(f"Poll error: {e}")
                raise

        elapsed = time.time() - start_time
        raise CaptchaSolverError(f"CAPTCHA solving timeout after {elapsed:.1f}s")

    def report_bad(self, captcha_id: str) -> bool:
        """
        Report unsolvable CAPTCHA to 2captcha for refund
        
        Args:
            captcha_id: ID of the CAPTCHA to report
        
        Returns:
            True if report was successful
        """
        try:
            params = {
                'key': self.api_key,
                'action': 'report',
                'captcha': captcha_id,
                'json': 1
            }
            
            response = requests.get(
                self.API_RESULT_URL,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 1:
                    self.logger.info(f"Bad CAPTCHA reported (ID: {captcha_id})")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Failed to report bad CAPTCHA: {e}")
            return False


class CaptchaTokenInjector:
    """Helper class to inject solved CAPTCHA tokens into page"""

    @staticmethod
    def get_injection_script(token: str, captcha_type: str, page_url: str = "") -> str:
        """
        Get JavaScript code to inject CAPTCHA token
        
        Args:
            token: Solved CAPTCHA token
            captcha_type: Type of CAPTCHA (recaptcha_v2, recaptcha_v3, hcaptcha, etc.)
            page_url: Page URL (for hCaptcha callback)
        
        Returns:
            JavaScript code to execute
        """
        
        if captcha_type == CaptchaType.RECAPTCHA_V2.value:
            return f"""
            (function() {{
                // Try to inject into g-recaptcha-response
                var elem = document.getElementById('g-recaptcha-response');
                if (elem) {{
                    elem.innerHTML = '{token}';
                    elem.value = '{token}';
                }}
                
                // Try to trigger callback if it exists
                if (typeof ___grecaptcha_cfg !== 'undefined') {{
                    Object.entries(___grecaptcha_cfg.clients).forEach(([key, client]) => {{
                        if (client.callback) {{
                            client.callback('{token}');
                        }}
                    }});
                }}
                
                // Try to trigger g-recaptcha callback
                if (typeof __recaptcha_api !== 'undefined' && __recaptcha_api.reset) {{
                    __recaptcha_api.reset();
                }}
                
                console.log('reCAPTCHA token injected');
            }})();
            """
        
        elif captcha_type == CaptchaType.RECAPTCHA_V3.value:
            return f"""
            (function() {{
                // For reCAPTCHA v3, set the token in the hidden field
                var elem = document.getElementById('g-recaptcha-response');
                if (elem) {{
                    elem.innerHTML = '{token}';
                    elem.value = '{token}';
                }}
                
                // Try to find and trigger the form submission callback
                var form = document.querySelector('form');
                if (form && form.onsubmit) {{
                    form.onsubmit();
                }}
                
                console.log('reCAPTCHA v3 token injected');
            }})();
            """
        
        elif captcha_type == CaptchaType.HCAPTCHA.value:
            return f"""
            (function() {{
                // hCaptcha token injection
                var elem = document.getElementById('h-captcha-response');
                if (elem) {{
                    elem.value = '{token}';
                }}
                
                // Try to trigger hcaptcha callback
                if (typeof window.__hcaptcha !== 'undefined') {{
                    window.__hcaptcha.onSuccess('{token}');
                }}
                
                // Alternative: look for the callback in window object
                var callbacks = Object.keys(window).filter(k => k.includes('callback'));
                callbacks.forEach(cb => {{
                    if (typeof window[cb] === 'function') {{
                        try {{ window[cb]('{token}'); }} catch(e) {{}}
                    }}
                }});
                
                console.log('hCaptcha token injected');
            }})();
            """
        
        elif captcha_type == CaptchaType.CLOUDFLARE.value:
            return f"""
            (function() {{
                // Cloudflare Turnstile token injection
                var elem = document.getElementById('cf-turnstile-response');
                if (elem) {{
                    elem.value = '{token}';
                }}
                
                // Try to trigger Turnstile callback
                if (typeof window.turnstile !== 'undefined' && window.turnstile.callback) {{
                    window.turnstile.callback('{token}');
                }}
                
                console.log('Cloudflare Turnstile token injected');
            }})();
            """
        
        else:
            # Generic injection for unknown types
            return f"""
            (function() {{
                // Generic token injection
                ['g-recaptcha-response', 'h-captcha-response', 'cf-turnstile-response'].forEach(id => {{
                    var elem = document.getElementById(id);
                    if (elem) {{
                        elem.value = '{token}';
                        elem.innerHTML = '{token}';
                    }}
                }});
                
                // Try to find and trigger any callbacks
                var callbacks = Object.keys(window).filter(k => 
                    k.includes('callback') || k.includes('recaptcha') || k.includes('captcha')
                );
                callbacks.forEach(cb => {{
                    if (typeof window[cb] === 'function') {{
                        try {{ window[cb]('{token}'); }} catch(e) {{}}
                    }}
                }});
                
                console.log('CAPTCHA token injected (generic)');
            }})();
            """
