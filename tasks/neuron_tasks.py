import asyncio
from discord.ext import tasks
from utils.redis_utils import store_neurons_lite
import bittensor

subtensor = bittensor.subtensor(network='finney')

@tasks.loop(minutes=10)
async def sync_subnets():
    print("syncing subnets")
    all_netuids = subtensor.get_all_subnet_netuids()
    await store_neurons_lite(all_netuids)
    print("finished syncing subnets")

