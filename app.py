from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  # ✅ Allow frontend like Blogger
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
CORS(app)  # ✅ Enable CORS for all routes

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

    service = Service("/opt/render/project/.render/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://minahalsimdata.com.pk/sim-info/")
    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "wp-block-search__input-1"))
    )
    return driver

try:
    chrome_driver = create_driver()
except Exception as e:
    print(f"[FATAL] Failed to launch Chrome: {e}")
    chrome_driver = None

def perform_search(number, retry=True):
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
        if retry:
            try:
                chrome_driver.quit()
            except:
                pass
            try:
                chrome_driver = create_driver()
            except Exception as e:
                chrome_driver = None
                raise Exception("Driver restart failed: " + str(e))
            return perform_search(number, retry=False)
        else:
            raise e

    return results

@app.route("/", methods=["GET", "POST"])
def index():
    global chrome_driver

    if request.method == "POST":
        try:
            data = request.get_json()
            number = data.get("number", "").strip()
            print("[📲] Number received:", number)  # ✅ Logging
            results = perform_search(number)
            return jsonify({"results": results})
        except Exception as e:
            print(f"[❌] Error: {e}")
            return jsonify({"error": str(e)}), 500

    return render_template("index.html")

@app.route("/health")
def health():
    return "OK", 200
