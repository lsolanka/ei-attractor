#!/usr/bin/env python
#
'''
Everything related to velocity: sweeps, lines, etc.
'''
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ti
from matplotlib.transforms import Bbox

from EI_plotting import sweeps, details, rasters
from EI_plotting import aggregate as aggr
from EI_plotting.base import NoiseDataSpaces
from plotting.global_defs import globalAxesSettings
from parameters import JobTrialSpace2D
from submitting import flagparse

# Other
from matplotlib import rc
rc('pdf', fonttype=42)
rc('mathtext', default='regular')

plt.rcParams['font.size'] = 11

###############################################################################

outputDir = "panels"
NTrials = 5
iterList  = ['g_AMPA_total', 'g_GABA_total']

noise_sigmas  = [0, 150, 300]
rasterRC      = [(5, 15), (5, 15), (5, 15)] # (row, col)
bumpDataRoot  = 'output_local/even_spacing/gamma_bump'
velDataRoot   = 'output_local/even_spacing/velocity_vertical'
gridsDataRoot = 'output_local/even_spacing/grids'
shape = (31, 31)

parser = flagparse.FlagParser()
parser.add_flag('--velLines')
parser.add_flag('--detailed_noise')
parser.add_flag('--slope_sweeps')
parser.add_flag('--rasters')
parser.add_flag('--rastersZoom')
parser.add_flag('--rates')
args = parser.parse_args()

###############################################################################

def plotSlopes(ax, dataSpace, pos, noise_sigma, **kw):
    # kwargs
    trialNum   = kw.pop('trialNum', 0)
    markersize = kw.pop('markersize', 4)
    color      = kw.pop('color', 'blue')
    xlabel     = kw.pop('xlabel', 'Velocity current (pA)')
    ylabel     = kw.pop('ylabel', 'Bump speed\n(neurons/s)')
    xticks     = kw.pop('xticks', True)
    yticks     = kw.pop('yticks', True)
    g_ann      = kw.pop('g_ann', True)
    sigma_ann  = kw.pop('sigma_ann', True)
    kw['markeredgecolor'] = color

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
    stdSlope = np.std(slopes, axis=0)

    if (ax is None):
        ax = plt.gca()
    plt.hold('on')
    globalAxesSettings(ax)

    ax.plot(IvelVec, slopes.T, 'o', markerfacecolor='none', markersize=markersize, **kw)
    #ax.errorbar(IvelVec, avgSlope, stdSlope, fmt='o-',
    #        markersize=markersize, color=color, alpha=0.5, **kw)
    ax.plot(fitIvelVec, lineFit, '-', linewidth=1, color=color, **kw)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_major_locator(ti.MultipleLocator(50))
    ax.xaxis.set_minor_locator(ti.AutoMinorLocator(5))
    ax.yaxis.set_major_locator(ti.MultipleLocator(20))
    ax.yaxis.set_minor_locator(ti.MultipleLocator(10))
    ax.margins(0.05)

    if (not xticks):
        ax.xaxis.set_ticklabels([])
    if (not yticks):
        ax.yaxis.set_ticklabels([])

    # Annotations
    if (sigma_ann):
        sigma_txt = '$\sigma$ = {0} pA'.format(noise_sigma)
        ax.set_title(sigma_txt, y=1.1, va='bottom')

    if (g_ann):
        Y, X = aggr.computeVelYX(dataSpace, iterList, r, c)
        gE = Y[r, c]
        gI = X[r, c]
        g_txt = '$g_E$ = {0}\n$g_I$ = {1} nS'.format(gE, gI)
    else:
        g_txt = ''

    txt = '{0}'.format(g_txt)
    ax.text(0.05, 1.1, txt, transform=ax.transAxes, va='top',
            ha='left', size='x-small')






###############################################################################
roots = NoiseDataSpaces.Roots(bumpDataRoot, velDataRoot, gridsDataRoot)
ps    = NoiseDataSpaces(roots, shape, noise_sigmas)


