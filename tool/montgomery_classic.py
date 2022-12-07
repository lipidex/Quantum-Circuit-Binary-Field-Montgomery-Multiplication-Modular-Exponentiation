def SetBit(n: int, num: int, input_wires: list) -> None:
    bits = bin(num)[2:].zfill(n)
    
    for bit, i in zip(reversed(bits), range(len(input_wires))):
        if bit == "1":
            input_wires[i]["q"] = not input_wires[i]["q"]
    
    return

def OperandMul(n: int, a: bool, B: list, C: list) -> None:
    for i in range(0, n):
        C[i]["q"] = (a["q"] and B[i]["q"]) ^ C[i]["q"]
    
    return

def ModulusMul(n: int, N: list, C: list) -> None:
    for i in reversed(range(0, n)):
        C[i]["q"] = (C[0]["q"] and N[i]["q"]) ^ C[i]["q"]
        
    return

def ModularExponentiations(N_num: int, n: int, A: list, B: list, C: list, N=[]) -> None:
    for i in range(0, n+3):
        # ModulusMul(N, C)
        ModulusMul(n, N[:n], C[:n])
        
        # SwapRotate(C)
        C.append(C.pop(0))
        
        # OperandMul(A[i], B, C)
        OperandMul(n+3, A[i], B, C)
    
    return

def montgomery_expected_result(n_bits: int, N_bin: str, A_bin: str, B_bin: str) -> str:
    N_bits = n_bits
    A_bits = n_bits+3
    B_bits = n_bits+3
    C_bits = n_bits+3

    N = [{'q': False} for _ in range(N_bits)]
    A = [{'q': False} for _ in range(A_bits)]
    B = [{'q': False} for _ in range(B_bits)]
    C = [{'q': False} for _ in range(C_bits)]

    N_num = int(N_bin, 2)
    A_num = int(A_bin, 2)
    B_num = int(B_bin, 2)

    SetBit(len(N), N_num, N)
    SetBit(len(A), A_num, A)
    SetBit(len(B), B_num, B)

    ModularExponentiations(N_num, n_bits, A, B, C, N)

    return "".join(["1" if c["q"] else "0" for c in C])[::-1]