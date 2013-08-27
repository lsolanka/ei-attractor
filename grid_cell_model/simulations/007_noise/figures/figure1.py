#!/usr/bin/env python
#
#   figure1.py
#
#   Noise publication Figure 1.
#
#       Copyright (C) 2013  Lukas Solanka <l.solanka@sms.ed.ac.uk>
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
from matplotlib.pyplot import *
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import AutoMinorLocator, ScalarFormatter

from fig_conn_func        import plotWeights
from data_storage         import DataStorage
from figures_shared       import plotStateSignal, plotThetaSignal, extractStateVars,\
        getOption, thetaLim
from plotting.grids       import plotGridRateMap, plotAutoCorrelation, plotSpikes2D
from plotting.global_defs import globalAxesSettings
from plotting.low_level   import xScaleBar
from analysis.visitors    import AutoCorrelationVisitor
from parameters           import DictDataSet

from matplotlib import rc
rc('pdf', fonttype=42)
rc('mathtext', default='regular')

outputDir = "."

trialNum = 0
jobNum = 573
dataRootDir = 'output_local'
root0   = "{0}/single_neuron".format(dataRootDir)
root150 = "{0}/single_neuron".format(dataRootDir)
root300 = "{0}/single_neuron".format(dataRootDir)
gridRootDir = '{0}/grids'.format(dataRootDir)
fileTemplate = "noise_sigma{0}_output.h5"

##############################################################################

def openJob(rootDir, noise_sigma):
    fileName = rootDir + '/' + fileTemplate.format(noise_sigma)
    return DataStorage.open(fileName, 'r')

def openGridJob(rootDir, noise_sigma, jobNum):
    fileName = rootDir + '/' + \
            'EI_param_sweep_{0}pA/job{1:05}_output.h5'.format(noise_sigma, jobNum)
    return DataStorage.open(fileName, 'a')


def plotHistogram(ax, sig, color='black', labelx="", labely="",
        labelyPos=-0.5, powerLimits=(0, 3)):
    hist(sig, bins=100, normed=True, histtype='step', align='mid', color=color)

    # y label manually
    if (labely is None):
        labely = 'Count'
    ax.text(labelyPos, 0.5, labely,
        verticalalignment='center', horizontalalignment='right',
        transform=ax.transAxes,
        rotation=90)
    xlabel(labelx)
    
    ax.minorticks_on()
    ax.xaxis.set_major_locator(LinearLocator(2))
    ax.yaxis.set_major_locator(LinearLocator(2))
    ax.xaxis.set_minor_locator(AutoMinorLocator(4))
    ax.yaxis.set_minor_locator(AutoMinorLocator(4))
    f = ScalarFormatter(useMathText=True)
    f.set_scientific(True)
    f.set_powerlimits(powerLimits)
    ax.yaxis.set_major_formatter(f)
    ax.tick_params(
            which='both',
            direction='out'
    )
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')


def plotGamma(gs, data, gsRow, gsCol, plotTStart, plotTEnd, yLabelOn=True,
        scaleBar=None):
    if (yLabelOn):
        IsynText = "I (nA)"
    else:
        IsynText = ""

    d = data['trials'][0]
    mon_e = d['stateMon_e']

    # E cell Isyn
    labelYPos = -0.175
    ax0 = subplot(gs[gsRow,gsCol]) 
    t, IsynMiddle = extractStateVars(mon_e, ['I_clamp_GABA_A'],
            plotTStart, plotTEnd)
    plotStateSignal(ax0, t, IsynMiddle*1e-3, labely=IsynText,
            labelyPos=labelYPos, color='red', scaleBar=scaleBar, scaleX=0.85,
            scaleY=-0.15, scaleText=None)

    # Autocorrelation of the 10s signal sample
    acStateList = ['I_clamp_GABA_A']
    acTEnd = 10e3 # ms
    v = AutoCorrelationVisitor('stateMon_e', acStateList, tEnd=acTEnd,
            forceUpdate=False)
    v.visitDictDataSet(DictDataSet(d))
    a = d['analysis']
    acVec = a['acVec'][0, :]
    freq_T = 1. / a['freq'][0] * 1e3
    acVal  = a['acVal'][0]
    dt    = a['ac_dt']
    times = np.arange(len(acVec))*dt
    ax1 = subplot(gs[gsRow + 1,gsCol]) 
    globalAxesSettings(ax1)
    ax1.plot(times, acVec, color='black')
    ax1.set_xlim([0, times[-1]])
    ax1.set_ylim([-1, 1])
    ax1.xaxis.set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.yaxis.set_major_locator(LinearLocator(3))
    ax1.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax1.text(labelYPos, 0.5, 'C',
        verticalalignment='center', horizontalalignment='right',
        transform=ax1.transAxes,
        rotation=90)
    xScaleBar(scaleBar, x=0.75, y=-0.15, ax=ax1, size='small',
            unitsText='ms')

    # Frequency annotation
    ann_x = freq_T
    ann_y = acVal
    ax1.annotate("",
        xy=(ann_x, ann_y ), xycoords='data',
        xytext=(ann_x, ann_y+0.9), textcoords='data',
        arrowprops=dict(arrowstyle="-|>",
                        connectionstyle="arc3"),
        )



