import os
import discord
from schedule_handler import ScheduleHandler
from discord import Client
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
SCHEDULE_CHANNEL_ID: int = 1202625883891040358
NOTIFICATION_CHANNEL_ID: int = 1201619083985162339
SCHEDULE_MESSAGE_ID: int = 1202627564888399904

# How often to check for updates (in minutes)
REFRESH_RATE: int = 10

client: Client = discord.Client(intents=discord.Intents.default())
schedule_handler: ScheduleHandler = ScheduleHandler()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    send_schedule.start()


@tasks.loop(minutes = REFRESH_RATE)
async def send_schedule():
    global last_output

    schedule_channel = client.get_channel(SCHEDULE_CHANNEL_ID)
    message = await schedule_channel.fetch_message(SCHEDULE_MESSAGE_ID)

    schedule: str = schedule_handler.get_schedule()
    notification: str = schedule_handler.get_notifications()
    
    if notification:
        notification_channel = client.get_channel(NOTIFICATION_CHANNEL_ID)
        await notification_channel.send(notification)

    await message.edit(content=schedule)


if __name__ == "__main__":
    if TOKEN is not None:
        client.run(TOKEN)

