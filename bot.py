from discord.ext import commands
import discord
from config import TOKEN

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