##############################################################################
velFigsize =(2.6, 2)
velLeft    = 0.3
velBottom  = 0.35
velRight   = 0.95
velTop     = 0.65

if args.velLines or args.all:
    #positions = ((4, 27), (4, 27), (4, 27))
    positions = ((5, 15), (5, 15), (5, 15))
    fig = plt.figure(figsize=(2.5, velFigsize[1]))
    ax = fig.add_axes(Bbox.from_extents(0.3, velBottom, velRight,
        velTop))
    plotSlopes(ax, ps.v[0], positions[0], noise_sigma=ps.noise_sigmas[0],
            xlabel='',
            color='blue')
    fname = outputDir + "/velocity_slope_examples_0.pdf"
    plt.savefig(fname, dpi=300, transparent=True)

    fig = plt.figure(figsize=(2.5, velFigsize[1]))
    ax = fig.add_axes(Bbox.from_extents(0.3, velBottom, velRight,
        velTop))
    plotSlopes(ax, ps.v[1], positions[1], noise_sigma=ps.noise_sigmas[1],
            ylabel='',
            g_ann=False,
            color='green')
    fname = outputDir + "/velocity_slope_examples_1.pdf"
    plt.savefig(fname, dpi=300, transparent=True)

    fig = plt.figure(figsize=(2.5, velFigsize[1]))
    ax = fig.add_axes(Bbox.from_extents(0.3, velBottom, velRight,
        velTop))
    plotSlopes(ax, ps.v[2], positions[2], noise_sigma=ps.noise_sigmas[2],
            xlabel='',
            ylabel='',
            g_ann=False,
            color='red')
    fname = outputDir + "/velocity_slope_examples_2.pdf"
    plt.savefig(fname, dpi=300, transparent=True)


##############################################################################
EI13Root  = 'output_local/detailed_noise/velocity/EI-1_3'
EI31Root  = 'output_local/detailed_noise/velocity/EI-3_1'
detailedShape = (31, 9)

EI13PS = JobTrialSpace2D(detailedShape, EI13Root)
EI31PS = JobTrialSpace2D(detailedShape, EI31Root)
detailedNTrials = None


sliceFigSize = (3.5, 2.5)
sliceLeft   = 0.25
sliceBottom = 0.3
sliceRight  = 0.95
sliceTop    = 0.8
if args.detailed_noise or args.all:
    ylabelPos = -0.27

    types = ('velocity', 'slope')
    fig = plt.figure(figsize=sliceFigSize)
    ax = fig.add_axes(Bbox.from_extents(sliceLeft, sliceBottom, sliceRight,
        sliceTop))
    details.plotDetailedNoise(EI13PS, detailedNTrials, types, ax=ax,
            ylabelPos=ylabelPos,
            xlabel='', xticks=False,
            color='red', markerfacecolor='red', zorder=10)
    details.plotDetailedNoise(EI31PS, detailedNTrials, types, ax=ax,
            xlabel='', xticks=False,
            ylabel='Slope\n(neurons/s/pA)', ylabelPos=ylabelPos,
            color='#505050')
    ax.xaxis.set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.yaxis.set_major_locator(ti.MultipleLocator(0.4))
    ax.yaxis.set_minor_locator(ti.MultipleLocator(0.2))
    ax.spines['bottom'].set_visible(False)

    fname = outputDir + "/velocity_detailed_noise_slope.pdf"
    plt.savefig(fname, dpi=300, transparent=True)
    plt.close()


    types = ('velocity', 'fitErr')
    fig = plt.figure(figsize=sliceFigSize)
    ax = fig.add_axes(Bbox.from_extents(sliceLeft, sliceBottom, sliceRight,
        sliceTop))
    _, p13, l13 = details.plotDetailedNoise(EI13PS, detailedNTrials, types, ax=ax,
            ylabelPos=ylabelPos,
            color='red', markerfacecolor='red', zorder=10)
    _, p31, l31 = details.plotDetailedNoise(EI31PS, detailedNTrials, types, ax=ax,
            ylabel='Fit error\n(neurons/s/trial)', ylabelPos=ylabelPos,
            color='#505050')
    ax.yaxis.set_major_locator(ti.MultipleLocator(4))
    ax.yaxis.set_minor_locator(ti.MultipleLocator(2))
    leg = ['(3, 1)',  '(1, 3)']
    l = ax.legend([p31, p13], leg, loc=(0.55, 0.3), fontsize='small', frameon=False,
            numpoints=1, title='($g_E,\ g_I$) (nS)')
    plt.setp(l.get_title(), fontsize='x-small')

    fname = outputDir + "/velocity_detailed_noise_error.pdf"
    plt.savefig(fname, dpi=300, transparent=True)
    plt.close()





