#!/usr/bin/env python3
"""
ANEM Pre-inscription Automation Script (Improved Version)
Automates the form submission process on https://minha.anem.dz/pre_inscription
Uses webdriver-manager for automatic ChromeDriver management
"""

import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
import pygame


class AnemSettings(BaseSettings):
    """Pydantic settings model for ANEM automation environment variables"""

    n1: str = Field(..., description="Wassit number", alias="N1")
    n2: str = Field(..., description="Piece Identite number", alias="N2")

    @field_validator("n1", "n2")
    @classmethod
    def validate_numbers(cls, v: str) -> str:
        """Validate that the numbers are not empty and contain only digits"""
        if not v or not v.strip():
            raise ValueError("Number cannot be empty")
        v = v.strip()
        if not v.isdigit():
            raise ValueError("Number must contain only digits")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def setup_driver():
    """Setup Chrome driver with automatic driver management"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Uncomment the next line if you want to run in headless mode
    # chrome_options.add_argument("--headless")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("Make sure you have Chrome browser installed")
        sys.exit(1)


def play_sound(sound_file="sound.mp3"):
    """Play a sound file using pygame"""
    try:
        pygame.mixer.init()
        if not os.path.exists(sound_file):
            print(f"⚠️  Warning: Sound file '{sound_file}' not found")
            return False
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        print(f"🔊 Played sound: {sound_file}")
        return True
    except Exception as e:
        print(f"❌ Error playing sound: {e}")
        return False


def wait_for_dialog_with_retry(driver, wait, max_retries=3):
    """
    Wait for dialog button with retry logic and spinner detection
    Returns: (success, is_still_on_login_page)
    """
    for attempt in range(max_retries):
        print(f"Attempt {attempt + 1}/{max_retries}: Waiting for dialog...")
        try:
            print("Checking for loading spinner...")
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            ".MuiDialogContent-root .MuiCircularProgress-root, .MuiCircularProgress-indeterminate",
                        )
                    )
                )
                print("Spinner detected, waiting for it to disappear...")
                WebDriverWait(driver, 30).until(
                    EC.invisibility_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            ".MuiDialogContent-root .MuiCircularProgress-root, .MuiCircularProgress-indeterminate",
                        )
                    )
                )
                print("✓ Spinner disappeared")
            except TimeoutException:
                print("No spinner detected or already gone")

            print("Waiting for dialog button...")
            wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.muirtl-1om64lz"))
            )
            print("✓ Dialog button found!")
            return True, False

        except TimeoutException:
            print(f"⚠️  Dialog button not found on attempt {attempt + 1}")
            current_url = driver.current_url
            page_source = driver.page_source
            login_indicators = [
                "numeroWassit" in page_source,
                "numeroPieceIdentite" in page_source,
                "pre_inscription" in current_url,
                "login" in current_url.lower(),
            ]
            if any(login_indicators):
                print("🔍 Still on login page - need to re-enter information")
                return False, True
            else:
                print("🔍 Not on login page - might be a different issue")
                return False, False

    print("❌ All attempts failed")
    return False, False


def refill_form_and_retry(driver, wait, settings):
    """Refill the form and try to submit again"""
    print("🔄 Refilling form and retrying...")
    try:
        # Clear and refill N1 and N2 if necessary
        submit_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button#mui-6"))
        )
        submit_button.click()
        print("✓ Submit button clicked again")
        return True
    except Exception as e:
        print(f"❌ Error refilling form: {e}")
        return False


def get_settings() -> AnemSettings:
    """Get and validate ANEM settings from environment variables"""
    try:
        settings = AnemSettings()
        return settings
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        print()
        print("Please set the following environment variables:")
        print("  N1=your_wassit_number")
        print("  N2=your_piece_identite_number")
        print()
        print("Example:")
        print("  export N1=123456789")
        print("  export N2=987654321")
        print("  python anem_automation.py")
        print()
        sys.exit(1)


def wait_for_text_in_page_source(driver, text, timeout=30):
    """Wait until the given text appears in the page source, with timeout in seconds."""
    print(
        f"Waiting for text to appear in page source: '{text}' (timeout={timeout}s)..."
    )
    start_time = time.time()
    while True:
        page_source = driver.page_source
        if text in page_source:
            print(f"✓ Text '{text}' appeared in page source.")
            return True
        elapsed = time.time() - start_time
        if elapsed > timeout:
            print(
                f"❌ Timeout waiting for text '{text}' in page source after {timeout} seconds."
            )
            return False
        time.sleep(0.5)


def automate_anem_form():
    """
    Main automation function

    1. Open https://minha.anem.dz/pre_inscription
    2. Auth
    3. After authentication and redirection, wait until the word 'CHEHROURI' appears in page source (ensure full page load).
    4. Only then check if the target message is present in the page.
       - If message exists: No appointment, script succeeded, do NOT play sound
       - If message doesn't exist: Appointments likely available, play sound!
    5. If not redirected to pre_rendez_vous, do not play sound and consider it an issue.
    """
    settings = get_settings()
    print(f"Using N1 (Wassit): {settings.n1}")
    print(f"Using N2 (Piece Identite): {settings.n2}")

    print("Setting up Chrome driver...")
    driver = setup_driver()
    wait = WebDriverWait(driver, 20)

    try:
        print("Navigating to ANEM pre-inscription page...")
        pre_inscription_url = "https://minha.anem.dz/pre_inscription"
        pre_rendez_vous_url = "https://minha.anem.dz/pre_rendez_vous"
        driver.get(pre_inscription_url)

        # Wait for page to load
        time.sleep(3)
        print(f"Current page URL: {driver.current_url}")
        print(f"Page title: {driver.title}")

        print("Filling N1 in numeroWassit field...")
        n1_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#numeroWassit"))
        )
        n1_input.clear()
        n1_input.send_keys(settings.n1)
        print("✓ N1 filled successfully")

        print("Filling N2 in numeroPieceIdentite field...")
        n2_input = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input#numeroPieceIdentite")
            )
        )
        n2_input.clear()
        n2_input.send_keys(settings.n2)
        print("✓ N2 filled successfully")

        print("Clicking submit button...")
        submit_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button#mui-6"))
        )
        submit_button.click()
        print("✓ Submit button clicked")

        print("Waiting for dialog popup...")
        dialog_success, is_still_on_login = wait_for_dialog_with_retry(driver, wait)

        if dialog_success:
            print("✓ Dialog popup appeared, clicking confirmation button...")
            dialog_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.muirtl-1om64lz"))
            )
            dialog_button.click()
            print("✓ Confirmation button clicked")
        elif is_still_on_login:
            print("🔄 Still on login page, attempting to refill and retry...")
            if refill_form_and_retry(driver, wait, settings):
                dialog_success, _ = wait_for_dialog_with_retry(driver, wait)
                if dialog_success:
                    dialog_button = wait.until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, "button.muirtl-1om64lz")
                        )
                    )
                    dialog_button.click()
                    print("✓ Confirmation button clicked after retry")
                else:
                    print("⚠️  Dialog still not appearing after retry")
            else:
                print("❌ Failed to refill form")
        else:
            print("⚠️  Dialog popup not found and not on login page")
            print("Continuing anyway...")

        # Wait for potential redirect after dialog
        print("Waiting for page redirect...")
        time.sleep(5)  # may adjust

        current_url = driver.current_url
        print(f"Redirected to: {current_url}")
        print(f"New page title: {driver.title}")

        target_message = "نعتذر منكم ! لا يوجد أي موعد متاح حاليا."

        if current_url.startswith(pre_rendez_vous_url):
            print(
                "✅ Authenticated and redirected to pre_rendez_vous, waiting for complete page load (CHEHROURI)..."
            )

            # Wait for "CHEHROURI" in page source to ensure complete load
            appeared = wait_for_text_in_page_source(driver, "CHEHROURI", timeout=45)
            if not appeared:
                print(
                    "WARNING: CHEHROURI did not appear - proceeding to check for appointments message, but result might be unreliable."
                )

            page_source = driver.page_source
            print(f"Checking for message: '{target_message}'")
            if target_message in page_source:
                print("The message was found on the page!")
                print(
                    "The system is currently showing: 'نعتذر منكم ! لا يوجد أي موعد متاح حاليا.'"
                )
                print("This means no appointments are currently available.")
                return True
            else:
                print("No unavailable message. Appointments may be available!")
                print("🔊 Playing sound notification...")
                play_sound("sound.mp3")
                print(
                    "✅ SUCCESS: You have authenticated and appointments might be available!"
                )
                # Do NOT quit the driver here. Leave the browser open so user can investigate/act
                return False
        else:
            print(
                "❌ Not redirected to pre_rendez_vous. Probably authentication failed or page flow changed."
            )
            print("No sound will be played since you're not authenticated.")
            return False

    except TimeoutException as e:
        print(f"❌ Timeout error: {e}")
        print("This might be due to slow page loading or element not appearing")
        return False
    except NoSuchElementException as e:
        print(f"❌ Element not found: {e}")
        print("The page structure might have changed")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        # Only close the browser if there is NO appointment (i.e. function returns True, or the function is about to return False for problems)
        # We'll check if we're at the "appointments available" branch (which returns False but doesn't close), and only quit otherwise.
        import inspect

        # Inspect the call stack to see if we're returning from appointments-available case
        stack = inspect.stack()
        called_from_appointments_available = False
        # Look for a parent frame where return False is immediately after detecting appointments available
        # We'll use a trick: main returns NOT True (i.e. False), and only "appointments available" skips the quit.
        # To avoid quitting in that case: only quit if the current_url branch was NOT appointments available.
        try:
            # try to get the 'current_url' and 'target_message' variables
            frame = stack[1].frame
            pre_rendez_vous_url_local = frame.f_locals.get("pre_rendez_vous_url", None)
            current_url_local = frame.f_locals.get("current_url", None)
            page_source_local = frame.f_locals.get("page_source", None)
            target_message_local = frame.f_locals.get("target_message", None)
            if pre_rendez_vous_url_local and current_url_local:
                # appointments available means we're on pre_rendez_vous AND target_message not in page
                if current_url_local.startswith(pre_rendez_vous_url_local):
                    if (
                        page_source_local
                        and target_message_local
                        and target_message_local not in page_source_local
                    ):
                        called_from_appointments_available = True
        except Exception:
            pass

        if not called_from_appointments_available:
            driver.quit()
            print("Browser closed.")
        else:
            print(
                "Appointments may be available: NOT closing the browser. Please check your browser window and take any necessary actions."
            )


def main():
    """Main entry point"""
    print("=" * 60)
    print("ANEM Pre-inscription Automation Script")
    print("=" * 60)
    print()

    success = automate_anem_form()

    print("\n" + "=" * 60)
    if success:
        print("🎉 Script completed successfully!")
        print("The system shows no appointments are currently available.")
    else:
        print("❌ Script completed with issues or appointments might be available")
        print("Check the output above for details.")
    print("=" * 60)


if __name__ == "__main__":
    main()
