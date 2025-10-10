# ANEM Pre-inscription Automation Script

This script automates the form submission process on the ANEM (Agence Nationale de l'Emploi) pre-inscription website to check for appointment availability.

## Features

- Automatically fills in the Wassit number (N1) and Piece Identite number (N2)
- Submits the form and handles dialog popups
- Checks for the specific Arabic message indicating no appointments are available
- Provides detailed logging and error handling

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Google Chrome** browser installed
3. **ChromeDriver** (automatically managed by webdriver-manager)

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Method 1: Using Environment Variables

1. Set the environment variables:

   ```bash
   # Windows (Command Prompt)
   set N1=your_wassit_number
   set N2=your_piece_identite_number

   # Windows (PowerShell)
   $env:N1="your_wassit_number"
   $env:N2="your_piece_identite_number"

   # Linux/Mac
   export N1=your_wassit_number
   export N2=your_piece_identite_number
   ```

2. Run the script:
   ```bash
   python anem_automation_improved.py
   ```

### Method 2: Using the Batch Script (Windows)

1. Run the batch script with your numbers:
   ```cmd
   run_anem_automation.bat 123456789 987654321
   ```

## Script Files

- `anem_automation.py` - Basic version of the automation script
- `anem_automation_improved.py` - Enhanced version with better error handling and logging
- `run_anem_automation.bat` - Windows batch script for easy execution
- `requirements.txt` - Python dependencies

## What the Script Does

1. **Navigates** to https://minha.anem.dz/pre_inscription
2. **Fills** the Wassit number in the `#numeroWassit` input field
3. **Fills** the Piece Identite number in the `#numeroPieceIdentite` input field
4. **Clicks** the submit button (`#mui-14`)
5. **Waits** for and handles any dialog popups
6. **Clicks** the confirmation button (`.muirtl-1om64lz`) if a dialog appears
7. **Waits** for page redirect and loads
8. **Checks** if the page contains the message: "نعتذر منكم ! لا يوجد أي موعد متاح حاليا."

## Expected Results

- **If the message is found**: The script will report that no appointments are currently available
- **If the message is not found**: The script will report that appointments might be available or the page content is different

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**: The script uses webdriver-manager to automatically download ChromeDriver
2. **Element not found**: The website structure might have changed
3. **Timeout errors**: The page might be loading slowly
4. **Environment variables not set**: Make sure N1 and N2 are properly set

### Debug Mode

The script keeps the browser open for 15 seconds after completion so you can manually inspect the page and see what happened.

## Notes

- The script includes anti-detection measures to avoid being blocked
- It waits for elements to be clickable before interacting with them
- It provides detailed logging throughout the process
- The browser will remain open for 15 seconds after completion for manual inspection

## Security

- Never share your Wassit number or Piece Identite number
- The script only uses these numbers for the intended form submission
- No data is stored or transmitted to any external services
