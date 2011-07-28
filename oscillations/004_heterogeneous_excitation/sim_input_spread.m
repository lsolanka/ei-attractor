% Network activity dependent on the spread in excitatory current
% Excitatory and inhibitory neurons receive a gaussian-distributed
% excitation current

% Simulate integrate and fire neuron
clear all;
close all;

path('..', path);

% All variables are in basic units, i.e. s, volt, etc.
opt.Ne = 800;
opt.Ni = 200;
N = opt.Ne + opt.Ni;


% Excitatory cells
opt.taum_e = 9.3e-3;
opt.taue = 2e-3;
opt.El_e = -68.5e-3;
opt.Vt_e = -50.0e-3;
opt.Vr_e = -60.0e-3;
opt.e_sparseness = 0.75;
opt.Ie_max = 19.35e-3;
opt.we = 140e-3 / N;


% Inhibitory cell
opt.taum_i = 10e-3;
opt.taui = 5e-3;
opt.El_i = -60e-3;
opt.Vt_i = -50e-3;
opt.Vr_i = -58e-3;
opt.i_sparseness = 0.75;
opt.Ii_max = 8e-3;
opt.wi = 20e-3 / N;



% Current distribution settings
% Diameter of the activated area
opt.D = 100e-6; % micrometers
opt.input_spread = 10*opt.D;


% Noise (mV)
opt.noise_sigma = 0.01e-3;


% Euler settings
opt.dt = 0.5e-3  % 0.5 ms
dt = opt.dt;


% Firing rate sliding window length
opt.rateWindowLen = 0.005; %ms
rateWindowLen = opt.rateWindowLen;

% Vm monitor, neuron index
opt.Emon_i = 100;
opt.Imon_i = 100;

% simulation time
opt.T = 2.5;

opt.input_spread_vec = [0:0.25:5]*opt.D;

% 
% Create simulation results
%
nTrials = 25;
param_i = 1;
for spread = opt.input_spread_vec
    opt.input_spread = spread;
    
    % Now assume neurons are uniformly distributed in the specified area,
    % generate their distances and input current according to the specified
    % spread function
    opt.Ie = gaussianSpread(opt.D*rand(opt.Ne, 1), opt.input_spread, opt.Ie_max);
    opt.Ii = gaussianSpread(opt.D*rand(opt.Ni, 1), opt.input_spread, opt.Ii_max);

    
    parfor trialNum = 1:nTrials
        trialNum
        [spikeRecord_e, spikeRecord_i, Vmon, times] = simulateEI(opt);
        
        tmpresults(trialNum).spikeRecord_e = spikeRecord_e;
        tmpresults(trialNum).spikeRecord_i = spikeRecord_i;
        tmpresults(trialNum).Vmon = Vmon;
        tmpresults(trialNum).times = times;

        
        tmpresults(trialNum).firingRate_e = getFiringRate(spikeRecord_e, dt, rateWindowLen);
        tmpresults(trialNum).spikeCell_e = spikeRecordToSpikeCell(spikeRecord_e, times);
        tmpresults(trialNum).spikeCell_i = spikeRecordToSpikeCell(spikeRecord_i, times);

        tmpresults(trialNum).opt = opt;
    end
    
    results(param_i, :) = tmpresults;
    
    param_i = param_i + 1;
end

clear tmpresults;
save('-v7.3', ['e_gaussian_spread_' date '_001.mat']);
