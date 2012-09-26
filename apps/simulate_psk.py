#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Perform the simulation of the transmission of PSK symbols through an
awgn channel.

"""

from simulations import *
from comm import modulators
from util.conversion import dB2Linear
import misc


class VerySimplePskSimulationRunner(SimulationRunner):
    """This is a complete example with the minimum code to actually perform
    a simulation.

    Basically, we implement the _run_simulation method, which here performs
    the simulation of a 4-PSK transmission in an AWGN channel, as well as
    the optional _keep_going method to allow an earlier termination of the
    simulation when a maximum number of bit errors is achieved.

    The simulation parameters can be directly set as regular attributes in
    the __init__ method, since they can be accessed in the _run_simulation
    method this way. The only exception is the SNR parameter, which is
    instead added to a SimulationParameters object (which is a regular
    attribute). The reason for this is because we want pass a vector with
    SNR values and employ the "unpack" functionality of the
    SimulationParameters class.
    """

    def __init__(self, ):
        SimulationRunner.__init__(self)

        #SNR = np.array([5, 10, 15])
        SNR = np.array([0, 3, 6, 9, 12, 15])
        M = 4
        self.modulator = modulators.PSK(M)
        self.NSymbs = 500
        self.max_bit_errors = 200

        self.rep_max = 1000

        #self.progressbar_message = None
        self.progressbar_message = "{0}-PSK".format(M) + \
                                   " Simulation - SNR: {SNR}"

        # Add the parameters to the self.params variable
        self.params.add('SNR', SNR)
        self.params.set_unpack_parameter('SNR')

    def _run_simulation(self, current_parameters):
        """The _run_simulation method is where the actual code to simulate
        the system is.

        The implementation of this method is required by every subclass of
        SimulationRunner.
        """
        # xxxxx Input parameters (set in the constructor) xxxxxxxxxxxxxxxxx
        NSymbs = self.NSymbs
        M = self.modulator.M
        SNR = current_parameters["SNR"]
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

        # xxxxx Input Data xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        inputData = np.random.randint(0, M, NSymbs)
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

        # xxxxx Modulate input data xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        modulatedData = self.modulator.modulate(inputData)
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

        # xxxxx Pass through the channel xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        noiseVar = 1 / dB2Linear(SNR)
        noise = ((np.random.randn(NSymbs) + 1j * np.random.randn(NSymbs)) *
                 np.sqrt(noiseVar / 2))
        receivedData = modulatedData + noise
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

        # xxxxx Demodulate received data xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        demodulatedData = self.modulator.demodulate(receivedData)
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

        # xxxxx Calculates the symbol and bit error rates xxxxxxxxxxxxxxxxx
        symbolErrors = sum(inputData != demodulatedData)
        aux = misc.xor(inputData, demodulatedData)
        # Count the number of bits in aux
        bitErrors = sum(misc.bitCount(aux))
        numSymbols = inputData.size
        numBits = inputData.size * modulators.level2bits(M)
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

        # xxxxx Return the simulation results xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        symbolErrorsResult = Result.create(
            "symbol_errors", Result.SUMTYPE, symbolErrors)

        numSymbolsResult = Result.create(
            "num_symbols", Result.SUMTYPE, numSymbols)

        bitErrorsResult = Result.create("bit_errors", Result.SUMTYPE, bitErrors)

        numBitsResult = Result.create("num_bits", Result.SUMTYPE, numBits)

        berResult = Result.create("ber", Result.RATIOTYPE, bitErrors, numBits)

        serResult = Result.create(
            "ser", Result.RATIOTYPE, symbolErrors, numSymbols)

        simResults = SimulationResults()
        simResults.add_result(symbolErrorsResult)
        simResults.add_result(numSymbolsResult)
        simResults.add_result(bitErrorsResult)
        simResults.add_result(numBitsResult)
        simResults.add_result(berResult)
        simResults.add_result(serResult)
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

        return simResults

    def _keep_going(self, simulation_results):
        """The _keep_going method is not really required, but it can speed
        up the simulation.

        The _keep_going method should return True if more itertions of
        _run_simulation should be run. If we can stop the simulation
        earlier because some condition was achieved, then _keep_going
        should return False to indicate that.
        """
        # Return true as long as cumulated_bit_errors is lower then
        # max_bit_errors
        cumulated_bit_errors = simulation_results['bit_errors'][-1].get_result()
        return cumulated_bit_errors < self.max_bit_errors

    def get_data_to_be_plotted(self):
        """The get_data_to_be_plotted is not part of the simulation, but it
        is useful after the simulation is finished to get the results
        easily for plot.
        """
        def get_result_value(index, param_name):
            return self.results[index][param_name][0].get_result()

        # xxxxx Concatenate the simulation results xxxxxxxxxxxxxxxxxxxxxxxx
        N_SNR_values = len(self.results)
        ber = np.zeros(N_SNR_values)
        ser = np.zeros(N_SNR_values)
        for i in range(0, N_SNR_values):
            ber[i] = get_result_value(i, 'ber')
            ser[i] = get_result_value(i, 'ser')
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

        # Get the SNR from the simulation parameters
        SNR = np.array(self.params['SNR'])

        # Calculates the Theoretical SER and BER
        theoretical_ser = self.modulator.calcTheoreticalSER(SNR)
        theoretical_ber = self.modulator.calcTheoreticalBER(SNR)
        return (SNR, ber, ser, theoretical_ber, theoretical_ser)


if __name__ == '__main__':
    from pylab import *
    sim = VerySimplePskSimulationRunner()
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