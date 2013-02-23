#
#   simulation_basic_grids.py
#
#   Main simulation run: grid fields with theta input and all the inhibition
#   (for gamma) and place input.
#
#       Copyright (C) 2012  Lukas Solanka <l.solanka@sms.ed.ac.uk>
#       
#       This program is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from scipy.io   import loadmat
from scipy.io   import savemat
from optparse   import OptionParser

from parameters              import *
from grid_cell_network_nest  import *
from spike_analysis          import *

import time
import numpy as np
import nest
import nest.raster_plot

mV = 1e-3


lg.basicConfig(level=lg.DEBUG)

parser          = getOptParser()
parser.add_option("--ndumps",  type="int",    help="Number of data output dumps during the simulation")

(options, args) = parser.parse_args()
options         = setOptionDictionary(parser, options)

# Other
figSize = (12,8)


################################################################################
#                              Network setup
################################################################################
print "Starting network and connections initialization..."
start_time=time.time()
total_start_t = time.time()

ei_net = NestGridCellNetwork(options, simulationOpts=None)

const_v = [50.0, 0.0]
ei_net.setConstantVelocityCurrent_e(const_v)
#ei_net.setVelocityCurrentInput_e()

#ei_net.uniformInhibition()
#ei_net.setStartCurrent()
#ei_net.setPlaceCells()


duration=time.time()-start_time
print "Network setup time:",duration,"seconds"
#                            End Network setup
################################################################################

rec_all_spikes = True
if rec_all_spikes:
    nrecSpike_e = ei_net.Ne_x*ei_net.Ne_y
    nrecSpike_i = ei_net.Ni_x*ei_net.Ni_y
else:
    nrecSpike_e = 200
    nrecSpike_i = 50

state_record_e = [ei_net.Ne_x/2 -1 , ei_net.Ne_y/2*ei_net.Ne_x + ei_net.Ne_x/2 - 1]
state_record_i = [ei_net.Ni_x/2 - 1, ei_net.Ni_y/2*ei_net.Ni_x + ei_net.Ni_x/2 - 1]

spikeMon_e = ei_net.getSpikeDetector("E")
spikeMon_i = ei_net.getSpikeDetector("I")
pc_spikemon = ei_net.getGenericSpikeDetector(ei_net.PC, "Place cells")

stateMon_params = {
        'withtime' : True,
        'interval' : 0.1,
        'record_from' : ['V_m', 'I_clamp_AMPA', 'I_clamp_NMDA',
            'I_clamp_GABA_A', 'I_stim']
}
stateMon_e = ei_net.getStateMonitor("E", state_record_e, stateMon_params)
stateMon_i = ei_net.getStateMonitor("I", state_record_i, stateMon_params)



#x_lim = [options.time-0.5, options.time]
x_lim = [0, options.time]



################################################################################
#                              Main cycle
################################################################################
print "Simulation running..."
start_time=time.time()
    
ei_net.simulate(options.time, printTime=True)
duration=time.time()-start_time
print "Simulation time:",duration,"seconds"

output_fname = "{0}/{1}job{2:05}_".format(options.output_dir, options.fileNamePrefix, options.job_num)


F_tstart = 0.0
F_tend = options.time
F_dt = 20.0
F_winLen = 500.0
senders = nest.GetStatus(spikeMon_e)[0]['events']['senders'] - ei_net.E_pop[0]
spikeTimes   = nest.GetStatus(spikeMon_e)[0]['events']['times']
Fe, Fe_t = slidingFiringRateTuple((senders, spikeTimes), ei_net.net_Ne,
        F_tstart, F_tend, F_dt, F_winLen)

senders = nest.GetStatus(spikeMon_i)[0]['events']['senders'] - ei_net.I_pop[0]
spikeTimes   = nest.GetStatus(spikeMon_i)[0]['events']['times']
Fi, Fi_t = slidingFiringRateTuple((senders, spikeTimes), ei_net.net_Ni,
        F_tstart, F_tend, F_dt, F_winLen)


# Print a plot of bump position
(pos, bumpPos_times) = torusPopulationVectorFromRates((Fe, Fe_t), [ei_net.Ne_y,
    ei_net.Ne_x])
figure(figsize=figSize)
plot(bumpPos_times, pos)
xlabel('Time (s)')
ylabel('Bump position (neurons)')
ylim([-ei_net.Ne_x/2 -5, ei_net.Ne_y/2 + 5])


# Raster plot
nest.raster_plot.from_device(spikeMon_e, hist=False)
nest.raster_plot.from_device(spikeMon_i, hist=False)
if (len(ei_net.PC) != 0):
    nest.raster_plot.from_device(pc_spikemon, hist=False)
    title('Place cells')

events_e = nest.GetStatus(stateMon_e)[0]['events']
events_i = nest.GetStatus(stateMon_i)[0]['events']


figure()
T, N_id = np.meshgrid(Fe_t, np.arange(ei_net.net_Ne))
pcolormesh(T, N_id,  Fe)
xlabel("Time (s)")
ylabel("Neuron #")
axis('tight')

figure()
pcolormesh(Fi)


# External currents
figure()
ax = subplot(211)
plot(events_e['times'], events_e['I_stim'])
ylabel('E cell $I_{stim}$')
axis('tight')
subplot(212)
plot(events_i['times'], events_i['I_stim'])
ylabel('I cell $I_{stim}$')
xlabel('Time (ms)')


# Histogram of E external current (to validate noise)
figure()
hist(events_e['I_stim'], 100)
xlabel('Current (pA)')
ylabel('Count')



# E/I Vm
figure()
ax = subplot(211)
plot(events_e['times'], events_e['V_m'])
ylabel('E cell $V_m$')
subplot(212)
plot(events_i['times'], events_i['V_m'])
ylabel('I cell $V_m$')
xlabel('Time (ms)')



figure()
ax = subplot(211)
plot(events_e['times'], events_e['I_clamp_GABA_A'])
ylabel('E synaptic current (pA)')
subplot(212, sharex=ax)
plot(events_i['times'], events_i['I_clamp_AMPA'] + events_i['I_clamp_NMDA'])
xlabel('Time (s)')
ylabel('I synaptic current (pA)')
xlim(x_lim)
savefig(output_fname + '_Isyn.pdf')


# Firing rate of E cells on the twisted torus
figure()
pcolormesh(np.reshape(Fe[:, len(Fe_t)/2], (ei_net.Ne_y, ei_net.Ne_x)))
xlabel('E neuron no.')
ylabel('E neuron no.')
colorbar()
axis('equal')
title('Firing rates (torus) of E cells')
savefig(output_fname + '_firing_snapshot_e.png')


## Firing rate of I cells on the twisted torus
figure()
pcolormesh(np.reshape(Fi[:, len(Fi_t)/2], (ei_net.Ni_y, ei_net.Ni_x)))
xlabel('I neuron no.')
ylabel('I neuron no.')
colorbar()
axis('equal')
title('Firing rates (torus) of I cells')
savefig(output_fname + '_firing_snapshot_i.png')


show()

        
#                            End main cycle
################################################################################

total_time = time.time()-total_start_t
print "Overall time: ", total_time, " seconds"

