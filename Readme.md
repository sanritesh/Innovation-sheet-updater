# Bitbucket InnovSheet Automation

## Overview
This project automates the download, processing, and reporting of booking data from Expresso, and uploads the results to Google Sheets. It is designed to run both locally and in Bitbucket Pipelines.

## Workflow
1. **main.py**: Automates browser to download the latest BookingData.xlsx from Expresso.
2. **upload_to_gsheet.py**: Processes the Excel file (filters, merges, transforms) and uploads all relevant sheets to your Google Sheet.
3. **send_email.py**: Sends an email notification with the link to the updated Google Sheet.

## How to Run Locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up environment variables (see below).
3. Run the scripts in order:
   ```bash
   python main.py
   python upload_to_gsheet.py
   python send_email.py
   ```

## Bitbucket Pipelines
- The pipeline will automatically:
  - Download the Excel file
  - Process and upload to Google Sheets
  - Send an email notification
- See `bitbucket-pipelines.yml` for details.

## Environment Variables
Set these in your Bitbucket repository variables or your local environment:
- `EXPRESSO_USERNAME` and `EXPRESSO_PASSWORD`: For Expresso login
- `GOOGLE_SHEET_URL`: Target Google Sheet URL
- `SERVICE_ACCOUNT_JSON`: Base64-encoded Google service account key (used in pipeline)
- `SERVICE_ACCOUNT_FILE`: Path to the service account key (default: `/tmp/service-account.json` in pipeline)
- `EMAIL_RECIPIENTS`: Comma-separated list of email recipients
- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`: For email sending

## Requirements
- Python 3.9+
- See `requirements.txt` for all dependencies

## Notes
- The project no longer uses pandas; all Excel processing is done with openpyxl and native Python.
- The pipeline is set up for headless Chrome/Selenium for automated downloads.
- All sensitive keys are handled via environment variables and not committed to the repo.

## Support
If you need to adjust the workflow or add new features, open an issue or contact the maintainer.
