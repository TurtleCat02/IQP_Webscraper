import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

options = webdriver.FirefoxOptions()
options.headless = True
driver = webdriver.Firefox(executable_path="C:\\Users\\bcspe\\.wdm\\drivers\\geckodriver\\win64\\v0.34.0\\geckodriver.exe", options=options)
# driver.implicitly_wait(5)


def check_imgs(imgs):
    for img in imgs:
        if driver.execute_script("return arguments[0].complete", img):
            return False
    return True


with open("websites.txt", "r") as f:
    websites = f.readlines()

for website in websites:
    original_size = driver.get_window_size()
    site_name = re.search(r'https://([\w.-]+)', website).group(1)
    print(f"Site: {site_name}")
    driver.get(website)
    required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(required_width, required_height)
    print("Waiting 30 seconds...")
    time.sleep(30)
    # imgs = driver.find_elements(By.TAG_NAME, "img")
    # wait = WebDriverWait(driver, 45)
    # print("Waiting...")
    # wait.until(lambda d: check_imgs(imgs))
    driver.find_element(By.TAG_NAME, 'body').screenshot(f"./output/{site_name}.png")  # avoids scrollbar
    driver.set_window_size(original_size['width'], original_size['height'])

driver.quit()
