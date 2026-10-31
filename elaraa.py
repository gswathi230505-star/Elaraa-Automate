
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# 1. Open Elaraa Studio
driver = webdriver.Edge()
driver.maximize_window()

wait = WebDriverWait(driver, 25)

try:
    driver.get("https://elaraastudio.com/home")

    wait.until(
        lambda d: d.execute_script(
            "return document.readyState"
        ) == "complete"
    )

    print("STEP 1: Website opened successfully")

    # 2. Search for kurti
    search = wait.until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//input[contains(translate(@placeholder,"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),'search')]"
        ))
    )

    search.clear()
    search.send_keys("kurti")
    search.send_keys(Keys.ENTER)

    # 3. Wait for search results
    wait.until(EC.url_contains("/filterdeal"))
    time.sleep(3)

    print("STEP 2: Kurti search completed")
    print("Search URL:", driver.current_url)

    driver.save_screenshot("elaraa_01_search.png")
    print("Screenshot saved: elaraa_01_search.png")

    # 4. Scroll down to the filters
    driver.execute_script("window.scrollTo(0, 300)")
    time.sleep(2)

    print("STEP 3: Scrolled to filters")

    # 5. Select filters without changing the existing flow
    def select_filter(filter_name):
        try:
            filter_label = wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    f"//*[normalize-space()='{filter_name}']"
                ))
            )

            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                filter_label
            )

            time.sleep(1)

            # Check for a checkbox in the same filter row
            row = filter_label.find_element(By.XPATH, "..")
            checkboxes = row.find_elements(
                By.CSS_SELECTOR,
                "input[type='checkbox']"
            )

            if checkboxes:
                checkbox = checkboxes[0]

                if not checkbox.is_selected():
                    driver.execute_script(
                        "arguments[0].click();",
                        filter_label
                    )
                    time.sleep(2)

                print(f"Filter checked: {filter_name}")
                return

            # Fallback: inspect the associated row for a selected
            # checkbox-style element
            selected = row.find_elements(
                By.CSS_SELECTOR,
                "[aria-checked='true'], [data-state='checked']"
            )

            if selected:
                print(f"Filter already selected: {filter_name}")
                return

            driver.execute_script(
                "arguments[0].click();",
                filter_label
            )

            time.sleep(2)
            print(f"Clicked filter: {filter_name}")

        except TimeoutException:
            print(f"Filter not found: {filter_name}")

    # Select the main Kurtis category first
    select_filter("Kurtis")

    # Select additional filters, if available
    select_filter("Office Wear")
    select_filter("Casual Wear")

    print("STEP 4: Filter selection completed")

    # 6. Return to the product results
    driver.execute_script("window.scrollTo(0, 0)")

    wait.until(
        EC.presence_of_all_elements_located((
            By.XPATH,
            "//*[normalize-space()='VIEW']"
        ))
    )

    time.sleep(2)

    driver.save_screenshot("elaraa_02_filtered_kurtis.png")
    print("Screenshot saved: elaraa_02_filtered_kurtis.png")

    # 7. Find the first visible VIEW button
    print("STEP 5: Finding a kurti to open")

    view_buttons = driver.find_elements(
        By.XPATH,
        "//*[self::button or self::a or @role='button']"
        "[normalize-space()='VIEW']"
    )

    view_button = None

    for button in view_buttons:
        if button.is_displayed() and button.is_enabled():
            view_button = button
            break

    if view_button is None:
        raise Exception("No visible VIEW button found.")

    # 8. Click the first visible product
    old_url = driver.current_url
    old_handles = driver.window_handles

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        view_button
    )

    time.sleep(1)

    driver.execute_script(
        "arguments[0].click();",
        view_button
    )

    # 9. Wait for navigation or a new tab
    try:
        wait.until(
            lambda d: (
                d.current_url != old_url
                or len(d.window_handles) > len(old_handles)
            )
        )
    except TimeoutException:
        driver.save_screenshot("elaraa_03_click_issue.png")
        raise Exception(
            "VIEW was clicked, but no navigation or new tab appeared. "
            "Check elaraa_03_click_issue.png."
        )

    # Switch to the new tab if one opened
    if len(driver.window_handles) > len(old_handles):
        new_handle = next(
            handle for handle in driver.window_handles
            if handle not in old_handles
        )
        driver.switch_to.window(new_handle)

    # 10. Verify product details page
    wait.until(EC.url_contains("/product/details/"))

    print("STEP 6: Kurti product page opened")
    print("Product URL:", driver.current_url)

    driver.save_screenshot("elaraa_03_selected_kurti.png")
    print("Screenshot saved: elaraa_03_selected_kurti.png")

except Exception as error:
    print("\nTEST FAILED")
    print(type(error).__name__ + ":", str(error))

    try:
        driver.save_screenshot("elaraa_error.png")
        print("Error screenshot saved: elaraa_error.png")
    except Exception:
        pass

finally:
    # Keep browser open for 10 seconds, then close automatically
    print("Kurti selection testing completed.")
    print("Screenshots saved in the project folder.")

    time.sleep(10)
    driver.quit()
    print("Browser closed successfully.")