##############################################################################
#                           Velocity (slope) sweeps

# This should be corresponding to the velLine examples as well !!
rasterRC      = [(5, 15), (5, 15), (5, 15)] # (row, col)
slopeVarList = ['lineFitSlope']
slope_vmin = -0.472
slope_vmax = 1.6
velSweep_cmap = 'jet'

slope_cbar_kw= dict(
        location='right',
        shrink = 0.8,
        pad = -0.05,
        label='Slope\n(neurons/s/pA)',
        ticks=ti.MultipleLocator(0.4),
        extend='max', extendfrac=0.1)

ann0 = dict(
        txt='A',
        rc=rasterRC[0],
        xytext_offset=(1.5, 0.5),
        color='white')

ann = [ann0]

def createSweepFig(name=None):
    sweepFigSize = (3.7, 2.6)
    sweepLeft   = 0.08
    sweepBottom = 0.2
    sweepRight  = 0.8
    sweepTop    = 0.85
    transparent  = True
    fig = plt.figure(name, figsize=sweepFigSize)
    ax = fig.add_axes(Bbox.from_extents(sweepLeft, sweepBottom, sweepRight,
        sweepTop))
    return fig, ax

if args.slope_sweeps or args.all:
    for ns_idx, noise_sigma in enumerate(ps.noise_sigmas):
        fig, ax = createSweepFig(None)
        kw = dict(cbar=False)
        if (ns_idx == 2):
            kw['cbar'] = True
        if (ns_idx != 0):
            kw['ylabel'] = ''
            kw['yticks'] = False
        _, ax, cax = sweeps.plotVelTrial(ps.v[ns_idx], slopeVarList, iterList,
                noise_sigma, sigmaTitle=True,
                ax=ax,
                cbar_kw=slope_cbar_kw,
                cmap=velSweep_cmap,
                vmin=slope_vmin, vmax=slope_vmax,
                annotations=ann,
                **kw)
        fname = outputDir + "/velocity_slope_sweeps{}.pdf"
        fig.savefig(fname.format(int(noise_sigma)), dpi=300, transparent=True)



##############################################################################
#                           Raster and rate plots
##############################################################################
tLimits  = [2e3, 3e3] # ms
trialNum = 10

rasterFigSize = (3.75, 2.2)
transparent   = True
rasterLeft    = 0.2
rasterBottom  = 0.2
rasterRight   = 0.99
rasterTop     = 0.8

ylabelPos   = -0.22


