# whatsapp_client.py

import pywhatkit
import time
from datetime import datetime

def send_message(phone_number: str, message: str):
    """
    Sends a WhatsApp message to a given phone number.
    Note: pywhatkit requires a logged-in WhatsApp Web session.
    """
    try:
        # pywhatkit needs the country code, so we ensure it's there
        if not phone_number.startswith('+'):
            # Assuming Indian numbers if no country code is present
            if not phone_number.startswith('91'):
                 phone_number = f'+91{phone_number}'
            else:
                 phone_number = f'+{phone_number}'

        print(f"Sending message to {phone_number}: '{message[:30]}...'")
        
        # Get current time to schedule message
        now = datetime.now()
        
        # Schedule message for 15 seconds from now to give pywhatkit time
        pywhatkit.sendwhatmsg_instantly(
            phone_no=phone_number,
            message=message,
            wait_time=15, # seconds to wait before sending
            tab_close=True,
            close_time=3 # seconds to wait before closing tab
        )
        print("Message scheduled successfully.")
        # Add a small delay to avoid rate-limiting issues when sending to many users
        time.sleep(10) 
        
    except Exception as e:
        print(f"Error sending message to {phone_number}: {e}")