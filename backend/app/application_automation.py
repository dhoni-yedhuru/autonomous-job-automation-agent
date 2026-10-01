from playwright.sync_api import sync_playwright


def apply_to_mock_portal(
    job_id: int,
    candidate: dict,
):
    url = f"http://127.0.0.1:8000/mock-portal/{job_id}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        page = browser.new_page()
        page.goto(url)

        page.locator('input[name="full_name"]').fill(
            candidate.get("full_name", "")
        )

        page.locator('input[name="email"]').fill(
            candidate.get("email", "")
        )

        page.locator('input[name="phone"]').fill(
            candidate.get("phone", "")
        )

        page.locator('input[name="experience_years"]').fill(
            str(candidate.get("experience_years", 0))
        )

        page.locator('textarea[name="skills"]').fill(
            candidate.get("skills", "")
        )

        page.get_by_role(
            "button",
            name="Submit Application"
        ).click()

        page.wait_for_load_state("networkidle")

        print("Application submitted:")
        print(page.url)

        browser.close()