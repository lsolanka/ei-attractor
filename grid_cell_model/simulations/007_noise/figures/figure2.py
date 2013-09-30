#!/usr/bin/env python
#
#   figure2.py
#
#   Noise publication Figure 2.
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
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot   import figure, subplot, plot, savefig, close, \
        errorbar
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MultipleLocator, AutoMinorLocator, LinearLocator, MaxNLocator, \
        ScalarFormatter
from matplotlib.colorbar import make_axes
from matplotlib.transforms import Bbox

from parameters  import JobTrialSpace2D
import EI_plotting as EI
from EI_plotting import plotBumpSigmaTrial, computeYX, aggregate2DTrial, \
        aggregate2D, drawEIRectSelection, drawBumpExamples, plotVelTrial
from plotting.grids import plotGridRateMap, plotAutoCorrelation, plotSpikes2D
from plotting.global_defs import globalAxesSettings
from figures_shared import plotOneHist, getNoiseRoots, createColorbar

import logging as lg
#lg.basicConfig(level=lg.WARN)
lg.basicConfig(level=lg.INFO)

from matplotlib import rc
rc('pdf', fonttype=42)
rc('mathtext', default='regular')

plt.rcParams['font.size'] = 10

outputDir = "."

NTrials=10
iterList  = ['g_AMPA_total', 'g_GABA_total']

noise_sigmas = [0, 150, 300]
exampleIdx   = [(0, 0), (0, 0), (0, 0)] # (row, col)
gridsDataRoot= 'output_local/even_spacing/grids'
bumpDataRoot= 'output_local/even_spacing/gamma_bump'
velDataRoot = 'output_local/even_spacing/velocity'
bumpShape = (31, 31)
velShape  = (31, 31)
gridShape  = (31, 31)

bumpExamples      = 0
bumpSweep0        = 0
bumpSweep150      = 0
bumpSweep300      = 0
velExamples       = 0
velSweep0         = 0
velSweep150       = 0
velSweep300       = 0
hists             = 0
velLines          = 0
gridness_vs_error = 1

##############################################################################


def drawBumpSweeps(ax, dataSpace, iterList, noise_sigma, NTrials=1, r=0, c=0, yLabelOn=True,
        yticks=True, cbar=False):
    xLabelText = '$g_I$ (nS)'
    if (yLabelOn):
        yLabelText = '$g_E$ (nS)'
    else:
        yLabelText = ''

    if (ax is None):
        ax = plt.gca()

    varList = ['bump_e', 'sigma']
    G = plotBumpSigmaTrial(dataSpace, varList, iterList,
            trialNumList=range(NTrials),
            xlabel=xLabelText,
            ylabel=yLabelText,
            colorBar=False,
            yticks=yticks,
            vmin=0,
            vmax=10)
    plt.set_cmap('jet_r')
    cax, kw = make_axes(ax, orientation='vertical', shrink=0.8,
            pad=0.05)
    globalAxesSettings(cax)
    cb = plt.colorbar(ax=ax, cax=cax, ticks=MultipleLocator(5), **kw)
    cb.set_label('Bump $\sigma$ (neurons)')
    if (cbar == False):
        cax.set_visible(False)
    ax.set_title('$\sigma$ = {0} pA'.format(int(noise_sigma)))
    cax.yaxis.set_minor_locator(AutoMinorLocator(2))

    return ax, cax


def plotBumpExample(exLeft, exBottom, w, h, fileName, exIdx, sweep_ax,
        sweepDataSpace, iterList, exGsCoords, **kw):
    #keyword
    wspace = kw.pop('wspace', 0)
    hspace = kw.pop('hspace', 0)
    figSize = kw.pop('figSize', (1.8, 1))
    rectColor = kw.pop('rectColor', 'black')

    # Create the example plot
    fig = plt.figure(figsize=figSize)

    exRect = [exLeft, exBottom, exLeft+w-1, exBottom+h-1]
    gs = drawBumpExamples(sweepDataSpace, exRect, iterList,
            gsCoords=exGsCoords, xlabel=False, ylabel=False, xlabel2=False,
            ylabel2=False, fontsize='xx-small', rateYPos=1.05, rateXPos=0.98,
            **kw)
    gs.update(wspace=wspace, hspace=hspace)
    plt.savefig(fileName, dpi=300, transparent=False)
    plt.close()

    # Draw the selection into the EI plot
    if (sweep_ax is not None):
        exRow, exCol = exIdx
        Y, X = computeYX(sweepDataSpace, iterList, r=exRow, c=exCol)
        drawEIRectSelection(sweep_ax, exRect, X, Y, color=rectColor)


