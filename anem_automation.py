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

        # Remove any whitespace
        v = v.strip()

        # Check if it contains only digits
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
        # Use webdriver-manager to automatically download and manage ChromeDriver
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
        # Initialize pygame mixer
        pygame.mixer.init()

        # Check if sound file exists
        if not os.path.exists(sound_file):
            print(f"⚠️  Warning: Sound file '{sound_file}' not found")
            return False

        # Load and play the sound
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()

        # Wait for the sound to finish playing
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
            # First, wait for any loading spinner to disappear
            print("Checking for loading spinner...")
            try:
                # Wait for spinner to appear and then disappear (max 10 seconds)
                # Target the specific MuiCircularProgress element in the dialog
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

            # Now wait for dialog button
            print("Waiting for dialog button...")
            wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.muirtl-1om64lz"))
            )
            print("✓ Dialog button found!")
            return True, False

        except TimeoutException:
            print(f"⚠️  Dialog button not found on attempt {attempt + 1}")

            # Check if we're still on the login page
            current_url = driver.current_url
            page_source = driver.page_source

            # Check for indicators that we're still on login page
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
        # Clear and refill N1
        # n1_input = wait.until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, "input#numeroWassit"))
        # )
        # n1_input.clear()
        # n1_input.send_keys(settings.n1)
        # print("✓ N1 refilled")

        # # Clear and refill N2
        # n2_input = wait.until(
        #     EC.presence_of_element_located(
        #         (By.CSS_SELECTOR, "input#numeroPieceIdentite")
        #     )
        # )
        # n2_input.clear()
        # n2_input.send_keys(settings.n2)
        # print("✓ N2 refilled")

        # Click submit again
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


def automate_anem_form():
    """Main automation function"""
    # Get and validate settings
    settings = get_settings()
    print(f"Using N1 (Wassit): {settings.n1}")
    print(f"Using N2 (Piece Identite): {settings.n2}")

    # Setup driver
    print("Setting up Chrome driver...")
    driver = setup_driver()
    wait = WebDriverWait(driver, 20)

    try:
        # Navigate to the pre-inscription page
        print("Navigating to ANEM pre-inscription page...")
        driver.get("https://minha.anem.dz/pre_inscription")

        # Wait for page to load
        time.sleep(3)
        print(f"Current page URL: {driver.current_url}")
        print(f"Page title: {driver.title}")

        # Fill N1 in input#numeroWassit
        print("Filling N1 in numeroWassit field...")
        n1_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#numeroWassit"))
        )
        n1_input.clear()
        n1_input.send_keys(settings.n1)
        print("✓ N1 filled successfully")

        # Fill N2 in input#numeroPieceIdentite
        print("Filling N2 in numeroPieceIdentite field...")
        n2_input = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input#numeroPieceIdentite")
            )
        )
        n2_input.clear()
        n2_input.send_keys(settings.n2)
        print("✓ N2 filled successfully")

        # Click on button#mui-14
        print("Clicking submit button...")
        submit_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button#mui-6"))
        )
        submit_button.click()
        print("✓ Submit button clicked")

        # Wait for dialog popup with retry logic
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
                # Try waiting for dialog again after refill
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

        # Wait for page redirect and load
        print("Waiting for page redirect...")
        time.sleep(5)

        # Check current page info
        print(f"Redirected to: {driver.current_url}")
        print(f"New page title: {driver.title}")

        # Check if the page contains the specific Arabic message
        target_message = "نعتذر منكم ! لا يوجد أي موعد متاح حاليا."
        print(f"Checking for message: '{target_message}'")

        # Get page source and check for the message
        page_source = driver.page_source

        if target_message in page_source:
            print("The message was found on the page!")
            print(
                "The system is currently showing: 'نعتذر منكم ! لا يوجد أي موعد متاح حاليا.'"
            )
            print("This means no appointments are currently available.")

            driver.quit()
            print("Browser closed.")
            return True
        else:
            print("🔊 Playing sound notification...")
            play_sound("sound.mp3")
            print(
                "✅ SUCCESS: This might mean appointments are available or the page content is different."
            )

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
        # Keep browser open for a few seconds to see the result
        driver.quit()
        print("Browser closed.")


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
        print("❌ Script completed with issues")
        print("Check the output above for details.")
    print("=" * 60)


if __name__ == "__main__":
    main()
