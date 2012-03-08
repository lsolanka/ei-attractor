from scipy.io import loadmat
from matplotlib.pyplot import *
from mpl_toolkits.mplot3d import Axes3D

import numpy as np

from data_analysis import bumpVariancePos

# Generate bump stability figures based on simulated stationary attractor
# network

pA = 1e-12
nS = 1e-9


jobRange = [200, 219]
trialRange = [0, 19]
jobN = jobRange[1] - jobRange[0] + 1
trialN = trialRange[1] - trialRange[0] + 1

t_start = 3

dirName = "output/job0200"
fileNamePrefix = ''
fileNameTemp = "{0}/{1}job{2:04}_trial{3:04}"

hist_nbins= 50

res = bumpVariancePos(dirName, fileNamePrefix, jobRange, trialRange, t_start)

Iext_N = 2
g_total_N = 10
Iext_e = np.ndarray(jobN)
g_total = np.ndarray(jobN)


for job_it in range(jobN):
    jobNum = job_it + jobRange[0]

    Iext_e[job_it] = res.o_vec[job_it, 0]['Iext_e'][0][0][0][0]
    g_total[job_it] = res.o_vec[job_it, 0]['g_AMPA_total'][0][0][0][0] + \
        res.o_vec[job_it, 0]['g_GABA_total'][0][0][0][0]
    for trial_it in range(trialN):
        if res.pos_x_vec[job_it, trial_it] is None:
            continue
        trialNum = trialRange[0] + trial_it
        fileName = fileNameTemp.format(dirName, fileNamePrefix, jobNum,
                                    trialNum)
        pos_x = res.pos_x_vec[job_it, trial_it]
        pos_y = res.pos_y_vec[job_it, trial_it]
        Ne = res.o_vec[job_it, trial_it]['Ne'][0][0][0][0]

        #figure
        #subplot(121)
        #hist(pos_x/Ne, hist_nbins, range=[-0.5, 0.5], normed=False)
        #xlabel('Position x (normalised)')
        #ylabel('Frequency')
        #subplot(122)
        #hist(pos_y/Ne, hist_nbins, range=[-0.5, 0.5], normed=False)
        #xlabel('Position y (normalised)')
        #savefig(fileName + '_bump_position_hist.pdf')
        #close(gcf())

Iext_e = np.reshape(Iext_e, (Iext_N, g_total_N))
g_total = np.reshape(g_total, (Iext_N, g_total_N))
ax = figure().gca(projection='3d')
ax.plot_surface(Iext_e/pA, g_total/nS, np.reshape(res.pos_var_mean[:, 0], (Iext_N,
    g_total_N)), rstride=1, cstride=1, cmap=cm.jet)

show()