def drawSignals(gs, data, colStart, noise_sigma, yLabelOn=True, letter='',
        letterPos=None, scaleBar=None):
    if (yLabelOn):
        VmText = "V (mV)"
        IsynText = "I (nA)"
        countText = None
    else:
        VmText = ""
        IsynText = ""
        countText = ""
    histLabelX = "V (mV)"

    ncols = 4
    plotTStart = 5e3
    plotTEnd   = 5.25e3

    stateYlim = [-80, -40]

    theta_start_t = getOption(data, 'theta_start_t')
    #theta_start_t = 1e3
    simTime = getOption(data, 'time')

    mon_e = data['stateMon_e']
    mon_i = data['stateMon_i']

    ax0 = subplot(gs[0, colStart:colStart+ncols])
    t, IStim_e = extractStateVars(mon_e, ['I_stim'], plotTStart,
            plotTEnd)
    plotThetaSignal(ax0, t, IStim_e, noise_sigma, yLabelOn, thetaLim,
            color='red')
    t, IStim_i = extractStateVars(mon_i, ['I_stim'], plotTStart,
            plotTEnd)
    plotThetaSignal(ax0, t, IStim_i, noise_sigma, yLabelOn, thetaLim,
            color='blue')

    # E cell Vm
    ax1 = subplot(gs[1, colStart:colStart+ncols])
    t, VmMiddle = extractStateVars(mon_e, ['V_m'], plotTStart,
            plotTEnd)
    plotStateSignal(ax1, t, VmMiddle, labely=VmText, color='red')
    ylim(stateYlim)

    # I cell Vm
    ax2 = subplot(gs[2, colStart:colStart+ncols])
    t, VmMiddle = extractStateVars(mon_i, ['V_m'], plotTStart,
            plotTEnd)
    plotStateSignal(ax2, t, VmMiddle, labely=VmText, color='blue',
            scaleBar=scaleBar)
    ylim(stateYlim)

    ## E cell Vm histogram
    #ax3 = subplot(gs[2, colStart:colStart+2])
    #t, VmMiddle = extractStateVars(mon_e, ['V_m'], theta_start_t,
    #        simTime)
    #plotHistogram(ax3, VmMiddle, labelx = histLabelX, labely=countText, color='red')

    ## I cell Vm histogram
    #ax4 = subplot(gs[2, colStart+2:colStart+4])
    #t, VmMiddle = extractStateVars(mon_i, ['V_m'], theta_start_t,
    #        simTime)
    #plotHistogram(ax4, VmMiddle, labelx = histLabelX, labely="", color='blue')


    #if (yLabelOn):
    #    ax1.legend(['E cell', 'I cell'], fontsize='small', frameon=False,
    #            loc=[0.0, 1.1], ncol=2)


