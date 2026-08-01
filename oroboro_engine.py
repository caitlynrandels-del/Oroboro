"""
Oroboro Engine

Universally applicable recursive loop cleaner and state mutator.

state_stream:
    Raw array of inputs, thoughts, or logic blocks

max_loops:
    Maximum number of nodes processed

Returns:
    Indexed ledger of resolved state nodes
"""

import json


def oroboro_engine(state_stream, max_loops=22):
    ledger = []
    current_state = "INIT_STABLE"

    # Safe slice of stream
    active_stream = state_stream[:max_loops]

    for i, item in enumerate(active_stream):
        raw_thought = str(item)

        # 1. Digest current state and create deterministic signature
        signature = abs(hash_code(raw_thought + current_state)) % len(active_stream)

        # 2. Self-correction / loop validation
        if "doubt" in raw_thought.lower():
            current_state = "RE_EVALUATE_FACT"
        else:
            current_state = f"NODE_{i}_RESOLVED"

        # 3. Record resolved state
        ledger.append({
            "loop": i,
            "state": current_state,
            "signature": signature,
            "payload": raw_thought[:30] + ("..." if len(raw_thought) > 30 else "")
        })

    return ledger


def hash_code(text):
    """JS-compatible style hash function."""
    hash_value = 0
    for char in text:
        hash_value = (hash_value << 5) - hash_value + ord(char)
        # simulate JS 32-bit integer overflow
        hash_value &= 0xFFFFFFFF
        if hash_value & 0x80000000:
            hash_value -= 0x100000000
    return hash_value


# ==========================
# Example Execution
# ==========================

sample_drive_bundle = [
    "Past the fjord, she follow",
    "Loop 2 - Experimental Design",
    "Doubt creeping in about the sequence",
    "Repetition is key, over and over",
    "These thoughts aren't delusions, they're memories"
]

execution_results = oroboro_engine(sample_drive_bundle, 5)

print(json.dumps(execution_results, indent=2))
