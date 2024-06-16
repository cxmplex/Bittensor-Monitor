import discord
from discord.ext import commands
from config import TOKEN
from tasks.neuron_tasks import sync_subnets

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    await bot.load_extension("commands.neuron_commands")
    await bot.load_extension("commands.watch_commands")

@bot.event
async def on_ready():
    print(f'Bot is logged in as {bot.user.name}!')
    sync_subnets.start()

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

