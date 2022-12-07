import itertools
from test.common_circuit import CircuitTestCase
from tool.montgomery_classic import montgomery_expected_result

from parameterized import parameterized
from qat.external.utils.bits import misc
from qat.external.utils.qroutines import montgomery_mul
from qat.external.utils.qroutines import qregs_init as qregs
from qat.lang.AQASM import Program


class MontgomeryTestCase(CircuitTestCase):
    def _prepare_montgomery_circuit(self, bits, fixed=False):
        self.qc = Program()

        N_bits = bits
        A_bits = bits+3
        B_bits = bits+3
        C_bits = bits+3
        anc_bits = bits+3

        if not fixed:
            self.N = self.qc.qalloc(N_bits)
        self.A = self.qc.qalloc(A_bits)
        self.B = self.qc.qalloc(B_bits)
        self.C = list(self.qc.qalloc(C_bits))
        self.anc = self.qc.qalloc(anc_bits)
        
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if cls.logger.level != 0:
            adder.LOGGER.setLevel(cls.logger.level)
            for handler in cls.logger.handlers:
                adder.LOGGER.addHandler(handler)

    @parameterized.expand([
        ('101', '01', '01'),
        ('101', '10', '01'),
        ('111', '11', '10'),
        ('111', '10', '10'),
    ])
    def test_montgomery(self, N_bin, A_bin, B_bin):
        """
        Calculate montgomery multiplication A_bin*B_bin MOD N_bin and check their result.
        The number of bits used to represent the ints is computed at runtime.
        """

        bits = misc.get_required_bits(N_bin, A_bin, B_bin)
        with self.subTest(N_bin=N_bin, A_bin=A_bin, B_bin=B_bin):
            self._prepare_montgomery_circuit(bits)
            self.logger.debug("N %d", len(self.N))
            self.logger.debug("A %d", len(self.A))
            self.logger.debug("B %d", len(self.B))
            self.logger.debug("C %d", len(self.C))
            self.logger.debug("anc %d", len(self.anc))

            qfun = qregs.initialize_qureg_given_bitstring(reversed(N_bin.zfill(len(self.N))), little_endian=False)
            self.qc.apply(qfun, self.N)
            qfun = qregs.initialize_qureg_given_bitstring(reversed(A_bin.zfill(len(self.A))), little_endian=False)
            self.qc.apply(qfun, self.A)
            qfun = qregs.initialize_qureg_given_bitstring(reversed(B_bin.zfill(len(self.B))), little_endian=False)
            self.qc.apply(qfun, self.B)

            to_measure_qbits = []
            qfun = (~montgomery_mul.modular_exponentiations)(bits, to_measure_qbits)
            self.logger.debug("apply montgomery circuit")
            self.qc.apply(qfun, self.N, self.A, self.B, self.C, self.anc)
            
            # self.draw_circuit(self.qc)

            self.logger.debug("C indices % s", [qbit.index for qbit in self.C])
            self.logger.debug("anc indices % s", [qbit.index for qbit in self.anc])
            self.logger.debug("to measure qubits %s", [qbit.index for qbit in to_measure_qbits])

            res_bits = self.qc.calloc(len(to_measure_qbits))
            self.qc.measure(to_measure_qbits, res_bits)

            res = self.qpu.submit(
                self.qc.to_circ().to_job())
            self.logger.debug("res %s", res)

            counts = len(res)
            self.assertEqual(counts, 1)

            self.logger.debug("state res %s", res[0].state)

            expected = montgomery_expected_result(bits, N_bin, A_bin, B_bin)

            self.logger.debug("expected res %s", expected)

            _res_bits = res[0].intermediate_measurements[-1].cbits
            obtained_result = "".join(list(map(lambda x: '1' if x else '0', _res_bits[::-1]))) 
            
            self.logger.debug("obtained res %s", obtained_result)
            self.assertEqual(obtained_result, expected)


    @parameterized.expand([
        ('101', '01', '01'),
        ('101', '10', '01'),
        ('111', '11', '10'),
        ('111', '10', '10'),
    ])
    def test_montgomery_fixed(self, N_bin, A_bin, B_bin):
        """
        Calculate montgomery multiplication A_bin*B_bin MOD N_bin with fixed module and check their result.
        The number of bits used to represent the ints is computed at runtime.
        """

        bits = misc.get_required_bits(N_bin, A_bin, B_bin)
        with self.subTest(N_bin=N_bin, A_bin=A_bin, B_bin=B_bin):
            self._prepare_montgomery_circuit(bits, fixed=True)
            self.logger.debug("A %d", len(self.A))
            self.logger.debug("B %d", len(self.B))
            self.logger.debug("C %d", len(self.C))
            self.logger.debug("anc %d", len(self.anc))

            qfun = qregs.initialize_qureg_given_bitstring(reversed(A_bin.zfill(len(self.A))), little_endian=False)
            self.qc.apply(qfun, self.A)
            qfun = qregs.initialize_qureg_given_bitstring(reversed(B_bin.zfill(len(self.B))), little_endian=False)
            self.qc.apply(qfun, self.B)

            to_measure_qbits = []
            qfun = (~montgomery_mul.fixed_modular_exponentiations)(bits, to_measure_qbits, N_bin)
            self.logger.debug("apply fixed montgomery circuit")
            self.qc.apply(qfun, self.A, self.B, self.C, self.anc)
            
            # self.draw_circuit(self.qc)

            self.logger.debug("C indices % s", [qbit.index for qbit in self.C])
            self.logger.debug("anc indices % s", [qbit.index for qbit in self.anc])
            self.logger.debug("to measure qubits %s", [qbit.index for qbit in to_measure_qbits])

            res_bits = self.qc.calloc(len(to_measure_qbits))
            self.qc.measure(to_measure_qbits, res_bits)

            res = self.qpu.submit(
                self.qc.to_circ().to_job())
            self.logger.debug("res %s", res)

            counts = len(res)
            self.assertEqual(counts, 1)

            self.logger.debug("state res %s", res[0].state)
            
            expected = montgomery_expected_result(bits, N_bin, A_bin, B_bin)

            self.logger.debug("expected res %s", expected)

            _res_bits = res[0].intermediate_measurements[-1].cbits
            obtained_result = "".join(list(map(lambda x: '1' if x else '0', _res_bits[::-1]))) 
            
            self.logger.debug("obtained res %s", obtained_result)
            self.assertEqual(obtained_result, expected)