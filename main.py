import gspread
from google.oauth2.service_account import Credentials
from googleads import ad_manager, errors
import smtplib
import os 
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

# 🔹 Google Sheets Authentication
creds_json = json.loads(GOOGLE_CREDENTIALS_JSON)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)

# 🔹 Open Google Sheet
SHEET_ID = "1Qx1GhhGUGM_3FWLDM04ygyAezUO2Zf6C4SlhG1h7IQA"

def get_dynamic_sheet_name():
    tomorrow = datetime.now() 
    return tomorrow.strftime('%#d %b')  # '5 Feb' (without leading zero)
SHEET_NAME=get_dynamic_sheet_name()
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
# 🔹 Define Column Mappings
COLUMN_MAPPING = {
    "order_id": 10,  # Column J
    "status": 11,  # Column K
    "trafficker_name": 9  # Column I
}

# 🔹 Get tomorrow's date in Ad Manager format
tomorrow = datetime.now() + timedelta(days=1)
tomorrow_str = tomorrow.strftime("%Y-%m-%d")
# 🔹 Store missing entries
missing_entries = []

def send_email_alert(missing_orders):
    sender_email = "anurag.mishra1@timesinternet.in"
    recipient_email = "anurag.mishra1@timesinternet.in"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    EMAIL_PASSWORD ='wyte ggls odnb yuup'

    if not EMAIL_PASSWORD:
        print("❌ SMTP password not found. Email alert skipped.")
        return

    subject = "🚨 Unconfigured Orders for Tomorrow in Google Ad Manager"
    body = "The following orders are not configured yet:\n" + "\n".join(missing_orders)

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, EMAIL_PASSWORD)
            server.send_message(msg)
        print("✅ Email Alert Sent!")
    except Exception as e:
        print(f"❌ Error Sending Email: {e}")
        
        
# Set the target date (February 2, 2024)
target_date = datetime(2025, 2, 4)  # Change the year if needed
target_date_str = target_date.strftime("%Y-%m-%d")

def fetch_order_data(account_yaml, order_name):
    """Fetch Order ID & Trafficker Name for the given order_name and start date as February 2, 2024."""
    
    try:
        ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage(account_yaml)
        order_service = ad_manager_client.GetService('OrderService')
        user_service = ad_manager_client.GetService('UserService')

        # Build query to fetch order by name and start date (Feb 2)
        statement = (
            ad_manager.StatementBuilder()
            .Where("name LIKE :orderName AND startDateTime >= :startDate AND startDateTime < :endDate")  
            .WithBindVariable("orderName", f"{order_name}%")  # Match order name
            .WithBindVariable("startDate", f"{target_date_str}T00:00:00")  # Start of Feb 2
            .WithBindVariable("endDate", f"{target_date_str}T23:59:59")  # End of Feb 2
        )

        # Fetch orders
        response = order_service.getOrdersByStatement(statement.ToStatement())

        if 'results' in response and response['results']:
            for order in response['results']:
                order_id = getattr(order, "id", None)
                trafficker_id = getattr(order, "traffickerId", None)
                # Fetch trafficker name
                trafficker_name = "Unknown"
                if trafficker_id:
                    user_statement = (
                        ad_manager.StatementBuilder()
                        .Where("id = :userId")
                        .WithBindVariable("userId", trafficker_id)
                    )
                    user_response = user_service.getUsersByStatement(user_statement.ToStatement())

                    if 'results' in user_response and user_response['results']:
                        trafficker_name = user_response['results'][0]['name']

                if order_id:
                    return order_id, trafficker_name  # Return the first found order

        # If no order found, now check for a "delivering" order (if no order found previously)
        statement_delivering = (
            ad_manager.StatementBuilder()
            .Where("name LIKE :orderName")
            .WithBindVariable("orderName", f"{order_name}%")
            .WithBindVariable("status", "DELIVERING")  # Looking for delivering orders
            .WithBindVariable("startDate", f"{target_date_str}T00:00:00")
            .WithBindVariable("endDate", f"{target_date_str}T23:59:59")
        )

        # Fetch delivering orders
        response_delivering = order_service.getOrdersByStatement(statement_delivering.ToStatement())

        if 'results' in response_delivering and response_delivering['results']:
            for order in response_delivering['results']:
                order_id = getattr(order, "id", None)
                trafficker_id = getattr(order, "traffickerId", None)
                # Fetch trafficker name
                trafficker_name = "Unknown"
                if trafficker_id:
                    user_statement = (
                        ad_manager.StatementBuilder()
                        .Where("id = :userId")
                        .WithBindVariable("userId", trafficker_id)
                    )
                    user_response = user_service.getUsersByStatement(user_statement.ToStatement())

                    if 'results' in user_response and user_response['results']:
                        trafficker_name = user_response['results'][0]['name']

                if order_id:
                    return order_id, trafficker_name  # Return the found delivering order

        return None, None  # If no order found, return None

    except Exception as e:
        print(f"❌ Error fetching order from {account_yaml}: {e}")
        return None, None