def drawVelSweep(ax, dataSpace, iterList, varList, noise_sigma, **kwargs):
    # process kwargs
    sigmaTitle    = kwargs.pop('sigmaTitle', True)
    xlabelOn      = kwargs.pop('xlabelOn', True)
    ylabelOn      = kwargs.pop('ylabelOn', True)
    cmap          = kwargs.pop('cmap', None)
    cbar          = kwargs.pop('cbar', True)
    cbar_kwargs                = kwargs.pop('cbar_kwargs', {})
    cbar_kwargs['label']       = cbar_kwargs.get('label', '')
    cbar_kwargs['shrink']      = cbar_kwargs.get('shrink', 0.8)
    cbar_kwargs['orientation'] = cbar_kwargs.get('orientation', 'vertical')
    cbar_kwargs['pad']         = cbar_kwargs.get('pad', 0.05)
    cbar_kwargs['ticks']       = cbar_kwargs.get('ticks', MultipleLocator(5))

    if (ax is None):
        ax = plt.gca()

    val = plotVelTrial(dataSpace, varList, iterList, **kwargs)
    plt.set_cmap(cmap)
    cax = createColorbar(ax, **cbar_kwargs)
    
    print("drawVelSweep: max(val): {0}".format(np.max(val.ravel())))

    if (cbar == False):
        cax.set_visible(False)
    if (sigmaTitle):
        ax.set_title('$\sigma$ = {0} pA'.format(int(noise_sigma)))

    return ax, cax



def plotVelHistogram(spList, varList, xlabel="", ylabel="", **kw):
    noise_sigma = [0, 150, 300]
    colors = ['red', 'green', 'blue']
    range = kw.get('range')
    plotLegend = kw.pop('plotLegend', False)

    ax = plt.gca()
    plt.hold('on')
    globalAxesSettings(ax)

    for idx, sp in enumerate(spList):
        var = np.abs(aggregate2D(sp, varList, funReduce=None))
        filtIdx = np.logical_not(np.isnan(var))
        if (range is not None):
            var[var < range[0]] = range[0]
            var[var > range[1]] = range[1]
        plotOneHist(var[filtIdx], normed=True, **kw)

    if (plotLegend):
        leg = []
        for s in noise_sigma:
            leg.append("{0}".format(int(s)))
        l = ax.legend(leg, loc=(0.75, 0.5), title='$\sigma$ (pA)',
                frameon=False, fontsize='x-small', ncol=1)
        plt.setp(l.get_title(), fontsize='x-small')

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    f = ScalarFormatter(useMathText=True)
    f.set_scientific(True)
    f.set_powerlimits([0, 3])
    ax.yaxis.set_major_formatter(f)
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    return ax

def plotErrHistogram(spList, varList, **kw):
    ax = plotVelHistogram(spList, varList, range=[0, 10], **kw)

    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.yaxis.set_major_locator(MaxNLocator(4))
    ax.set_ylim([-0.0025, 2])
    #ax.margins(0.01)
    
def plotSlopeHistogram(spList, varList, **kw):
    ax = plotVelHistogram(spList, varList, range=[0, 1.5], **kw)

    ax.xaxis.set_major_locator(MultipleLocator(0.4))
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.yaxis.set_major_locator(MaxNLocator(4))
    ax.set_ylim([-0.0025, 9])
    #ax.margins(0.01)
    

def plotSlopes(ax, dataSpace, pos, **kw):
    # kwargs
    trialNum = kw.pop('trialNum', 0)
    markersize = kw.pop('markersize', 4)
    color = kw.pop('color', 'blue')

    r = pos[0]
    c = pos[1]
    d = dataSpace[r][c].getAllTrialsAsDataSet().data
    a = d['analysis']
    IvelVec = dataSpace[r][c][trialNum].data['IvelVec']
    slopes = a['bumpVelAll']
    lineFit = a['lineFitLine']
    fitIvelVec = a['fitIvelVec']

    nTrials = slopes.shape[0]
    avgSlope = np.mean(slopes, axis=0)
    stdErrSlope = np.std(slopes, axis=0) / np.sqrt(nTrials)

    if (ax is None):
        ax = plt.gca()
    plt.hold('on')
    globalAxesSettings(ax)

    errorbar(IvelVec, avgSlope, stdErrSlope, fmt='o-', markersize=markersize,
            color=color, alpha=0.5, **kw)
    plot(fitIvelVec, lineFit, '-', linewidth=2, color=color, **kw)

