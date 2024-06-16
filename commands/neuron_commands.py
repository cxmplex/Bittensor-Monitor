from discord.ext import commands
from utils.pagination import paginate
from utils.redis_utils import get_all_neuron_info_lites
import aiohttp
import asyncio
from aiohttp.client_exceptions import ClientConnectorError, ClientResponseError

class NeuronCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='test')
    async def test(self, ctx, coldkey: str):
        print(f"retrieving neuron info for coldkey {coldkey}")
        neuron_info_lites = await get_all_neuron_info_lites([coldkey])

        if neuron_info_lites:
            neuron_info_lites_sorted = sorted(neuron_info_lites, key=lambda x: x.netuid)
            response_parts = []
            current_uid = None
            current_message = ""

            async with aiohttp.ClientSession() as session:
                for neuron in neuron_info_lites_sorted:
                    if neuron.netuid != current_uid:
                        if current_uid is not None:
                            response_parts.append(current_message)
                            current_message = ""
                        current_uid = neuron.netuid
                        current_message += f'Subnet {current_uid}:\n'

                    addr = neuron.axon_info.addr
                    if "0.0.0.0" in addr:
                        status = "N/A"
                    else:
                        try:
                            async with session.get(f'http://{addr}', timeout=10) as response:
                                status = "✅" if response.status else "❌"
                        except asyncio.TimeoutError:
                            status = "❌"
                        except ClientConnectorError:
                            status = "❌"
                        except ClientResponseError:
                            status = "✅"

                    current_message += f'{neuron.hotkey}:{addr} - {status}\n'

                    if len(current_message) > 1800:  # Check if the response is getting too long
                        response_parts.append(current_message)
                        current_message = f'Subnet {current_uid} (continued):\n'

                if current_message:
                    response_parts.append(current_message)

            await paginate(ctx, response_parts)
        else:
            await ctx.send(f'{ctx.author.mention}, no neurons found for coldkey {coldkey}.')

async def setup(bot):
    print("setup called for neuron_commands")
    await bot.add_cog(NeuronCommands(bot))

