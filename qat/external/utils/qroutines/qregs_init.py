import nptyping
import functools
import logging
from typing import TYPE_CHECKING, Sequence, Union, List

from qat.lang.AQASM.gates import X
from qat.lang.AQASM.misc import build_gate
from qat.lang.AQASM.routines import QRoutine

if TYPE_CHECKING:
    from qat.lang.AQASM.bits import QRegister

LOGGER = logging.getLogger(__name__)


# In big endian the MSB is on the left, while the LSB is on the right. So in
# big endian |100> would be equal to 4, while in little endian it will be equal
# to 1. Big endian is used by both ibm's qiskit and atos' qlm results. However,
# Atos qlm uses little endian for all other stuffs
def _conditionally_initialize_qureg_given_bitarray(
    a_arr: Sequence[int],
    ncontrols: int,
    little_endian: bool,
) -> QRoutine:
    qr = QRoutine()
    bits = qr.new_wires(len(a_arr))
    cbits = qr.new_wires(ncontrols) if ncontrols > 0 else None

    gate = X
    if ncontrols > 0:
        gate = gate.ctrl(ncontrols)
    part = functools.partial(qr.apply, gate)
    if ncontrols > 0:
        part = functools.partial(part, *cbits)
    mrange = zip(bits, reversed(a_arr)) if little_endian else zip(bits, a_arr)
    for qbit, aint in mrange:
        if aint == 1:
            part(qbit)
        elif aint != 0:
            err_mes = "string %s contains non-binary value %s" % (a_arr, aint)
            raise ValueError(err_mes)
    return qr

def conditionally_initialize_qureg_given_bitstring(a_str, ncontrols,
                                                   little_endian) -> QRoutine:
    a_list = [int(c) for c in a_str]
    return _conditionally_initialize_qureg_given_bitarray(
        a_list, ncontrols, little_endian)


def initialize_qureg_given_bitstring(a_str, little_endian) -> QRoutine:
    """Given a binary string, initialize the qreg to the proper value
    corresponding to it. Basically, if a_str is 1011, the function negate bits
    0, 1 and 3 of the qreg. # 3->0; 2->1; 1->2; 0;3 Note that the qreg has the
    most significant bit in the rightmost part (little endian) of the qreg,
    i.e. the most significant bit is on qreg 0. In the circuit, it means that
    the most significant bits are the lower ones of the qreg

    :param a_str: the binary digits bit string
    :param little_endian: if order of bit is little endian or not

    :return  the QuantumCircuit routine containing the q_reg initialization
    """
    return conditionally_initialize_qureg_given_bitstring(
        a_str, 0, little_endian)