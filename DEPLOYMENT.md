# Deployment Guide

This guide explains how to deploy the Times Internet Innovation Sheet Updater to Bitbucket Pipelines.

## 🚀 Prerequisites

1. **Bitbucket Repository**: The code must be in a Bitbucket repository
2. **Bitbucket Pipelines**: Pipelines must be enabled for the repository
3. **Google Cloud Project**: For Google Sheets API access
4. **SMTP Access**: For email notifications

## 🔧 Step-by-Step Deployment

### 1. Repository Setup

1. Push your code to a Bitbucket repository
2. Ensure the following files are present:
   - `main.py`
   - `data_processing.py`
   - `send_email.py`
   - `requirements.txt`
   - `bitbucket-pipelines.yml`
   - `test_setup.py` (optional, for testing)

### 2. Enable Bitbucket Pipelines

1. Go to your repository in Bitbucket
2. Navigate to **Repository settings** → **Pipelines**
3. Click **Enable Pipelines**
4. Choose **Python** as the language

### 3. Configure Repository Variables

Go to **Repository settings** → **Pipelines** → **Repository variables** and add:

#### Required Variables:
- `EXPRESSO_USERNAME`: Your Expresso login username
- `EXPRESSO_PASSWORD`: Your Expresso login password
- `GOOGLE_APPS_SCRIPT_URL`: URL of your target Google Sheet
- `SERVICE_ACCOUNT_JSON`: Base64-encoded Google service account JSON

#### Optional Variables:
- `SMTP_SERVER`: SMTP server (default: smtp.gmail.com)
- `SMTP_PORT`: SMTP port (default: 587)
- `SMTP_USERNAME`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `EMAIL_RECIPIENTS`: Comma-separated email addresses

### 4. Google Service Account Setup

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable APIs**:
   - Go to **APIs & Services** → **Library**
   - Enable **Google Sheets API**
   - Enable **Google Drive API**

3. **Create Service Account**:
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **Service Account**
   - Fill in details and click **Create**

4. **Generate Key**:
   - Click on the created service account
   - Go to **Keys** tab
   - Click **Add Key** → **Create New Key**
   - Choose **JSON** format
   - Download the key file

5. **Base64 Encode**:
   ```bash
   base64 -i service-account.json
   ```
   Copy the output and paste it into `SERVICE_ACCOUNT_JSON` variable

6. **Share Google Sheet**:
   - Open your target Google Sheet
   - Click **Share** button
   - Add the service account email (from the JSON file) with **Editor** access

### 5. Test the Setup

1. **Run Test Script** (optional):
   ```bash
   python test_setup.py
   ```

2. **Manual Pipeline Trigger**:
   - Go to **Pipelines** in your repository
   - Click **Run pipeline**
   - Select **main** branch
   - Click **Run**

### 6. Monitor Deployment

1. **Check Pipeline Status**:
   - Monitor the pipeline execution in real-time
   - Check logs for any errors

2. **Verify Artifacts**:
   - After successful completion, check the artifacts
   - Verify logs are generated
   - Check if data is uploaded to Google Sheets

3. **Check Email Notifications**:
   - Verify that email notifications are sent
   - Check spam folder if emails don't arrive

## 🔍 Troubleshooting

### Common Issues:

1. **Chrome Installation Failed**:
   - The pipeline now uses updated Chrome installation
   - Check logs for specific error messages

2. **Service Account Issues**:
   - Verify the JSON is properly base64 encoded
   - Check that the service account has proper permissions
   - Ensure the Google Sheet is shared with the service account

3. **Environment Variable Issues**:
   - Double-check all required variables are set
   - Verify variable names match exactly (case-sensitive)
   - Check for extra spaces or special characters

4. **Permission Issues**:
   - Ensure the service account has Editor access to the Google Sheet
   - Check that Google Sheets API is enabled
   - Verify the sheet URL is correct

### Debug Steps:

1. **Check Pipeline Logs**:
   - Review the complete pipeline execution log
   - Look for error messages and stack traces

2. **Verify File Structure**:
   - Ensure all required files are present
   - Check file permissions and content

3. **Test Locally**:
   - Run the test script locally if possible
   - Check environment variables locally

4. **Review Artifacts**:
   - Check generated log files
   - Verify downloaded data files

## 📊 Monitoring and Maintenance

### Regular Checks:

1. **Pipeline Execution**:
   - Monitor scheduled pipeline runs
   - Check for failed executions

2. **Data Quality**:
   - Verify data is being uploaded correctly
   - Check Google Sheets for completeness

3. **Email Notifications**:
   - Ensure emails are being sent
   - Verify recipient lists are current

### Updates and Maintenance:

1. **Dependency Updates**:
   - Regularly update Python packages
   - Test updates in development environment

2. **Configuration Changes**:
   - Update environment variables as needed
   - Modify Google Sheet URLs if required

3. **Error Handling**:
   - Review and improve error handling
   - Add more detailed logging if needed

## 🆘 Support

If you encounter issues:

1. **Check the logs** first for specific error messages
2. **Review this deployment guide** for common solutions
3. **Contact the development team** with specific error details
4. **Check Bitbucket Pipelines documentation** for general issues

## 📝 Notes

- The pipeline runs twice daily (morning and evening)
- All sensitive data is stored in repository variables
- The system is designed to run headless in CI environment
- Chrome and Xvfb are automatically installed and configured
- Logs and artifacts are preserved for debugging 