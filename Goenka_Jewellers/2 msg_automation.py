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
df = pd.read_csv("whatsapp_msg/try.csv")  # ensure 'Name' and 'Contact' columns exist

# 2) Define message builder
def get_messages(first_name):
    msg1 = f"Hi {first_name}"
    msg2 = (
        "We’re a 3-member tech team from IIIT Delhi - passionate about building for startups. "
        "We’ve done projects across automation, dashboards, web/apps, scraping, SEO, and GPT-based tools - helping founders move faster.\n\n"
        "We're also part of our campus's Entrepreneurship Cell, so we live and breathe early-stage problem solving - not just writing code, but thinking like builders.\n\n"
        "If you’re ever looking for hands-on tech help - from something quick to something big - here’s where you can find us: https://techtrio.netlify.app/\n\n"
        "Always happy to connect, brainstorm, or just explore ideas.\n– Prajil (+91 73200 61608)"
    )
    return [msg1, msg2]

# 3) Set up Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.maximize_window()
driver.get("https://web.whatsapp.com/")

print("→ Please scan the QR code in the browser.")
input("→ Press ENTER once WhatsApp Web has fully loaded and you're logged in...")

wait = WebDriverWait(driver, 20)

# 4) Send messages
for _, row in df.iterrows():
    full_name = str(row["Name"]).strip()
    first_name = full_name.split()[0]
    phone = str(row["Contact"]).strip()

    if not phone.isdigit() or len(phone) != 10:
        print(f"⚠️ Skipping invalid number: {phone}")
        continue

    # WhatsApp expects country code — assume Indian numbers
    phone = "91" + phone

    for msg in get_messages(first_name):
        encoded_msg = urllib.parse.quote(msg)
        url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
        driver.get(url)

        try:
            # Wait until message box is ready
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[contenteditable='true'][data-tab]"))
            )
            # Wait for send button and click
            send_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[@aria-label='Send']"))
            )
            send_button.click()
            time.sleep(2)

        except Exception as e:
            print(f"❌ Failed to send message to {first_name} ({phone}): {e}")
            break  # skip second message if first fails

    print(f"✅ Sent messages to {first_name} ({phone})")
    time.sleep(5)  # wait between contacts

# 5) Done
driver.quit()