def plotGrids(gs, data, gsRow=0, colStart=0):
    a = data['trials'][0]['analysis']
    arenaDiam = data['trials'][0]['options']['arenaSize']
    rateMap = a['rateMap_e']
    _, nCols = gs.get_geometry()
    nColsPerPlot = nCols/3

    # Spikes
    it = 0
    cStart = colStart + it*nColsPerPlot
    cEnd = cStart + nColsPerPlot
    ax0 = subplot(gs[gsRow, cStart:cEnd])
    plotSpikes2D(a['spikes_e'], a['rat_pos_x'], a['rat_pos_y'], a['rat_dt'],
            scaleBar=50, scaleText=False, spikeDotSize=2)

    # Grid field
    it = 1
    cStart = colStart + it*nColsPerPlot
    cEnd = cStart + nColsPerPlot
    ax1 = subplot(gs[gsRow, cStart:cEnd])
    X = a['rateMap_e_X']
    Y = a['rateMap_e_Y']
    plotGridRateMap(rateMap, X, Y, diam=arenaDiam, scaleBar=50, scaleText=False)

    # Grid field autocorrelation
    it = 2
    cStart = colStart + it*nColsPerPlot
    cEnd = cStart + nColsPerPlot
    ax2 = subplot(gs[gsRow, cStart:cEnd])
    X = a['corr_X']
    Y = a['corr_Y']
    ac = a['corr']
    plotAutoCorrelation(ac, X, Y, diam=arenaDiam, scaleBar=50)





figSize = (10, 5.2)
fig = figure(figsize=figSize)

hr = 0.75
vh = 1.  # Vm height
th = 0.75 # top plot height
height_ratios = [th, vh, vh]

top = 0.4
bottom = 0.05
margin = 0.075
div = 0.06
width = 0.26
hspace = 0.3
wspace = 1.2

letter_top=0.95
letter_div = 0.05
letter_left=0.01
letter_va='bottom'
letter_ha='left'

gs_rows = 3
gs_cols = 4

# Model schematic
gs = GridSpec(1, 4)
top_margin = 0.125
top_top = 0.97
top_letter_pos = 1.5
fig.text(letter_left, letter_top, "A", va=letter_va, ha=letter_ha, fontsize=19,
        fontweight='bold')


# noise_sigm = 0 pA
left = margin
right = left + width
ds = openJob(root0, noise_sigma=0)
gs = GridSpec(gs_rows, gs_cols, height_ratios=height_ratios, hspace=hspace,
        wspace=wspace)
# do not update left and right
gs.update(left=left, right=right, bottom=bottom, top=top)
drawSignals(gs, ds, colStart=0, noise_sigma=0)
fig.text(letter_left, top+letter_div, "C", va=letter_va, ha=letter_ha,
        fontsize=19, fontweight='bold')


# noise_sigma = 150 pA
ds = openJob(root150, noise_sigma=150)
gs = GridSpec(gs_rows, gs_cols, height_ratios=height_ratios, hspace=hspace,
        wspace=wspace)
left = right + div
right = left + width
gs.update(left=left, right=right, bottom=bottom, top=top)
drawSignals(gs, ds, colStart=0, yLabelOn=False, noise_sigma=150, letterPos=-0.2)
#fig.text(letter_left+margin+width+0.5*div, top+letter_div, "E", va=letter_va,
#        ha=letter_ha, fontsize=19, fontweight='bold')


# Grid fields and gamma
gs = GridSpec(3, 6, wspace=0, height_ratios=[1, 0.5, 0.5])
g_shift = 0.1*width + div
g_left  = left - g_shift
g_right = g_left + 0.3
gs.update(left=g_left, right=g_right, bottom=top+top_margin, top=top_top,
        hspace=0.35)
grids_ds = openGridJob(gridRootDir, noise_sigma=150, jobNum=340)
plotGrids(gs, grids_ds, colStart=0) 
fig.text(g_left-0.2*div, letter_top, "B", va=letter_va, ha=letter_ha, fontsize=19,
        fontweight='bold')
plotGamma(gs, grids_ds, 1, slice(1, 6), plotTStart=582e3, plotTEnd=582.25e3,
        scaleBar=25)


# noise_sigma = 300 pA
ds = openJob(root300, noise_sigma=300)
gs = GridSpec(gs_rows, gs_cols, height_ratios=height_ratios, hspace=hspace,
        wspace=wspace)
left = right + div
right = left + width
gs.update(left=left, right=right, bottom=bottom, top=top)
drawSignals(gs, ds, colStart=0, yLabelOn=False, noise_sigma=300,
        letterPos=-0.2, scaleBar=50)
#fig.text(letter_left+margin+2*width+1.5*div, top+letter_div, "F", va=letter_va,
#        ha=letter_ha, fontsize=19, fontweight='bold')

fname = outputDir + "/figure1.pdf"
savefig(fname, dpi=300)

