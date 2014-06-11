#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Perform the simulation of the transmission of QAM symbols through an
awgn channel.

"""
# xxxxxxxxxx Add the parent folder to the python path. xxxxxxxxxxxxxxxxxxxx
import sys
import os
try:
    parent_dir = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
    sys.path.append(parent_dir)
except NameError:
    sys.path.append('../')
# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

from apps.simulate_psk import VerySimplePskSimulationRunner
from pyphysim.comm import modulators


class VerySimpleQamSimulationRunner(VerySimplePskSimulationRunner):
    """Minimum code to perform a simulation of a QAM transmission through
    an AWGN channel. Only the modulator is changed from the
    VerySimplePskSimulationRunner.

    """

    def __init__(self, ):
        VerySimplePskSimulationRunner.__init__(self)
        M = 16

        SNR = np.array([0, 3, 6, 9, 12, 15, 18])
        self.params.add('SNR', SNR)

        self.modulator = modulators.QAM(M)
        self.progressbar_message = "{0}-QAM".format(M) + \
                                   " Simulation - SNR: {SNR}"

if __name__ == '__main__':
    from pylab import *
    sim = VerySimpleQamSimulationRunner()
    sim.simulate()
    SNR, ber, ser, theoretical_ber, theoretical_ser = sim.get_data_to_be_plotted()

    # Can only plot if we simulated for more then one value of SNR
    if SNR.size > 1:
        semilogy(SNR, ber, '--g*', label='BER')
        semilogy(SNR, ser, '--b*', label='SER')
        semilogy(SNR, theoretical_ber, '-g+', label='Theoretical BER')
        semilogy(SNR, theoretical_ser, '-b+', label='theoretical SER')

        xlabel('SNR')
        ylabel('Error')
        title('BER and SER for {0} modulation in AWGN channel'.format(sim.modulator.name))
        legend()

        grid(True, which='both', axis='both')
        show()

    print sim.elapsed_time
