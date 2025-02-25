import discord
import re
import os
import dotenv
from discord.ext import commands
from ProjectFiles.API_Backend import studocu_scraper, quizlet_scraper, brainly_scraper, homework_scraper  # Import Homework scraper

# Load environment variables from .env
dotenv.load_dotenv()

# Retrieve the token
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    raise ValueError("❌ DISCORD_TOKEN not found! Make sure your .env file is correctly set.")

WATCHED_CHANNELS = ["123456789012345678", "1262248819895177416"]  # Replace with actual channel IDs

# Define the bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Required to read message content
bot = commands.Bot(command_prefix="!", intents=intents)

# Regex patterns for supported websites
STUDOCU_REGEX = re.compile(r"(https?:\/\/www\.studocu\.com[^\s]*)")
QUIZLET_REGEX = re.compile(r"(https?:\/\/quizlet\.com[^\s]*)")
BRAINLY_REGEX = re.compile(r"(https?:\/\/brainly\.[^\s]*)")
HOMEWORK_REGEX = re.compile(r"(https?:\/\/homework\.study\.com[^\s]*)")  # New Homework.Study.com support

@bot.event
async def on_ready():
    print(f"✅ {bot.user.name} is online and watching channels: {WATCHED_CHANNELS}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore bot's own messages

    if str(message.channel.id) not in WATCHED_CHANNELS:
        return  # Ignore messages from channels not being watched

    html_file = None  # Variable to store the scraped file path

    # Check if it's a Studocu link
    if STUDOCU_REGEX.search(message.content):
        studocu_url = STUDOCU_REGEX.search(message.content).group(0)
        await message.channel.send(f"📄 Processing Studocu link: {studocu_url}")
        html_file = studocu_scraper.scrape_studocu(studocu_url)
    
    # Check if it's a Quizlet link
    elif QUIZLET_REGEX.search(message.content):
        quizlet_url = QUIZLET_REGEX.search(message.content).group(0)
        await message.channel.send(f"📄 Processing Quizlet link: {quizlet_url}")
        html_file = quizlet_scraper.scrape_quizlet(quizlet_url)

    # Check if it's a Brainly link
    elif BRAINLY_REGEX.search(message.content):
        brainly_url = BRAINLY_REGEX.search(message.content).group(0)
        await message.channel.send(f"📄 Processing Brainly link: {brainly_url}")
        html_file = brainly_scraper.scrape_brainly(brainly_url)

    # Check if it's a Homework.Study.com link
    elif HOMEWORK_REGEX.search(message.content):
        homework_url = HOMEWORK_REGEX.search(message.content).group(0)
        await message.channel.send(f"📄 Processing Homework.Study.com link: {homework_url}")
        html_file = homework_scraper.scrape_homework(homework_url)

    else:
        return  # No supported links

    if html_file:
        # Send the HTML file back to the user
        await message.channel.send(file=discord.File(html_file))

        # Delete the file after sending
        os.remove(html_file)

# Run the bot
bot.run(TOKEN)