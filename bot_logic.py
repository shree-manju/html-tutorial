# bot_logic.py

from datetime import date, timedelta
from database import SessionLocal, Member, Poll, Vote
from whatsapp_client import send_message
import config

MENU_OPTIONS = {
    '1': 'Breakfast',
    '2': 'Tiffin Box',
    '3': 'Lunch',
    '4': 'Dinner',
    '5': 'Nothing'
}

def create_daily_poll():
    print("Running job: create_daily_poll")
    db = SessionLocal()
    try:
        # 1. Deactivate any old polls
        db.query(Poll).filter(Poll.is_active == True).update({"is_active": False})
        
        # 2. Create a new poll for the next day
        poll_date = date.today() + timedelta(days=1)
        new_poll = Poll(poll_date=poll_date, is_active=True)
        db.add(new_poll)
        db.commit()

        # 3. Construct the poll message
        poll_message = f"""
        🔔 *Hostel Mess Poll for {poll_date.strftime('%A, %d %B')}* 🔔

Please select your required meals for tomorrow by replying with numbers.

1. Breakfast 🍳
2. Tiffin Box 🍱
3. Lunch 🍛
4. Dinner 🍲
5. Nothing 🙏

*Example*: To select Breakfast and Dinner, reply: `1 4`
*Important*: If you want nothing, please reply with only: `5`
"""
        # 4. Send the message to all members
        members = db.query(Member).all()
        for member in members:
            send_message(member.phone_number, poll_message)
        print("Daily poll sent to all members.")
    finally:
        db.close()

def handle_user_vote(phone_number: str, message: str):
    """Processes a user's vote from their message."""
    db = SessionLocal()
    try:
        # 1. Find the active poll
        active_poll = db.query(Poll).filter(Poll.is_active == True).first()
        if not active_poll:
            return "Sorry, there is no active poll right now."

        # 2. Parse and validate the user's choices
        choices = message.strip().split()
        if not all(c in MENU_OPTIONS for c in choices):
            return "Invalid choice. Please reply with numbers from 1 to 5 only (e.g., '1 3')."

        # 3. Enforce the "Nothing" rule
        if '5' in choices and len(choices) > 1:
            return "Invalid choice! If you select '5' (Nothing), you cannot select other options. Please vote again."

        # 4. Convert choices to text
        selection_text = ", ".join(MENU_OPTIONS[c] for c in sorted(choices))

        # 5. Save the vote to the database
        # Check if a vote from this user for this poll already exists
        existing_vote = db.query(Vote).filter_by(poll_id=active_poll.id, member_phone=phone_number).first()
        if existing_vote:
            existing_vote.selection = selection_text
        else:
            new_vote = Vote(poll_id=active_poll.id, member_phone=phone_number, selection=selection_text)
            db.add(new_vote)
        
        db.commit()
        
        # 6. Return a confirmation message
        return f"✅ Thank you! Your vote has been recorded: *{selection_text}*"
    finally:
        db.close()

def send_reminders():
    print("Running job: send_reminders")
    db = SessionLocal()
    try:
        active_poll = db.query(Poll).filter_by(is_active=True).first()
        if not active_poll:
            print("No active poll. Skipping reminders.")
            return

        all_members = {m.phone_number for m in db.query(Member).all()}
        voted_members = {v.member_phone for v in db.query(Vote).filter_by(poll_id=active_poll.id).all()}
        
        members_to_remind = all_members - voted_members
        
        if members_to_remind:
            reminder_message = "👋 *Gentle Reminder!* Please vote for tomorrow's meals. The poll is waiting for you."
            print(f"Sending reminders to {len(members_to_remind)} members.")
            for phone_number in members_to_remind:
                send_message(phone_number, reminder_message)
        else:
            print("All members have voted. No reminders to send.")
    finally:
        db.close()