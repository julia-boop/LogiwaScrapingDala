from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller
import tempfile
import time
import os

# download_path = "/Users/juliacordero/Downloads"
# screenshot_path = "/Users/juliacordero/Documents/Python/LogiwaScraping/Screenshots/"

temp_dir = tempfile.mkdtemp()
download_path = temp_dir

chromedriver_autoinstaller.install()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = "/usr/bin/chromium"

driver = webdriver.Chrome(options=chrome_options)

chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_path,  
    "download.prompt_for_download": False,       
    "download.directory_upgrade": True,        
    "safebrowsing.enabled": True               
})

service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

def get_latest_file(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if not files:
        return None  
    latest_file = max(files, key=os.path.getmtime)  
    return latest_file

def get_file():
    driver.get("https://app.logiwa.com/en/Login")

    username_field = driver.find_element(By.ID, "UserName")
    password_field = driver.find_element(By.ID, "Password")

    print(username_field)
    print(password_field)

    time.sleep(3)

    username_field.send_keys(os.getenv("LOGIWA_USERNAME"))
    password_field.send_keys(os.getenv("LOGIWA_PASSWORD"))

    login_button = driver.find_element(By.ID, "LoginButton")
    login_button.click()

    time.sleep(3)

    login_handle = None

    try:
        login_handle = driver.find_element(By.CSS_SELECTOR, ".bootbox-body")
    except Exception as e:
        print("No login handle needed")

    if login_handle:
        buttons = driver.find_elements(By.CLASS_NAME, "btn-success")
        for b in buttons:
            text = b.text
            if text == "Ok":
                b.click()
                time.sleep(3)
    else:
        print("No login handle needed")
    
    driver.get("https://app.logiwa.com/en/WMS/Stock")

    time.sleep(3)

    # timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # driver.save_screenshot(f"{screenshot_path}screenshot1-{timestamp}.png")

    input_element = driver.find_element(By.XPATH, "(//input[@class='form-control'])[1]")

    input_element.send_keys("Nude Lucy")
    input_element.send_keys(Keys.ENTER)

    time.sleep(3)

    button_search = driver.find_element(By.CSS_SELECTOR, ".btn-success")
    button_search.click()

    time.sleep(3)

    button_excel = driver.find_element(By.CSS_SELECTOR, ".fa-file-excel-o")
    button_excel.click()

    time.sleep(10)

    driver.quit() 

    latest_file = get_latest_file(download_path)

    if latest_file:
        print(f"Latest download file: {latest_file}")
        return latest_file
    else:
        print(f"No files found in the directory {download_path}")
        return
