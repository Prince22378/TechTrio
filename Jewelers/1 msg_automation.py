import pandas as pd
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1) Load your student list
df = pd.read_csv("whatsapp_msg/startup_contacts.csv")  # Make sure columns are: 'Name' and 'Contact'

# 2) Define the single message
def get_message(first_name):
    return (
        f"Hey {first_name} – Prajil this side.\n\n"
        "I’m part of a small 3-member tech team from IIIT Delhi — we love building stuff that helps startups move faster.\n\n"
        "We’ve built solutions across the board — from automation tools to web/app development, data management and analytics, SEO, and more. "
        "We’re also part of our campus’s Entrepreneurship Cell, so we live and breathe early-stage problem solving.\n\n"
        "Just reaching out in case you or someone you know ever needs tech hands — we would love to get involved.\n\n"
        "→ https://techtrio.netlify.app\n\n"
        "Cheers,\n"
        "Prajil - +91 73200 61608"
    )

# 3) Set up Chrome browser
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.maximize_window()
driver.get("https://web.whatsapp.com/")

print("→ Please scan the QR code in the browser.")
input("→ Press ENTER once WhatsApp Web has fully loaded and you're logged in...")

wait = WebDriverWait(driver, 20)

# 4) Send one message to each contact
for _, row in df.iterrows():
    full_name = str(row["Name"]).strip()
    first_name = full_name.split()[0]
    phone = str(int(float(row["Contact"]))).strip()

    if not phone.isdigit() or len(phone) != 10:
        print(f"⚠️ Skipping invalid number: {phone}")
        continue

    phone = "91" + phone  # Add Indian country code

    msg = get_message(first_name)
    encoded_msg = urllib.parse.quote(msg)
    url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
    driver.get(url)

    try:
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div[contenteditable='true'][data-tab]"))
        )
        send_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@aria-label='Send']"))
        )
        send_button.click()
        time.sleep(2)
        print(f"✅ Sent message to {first_name} ({phone})")
    except Exception as e:
        print(f"❌ Failed to send message to {first_name} ({phone}): {e}")

    time.sleep(5)  # delay between contacts

# 5) Done
driver.quit()
