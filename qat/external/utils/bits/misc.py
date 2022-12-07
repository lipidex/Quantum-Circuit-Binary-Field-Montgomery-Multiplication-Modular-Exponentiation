import logging

LOGGER = logging.getLogger(__name__)

def get_required_bits(*bits: int) -> int:
    """Get the maximum number of bits required to represent all the inputs."""
    
    if len(bits) == 0:
        raise ValueError("Number of bitstreams must be greater than 0")
    if any(len(b) == 0 for b in bits):
        raise ValueError("All bitstreams must be greater than zero")
    to_check_bit = max([len(b) for b in bits])

    return to_check_bit