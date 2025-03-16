import discord
from discord.ext import commands
import random
import asyncio
import json
import os
from datetime import datetime

# Set up intents
intents = discord.Intents.default()
intents.messages = True  # Allow the bot to read messages
intents.message_content = True  # Enable Message Content Intent

# Initialize the bot with no command prefix (prefix will be handled manually)
bot = commands.Bot(command_prefix="", intents=intents)

# File to store user data
DATA_FILE = "user_data.json"

# Load user data from file
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {"cash": {}, "daily_cooldown": {}, "puzzle_cooldown": {}}

# Save user data to file
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Dictionary to store user cash balances and cooldowns
user_data = load_data()

# Function to get a user's cash balance
def get_cash(user_id):
    return user_data["cash"].get(str(user_id), 0)

# Function to add cash to a user's balance
def add_cash(user_id, amount):
    user_data["cash"][str(user_id)] = get_cash(user_id) + amount
    save_data(user_data)

# Function to remove cash from a user's balance
def remove_cash(user_id, amount):
    user_data["cash"][str(user_id)] = max(0, get_cash(user_id) - amount)
    save_data(user_data)

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} is online!')

# Command: Help
@bot.event
async def on_message(message):
    if message.author.bot:  # Ignore messages from bots
        return

    # Check if the message starts with "ll"
    if message.content.startswith("ll "):
        content = message.content[3:].strip().lower()  # Remove "ll " from the message
        ctx = await bot.get_context(message)

        if content.startswith("cash"):
            # Handle cash command
            user_id = message.author.id
            cash_balance = get_cash(user_id)
            await message.reply(f"{message.author.mention}, you have **{cash_balance}** cash! 💰")

        elif content.startswith("daily"):
            # Handle daily command
            user_id = str(message.author.id)

            # Check if the user has already claimed their daily cash today
            if user_id in user_data["daily_cooldown"]:
                last_claimed = datetime.fromtimestamp(user_data["daily_cooldown"][user_id])
                if datetime.now().date() == last_claimed.date():
                    await message.reply(f"{message.author.mention}, you've already claimed your daily cash today! Come back tomorrow. ⏳")
                    return

            # Add 2,000 cash to the user's balance
            add_cash(message.author.id, 2000)
            user_data["daily_cooldown"][user_id] = datetime.now().timestamp()
            save_data(user_data)
            await message.reply(f"{message.author.mention}, you claimed **2,000** daily cash! 💸")

        elif content.startswith("gg"):
            # Handle gg command with animation
            try:
                amount = content.split()[1]
                if amount == "all":
                    amount = get_cash(message.author.id)
                else:
                    amount = int(amount)

                user_id = message.author.id
                cash_balance = get_cash(user_id)

                # Check if the user has enough cash to gamble
                if amount <= 0:
                    await message.reply(f"{message.author.mention}, you must gamble a positive amount! ❌")
                    return
                if cash_balance < amount:
                    await message.reply(f"{message.author.mention}, you don't have enough cash! ❌")
                    return

                # Start the gambling animation
                animation_message = await message.reply("🎰 Rolling... 🎰")
                for _ in range(3):  # Simulate a rolling effect
                    await asyncio.sleep(1)  # Wait for 1 second
                    await animation_message.edit(content="🎰 Rolling... 🎰\n" + " ".join(random.choices(["💎", "🍒", "🍀", "💰", "🎯"], k=3)))

                # Determine the result of the gamble
                if random.choice([True, False]):  # 50% chance to win or lose
                    add_cash(user_id, amount)
                    await animation_message.edit(content=f"🎉 {message.author.mention}, you won **{amount}** cash! 🎉\nYour new balance is **{get_cash(user_id)}** cash. 💰")
                else:
                    remove_cash(user_id, amount)
                    await animation_message.edit(content=f"😢 {message.author.mention}, you lost **{amount}** cash! 😢\nYour new balance is **{get_cash(user_id)}** cash. 💰")

            except (IndexError, ValueError):
                await message.reply(f"{message.author.mention}, please specify a valid amount! ❌")

        elif content.startswith("give"):
            # Handle give command
            try:
                parts = content.split()
                amount = int(parts[1])  # Extract the amount
                recipient = message.mentions[0]  # Extract the mentioned user
                user_id = message.author.id
                recipient_id = recipient.id

                # Check if the user has enough cash to give
                if amount <= 0:
                    await message.reply(f"{message.author.mention}, you must give a positive amount! ❌")
                    return
                if get_cash(user_id) < amount:
                    await message.reply(f"{message.author.mention}, you don't have enough cash! ❌")
                    return

                # Transfer cash
                remove_cash(user_id, amount)
                add_cash(recipient_id, amount)
                await message.reply(f"{message.author.mention}, you gave **{amount}** cash to {recipient.mention}! 💸")
            except (IndexError, ValueError):
                await message.reply(f"{message.author.mention}, please specify a valid amount and recipient! ❌")

        elif content.startswith("leaderboard"):
            # Handle leaderboard command
            sorted_users = sorted(user_data["cash"].items(), key=lambda x: x[1], reverse=True)[:10]
            leaderboard_message = "🏆 **Top 10 Players** 🏆\n"
            for i, (user_id, cash) in enumerate(sorted_users, start=1):
                user = await bot.fetch_user(user_id)
                leaderboard_message += f"{i}. {user.name}: **{cash}** cash\n"
            await message.reply(leaderboard_message)

        elif content.startswith("puzzle"):
            # Handle puzzle command
            user_id = str(message.author.id)

            # Check if the user has already solved the puzzle today
            if user_id in user_data["puzzle_cooldown"]:
                last_solved = datetime.fromtimestamp(user_data["puzzle_cooldown"][user_id])
                if datetime.now().date() == last_solved.date():
                    await message.reply(f"{message.author.mention}, you've already solved the puzzle today! Come back tomorrow. ⏳")
                    return

            # Generate a unique puzzle (example: math puzzle)
            puzzle_question = "What is 12 + 15?"
            correct_answer = "27"
            options = ["22", "27", "30", "35"]

            # Send the puzzle
            await message.reply(
                f"🧩 **Daily Puzzle** 🧩\n"
                f"{message.author.mention}, solve this puzzle to earn **20,000** cash!\n"
                f"**Question:** {puzzle_question}\n"
                f"**Options:** {', '.join(options)}"
            )

            # Wait for the user's response
            def check(m):
                return m.author == message.author and m.channel == message.channel

            try:
                response = await bot.wait_for("message", timeout=30.0, check=check)
                if response.content == correct_answer:
                    add_cash(message.author.id, 20000)
                    user_data["puzzle_cooldown"][user_id] = datetime.now().timestamp()
                    save_data(user_data)
                    await message.reply(f"🎉 Correct! {message.author.mention}, you earned **20,000** cash! 💰")
                else:
                    await message.reply(f"❌ Incorrect! The correct answer was **{correct_answer}**. Better luck tomorrow! 😢")
            except asyncio.TimeoutError:
                await message.reply(f"⏰ Time's up! {message.author.mention}, you took too long to answer. 😢")

    # Allow other commands to work
    await bot.process_commands(message)

# Run the bot
bot.run('MTM1MDMwNTIwMjcxNjE1MTk3MQ.GMIo-l.IL-C02M_PPLAigXpWPdAyD1K9pUOHfz5jTWC6k')  # Replace with your bot's token