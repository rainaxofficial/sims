from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import threading
import time

app = Flask(__name__)
driver_lock = threading.Lock()

def create_driver():
    print("[🚀] Creating Chrome driver...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"

    # ✅ Use manually downloaded ChromeDriver v138
    service = Service("/opt/render/project/.render/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://minahalsimdata.com.pk/sim-info/")
    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "wp-block-search__input-1"))
    )
    return driver

try:
    chrome_driver = create_driver()
    print("[✅] Chrome driver initialized")
except Exception as e:
    print(f"[FATAL] Failed to launch Chrome: {e}")
    chrome_driver = None

def perform_search(number):
    global chrome_driver
    results = []

    if chrome_driver is None:
        raise Exception("Chrome driver is not available.")

    try:
        with driver_lock:
            input_box = chrome_driver.find_element(By.ID, "wp-block-search__input-1")
            input_box.clear()
            input_box.send_keys(number)
            input_box.submit()

            WebDriverWait(chrome_driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".output-container"))
            )

            soup = BeautifulSoup(chrome_driver.page_source, "html.parser")
            blocks = soup.select(".resultcontainer")

            for block in blocks:
                data = {}
                for row in block.select(".row"):
                    head = row.select_one(".detailshead").text.strip().rstrip(':')
                    value = row.select_one(".details").text.strip()
                    data[head] = value
                results.append({
                    'Name': data.get('Name', ''),
                    'Mobile': data.get('Mobile', ''),
                    'Country': data.get('Country', ''),
                    'CNIC': data.get('CNIC', ''),
                    'Address': data.get('Address', ''),
                })

    except Exception as e:
        print(f"[❌] Chrome error: {e}")
        print("[🔁] Relaunching Chrome...")
        try:
            chrome_driver.quit()
        except:
            pass
        try:
            chrome_driver = create_driver()
        except Exception as e:
            print(f"[FATAL] Re-launch failed: {e}")
            chrome_driver = None
            raise
        time.sleep(1)
        return perform_search(number)

    return results

@app.route("/", methods=["GET", "POST"])
def index():
    global chrome_driver
    results = []
    number = ""
    error = None

    if request.method == "POST":
        number = request.form.get("number", "").strip()
        if not number:
            error = "Please enter a number or CNIC."
        else:
            try:
                results = perform_search(number)
            except Exception as e:
                error = f"[FATAL ERROR] {e}"

    return render_template("index.html", number=number, results=results, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
