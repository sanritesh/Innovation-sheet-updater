# Times Internet Innovation Sheet Updater

This project automates the daily process of downloading booking data from Expresso, processing it, and uploading the results to Google Sheets. It runs on a scheduled basis via Bitbucket Pipelines.

## 🚀 Overview

The system performs the following automated workflow:

1. **Data Download**: Uses Selenium to log into Expresso and download booking data for the next day
2. **Data Processing**: Processes the Excel data to create multiple sheets with campaign and configuration information
3. **Google Sheets Upload**: Uploads all processed data to Google Sheets
4. **Email Notification**: Sends daily email notifications with links to the updated sheets

## 📁 Project Structure

```
├── main.py                 # Main script for downloading data from Expresso
├── data_processing.py      # Processes Excel data and uploads to Google Sheets
├── send_email.py          # Sends email notifications
├── requirements.txt       # Python dependencies
├── bitbucket-pipelines.yml # CI/CD pipeline configuration
└── Readme.md             # This file
```

## 🔧 Setup Requirements

### Environment Variables

The following environment variables must be configured in Bitbucket Pipelines:

- `EXPRESSO_USERNAME`: Username for Expresso login
- `EXPRESSO_PASSWORD`: Password for Expresso login
- `GOOGLE_SHEET_URL`: URL of the target Google Sheet
- `SERVICE_ACCOUNT_JSON`: Base64-encoded Google Service Account JSON
- `SMTP_SERVER`: SMTP server for email notifications
- `SMTP_PORT`: SMTP port (usually 587)
- `SMTP_USERNAME`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `EMAIL_RECIPIENTS`: Comma-separated list of email recipients

### Google Service Account Setup

1. Create a Google Cloud Project
2. Enable Google Sheets API and Google Drive API
3. Create a Service Account
4. Download the JSON key file
5. Base64 encode the JSON file: `base64 -i service-account.json`
6. Add the encoded string to `SERVICE_ACCOUNT_JSON` environment variable

## 🏗️ Pipeline Configuration

The project uses Bitbucket Pipelines with the following configuration:

- **Base Image**: Python 3.9
- **Services**: Docker (for memory allocation)
- **Schedule**: 
  - Morning: 11:30 AM IST (6:00 UTC) daily
  - Evening: 4:30 PM IST (11:00 UTC) daily

### Pipeline Steps

1. **Setup**: Install system dependencies (Chrome, Xvfb, etc.)
2. **Download**: Run `main.py` to download data from Expresso
3. **Process**: Run `data_processing.py` to process and upload data
4. **Notify**: Run `send_email.py` to send email notifications
5. **Artifacts**: Save logs and downloaded files

## 📊 Data Flow

### 1. Data Download (`main.py`)
- Logs into Expresso booking system
- Navigates to booking dashboard
- Sets date range to tomorrow
- Exports data as Excel file
- Renames file to `.xlsx` format

### 2. Data Processing (`data_processing.py`)
- Reads Excel file with multiple sheets (Data, Configs)
- Filters data for HB/PHB booking types
- Creates expanded Sheet2 by matching Data with Configs
- Builds Final_Innov_Details with parsed website/platform information
- Fetches impression commitment data from separate Google Sheet
- Uploads all processed data to target Google Sheet

### 3. Email Notification (`send_email.py`)
- Sends daily notification emails
- Includes link to updated Google Sheet
- Uses configured SMTP settings

## 🐛 Troubleshooting

### Common Issues

1. **Chrome Installation Failed**
   - The pipeline now uses the updated Chrome installation process for newer Debian versions
   - Uses `gpg --dearmor` instead of deprecated `apt-key`
   - Fixed duplicate repository warnings

2. **Missing Environment Variables**
   - Ensure all required environment variables are set in Bitbucket Pipelines
   - Check that `GOOGLE_SHEET_URL` is correctly configured

3. **Chrome Driver Issues**
   - The project now uses `webdriver-manager` for automatic Chrome driver management
   - This should resolve compatibility issues in CI environments

4. **Package Installation Warnings**
   - Removed deprecated `libgconf-2-4` package
   - Added error handling for optional package failures
   - Pipeline continues even if some optional packages fail

5. **Pipeline Execution Issues**
   - Added verification steps for Chrome installation
   - Added verification for service account setup
   - Added directory creation verification
   - Added Python dependency verification

### Logs

The pipeline generates detailed logs:
- `logs/download.log`: Data download process
- `logs/processing.log`: Data processing and upload
- `logs/error.log`: Any errors encountered

## 🔄 Scheduled Execution

The pipeline runs automatically twice daily:
- **Morning Update**: 11:30 AM IST - Processes data for the next day
- **Evening Update**: 4:30 PM IST - Ensures data is current

## 📈 Output Sheets

The system creates/updates the following sheets in Google Sheets:

1. **Data**: Raw data from Expresso
2. **Configs**: Configuration data with package information
3. **Config2**: Enhanced configuration data with forward-filled package details
4. **Sheet2**: Expanded data combining booking data with configurations
5. **Final_Innov_Details**: Final processed data with parsed website/platform information

## 🛠️ Local Development

To run the project locally:

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables
3. Ensure Chrome/ChromeDriver is installed
4. Run scripts individually:
   - `python main.py`
   - `python data_processing.py`
   - `python send_email.py`

### Quick Testing

For a quick verification of your setup without running the full pipeline:

```bash
python quick_test.py
```

This script tests:
- Package imports
- Selenium setup
- File structure
- Environment variables (local only)

## 📝 Notes

- The system is designed to run in headless mode in CI environments
- Uses Xvfb for virtual display when running Chrome
- Implements human-like behavior (random delays, typing patterns) to avoid detection
- Handles various website/platform parsing for different ad unit types
- Supports both ET language websites and other platforms

## 🤝 Support

For issues or questions, contact the development team or check the pipeline logs in Bitbucket Pipelines.