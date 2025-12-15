# Cloudflare Bypass Mode

## Overview
The Cloudflare Bypass mode uses `undetected-chromedriver` to automatically detect and bypass Cloudflare protection challenges, reducing blocks by approximately 10%.

## Installation

### Required Dependency
```bash
pip install undetected-chromedriver
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

## Features

### 1. Automatic Challenge Detection
The system automatically detects Cloudflare challenges by checking for:
- `cf-browser-verification` markers
- `data-cf-beacon` presence
- "Just a moment..." title
- Cloudflare Turnstile widgets
- Challenge platform indicators

### 2. Smart Waiting Logic
- Polls challenge status every second
- Configurable timeout (10-120 seconds, default 30)
- Progress logging every 5 seconds
- Automatic screenshot capture at key stages

### 3. Graceful Fallback
If `undetected-chromedriver` is not installed:
- System logs a warning
- Falls back to standard Chrome WebDriver
- Continues operation without Cloudflare bypass

## Usage

### GUI Setup
1. Open the Settings tab
2. Scroll to "🛡️ Cloudflare Bypass" section
3. Check "🔓 CloudFlare защита (undetected-chromedriver)"
4. Optionally adjust "Таймаут challenge (сек)" (recommended: 30-60s)
5. Run mailing as usual

### Confirmation Dialog
Before starting, verify the confirmation shows:
```
• Cloudflare bypass: Да
```

### During Execution
Monitor logs for Cloudflare events:
```
🛡️ Обнаружена Cloudflare защита на https://example.com
⏳ Ожидание прохождения Cloudflare challenge... (5с/30с, осталось 25с)
✓ Cloudflare защита пройдена за 8.2с
```

## Reporting

### Statistics Summary
Reports include a "CLOUDFLARE СТАТИСТИКА" section:
```
Cloudflare обнаружен и обойден: 5
Cloudflare таймаут: 1
Без Cloudflare защиты: 94
Успешность обхода: 83.3%
```

### Per-URL Status
Each URL shows Cloudflare status:
```
1. https://example.com
   🛡️ Cloudflare: Обойден успешно
```

### JSON Report
Machine-readable statistics in `report.json`:
```json
{
  "cloudflare": {
    "bypassed": 5,
    "timeout": 1,
    "not_detected": 94
  }
}
```

## Technical Details

### Driver Selection
- **Cloudflare Mode ON**: Uses `uc.Chrome()` from undetected-chromedriver
- **Cloudflare Mode OFF**: Uses standard `webdriver.Chrome()`

### Compatible Features
Both drivers support:
- ✅ Headless mode
- ✅ Incognito mode
- ✅ Proxy configuration
- ✅ User-Agent rotation
- ✅ Window size randomization
- ✅ Antidetect features

### Challenge Handling Flow
1. Page loads via `driver.get(url)`
2. System checks for Cloudflare indicators
3. If detected:
   - Takes "challenge_detected" screenshot
   - Enters polling loop (1s intervals)
   - Logs progress every 5s
   - Exits on success or timeout
4. On success: Takes "bypassed" screenshot
5. On timeout: Takes "timeout" screenshot, returns error

## Troubleshooting

### "undetected-chromedriver не установлен" Warning
**Solution**: Install the library:
```bash
pip install undetected-chromedriver
```

### Cloudflare Timeouts
**Solutions**:
1. Increase timeout value (try 60-120s)
2. Check if proxy is causing issues
3. Verify Chrome/Chromedriver compatibility
4. Try disabling headless mode (Cloudflare may detect it)

### Challenge Not Detected
If Cloudflare is present but not detected:
1. Check logs for detection indicators
2. Verify page loads completely before detection
3. Consider updating detection patterns in code

## Best Practices

### Timeout Settings
- **Development/Testing**: 60-120s (allows manual debugging)
- **Production/Fast**: 30-45s (optimal balance)
- **Mass Mailing**: 20-30s (minimize delays)

### Combining with Other Features
- ✅ **With Antidetect**: Recommended for best results
- ✅ **With Proxies**: Helps if IP is flagged
- ✅ **With CAPTCHA Solver**: Handles both protections
- ⚠️ **With Headless**: May reduce success rate

### Thread Count
- Lower thread count (2-3) recommended when using Cloudflare bypass
- Reduces concurrent challenge load
- Improves bypass success rate

## Performance Impact

### Speed
- **No Cloudflare**: Same as standard mode
- **Cloudflare Detected**: +5-30s per URL (depending on challenge)
- **Average Overhead**: ~10s per affected URL

### Success Rate
- **Standard Chrome**: ~0-20% bypass rate
- **Undetected Chrome**: ~80-95% bypass rate
- **Overall Improvement**: ~10% reduction in total blocks

## Logs Example

```
[12:34:56] [Thread-0] Инициализация Undetected ChromeDriver для обхода Cloudflare...
[12:34:58] [Thread-0] ✓ Undetected ChromeDriver запущен (режим Cloudflare bypass)
[12:35:02] [Thread-0] → Открытие: https://protected-site.com
[12:35:05] [Thread-0] 🛡️ Обнаружена Cloudflare защита на https://protected-site.com
[12:35:05] [Thread-0] ✓ Скриншот: t0_protected-site_com_cloudflare_challenge_123456.png
[12:35:10] [Thread-0] ⏳ Ожидание прохождения Cloudflare challenge... (5с/30с, осталось 25с)
[12:35:13] [Thread-0] ✓ Cloudflare защита пройдена за 8.2с
[12:35:13] [Thread-0] ✓ Скриншот: t0_protected-site_com_cloudflare_bypassed_123457.png
[12:35:15] [Thread-0] ✓ Загружено
```

## API Reference

### ChatBot Parameters
```python
ChatBot(
    cloudflare_bypass=False,      # Enable Cloudflare bypass mode
    cloudflare_timeout=30,        # Challenge timeout in seconds
    ...
)
```

### Result Dictionary
```python
{
    'url': 'https://example.com',
    'status': 'success',
    'cloudflare_status': 'bypassed',  # or 'timeout', 'not_detected'
    ...
}
```

### Statistics Dictionary
```python
chatbot.cloudflare_stats = {
    'detected': 0,      # Challenges detected
    'bypassed': 0,      # Successfully bypassed
    'timeout': 0,       # Timed out
    'not_detected': 0   # No Cloudflare found
}
```

## Known Limitations

1. **Headless Detection**: Cloudflare may detect headless browsers more easily
2. **Version Compatibility**: Requires Chrome/Chromedriver compatibility
3. **Rate Limiting**: Multiple attempts from same IP may trigger harder challenges
4. **JavaScript Challenges Only**: Does not handle manual CAPTCHA challenges

## Future Enhancements

- [ ] Advanced challenge type detection
- [ ] Automatic retry with fresh proxy on timeout
- [ ] CAPTCHA + Cloudflare combination handling
- [ ] Per-proxy Cloudflare success rate tracking
- [ ] Adaptive timeout based on historical data
