import telebot
from datetime import datetime, timedelta
from supabase import create_client, Client
import re

# Initialize Supabase
SUPABASE_URL = "https://ywhnhtzxhfqcmmululxu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl3aG5odHp4aGZxY21tdWx1bHh1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQ5NDA1NzUsImV4cCI6MjA1MDUxNjU3NX0.gUFcc9VsVUGsiy3A020fOzci9z4WYr8n9ZMuMknxU34"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

bot = telebot.TeleBot("8064399090:AAHgWV2RflfYE-TEeOYn-cvLdHjlbua44ow")

GAS_FEE_ADDRESS = "0x31b63faefc80f4570812aa75743d46d03c22574e"
GAS_FEE_BNB = 0.00314542  # Gas fee in BNB


@bot.message_handler(commands=['start', 'help', 'claim', 'balance', 'refferfriends', 'refferals', 'connectwallet', 'withdraw'])
def handle_command(message):
    user_id = message.from_user.id

    if message.text.startswith('/start'):
        referrer_id = None
        # Parse referrer ID if provided in the start command
        if len(message.text.split()) > 1:
            referrer_id = int(message.text.split()[1])
        
        # Check if user exists in the database
        user = get_user(user_id)
        if not user:
            add_user(user_id, referrer_id)

        with open("C:/Users/ADMI8N/Desktop/bots/R8_SD3_00001_.webp", "rb") as image_file:
            bot.send_photo(
                message.chat.id,
                image_file,
                caption=(
                    "Hello, I am ODOSE Airdrop Bot.\n"
                    "Get 1 $ODOSE For Completing All Tasks\n"
                    "Get Extra 0.2 $ODOSE For Every Referral\n"
                    "Mandatory Airdrop Tasks:\n"
                    "Join: @aic_coin_community\n"
                    "Must complete mandatory tasks to proceed."
                )
            )

    elif message.text == '/withdraw':
        bot.send_message(
            message.chat.id,
            f"To withdraw your poinst, wait until the listind date"
            # f"To withdraw your points, please enter the amount you wish to withdraw (in $ODOSE). The gas fee of {GAS_FEE_BNB} BNB will be sent to {GAS_FEE_ADDRESS}."
        )
        # bot.register_next_step_handler(message, handle_withdraw)

    elif message.text == '/help':
        bot.send_message(
            message.chat.id,
            "Command:\n"
            "/start - Start the bot\n"
            "/help - Open help menu\n"
            # "/info - Show bot info\n"
            # "/status - Show status of user\n"
            "/claim - Claim points every 4 hours\n"
            "/balance - Show your current balance\n"
            "/refferfriends - Get your referral link\n"
            "/refferals - See how many users you referred\n"
            "/connectwallet - Connect your BNB wallet\n"
            "/withdraw - Withdraw your points"
        )

    elif message.text == '/info':
        bot.send_message(message.chat.id, "I am a simple Telegram bot created by NOCORPS org.")
    
    elif message.text == '/status':
        bot.send_message(message.chat.id, "Not fully completed bot. Please wait until we finish this bot.")
    
    elif message.text == '/claim':
        now = datetime.now()

        user = get_user(user_id)
        if user:
            last_claim_time = user['last_claim_time']
            if last_claim_time:
                last_claim_time = datetime.fromisoformat(last_claim_time)
                if now - last_claim_time < timedelta(hours=4):
                    remaining_time = timedelta(hours=4) - (now - last_claim_time)
                    bot.send_message(
                        message.chat.id,
                        f"You can claim again in {remaining_time.seconds // 3600} hours and "
                        f"{(remaining_time.seconds // 60) % 60} minutes."
                    )
                    return
            
            # Update claim time and balance
            new_balance = round(user['balance'] + 12.565, 2)
            update_user(user_id, now, new_balance)
            bot.send_message(
                message.chat.id,
                f"Congratulations! You've claimed 12.565 $ODOSE. Your new balance is {new_balance} $ODOSE. Come back after 4 hours to claim again!"
            )
        else:
            add_user(user_id, None)
            bot.send_message(
                message.chat.id,
                "Congratulations! You've claimed 12.565 $ODOSE. Come back after 4 hours to claim again!"
            )
    
    elif message.text == '/balance':
        user = get_user(user_id)
        if user:
            bot.send_message(
                message.chat.id,
                f"Your current balance is {user['balance']} $ODOSE."
            )
        else:
            add_user(user_id, None)
            bot.send_message(
                message.chat.id,
                "Your current balance is 0 $ODOSE."
            )
    
    elif message.text == '/refferfriends':
        bot.send_message(
            message.chat.id,
            f"Share this referral link to your friends:\n"
            f"https://t.me/odose_bot?start={user_id}"
        )
    
    elif message.text == '/refferals':
        user = get_user(user_id)
        if user:
            bot.send_message(
                message.chat.id,
                f"You have referred {user['referral_count']} friends successfully!"
            )
        else:
            bot.send_message(
                message.chat.id,
                "You haven't referred anyone yet."
            )
    
    elif message.text == '/connectwallet':
        bot.send_message(
            message.chat.id,
            "To connect your BNB wallet, send your BEP20 BNB wallet address."
        )
        bot.register_next_step_handler(message, save_wallet_address)

# def handle_withdraw(message):
#     user_id = message.from_user.id
#     withdraw_amount = float(message.text.strip())

