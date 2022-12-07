# -*- coding: utf-8 -*-

import itertools
import logging
import sys

from qat.lang.AQASM.gates import CCNOT, CNOT, X
from qat.lang.AQASM.routines import QRoutine
from qat.lang.AQASM.misc import build_gate

LOGGER = logging.getLogger(__name__)

def _common_init(n, fixed=False):
    qfun = QRoutine()

    if not fixed:
        N = qfun.new_wires(n)
    A = qfun.new_wires(n+3)
    B = qfun.new_wires(n+3)
    C = qfun.new_wires(n+3)
    anc = qfun.new_wires(n+3)

    if not fixed:
        LOGGER.debug("N %s", [qbit.index for qbit in N])
    LOGGER.debug("A %s", [qbit.index for qbit in A])
    LOGGER.debug("B %s", [qbit.index for qbit in B])
    LOGGER.debug("C %s", [qbit.index for qbit in C])
    LOGGER.debug("anc %s", [qbit.index for qbit in anc])

    if not fixed:
        return qfun, N, A, B, C, anc
    return qfun, A, B, C, anc
    
def OperandMul(n: int) -> QRoutine:
    # a, B, C
    subprog = QRoutine()
    a = subprog.new_wires(1)
    B = subprog.new_wires(n)
    C = subprog.new_wires(n)
    
    for i in range(0, n):
        subprog.apply(CCNOT, a, B[i], C[i])
    
    return subprog

def ModulusMul(n: int) -> QRoutine:
    # N, C
    subprog = QRoutine()
    N = subprog.new_wires(n)
    C = subprog.new_wires(n)
    anc_1 = subprog.new_wires(1)
    
    for i in reversed(range(0, n)):
        subprog.apply(CCNOT, anc_1, N[i], C[i])
    
    return subprog

def FixedModulusMul(N_bin: str, n: int) -> QRoutine:
    # C
    subprog = QRoutine()
    C = subprog.new_wires(n)
    anc_1 = subprog.new_wires(1)
    
    N_bits = N_bin.zfill(n)[::-1]

    for i in reversed(range(0, n)):
        if (i>0 and N_bits[i] == "1") or (i==0 and N_bits[i] == "0"):
            subprog.apply(CNOT, anc_1, C[i])
    
    return subprog

def ModularExponentiations(n: int, to_measure_qbits: list, N_bin=None):
    subprog = QRoutine()

    if not N_bin:
        N = subprog.new_wires(n)
    A = subprog.new_wires(n+3)
    B = subprog.new_wires(n+3)
    C = list(subprog.new_wires(n+3))
    anc = list(subprog.new_wires(n+3))

    # Used to satisfy CCNOT condition (when x_0=1 and N_0=0)
    if not N_bin:
        subprog.apply(X, N[0])
    
    for i in range(0, n+3):
        # Re-label qubit anc with qubit x_0
        C[0], anc[i] = anc[i], C[0]
        
        if N_bin:
            # FixedModulusMul(C)
            subprog.apply(FixedModulusMul(N_bin, n), C[:n], anc[i])
        else:
            # ModulusMul(N, C)
            subprog.apply(ModulusMul(n), N[:n], C[:n], anc[i])
        
        # SwapRotate(C)
        C.append(C.pop(0))
        
        # OperandMul(A[i], B, C)
        subprog.apply(OperandMul(n+3), A[i], B, C)
    
    # Used to restore qubit N_0
    if not N_bin:
        subprog.apply(X, N[0])

    to_measure_qbits += C

    return subprog

@build_gate("MMME", [int, int, int, int, int])
def modular_exponentiations(n: int, to_measure_qbits: list):
    qfun, N, A, B, C, anc = _common_init(n)

    qfun.apply(ModularExponentiations(n, to_measure_qbits), N, A, B, C, anc)

    return qfun

@build_gate("MMMEF", [int, int, int, int, int])
def fixed_modular_exponentiations(n: int, to_measure_qbits: list, N_bin: str):
    qfun, A, B, C, anc = _common_init(n, fixed=True)

    qfun.apply(ModularExponentiations(n, to_measure_qbits, N_bin), A, B, C, anc)

    return qfun