def plotAllSlopes(ax, spList, positions, **kw):
    colors = kw.pop('colors', ('blue', 'green', 'red'))

    for idx, dataSpace in enumerate(spList):
        kw['color'] = colors[idx]
        plotSlopes(ax, dataSpace, positions[idx], **kw)

    ax.set_xlabel('Velocity current (pA)')
    ax.set_ylabel('$v_{bump}$ (neurons/s)')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_major_locator(MultipleLocator(50))
    ax.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(20))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.margins(0.05)
    

def plotGridnessVsFitErr(spListGrids, spListVelocity, trialNumList,
        ylabelPos=-0.2, maxErr=None):
    GVars = ['gridnessScore']
    errVars = ['lineFitErr']
    slopeVars = ['lineFitSlope']
    noise_sigma = [0, 150, 300]
    markers = ['o', '^', '*']
    colors = ['blue', 'green', 'red']
    errMins = []
    errMaxs = []

    ax = plt.gca()
    plt.hold('on')
    globalAxesSettings(ax)
    ax.set_yscale('log')

    for idx, (spGrids, spVel) in enumerate(zip(spListGrids, spListVelocity)):
        G = aggregate2DTrial(spGrids, GVars, trialNumList).flatten()
        errs = aggregate2D(spVel, errVars, funReduce=np.sum).flatten()
        #slopes = np.abs(aggregate2D(spVel, slopeVars,
        #    funReduce=None).flatten())
        i = np.logical_not(np.logical_and(np.isnan(G), np.isnan(errs)))
        ax.scatter(G[i], errs[i],  s=5, marker=markers[idx], 
                color=colors[idx], edgecolors='None')
        errMins.append(np.min(errs[i]))
        errMaxs.append(np.max(errs[i]))

    if (maxErr is not None):
        ax.set_ylim([0, maxErr])
    else:
        ax.set_ylim([0, None])

    leg = []
    for s in noise_sigma:
        leg.append("{0}".format(int(s)))
    l = ax.legend(leg, loc=(0.3, 0.85), title='$\sigma$ (pA)', frameon=False,
            fontsize='small', ncol=3, columnspacing=1.5)
    plt.setp(l.get_title(), fontsize='small')

    ax.set_xlabel("Gridness score")
    ax.set_ylabel('Error (nrns/s/data point)')
    #ax.text(ylabelPos, 0.5, 'Error (nrns/s/data point)', rotation=90, transform=ax.transAxes,
    #        va='center', ha='right')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_major_locator(MultipleLocator(0.5))
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.set_xmargin(0.05)
    ax.autoscale_view(tight=True)
    ax.set_ylim(np.min(errMins), np.max(errMaxs)*1.5)


###############################################################################
bumpRoots = getNoiseRoots(bumpDataRoot, noise_sigmas)
bumpDataSpace0   = JobTrialSpace2D(bumpShape, bumpRoots[0])
bumpDataSpace150 = JobTrialSpace2D(bumpShape, bumpRoots[1])
bumpDataSpace300 = JobTrialSpace2D(bumpShape, bumpRoots[2])

velRoots = getNoiseRoots(velDataRoot, noise_sigmas)
velDataSpace0   = JobTrialSpace2D(velShape, velRoots[0])
velDataSpace150 = JobTrialSpace2D(velShape, velRoots[1])
velDataSpace300 = JobTrialSpace2D(velShape, velRoots[2])

gridRoots = getNoiseRoots(gridsDataRoot, noise_sigmas)
gridDataSpace0   = JobTrialSpace2D(gridShape, gridRoots[0])
gridDataSpace150 = JobTrialSpace2D(gridShape, gridRoots[1])
gridDataSpace300 = JobTrialSpace2D(gridShape, gridRoots[2])


exW = 4
exH = 2
exMargin = 0.075
exGsCoords = 0.02, 0, 0.98, 1.0-exMargin
exWspace=0.2
exHspace=0.15

sweepFigSize = (2.5, 2.1)
sweepLeft   = 0.15
sweepBottom = 0.2
sweepRight  = 0.87
sweepTop    = 0.85

histFigsize =(2.6, 1.7)
histLeft    = 0.22
histBottom  = 0.3
histRight   = 0.95
histTop     = 0.86

