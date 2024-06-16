import aioredis
import json
from typing import List
from models.neuron_info import NeuronInfoLite, AxonInfo
import asyncio
import time
from config import REDIS_URL
import bittensor

subtensor = bittensor.subtensor(network='finney')
redis = aioredis.from_url(REDIS_URL)

async def store_neurons_for_netuid(netuids: List[int]):
    start = time.time()
    coldkey_neurons = {}

    for netuid in netuids:
        if netuid not in [17, 23, 26, 27, 30]:
            continue
        print(f"querying {netuid}")
        neurons = await asyncio.to_thread(subtensor.neurons_lite, netuid=netuid)
        for neuron in neurons:
            neuron_info = NeuronInfoLite(
                hotkey=neuron.hotkey,
                coldkey=neuron.coldkey,
                uid=neuron.uid,
                netuid=neuron.netuid,
                active=neuron.active,
                stake=float(neuron.stake.tao),
                total_stake=float(neuron.total_stake.tao),
                rank=float(neuron.rank),
                emission=float(neuron.emission),
                incentive=float(neuron.incentive),
                consensus=float(neuron.consensus),
                trust=float(neuron.trust),
                last_update=neuron.last_update,
                validator_permit=neuron.validator_permit,
                axon_info=AxonInfo(
                    addr=f"{neuron.axon_info.ip}:{neuron.axon_info.port}",
                    hotkey=neuron.axon_info.hotkey,
                    coldkey=neuron.axon_info.coldkey,
                ),
            )

            if neuron.coldkey not in coldkey_neurons:
                coldkey_neurons[neuron.coldkey] = []
            coldkey_neurons[neuron.coldkey].append(neuron_info.dict())

    for coldkey, neuron_info_list in coldkey_neurons.items():
        await redis.set(coldkey, json.dumps(neuron_info_list), ex=1200)
     
    print(f"{netuid} finished in {(time.time() - start)} seconds")

async def store_neurons_lite(netuids: List[int]):
    await store_neurons_for_netuid(netuids)

async def get_neuron_info_lites(input_ss58: str) -> List[NeuronInfoLite]:
    neuron_info_list_json = await redis.get(input_ss58)
    if neuron_info_list_json:
        neuron_info_list = json.loads(neuron_info_list_json)
        return [NeuronInfoLite(**neuron_info) for neuron_info in neuron_info_list]
    return []

async def get_all_neuron_info_lites(input_ss58_list: List[str]) -> List[NeuronInfoLite]:
    tasks = [get_neuron_info_lites(input_ss58) for input_ss58 in input_ss58_list]
    results = await asyncio.gather(*tasks)
    return [neuron for sublist in results for neuron in sublist]

async def get_watch_tasks() -> List[dict]:
    watch_tasks_json = await redis.get("watch_tasks")
    if watch_tasks_json:
        return json.loads(watch_tasks_json)
    return []

async def update_watch_tasks(discord_user_id: str, coldkey: str):
    watching_key = f"{discord_user_id}_watching"
    watching_list_json = await redis.get(watching_key)
    if watching_list_json:
        watching_list = json.loads(watching_list_json)
    else:
        watching_list = []

    if coldkey not in watching_list:
        watching_list.append(coldkey)
        await redis.set(watching_key, json.dumps(watching_list), ex=86400)

    watch_tasks_json = await redis.get("watch_tasks")
    if watch_tasks_json:
        watch_tasks = json.loads(watch_tasks_json)
    else:
        watch_tasks = []

    user_found = False
    for task in watch_tasks:
        if task["discord_user_id"] == discord_user_id:
            task["coldkeys"].append(coldkey)
            user_found = True
            break

    if not user_found:
        watch_tasks.append({"discord_user_id": discord_user_id, "coldkeys": [coldkey]})

    await redis.set("watch_tasks", json.dumps(watch_tasks), ex=86400)

async def remove_watch_task(discord_user_id: str, coldkey: str):
    watching_key = f"{discord_user_id}_watching"
    watching_list_json = await redis.get(watching_key)
    if watching_list_json:
        watching_list = json.loads(watching_list_json)
    else:
        watching_list = []

    if coldkey in watching_list:
        watching_list.remove(coldkey)
        await redis.set(watching_key, json.dumps(watching_list), ex=86400)

    watch_tasks_json = await redis.get("watch_tasks")
    if watch_tasks_json:
        watch_tasks = json.loads(watch_tasks_json)
    else:
        watch_tasks = []

    for task in watch_tasks:
        if task["discord_user_id"] == discord_user_id:
            task["coldkeys"].remove(coldkey)
            if not task["coldkeys"]:
                watch_tasks.remove(task)
            break

    await redis.set("watch_tasks", json.dumps(watch_tasks), ex=86400)