#     user = get_user(user_id)
#     if user:
#         balance = user['balance']
        
#         if withdraw_amount <= 0:
#             bot.send_message(message.chat.id, "Invalid amount. Please enter a positive number.")
#             return

#         if withdraw_amount > balance:
#             bot.send_message(message.chat.id, f"Insufficient balance. Your current balance is {balance} $ODOSE.")
#             return
        
#         # Deduct the gas fee and transfer points
#         transfer_amount = withdraw_amount - GAS_FEE_BNB

#         if transfer_amount <= 0:
#             bot.send_message(message.chat.id, "Insufficient points to cover the gas fee. Please try a smaller amount.")
#             return
        
#         # Simulating sending gas fee and tracking the reference number
#         transaction_reference = "REFERENCE_123456789"  # Simulated transaction reference

#         # Update the user's balance and store the transaction reference in the database
#         new_balance = round(balance - withdraw_amount, 2)
#         update_user(user_id, None, new_balance, user['referral_count'], user.get('wallet_address'))

#         # Log the gas fee transaction
#         log_gas_fee_transaction(user_id, GAS_FEE_BNB, transaction_reference)

#         bot.send_message(
#             message.chat.id,
#             f"Your withdrawal of {withdraw_amount} $ODOSE has been successfully processed!\n"
#             f"Gas Fee of {GAS_FEE_BNB} BNB has been sent to {GAS_FEE_ADDRESS}.\n"
#             f"Transaction Reference: {transaction_reference}\n"
#             f"Your new balance is {new_balance} $ODOSE."
#         )
#     else:
#         bot.send_message(message.chat.id, "You are not registered. Please use /start to begin.")

def log_gas_fee_transaction(user_id, gas_fee, reference_number):
    """Store the gas fee transaction details in a separate table."""
    supabase.table('gas_fee_transactions').insert({
        'user_id': user_id,
        'gas_fee': gas_fee,
        'reference_number': reference_number,
        'timestamp': datetime.now().isoformat()
    }).execute()

# Database helper functions
def get_user(user_id):
    response = supabase.table('user_data').select('*').eq('user_id', user_id).execute()
    return response.data[0] if response.data else None

def add_user(user_id, referrer_id):
    if referrer_id:
        referrer = get_user(referrer_id)
        if referrer:
            # Increment referrer's referral count and update balance
            update_user(referrer_id, None, referrer['balance'] + 0.2, referrer['referral_count'] + 1)
    supabase.table('user_data').insert({
        'user_id': user_id,
        'last_claim_time': None,
        'balance': 0,
        'referrer_id': referrer_id,
        'referral_count': 0,
        'wallet_address': None  # New field to store the wallet address
    }).execute()

def update_user(user_id, last_claim_time, balance, referral_count=None, wallet_address=None):
    update_data = {}
    if balance is not None:
        update_data['balance'] = balance
    if last_claim_time:
        update_data['last_claim_time'] = last_claim_time.isoformat()
    if referral_count is not None:
        update_data['referral_count'] = referral_count
    if wallet_address is not None:
        update_data['wallet_address'] = wallet_address

    supabase.table('user_data').update(update_data).eq('user_id', user_id).execute()

# def save_wallet_address(message):
#     user_id = message.from_user.id
#     wallet_address = message.text.strip()

#     # Validate BEP20 address format using regex (simplified version)
#     if re.match(r"^(0x)?[0-9a-fA-F]{40}$", wallet_address):
#         user = get_user(user_id)
#         if user:
#             # Use the existing update_user function to save the wallet address
#             update_user(user_id, None, None, None, wallet_address)
#             bot.send_message(
#                 message.chat.id,
#                 f"Your BNB wallet address has been connected successfully!\n"
#                 f"Wallet Address: {wallet_address}"
#             )
#         else:
#             bot.send_message(
#                 message.chat.id,
#                 "It seems like you're not registered. Please use /start to begin."
#             )
#     else:
#         bot.send_message(
#             message.chat.id,
#             "Invalid BNB wallet address. Please provide a valid BNB address (format: 0x or 40 alphanumeric characters)."
#         )
#         bot.register_next_step_handler(message, save_wallet_address)


def save_wallet_address(message):
    user_id = message.from_user.id
    wallet_address = message.text.strip()

    # Validate BEP20 address format using regex (simplified version)
    if re.match(r"^(0x)?[0-9a-fA-F]{40}$", wallet_address):
        user = get_user(user_id)
        if user:
            if user.get('wallet_address'):  # Check if wallet is already connected
                bot.send_message(
                    message.chat.id,
                    f"You have already connected a wallet.\n"
                    f"Connected Wallet Address: {user['wallet_address']}"
                )
                return
            
            # Use the existing update_user function to save the wallet address
            update_user(user_id, None, None, None, wallet_address)
            bot.send_message(
                message.chat.id,
                f"Your BNB wallet address has been connected successfully!\n"
                f"Wallet Address: {wallet_address}"
            )
        else:
            bot.send_message(
                message.chat.id,
                "It seems like you're not registered. Please use /start to begin."
            )
    else:
        bot.send_message(
            message.chat.id,
            "Invalid BNB wallet address. Please provide a valid BNB address (format: 0x or 40 alphanumeric characters)."
        )
        bot.register_next_step_handler(message, save_wallet_address)

print("Bot started...")
bot.polling()