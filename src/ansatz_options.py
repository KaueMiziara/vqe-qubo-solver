from dataclasses import dataclass


@dataclass
class AnsatzOptions:
    rotation_blocks: str | list[str]
    entanglement_blocks: str | list[str]
    entanglement: str
    reps: int = 0