if (bumpSweep0):
    # noise_sigma = 0 pA
    fig = figure("sweeps0", figsize=sweepFigSize)
    exRows = [28, 15]
    exCols = [3, 15]
    ax = fig.add_axes(Bbox.from_extents(sweepLeft, sweepBottom, sweepRight,
        sweepTop))
    ax, cax = drawBumpSweeps(ax, bumpDataSpace0, iterList,
            noise_sigma=noise_sigmas[0], NTrials=NTrials, cbar=False)
    if (bumpExamples):
        exLeft = 1
        exBottom = 24
        fname = outputDir + "/figure2_examples_0pA_0.png"
        plotBumpExample(exLeft, exBottom, exW, exH, fname, exampleIdx[0],
                ax, bumpDataSpace0, iterList, exGsCoords, wspace=exWspace,
                hspace=exHspace, rectColor='red')

        exLeft = 25
        exBottom = 15
        fname = outputDir + "/figure2_examples_0pA_1.png"
        plotBumpExample(exLeft, exBottom, exW, exH, fname, exampleIdx[0],
                ax, bumpDataSpace0, iterList, exGsCoords, wspace=exWspace,
                hspace=exHspace, rectColor='red')

    fname = outputDir + "/figure2_sweeps0.png"
    fig.savefig(fname, dpi=300, transparent=True)



if (bumpSweep150):
    # noise_sigma = 150 pA
    fig = figure("sweeps150", figsize=sweepFigSize)
    exRows = [8, 2]
    exCols = [10, 9]
    ax = fig.add_axes(Bbox.from_extents(sweepLeft, sweepBottom, sweepRight,
        sweepTop))
    ax, cax = drawBumpSweeps(ax, bumpDataSpace150, iterList,
            noise_sigma=noise_sigmas[1],  NTrials=NTrials, yLabelOn=False,
            yticks=False) 
    if (bumpExamples):
        exLeft = 1
        exBottom = 24
        fname = outputDir + "/figure2_examples_150pA_0.png"
        plotBumpExample(exLeft, exBottom, exW, exH, fname, exampleIdx[1],
                ax, bumpDataSpace150, iterList, exGsCoords, wspace=exWspace,
                hspace=exHspace, rectColor='red')

        exLeft = 25
        exBottom = 15
        fname = outputDir + "/figure2_examples_150pA_1.png"
        plotBumpExample(exLeft, exBottom, exW, exH, fname, exampleIdx[1],
                ax, bumpDataSpace150, iterList, exGsCoords, wspace=exWspace,
                hspace=exHspace, rectColor='black')


    fname = outputDir + "/figure2_sweeps150.png"
    fig.savefig(fname, dpi=300, transparent=True)



if (bumpSweep300):
    # noise_sigma = 300 pA
    fig = figure("sweeps300", figsize=sweepFigSize)
    exRows = [16, 15]
    exCols = [6, 23]
    ax = fig.add_axes(Bbox.from_extents(sweepLeft, sweepBottom, sweepRight,
        sweepTop))
    ax.set_clip_on(False)
    _, cax = drawBumpSweeps(ax, bumpDataSpace300, iterList,
            noise_sigma=noise_sigmas[2],  NTrials=NTrials, yLabelOn=False,
            yticks=False, cbar=True)
    if (bumpExamples):
        exLeft = 1
        exBottom = 24
        fname = outputDir + "/figure2_examples_300pA_0.png"
        plotBumpExample(exLeft, exBottom, exW, exH, fname, exampleIdx[2],
                ax, bumpDataSpace300, iterList, exGsCoords, wspace=exWspace,
                hspace=exHspace, rectColor='red')

        exLeft = 25
        exBottom = 15
        fname = outputDir + "/figure2_examples_300pA_1.png"
        plotBumpExample(exLeft, exBottom, exW, exH, fname, exampleIdx[2],
                ax, bumpDataSpace300, iterList, exGsCoords, wspace=exWspace,
                hspace=exHspace, rectColor='black')


    fname = outputDir + "/figure2_sweeps300.png"
    fig.savefig(fname, dpi=300, transparent=True)

###############################################################################

velSpList = [velDataSpace0, velDataSpace150, velDataSpace300]
errVarList = ['lineFitErr']
slopeVarList = ['lineFitSlope']
err_vmin = 0
err_vmax = 10
slope_vmin = 0
slope_vmax = 1.6


def createSweepFig(name):
    fig = figure(name, figsize=sweepFigSize)
    ax = fig.add_axes(Bbox.from_extents(sweepLeft, sweepBottom, sweepRight,
        sweepTop))
    return fig, ax