if __name__ == "__main__":
    # 🔹 Read Column C (Order Names) - Skipping header
    old_client = ad_manager.AdManagerClient.LoadFromString(f"""
   ad_manager:
    application_name: {os.getenv('APPLICATION_NAME')}
    network_code: {os.getenv('NETWORK_CODE1')}
    client_id: {os.getenv('CLIENT_ID')}
    client_secret: {os.getenv('CLIENT_SECRET')}
    refresh_token: {os.getenv('REFRESH_TOKEN')}
  """)
    new_client = ad_manager.AdManagerClient.LoadFromString(f"""
   ad_manager:
    application_name: {os.getenv('APPLICATION_NAME')}
    network_code: {os.getenv('NETWORK_CODE2')}
    client_id: {os.getenv('CLIENT_ID')}
    client_secret: {os.getenv('CLIENT_SECRET')}
    refresh_token: {os.getenv('REFRESH_TOKEN')}
  """)
    expresso_id = sheet.col_values(3)[1:]
    print(f'Expresso ID:{expresso_id}')
    for i, expresso_id in enumerate(expresso_id):
        try:
            # Fetch order details from both GAM accounts
            order_id_7176, trafficker_7176 = fetch_order_data(old_client, expresso_id)
            print(f'order id for old is {order_id_7176}')
            
            order_id_23037861279, trafficker_23037861279 = fetch_order_data(new_client, expresso_id)
            print(f'order id for new is {order_id_23037861279}')

            order_ids = []
            trafficker_names = []

            if order_id_7176 and order_id_23037861279:
                status = "Configured"
                order_ids.extend([str(order_id_7176), str(order_id_23037861279)])
                trafficker_names.extend([trafficker_7176, trafficker_23037861279])
            elif order_id_7176:
                status = "Configured for 7176 only"
                order_ids.append(str(order_id_7176))
                trafficker_names.append(trafficker_7176)
            elif order_id_23037861279:
                status = "Configured in 23037861279 only"
                order_ids.append(str(order_id_23037861279))
                trafficker_names.append(trafficker_23037861279)
            else:
                # Check if the order is "Delivering" in either of the accounts
                status = "Not Configured"
                missing_entries.append(expresso_id)

            # 🔹 Update Google Sheet
            sheet.update_cell(i + 2, COLUMN_MAPPING["order_id"], ", ".join(order_ids) if order_ids else "N/A")
            sheet.update_cell(i + 2, COLUMN_MAPPING["status"], status)
            sheet.update_cell(i + 2, COLUMN_MAPPING["trafficker_name"], ", ".join(set(trafficker_names)) if trafficker_names else "Unknown")

            print(f"✅ Updated {expresso_id}: {status}")

        except errors.GoogleAdsServerFault as e:
            print(f"❌ GAM Server Error for {expresso_id}: {e}")
        except errors.GoogleAdsValueError as e:
            print(f"❌ Value Error in Query for {expresso_id}: {e}")
        except Exception as e:
            print(f"❌ General Error for {expresso_id}: {e}")
            missing_entries.append(expresso_id)

    # 🔹 Trigger Email Alert if Orders are Missing
    if missing_entries:
        send_email_alert(missing_entries)

    print("✅ Google Sheet Updated Successfully!")
