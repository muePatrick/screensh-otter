import io
import time
from typing import List

from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def screenshot_element(
    server: str,
    url: str,
    xpath: str,
    elements_to_remove: List[str] = []
    ) -> bool:
    screenshot_successful = False
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=959,9999")
    options.add_argument("--headless")
    try:
        print(" ↳ Setting up...")
        driver = webdriver.Remote(command_executor=server, options=options)
        driver.set_window_size(959, 9999)
        
        print(" ↳ Opening page...")
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        
        try:
            print(" ↳ Getting element...")
            element = wait.until(EC.presence_of_element_located((By.XPATH,xpath)))
            element_height = element.size['height']
            driver.set_window_size(959, element_height + 200)
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
        except Exception as e:
            raise Exception(f"Could not get element: {e}")

        try:
            for selector in elements_to_remove:
                print(f" ↳ Removing element with selector: {selector}...")
                driver.execute_script(f"""
                    var element = document.querySelector('{selector}')
                    if (element) {{
                        element.remove();
                    }}
                """)
            time.sleep(1)
        except Exception as e:
            raise Exception(f"Could not remove elemnts: {e}")

        try:
            print(" ↳ Taking screenshot...")
            image_binary = element.screenshot_as_png 
            img = Image.open(io.BytesIO(image_binary))
            img.save("image.png")
            screenshot_successful = True
        except Exception as e:
            raise Exception("Could not take screenshot: {e}")
        
    except Exception as e:
        print(f" ↳ Could not complete screenshot flow: {e}")
    finally:
        if 'driver' in locals():
            print(" ↳ Closing browser...")
            driver.quit()

    return screenshot_successful
