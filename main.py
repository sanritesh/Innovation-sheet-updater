#!/usr/bin/env python3
"""
Expresso Booking Data Export - Complete Production Script
"""

import os
import time
import random
import shutil
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ===== CONFIGURATION =====
EXPRESSO_URL = "https://expresso.colombiaonline.com"
GOOGLE_DRIVE_FOLDER_ID = "1puKfKGAPKXyJPOBo_OtKZmP8ZUtWjITp"
SERVICE_ACCOUNT_FILE = 'service_account.json'

# Get credentials from environment variables
USERNAME = os.getenv('EXPRESSO_USERNAME')
PASSWORD = os.getenv('EXPRESSO_PASSWORD')

# Temporary directory for downloads (cross-platform)
DOWNLOAD_DIR = os.path.join(os.getenv('TEMP', '/tmp'), 'expresso_downloads')

# ===== UTILITY FUNCTIONS =====
def clear_download_directory():
    """Clears all files in the download directory"""
    if os.path.exists(DOWNLOAD_DIR):
        print(f"🧹 Clearing download directory: {DOWNLOAD_DIR}")
        for filename in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"⚠️ Failed to delete {file_path}. Reason: {e}")
    else:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        print(f"📁 Created download directory: {DOWNLOAD_DIR}")

def get_next_day_date():
    """Returns tomorrow's date in MM/DD/YYYY format"""
    tomorrow = datetime.now() + timedelta(days=1)
    return tomorrow.strftime("%m/%d/%Y")

def random_delay(min=0.5, max=3.0):
    """Random delay between actions to mimic human behavior"""
    time.sleep(random.uniform(min, max))

def human_type(element, text):
    """Simulates human typing with random delays"""
    for character in text:
        element.send_keys(character)
        time.sleep(random.uniform(0.05, 0.3))

# ===== BROWSER FUNCTIONS =====
def get_stealth_driver():
    """Configure and return a stealthy Chrome WebDriver"""
    options = Options()
    
    # Basic stealth settings
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # Disable automation flags
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Download settings
    options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_settings.popups": 0,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2
    })
    
    # Additional settings
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    # Remove navigator.webdriver flag
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        }
    )
    
    return driver

def upload_to_drive(file_path):
    """Upload file to Google Drive using service account"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        service = build('drive', 'v3', credentials=credentials)
        
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [GOOGLE_DRIVE_FOLDER_ID]
        }
        
        media = MediaFileUpload(file_path)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f"✅ Uploaded to Google Drive. File ID: {file.get('id')}")
        return True
        
    except Exception as e:
        print(f"❌ Google Drive upload failed: {str(e)}")
        return False

def wait_for_download_complete(timeout=60):
    """Wait for download to complete in the download directory"""
    print("⏳ Waiting for download to complete...")
    end_time = time.time() + timeout
    while time.time() < end_time:
        # Check for .crdownload files (Chrome temporary download files)
        if not any(f.endswith('.crdownload') for f in os.listdir(DOWNLOAD_DIR)):
            downloaded_files = [f for f in os.listdir(DOWNLOAD_DIR) 
                             if not f.startswith('.') and not f.endswith('.tmp')]
            if downloaded_files:
                return max(
                    [os.path.join(DOWNLOAD_DIR, f) for f in downloaded_files],
                    key=os.path.getctime
                )
        time.sleep(2)
    raise TimeoutError(f"Download did not complete within {timeout} seconds")

# ===== MAIN WORKFLOW =====
def main():
    try:
        if not USERNAME or not PASSWORD:
            raise ValueError("Missing credentials. Set EXPRESSO_USERNAME and EXPRESSO_PASSWORD environment variables")
        
        # Initialize
        clear_download_directory()
        driver = get_stealth_driver()
        driver.delete_all_cookies()
        
        # Login
        print("🔑 Navigating to login page...")
        driver.get(EXPRESSO_URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys(USERNAME)
        
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        human_type(password_field, PASSWORD)
        password_field.send_keys(Keys.RETURN)
        
        # Verify login
        WebDriverWait(driver, 20).until(
            lambda d: "home" in d.current_url.lower()
        )
        print("✅ Login successful")
        random_delay(2, 3)
        
        # Navigate to dashboard
        print("📊 Redirecting to booking dashboard...")
        booking_url = "https://expresso.colombiaonline.com/expresso/viewBookingDashboard.htm"
        driver.get(booking_url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "pckDateRange"))
        )
        
        # Set date range
        tomorrow_date = get_next_day_date()
        print(f"📅 Setting date range to: {tomorrow_date}")
        
        date_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pckDateRange"))
        )
        date_button.click()
        
        sixth_li_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "body > div.daterangepicker.dropdown-menu.ltr.opensright > div.ranges > ul > li:nth-child(6)"))
        )
        sixth_li_element.click()
        
        date_from = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "body > div.daterangepicker.dropdown-menu.ltr.opensright.show-calendar > div.calendar.left > div.daterangepicker_input > input"))
        )
        date_from.clear()
        human_type(date_from, tomorrow_date)
        
        date_to = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "body > div.daterangepicker.dropdown-menu.ltr.opensright.show-calendar > div.calendar.right > div.daterangepicker_input > input"))
        )
        date_to.clear()
        human_type(date_to, tomorrow_date)
        
        apply_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "body > div.daterangepicker.dropdown-menu.ltr.opensright.show-calendar > div.ranges > div > button.applyBtn.btn.btn-sm.btn-success"))
        )
        apply_button.click()
        random_delay(1, 2)
        
        # Export data
        print("📤 Preparing to export...")
        export_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.t-btn-green"))
        )
        export_button.click()
        print("✅ Export initiated")
        
        # Wait for download and process file
        downloaded_file = wait_for_download_complete()
        print(f"📥 Downloaded: {downloaded_file}")
        
        # Upload to Google Drive
        if upload_to_drive(downloaded_file):
            os.remove(downloaded_file)
            print("🧹 Cleaned up local file")
        print(f"🎉 Process completed for {tomorrow_date}")
            
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(DOWNLOAD_DIR, f"error_{timestamp}.png")
        if 'driver' in locals():
            driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
        raise  # Re-raise for CI/CD systems to catch
        
    finally:
        # Clean up service account file
        if os.path.exists(SERVICE_ACCOUNT_FILE):
            try:
                os.remove(SERVICE_ACCOUNT_FILE)
                print("🧹 Removed temporary service account file")
            except Exception as e:
                print(f"⚠️ Failed to remove service account file: {e}")
        
        # Close browser
        if 'driver' in locals():
            driver.quit()
            print("🛑 Browser closed")

if __name__ == "__main__":
    main()