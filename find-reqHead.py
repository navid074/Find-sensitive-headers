import requests
from bs4 import BeautifulSoup
import logging

# Config Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_sensitive_headers(url):
    try:
        logger.info(f"Starting to check URL: {url}")
        
        # Send GET req to URL
        logger.info("Sending GET request to the URL...")
        response = requests.get(url)
        logger.info(f"Received response with status code: {response.status_code}")
        
        # List Of Sensitive Headers
        sensitive_headers = [
            "x-powered-by",  # نشان‌دهنده فریم‌ورک یا زبان برنامه‌نویسی
            "server",        # نشان‌دهنده سرور استفاده شده (مثل Apache, Nginx)
            "x-aspnet-version",  # نشان‌دهنده نسخه ASP.NET
            "x-runtime",     # نشان‌دهنده Ruby on Rails
            "x-library",     # نشان‌دهنده کتابخانه‌های خاص
            "x-framework",   # نشان‌دهنده فریم‌ورک‌ها
            "x-generator",   # نشان‌دهنده ابزارهای ساخت (مثل WordPress)
            "via",           # نشان‌دهنده پروکسی‌ها
            "x-cache",       # نشان‌دهنده سیستم‌های کش
            "x-cdn",         # نشان‌دهنده CDN استفاده شده
        ]
        
        # Check Req Headers
        logger.info("Checking Request Headers...")
        for header, value in response.request.headers.items():
            logger.info(f"Request Header: {header} = {value}")
            if any(sensitive in header.lower() for sensitive in sensitive_headers):
                logger.warning(f"🚨 Sensitive header found in Request: {header} = {value}")
        
        # Check Res Headers
        logger.info("Checking Response Headers...")
        for header, value in response.headers.items():
            logger.info(f"Response Header: {header} = {value}")
            if any(sensitive in header.lower() for sensitive in sensitive_headers):
                logger.warning(f"🚨 Sensitive header found in Response: {header} = {value}")
        
        # Check HTML
        logger.info("Parsing HTML content to find script and link tags...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check <script> Tags
        logger.info("Checking script tags...")
        for script in soup.find_all('script'):
            if script.src:  # اگر فایل خارجی باشد
                script_url = script.src if script.src.startswith('http') else url + script.src
                logger.info(f"Found script: {script_url}")
                try:
                    logger.info(f"Fetching script content from: {script_url}")
                    script_response = requests.get(script_url)
                    if "version" in script_response.text.lower():
                        logger.warning(f"⚠️ Possible library version found in script: {script_url}")
                except requests.exceptions.RequestException as e:
                    logger.error(f"Failed to fetch script: {script_url} - {e}")
        
        # Check CSS for CDN
        logger.info("Checking CSS link tags...")
        for link in soup.find_all('link', rel='stylesheet'):
            if link.href:  # اگر فایل خارجی باشد
                css_url = link.href if link.href.startswith('http') else url + link.href
                logger.info(f"Found CSS: {css_url}")
                try:
                    logger.info(f"Fetching CSS content from: {css_url}")
                    css_response = requests.get(css_url)
                    if "version" in css_response.text.lower():
                        logger.warning(f"⚠️ Possible library version found in CSS: {css_url}")
                except requests.exceptions.RequestException as e:
                    logger.error(f"Failed to fetch CSS: {css_url} - {e}")
        
        logger.info("Finished checking the URL.")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error: {e}")

# URL HERE
url = "example.com"
check_sensitive_headers(url)