if args.rasters or args.all:
    for idx, noise_sigma in enumerate(ps.noise_sigmas):
        fig = plt.figure(figsize=rasterFigSize)
        ax = fig.add_axes(Bbox.from_extents(rasterLeft, rasterBottom, rasterRight,
            rasterTop))
        kw = dict(scaleBar=None)
        if (idx != 0):
            kw['ylabel'] = ''
            kw['yticks'] = False
        if idx == 2:
            kw['scaleBar'] = 125
        rasters.EIRaster(ps.v[idx], 
                noise_sigma=noise_sigma,
                spaceType='velocity',
                r=rasterRC[idx][0], c=rasterRC[idx][1],
                ylabelPos=ylabelPos,
                tLimits=tLimits,
                trialNum=trialNum,
                ann_EI=True,
                scaleX=0.85,
                scaleY=-0.15,
                **kw)
        fname = outputDir + "/velocity_raster{0}.png"
        fig.savefig(fname.format(int(noise_sigma)), dpi=300,
                transparent=transparent)
        plt.close()
        
        

##############################################################################
rateFigSize   = (rasterFigSize[0], 1)
rateLeft    = rasterLeft
rateBottom  = 0.2
rateRight   = rasterRight
rateTop     = 0.7


if args.rates or args.all:
    for idx, noise_sigma in enumerate(ps.noise_sigmas):
        # E cells
        fig = plt.figure(figsize=rateFigSize)
        ax = fig.add_axes(Bbox.from_extents(rateLeft, rateBottom, rateRight,
            rateTop))
        kw = {}
        if (idx != 0):
            kw['ylabel'] = ''

        rasters.plotAvgFiringRate(ps.v[idx],
                spaceType='velocity',
                noise_sigma=noise_sigma,
                popType='E',
                r=rasterRC[idx][0], c=rasterRC[idx][1],
                ylabelPos=ylabelPos,
                color='red',
                tLimits=tLimits,
                trialNum=trialNum,
                sigmaTitle=False,
                ax=ax, **kw)
        fname = outputDir + "/velocity_rate_e{0}.pdf".format(noise_sigma)
        fig.savefig(fname, dpi=300, transparent=transparent)
        plt.close()

        # I cells
        fig = plt.figure(figsize=rateFigSize)
        ax = fig.add_axes(Bbox.from_extents(rateLeft, rateBottom, rateRight,
            rateTop))
        kw = {}
        if (idx != 0):
            kw['ylabel'] = ''

        rasters.plotAvgFiringRate(ps.v[idx],
                spaceType='velocity',
                noise_sigma=noise_sigma,
                popType='I', 
                r=rasterRC[idx][0], c=rasterRC[idx][1],
                ylabelPos=ylabelPos,
                color='blue',
                tLimits=tLimits,
                trialNum=trialNum,
                sigmaTitle=False,
                ax=ax, **kw)
        fname = outputDir + "/velocity_rate_i{0}.pdf".format(noise_sigma)
        fig.savefig(fname, dpi=300, transparent=transparent)
        plt.close()




##############################################################################
#                           Raster and rate zoom-ins
##############################################################################
tLimits  = [2.75e3, 2.875e3] # ms
trialNum = 10

c = 0.75
rasterZoomFigSize = c*rasterFigSize[0], c*rasterFigSize[1]
ylabelPos   = -0.22


if args.rastersZoom or args.all:
    for idx, noise_sigma in enumerate(ps.noise_sigmas):
        fig = plt.figure(figsize=rasterZoomFigSize)
        ax = fig.add_axes(Bbox.from_extents(rasterLeft, rasterBottom, rasterRight,
            rasterTop))
        kw = dict(scaleBar=None)
        if idx == 2:
            kw['scaleBar'] = 25
        rasters.EIRaster(ps.v[idx], 
                noise_sigma=noise_sigma,
                spaceType='velocity',
                r=rasterRC[idx][0], c=rasterRC[idx][1],
                ylabelPos=ylabelPos,
                tLimits=tLimits,
                trialNum=trialNum,
                sigmaTitle=False,
                ann_EI=True,
                scaleX=0.75,
                scaleY=-0.15,
                ylabel='', yticks=False,
                **kw)
        fname = outputDir + "/velocity_raster_zooms{0}.png"
        fig.savefig(fname.format(int(noise_sigma)), dpi=300,
                transparent=transparent)
        plt.close()
        
