from discord.ext import commands
from utils.redis_utils import get_watch_tasks, update_watch_tasks, remove_watch_task, get_all_neuron_info_lites
from utils.pagination import paginate
import json

class WatchCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='watch')
    async def watch(self, ctx, coldkey: str):
        discord_user_id = str(ctx.author.id)
        # Add the coldkey to the user's watch list
        await update_watch_tasks(discord_user_id, coldkey)

        # Retrieve all neuron info lites for the given coldkey
        neuron_info_lites = await get_all_neuron_info_lites([coldkey])
        if neuron_info_lites:
            neuron_info_lites_sorted = sorted(neuron_info_lites, key=lambda x: x.netuid)
            response_parts = []
            current_uid = None
            current_message = ""

            for neuron in neuron_info_lites_sorted:
                if neuron.netuid != current_uid:
                    if current_uid is not None:
                        response_parts.append(current_message)
                        current_message = ""
                    current_uid = neuron.netuid
                    current_message += f'Subnet {current_uid}:\n'
                current_message += f'{neuron.hotkey}:{neuron.axon_info.addr}\n'

                if len(current_message) > 1800:  # Check if the response is getting too long
                    response_parts.append(current_message)
                    current_message = f'Subnet {current_uid} (continued):\n'

            if current_message:
                response_parts.append(current_message)

            await paginate(ctx, response_parts)
        else:
            await ctx.send(f'{ctx.author.mention}, you are now watching {coldkey} but no neurons found yet!')

    @commands.command(name='unwatch')
    async def unwatch(self, ctx, coldkey: str):
        discord_user_id = str(ctx.author.id)
        await remove_watch_task(discord_user_id, coldkey)
        await ctx.send(f'{ctx.author.mention}, you have stopped watching {coldkey}.')

    @commands.command(name='watch_tasks')
    async def watch_tasks(self, ctx):
        watch_tasks = await get_watch_tasks()
        if watch_tasks:
            response = "Current watch tasks:\n\n"
            for task in watch_tasks:
                user_id = task["discord_user_id"]
                coldkeys = task["coldkeys"]
                response += f"User ID: {user_id}\nColdkeys:\n" + "\n".join(coldkeys) + "\n\n"
            await ctx.send(response)
        else:
            await ctx.send("No watch tasks found.")

async def setup(bot):
    await bot.add_cog(WatchCommands(bot))

