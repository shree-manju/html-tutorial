# app.py

from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
import bot_logic
import database
import config
import atexit

# Initialize the database and add members from config
print("Initializing database...")
database.init_db()
print("Database initialized.")

# -- NOTE ON RECEIVING MESSAGES --
# To receive messages automatically, you need a webhook.
# The code below sets up a Flask server for this purpose.
# However, this only works with the OFFICIAL WhatsApp Business API.
# With the current pywhatkit setup, you cannot receive replies automatically.
# This webhook is here as a template for when you upgrade to the official API.

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    # This is a placeholder for the official API integration
    # You would parse the incoming message from the request body
    # For example:
    # data = request.get_json()
    # sender_phone = data['messages'][0]['from']
    # message_text = data['messages'][0]['text']['body']
    # confirmation = bot_logic.handle_user_vote(sender_phone, message_text)
    # whatsapp_client.send_message(sender_phone, confirmation)
    print("Webhook received (placeholder).")
    return "OK", 200


if __name__ == '__main__':
    # Setup the scheduler
    scheduler = BackgroundScheduler()
    
    # Schedule the daily poll job
    poll_hour, poll_minute = map(int, config.POLL_CREATION_TIME.split(':'))
    scheduler.add_job(
        bot_logic.create_daily_poll,
        'cron',
        hour=poll_hour,
        minute=poll_minute
    )
    
    # Schedule the reminder job
    scheduler.add_job(
        bot_logic.send_reminders,
        'interval',
        minutes=config.REMINDER_INTERVAL_MINUTES
    )
    
    # Start the scheduler
    scheduler.start()
    print("Scheduler started. Poll will be sent daily at", config.POLL_CREATION_TIME)
    print("Reminders will be sent every", config.REMINDER_INTERVAL_MINUTES, "minutes.")
    
    # Ensure scheduler shuts down when the app exits
    atexit.register(lambda: scheduler.shutdown())
    
    # Since we can't receive messages, we will simulate it via command line
    # for testing purposes.
    print("\n--- MANUAL VOTE SIMULATION ---")
    print("The bot is running. To test voting, enter a phone number and their vote.")
    print("Type 'exit' to quit.")
    while True:
        try:
            inp = input("Enter [phone_number] [vote] (e.g., 919876543210 1 3): ")
            if inp.lower() == 'exit':
                break
            parts = inp.split()
            phone = parts[0]
            vote_msg = " ".join(parts[1:])
            confirmation = bot_logic.handle_user_vote(phone, vote_msg)
            print(f"--> BOT: {confirmation}")
        except Exception as e:
            print(f"Invalid input or error: {e}")

    # In a real scenario with the official API, you would run the Flask app:
    # app.run(port=5000, debug=True)