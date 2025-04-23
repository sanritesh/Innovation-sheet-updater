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
import sys

# ===== CONFIGURATION =====
# Get environment variables or use default values
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', '/tmp/BookingData_folder')
EXPRESSO_URL = "https://expresso.colombiaonline.com"
USERNAME = os.getenv('EXPRESSO_USERNAME')  # Get from Bitbucket variables
PASSWORD = os.getenv('EXPRESSO_PASSWORD')  # Get from Bitbucket variables

# Validate required environment variables
if not USERNAME or not PASSWORD:
    raise ValueError("EXPRESSO_USERNAME and EXPRESSO_PASSWORD environment variables must be set")

# ===== DIRECTORY MANAGEMENT =====
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

def rename_to_xlsx(downloaded_file):
    """Rename the .xls file to .xlsx"""
    try:
        print(f"🔄 Renaming {downloaded_file} to .xlsx format...")
        
        # Create new filename with .xlsx extension
        new_filename = os.path.splitext(downloaded_file)[0] + '.xlsx'
        
        # Rename the file
        os.rename(downloaded_file, new_filename)
        
        print(f"✅ Successfully renamed to: {new_filename}")
        return new_filename
    except Exception as e:
        print(f"❌ Error renaming file: {str(e)}")
        return None

def wait_for_download_complete(download_dir, timeout=60):
    """Wait for the download to complete and return the downloaded file path"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        files = os.listdir(download_dir)
        for file in files:
            if file.endswith('.xls') and not file.startswith('~$'):
                # Wait a bit more to ensure the file is completely written
                time.sleep(2)
                return os.path.join(download_dir, file)
        time.sleep(1)
    return None

# ===== DATE FUNCTIONS =====
def get_next_day_date():
    """Returns tomorrow's date in MM/DD/YYYY format"""
    tomorrow = datetime.now() + timedelta(days=1)
    return tomorrow.strftime("%m/%d/%Y")

# ===== HUMAN-LIKE BEHAVIOR =====
def random_delay(min=0.5, max=3.0):
    """Random delay between actions to mimic human behavior"""
    time.sleep(random.uniform(min, max))

def human_type(element, text):
    """Simulates human typing with random delays"""
    for character in text:
        element.send_keys(character)
        time.sleep(random.uniform(0.05, 0.3))

# ===== STEALTH CHROME CONFIG (WITH POPUP BLOCKING) =====
def get_chrome_options():
    """Configure Chrome options for headless operation"""
    options = Options()
    
    # Basic stealth settings
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Disable automation flags
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Custom User-Agent
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    # Window size (helps avoid headless detection)
    options.add_argument("--window-size=1920,1080")
    
    # Download settings + POPUP BLOCKING
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
    
    # Additional popup blocking
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-save-password-bubble")
    
    return options

def main():
    """Main execution function"""
    try:
        # Clear download directory before starting
        clear_download_directory()
        
        print("🚀 Launching browser with stealth configuration...")
        driver = webdriver.Chrome(options=get_chrome_options())
        random_delay(1, 2)

        # Clear cookies and cache
        driver.delete_all_cookies()
        print("🧹 Cookies cleared")
        random_delay()

        # Access login page
        print("🔑 Navigating to login page...")
        driver.get(EXPRESSO_URL)
        random_delay(2, 4)

        # Login process
        print("🔐 Attempting login...")
        username_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        human_type(username_field, USERNAME)
        random_delay()

        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        human_type(password_field, PASSWORD)
        random_delay(0.5, 1.5)
        password_field.send_keys(Keys.RETURN)

        # Verify successful login
        WebDriverWait(driver, 20).until(
            lambda d: "home" in d.current_url.lower()
        )
        print("✅ Login successful")
        random_delay(2, 3)

        # Navigate to booking dashboard
        print("📊 Redirecting to booking dashboard...")
        booking_url = "https://expresso.colombiaonline.com/expresso/viewBookingDashboard.htm"
        driver.get(booking_url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "pckDateRange"))
        )
        print("✅ Dashboard loaded")
        random_delay(1, 2)

        # Get tomorrow's date
        tomorrow_date = get_next_day_date()
        print(f"📅 Setting date range to: {tomorrow_date}")

        # Date range selection
        date_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "pckDateRange")))
        date_button.click()
        range = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ranges")))

        # Click on the 6th <li> element inside the .ranges list
        sixth_li_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "body > div.daterangepicker.dropdown-menu.ltr.opensright > div.ranges > ul > li:nth-child(6)")))
        sixth_li_element.click()
        
        # Set the date inputs to tomorrow's date
        date_input_from_text = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "body > div.daterangepicker.dropdown-menu.ltr.opensright.show-calendar > div.calendar.left > div.daterangepicker_input > input")))
        date_input_to_text = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "body > div.daterangepicker.dropdown-menu.ltr.opensright.show-calendar > div.calendar.right > div.daterangepicker_input > input")))
        
        date_input_from_text.clear()
        human_type(date_input_from_text, tomorrow_date)
        date_input_to_text.clear()
        human_type(date_input_to_text, tomorrow_date)
       
        apply_button=WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "body > div.daterangepicker.dropdown-menu.ltr.opensright.show-calendar > div.ranges > div > button.applyBtn.btn.btn-sm.btn-success")))
        apply_button.click()
        
        export_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#yoyoId > div.m-content > div:nth-child(1) > div > div > div:nth-child(5) > button.btn.t-btn-global.t-btn-green")))
        export_button.click()

        # Export data
        print("📤 Preparing to export...")
        export_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.t-btn-green"))
        )
        export_btn.click()
        print("✅ Export initiated")

        # Wait for download to complete and get the file path
        print("⏳ Waiting for download to complete...")
        downloaded_file = wait_for_download_complete(DOWNLOAD_DIR)
        
        if downloaded_file:
            # Rename to .xlsx
            xlsx_file = rename_to_xlsx(downloaded_file)
            if xlsx_file:
                print(f"🎉 Process completed successfully! File saved as: {xlsx_file}")
            else:
                print("❌ Failed to rename file")
                return False
        else:
            print("❌ Download failed or timed out")
            return False

        return True

    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        # Take screenshot for debugging
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        driver.save_screenshot(f"error_{timestamp}.png")
        print(f"📸 Screenshot saved as 'error_{timestamp}.png'")
        return False

    finally:
        if 'driver' in locals():
            driver.quit()
            print("🛑 Browser closed")

if __name__ == "__main__":
    sys.exit(0 if main() else 1)