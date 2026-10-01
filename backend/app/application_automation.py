from playwright.sync_api import sync_playwright


def open_application_page(job_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        page = browser.new_page()
        page.goto(job_url)

        print("Application page opened:")
        print(page.url)

        input("Press Enter to close browser...")

        browser.close()