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

# ===== CONFIGURATION =====
DOWNLOAD_DIR = "/Users/Ritesh.Sanjay/BookingData_folder"
EXPRESSO_URL = "https://expresso.colombiaonline.com"
USERNAME = "ritesh.sanjay@timesinternet.in"
PASSWORD = "Aouto@2307"  # Consider using environment variables or secure storage

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
def get_stealth_driver():
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
        # Password manager blocking
        "credentials_enable_service": False,          # Disable password saving
        "profile.password_manager_enabled": False,    # Disable password manager
        "profile.default_content_setting_values.notifications": 2  # Block notifications
    })
    
    # Additional popup blocking
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-save-password-bubble")  # Explicit disable
    
    driver = webdriver.Chrome(options=options)
    
    # Remove navigator.webdriver flag
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.onload = function() {
                    document.body.style.visibility = 'visible';
                };
            """
        }
    )
    
    return driver

# ===== MAIN SCRIPT =====
try:
    # Clear download directory before starting
    clear_download_directory()
    
    print("🚀 Launching browser with stealth configuration...")
    driver = get_stealth_driver()
    random_delay(1, 2)

    # Clear cookies and cache
    driver.delete_all_cookies()
    print("🧹 Cookies cleared")
    random_delay()

    # Access login page
    print("🔑 Navigating to login page...")
    driver.get(EXPRESSO_URL)
    random_delay(2, 4)  # Simulate page load time

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

    # Wait for download to complete
    print("⏳ Waiting for download to complete...")
    time.sleep(10)  # Adjust based on expected file size
    print(f"🎉 Process completed successfully! Data for {tomorrow_date} downloaded.")

except Exception as e:
    print(f"❌ Error occurred: {str(e)}")
    # Take screenshot for debugging
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    driver.save_screenshot(f"error_{timestamp}.png")
    print(f"📸 Screenshot saved as 'error_{timestamp}.png'")

finally:
    input("Press Enter to close the browser...")
    driver.quit()
    print("🛑 Browser closed")