import logging
import os
import sys
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/process_data.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    try:
        logging.info("Starting data processing")
        
        # Create necessary directories
        os.makedirs('BookingData_folder', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        logging.info("Created directories: BookingData_folder and logs")
        
        # Your existing data processing code here
        # ...
        
        logging.info("Data processing completed successfully")
        
    except Exception as e:
        logging.error(f"Error in data processing: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 