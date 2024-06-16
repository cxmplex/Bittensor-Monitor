from pydantic import BaseModel

class AxonInfo(BaseModel):
    addr: str
    hotkey: str
    coldkey: str

class NeuronInfoLite(BaseModel):
    hotkey: str
    coldkey: str
    uid: int
    netuid: int
    active: bool
    stake: float
    total_stake: float
    rank: float
    emission: float
    incentive: float
    consensus: float
    trust: float
    last_update: int
    validator_permit: bool
    axon_info: AxonInfo

