import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope="module")
def driver():
    service = Service("/usr/local/bin/chromedriver")
    options = Options()
    options.add_argument("--ignore-certificate-errors")
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    yield driver
    driver.quit()
URL = "https://127.0.0.1:2443"



# ====================тесты на успешный логин и функциональность====================
def test_successful_login(driver):
    driver.get(URL)
    driver.find_element(By.ID, "username").send_keys("root")
    driver.find_element(By.ID, "password").send_keys("0penBmc")
    driver.find_element(By.CSS_SELECTOR, "[data-test-id='login-button-submit']").click()

    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Overview")
    )
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Overview" in body_text
    
def test_power_status(driver):
    driver.get(URL)
    driver.find_element(By.ID, "username").send_keys("root")
    driver.find_element(By.ID, "password").send_keys("0penBmc")
    driver.find_element(By.CSS_SELECTOR, "[data-test-id='login-button-submit']").click()
    
    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR, "[data-test-id='nav-button-operations']").click()
    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR, "[data-test-id='nav-item-server-power-operations']").click()
    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR, "[data-test-id='serverPowerOperations-button-powerOn']").click()
    WebDriverWait(driver, 5).until(
        EC.text_to_be_present_in_element((By.CLASS_NAME, "alert-msg"), "There are no options to display while a power operation is in progress. When complete, power operations will be displayed here."))
    body_text = driver.find_element(By.CLASS_NAME, "alert-msg").text
    assert "There are no options to display while a power operation is in progress. When complete, power operations will be displayed here." in body_text

def test_logs(driver):
    driver.get(URL)
    driver.find_element(By.ID, "username").send_keys("root")
    driver.find_element(By.ID, "password").send_keys("0penBmc")
    driver.find_element(By.CSS_SELECTOR, "[data-test-id='login-button-submit']").click()
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='nav-button-logs']"))
    ).click()
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='nav-item-event-logs'"))
    ).click()
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='nav-item-event-logs']"))
    )
    assert "event-logs" in driver.current_url, "не отображается страница журналов событий"
    
# ====================тесты на блокировку и неверный логин====================    
def test_invailid_login(driver):
    driver.get(URL)
    driver.find_element(By.ID, "username").send_keys("root")
    driver.find_element(By.ID, "password").send_keys("wrongpassword")
    driver.find_element(By.CSS_SELECTOR, "[data-test-id='login-button-submit']").click()
    
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    assert "dashboard" not in driver.current_url, "выполнен вход с неверными учетными данными"
    assert driver.find_element(By.ID, "username").is_displayed(), "не отображается страница входа после неверных учетных данных"

def test_blocked_login(driver):
    driver.get(URL)
   
    for _ in range(5):
        driver.find_element(By.ID, "username").clear()
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "username").send_keys("wasr")
        driver.find_element(By.ID, "password").send_keys("wrongpassword")
        driver.find_element(By.CSS_SELECTOR, "[data-test-id='login-button-submit']").click()
        
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    assert "dashboard" not in driver.current_url, "выполнен вход с заблокированной учетной записью"
    assert driver.find_element(By.ID, "username").is_displayed(), "не отображается страница входа после заблокированной учетной записи"
    