if (velSweep0):
    # noise_sigma = 0 pA
    fig, ax = createSweepFig("velErrSweeps0")
    ax, cax = drawVelSweep(ax, velDataSpace0, iterList, errVarList,
            noise_sigma=noise_sigmas[0],
            cbar=False,
            xlabel='', xticks=False,
            vmin=err_vmin, vmax=err_vmax)
    fname = outputDir + "/figure2_err_sweeps0.png"
    fig.savefig(fname, dpi=300, transparent=True)

    fig, ax = createSweepFig("velSlopeSweep0")
    ax, cax = drawVelSweep(ax, velDataSpace0, iterList, slopeVarList,
            noise_sigma=noise_sigmas[0],
            cbar=False,
            sigmaTitle=False,
            vmin=slope_vmin, vmax=slope_vmax)
    fname = outputDir + "/figure2_slope_sweeps0.png"
    fig.savefig(fname, dpi=300, transparent=True)


if (velSweep150):
    # noise_sigma = 150 pA
    fig, ax = createSweepFig("velErrSweeps150")
    ax, cax = drawVelSweep(ax, velDataSpace150, iterList, errVarList,
            ylabel='', yticks=False,
            noise_sigma=noise_sigmas[1],
            cbar=False,
            xlabel='', xticks=False,
            vmin=err_vmin, vmax=err_vmax)
    fname = outputDir + "/figure2_err_sweeps150.png"
    fig.savefig(fname, dpi=300, transparent=True)

    fig, ax = createSweepFig("velSlopeSweep150")
    ax, cax = drawVelSweep(ax, velDataSpace150, iterList, slopeVarList,
            noise_sigma=noise_sigmas[1],
            ylabel='', yticks=False,
            cbar=False,
            sigmaTitle=False,
            vmin=slope_vmin, vmax=slope_vmax)
    fname = outputDir + "/figure2_slope_sweeps150.png"
    fig.savefig(fname, dpi=300, transparent=True)


if (velSweep300):
    # noise_sigma = 300 pA
    fig, ax = createSweepFig("velErrSweeps300")
    ax, cax = drawVelSweep(ax, velDataSpace300, iterList, errVarList,
            ylabel='', yticks=False,
            noise_sigma=noise_sigmas[2],
            cbar=True,
            xlabel='', xticks=False,
            vmin=err_vmin, vmax=err_vmax,
            cbar_kwargs = {'label' : 'Fit error (neurons/s)'})
    fname = outputDir + "/figure2_err_sweeps300.png"
    fig.savefig(fname, dpi=300, transparent=True)

    fig, ax = createSweepFig("velSlopeSweep300")
    ax, cax = drawVelSweep(ax, velDataSpace300, iterList, slopeVarList,
            noise_sigma=noise_sigmas[2],
            ylabel='', yticks=False,
            cbar=True,
            sigmaTitle=False,
            vmin=slope_vmin, vmax=slope_vmax,
            cbar_kwargs = {'label' : 'Slope (neurons/s/pA)',
                'ticks' : MultipleLocator(0.5)})
    fname = outputDir + "/figure2_slope_sweeps300.png"
    fig.savefig(fname, dpi=300, transparent=True)

# Stats
if (hists):
    fig = figure(figsize=histFigsize)
    ax = fig.add_axes(Bbox.from_extents(histLeft, histBottom, histRight,
        histTop))
    plotErrHistogram(velSpList, ['lineFitErr'], xlabel='Fit error (neurons/s)',
            ylabel='p(error)')
    fname = outputDir + "/figure2_err_histograms.pdf"
    savefig(fname, dpi=300, transparent=True)

    fig = figure(figsize=histFigsize)
    ax = fig.add_axes(Bbox.from_extents(histLeft, histBottom, histRight,
        histTop))
    plotSlopeHistogram(velSpList, ['lineFitSlope'], xlabel='Slope (neurons/s/pA)',
            ylabel='p(slope)', plotLegend=True)
    fname = outputDir + "/figure2_slope_histograms.pdf"
    savefig(fname, dpi=300, transparent=True)


if (velLines):
    positions = ((4, 27), (4, 27), (4, 27))
    fig = figure(figsize=(2.5, histFigsize[1]))
    ax = fig.add_axes(Bbox.from_extents(0.3, histBottom, histRight,
        histTop))
    plotAllSlopes(ax, velSpList, positions)
    fname = outputDir + "/figure2_slope_examples.pdf"
    savefig(fname, dpi=300, transparent=True)

if (gridness_vs_error):
    gridSpList = [gridDataSpace0, gridDataSpace150, gridDataSpace300]
    fig = figure(figsize=(3.4, 2.5))
    plotGridnessVsFitErr(gridSpList, velSpList, range(NTrials), maxErr=None)
    fig.tight_layout()
    fname = outputDir + "/figure2_gridness_vs_error.pdf"
    savefig(fname, dpi=300, transparent=True)

