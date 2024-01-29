import os
import discord
from schedule_handler import ScheduleHandler
from discord import Client
from discord.ext import tasks


TOKEN: str|None = os.getenv('DISCORD_TOKEN')
TOKEN = "MTIwMTU2ODAwNTkwMjA1MzUxNg.GtTlCI.nknJfx20MtrQnZt05uhQIx72rRDudxW6aoS_BE"
SCHEDULE_CHANNEL_ID: int = 1201567101324890252
NOTIFICATION_CHANNEL_ID: int = 1201619083985162339
SCHEDULE_MESSAGE_ID: int = 1201617633024422088

client: Client = discord.Client(intents=discord.Intents.default())
schedule_handler: ScheduleHandler = ScheduleHandler()
last_output: str = ""


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    send_schedule.start()


@tasks.loop(minutes = 15)
async def send_schedule():
    global last_output

    schedule_channel = client.get_channel(SCHEDULE_CHANNEL_ID)
    message = await schedule_channel.fetch_message(SCHEDULE_MESSAGE_ID)

    output: str = schedule_handler.get_schedule()

    if not output == last_output:
        notification_channel = client.get_channel(NOTIFICATION_CHANNEL_ID)
        await notification_channel.send(":exclamation: Ett nytt rep har lagts till!")

    last_output = output
    
    await message.edit(content=output)


if __name__ == "__main__":
    if TOKEN is not None:
        client.run(TOKEN)

