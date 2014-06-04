from __future__ import absolute_import, print_function

import matplotlib.ticker as ti
from configobj import ConfigObj

_default_config = ConfigObj()

scale_factor = 1.

exampleRC = ((5, 15), (15, 5))
tick_width = 1. * scale_factor
tick_len   = 6. * scale_factor

_default_config.merge({
    'scale_factor': 1.,

    'iter_list': ['g_AMPA_total', 'g_GABA_total'],

    'output_dir': 'panels/',

    'grids_data_root':     'simulation_data/submission/grids',
    'bump_data_root':      'simulation_data/submission/gamma_bump',
    'vel_data_root':       'simulation_data/submission/velocity',
    'const_pos_data_root': 'simulation_data/submission/const_position',
    'singleDataRoot':      'simulation_data/submission/single_neuron',

    'even_shape': (31, 31),
    'noise_sigmas': [0, 150, 300],

    # Sections
    'mpl': {
        'font.size': 11,
        'pdf.fonttype': 42,
        'mathtext.default': 'regular',

        'xtick.major.size'  : tick_len,
        'xtick.major.width' : tick_width,
        'xtick.minor.size'  : tick_len / 2.,
        'xtick.minor.width' : tick_width,
        'xtick.direction'   : 'out',

        'ytick.major.size'  : tick_len,
        'ytick.major.width' : tick_width,
        'ytick.minor.size'  : tick_len / 2.,
        'ytick.minor.width' : tick_width,
        'ytick.direction'   : 'out',
    },

    'sweeps': {
        'fig_size': (3.7, 2.6),         # inches
        'bbox': (0.08, 0.2, .72, .65),  # l, b, w, h
        'transparent': True,
    },

    'grids': {
        'example_rc': ((5, 15), (15, 5)),
        'example_idx': [(5, 15), (5, 15), (5, 15)],  # (row, col)
        'ntrials': 3,
    },

    'bumps': {
        'n_trials': 5,
    },

    'p_bumps': {
        'frac_total_text' : 'P(bumps)'
    },

    'bump_sigma': {
        'sigma_bump_text': '$\sigma_{bump}^{-1}\ (neurons^{-1})$',
    },

    'seizures': {
        'thetaT': 125.,  # ms
        'sig_dt': .5     # ms
    }
})


def get_config():
    return _default_config


##############################################################################

GridSweepsPlotter_config = {
    'cbar': [0, 0, 1],
    'cbar_kw': {
        'label': 'Gridness score',
        'location': 'right',
        'shrink': 0.8,
        'pad': -0.05,
        'ticks': ti.MultipleLocator(0.5),
        'rasterized': True
    },
    'vmin': -0.505,
    'vmax': 1.141,
    'ann': [
        dict(
            txt='b',
            rc=get_config()['grids']['example_rc'][0],
            xytext_offset=(1.5, 1),
            color='black'
        ),
        dict(
            txt='a',
            rc=get_config()['grids']['example_rc'][1],
            xytext_offset=(0.5, 1.5),
            color='black'
        )
    ],
}
_default_config['GridSweepsPlotter'] = GridSweepsPlotter_config

##############################################################################
GridExamplesPlotter_config = {
    'fig_size': (1, 1.2),
    'ax_box': (0.01, 0.01, 0.99, 0.85),  # l, b, r, t
    'transparent': True,
}
_default_config['GridExamplesPlotter'] = GridExamplesPlotter_config

##############################################################################

GridsDiffSweep_config = {
    'cbar_kw': dict(
        label      = '$\Delta_{150 - 0}$(Gridness score)',
        location   = 'right',
        shrink     = 0.8,
        pad        = -0.05,
        ticks      = ti.MultipleLocator(0.5),
        rasterized = True
    )
}
_default_config['GridsDiffSweep'] = GridsDiffSweep_config

##############################################################################

VmExamplesPlotter_config = {
    'fig_size': (2.5, 1.25),
    'ax_rect': (0.01, 0.01, 0.999, 0.6),  # l, b, r, t
}
_default_config['VmExamplesPlotter'] = VmExamplesPlotter_config

##############################################################################

ConnectionFunctionPlotter_config = {
    'fig_size': (3, 1.5),
}
_default_config['ConnectionFunctionPlotter'] = ConnectionFunctionPlotter_config

##############################################################################

GammaSweepsPlotter_config = {
    'scale_factor': .8,
    'AC_cbar_kw': dict(
        location   = 'left',
        ticks      = ti.MultipleLocator(0.3),
        fraction   = 0.25,
        shrink     = 0.8,
        pad        = .2,
        labelpad   = 8,
        label      = '$1^{st}$ autocorrelation\npeak',
        rasterized = True,
    ),
    'AC_xticks': [False]*3,

    'F_cbar_kw': dict(
        location   = 'left',
        ticks      = ti.MultipleLocator(30),
        fraction   = 0.25,
        shrink     = 0.8,
        pad        = .2,
        labelpad   = 8,
        label      = 'Oscillation\nfrequency (Hz)',
        extend     = 'max',
        extendfrac = 0.1,
        rasterized = True
    ),

    'cbar_kw' : {
        'location': 'left',
    }
}
_default_config['GammaSweepsPlotter'] = GammaSweepsPlotter_config

##############################################################################

GammaScatterAllPlotter_config = {
    'fig_size': (5., 3.2),
    'legend_kwargs': dict(
        loc=(0.9, 0.4),
        fontsize='small',
        frameon=False,
        numpoints=1,
        title='$\sigma$ (pA)'
    ),
    'tight_layout_kwargs': {
        'pad': 3.,
    },
}
_default_config['GammaScatterAllPlotter'] = GammaScatterAllPlotter_config

##############################################################################

fracTotalText = _default_config['p_bumps']['frac_total_text']

FracTotalSweepAnnPlotter_config = {
    'scale_factor': .8,
    'cbar_kw': dict(
        label       = fracTotalText,
        location    = 'left',
        shrink      = 0.8,
        pad         = 0.25,
        ticks       = ti.MultipleLocator(0.5),
        rasterized  = True
    )
}
_default_config['FracTotalSweepAnnPlotter'] = FracTotalSweepAnnPlotter_config

##############################################################################

MainBumpFormationPlotter_config = {
    'scale_factor': .8,
    'cbar_kw': dict(
        label       = fracTotalText,
        location    = 'left',
        shrink      = 0.8,
        pad         = 0.25,
        ticks       = ti.MultipleLocator(0.5),
        rasterized  = True
    ),
    'xticks': [True]*3,
}
_default_config['MainBumpFormationPlotter'] = MainBumpFormationPlotter_config

##############################################################################

_default_config['MainIsBumpPlotter'] = FracTotalSweepAnnPlotter_config

##############################################################################

_default_config['IsBumpPlotter'] = FracTotalSweepAnnPlotter_config

##############################################################################

MainScatterGridsBumpsPlotter_config = {
    'fig_size': (5.8, 3.2),
    'tight_layout_kwargs': {
        'rect': (0.05, 0.05, 0.95, 0.9),
    },
    'legend_kwargs': dict(
        loc=(0.2, 1.02),
        fontsize='small',
        frameon=True,
        fancybox=True,
        framealpha=0.5,
        handletextpad=0,
        scatterpoints=1,
        ncol=3,
        title='$\sigma$ (pA)'
    ),
}
_default_config['MainScatterGridsBumpsPlotter'] = MainScatterGridsBumpsPlotter_config

##############################################################################
BumpDriftAtTimePlotter_config = {
    'cbar_kw': dict(
        label       = 'Average bump drift\n(neurons)',
        location    = 'right',
        shrink      = 0.8,
        pad         = -0.05,
        ticks       = ti.MultipleLocator(10),
        rasterized  = True
    )
}
_default_config['BumpDriftAtTimePlotter'] = BumpDriftAtTimePlotter_config

##############################################################################
BumpDiffAtInitPlotter_config = {
    'cbar_kw': dict(
        label       = 'Distance from init\nposition (neurons)',
        location    = 'right',
        shrink      = 0.8,
        pad         = -0.05,
        ticks       = ti.MultipleLocator(10),
        rasterized  = True
    )
}
_default_config['BumpDiffAtInitPlotter'] = BumpDiffAtInitPlotter_config

##############################################################################
BumpDiffResetPlotter_config = {
    'cbar_kw': dict(
        label       = 'Distance from reset\nposition (neurons)',
        location    = 'right',
        shrink      = 0.8,
        pad         = -0.05,
        ticks       = ti.MultipleLocator(5),
        rasterized  = True
    )
}
_default_config['BumpDiffResetPlotter'] = BumpDiffResetPlotter_config

##############################################################################

MaxPopulationFRSweepsPlotter_config = {
    'cbar_kw': dict(
        label       = "max(E rate) (Hz)",
        location    = 'left',
        shrink      = 0.8,
        pad         = 0.25,
        ticks       = ti.MultipleLocator(100),
        rasterized  = True
    )
}
_default_config['MaxPopulationFRSweepsPlotter'] = MaxPopulationFRSweepsPlotter_config

##############################################################################

BumpSigmaSweepPlotter_config = {
    'cbar_kw': dict(
        label       = get_config()['bump_sigma']['sigma_bump_text'],
        location    = 'right',
        shrink      = 0.8,
        pad         = -0.05,
        ticks       = ti.MultipleLocator(0.2),
        rasterized  = True
    )
}
_default_config['BumpSigmaSweepPlotter'] = BumpSigmaSweepPlotter_config

##############################################################################

EIRasterPlotter_config = {
    'fig_size': (3, 1.9),
}
_default_config['EIRasterPlotter'] = EIRasterPlotter_config

##############################################################################

EIRatePlotter_config = {
    'fig_size': (3, .65),
    'rateTop': .9
}
_default_config['EIRatePlotter'] = EIRatePlotter_config

##############################################################################

MaxMeanThetaFRSweepPlotter_config = {
    'cbar_kw': dict(
        label       = "max(E rate)/$\\theta$ cycle (Hz)",
        location    = 'left',
        shrink      = 0.8,
        pad         = 0.25,
        ticks       = ti.MultipleLocator(100),
        #ticks       = ti.LogLocator(base=4),
        #format      = ti.LogFormatter(4),
        rasterized  = True
    )
}
_default_config['MaxMeanThetaFRSweepPlotter'] = MaxMeanThetaFRSweepPlotter_config

##############################################################################

PSeizureSweepPlotter_config = {
    'FRThreshold': 300
}
PSeizureSweepPlotter_config.update({
    'cbar_kw': dict(
        label       = "P[max(rate during $\\theta$) > {0}]".format(
                        PSeizureSweepPlotter_config['FRThreshold']),
        location    = 'left',
        shrink      = 0.8,
        pad         = 0.25,
        ticks       = ti.MultipleLocator(0.5),
        rasterized  = True
    )
})
_default_config['PSeizureSweepPlotter'] = PSeizureSweepPlotter_config

##############################################################################

MaxStdThetaFRSweepPlotter_config = {
    'cbar_kw': dict(
        label       = "max(E rate)/$\\theta$ cycle (Hz)",
        location    = 'left',
        shrink      = 0.8,
        pad         = 0.25,
        ticks       = ti.MaxNLocator(4),
        rasterized  = True
    )
}
_default_config['MaxStdThetaFRSweepPlotter'] = MaxStdThetaFRSweepPlotter_config

##############################################################################

_default_config['MaxMedianThetaFRSweepPlotter'] = MaxStdThetaFRSweepPlotter_config

##############################################################################
VelFitErrSweepPlotter_config = {
    'scale_factor': .7,
    'cbar_kw': dict(
        label       = 'Fit error (neurons/s)',
        location    = 'right',
        shrink      = 0.8,
        pad         = 0.05,
        ticks       = ti.MultipleLocator(1),
        extend      = 'max',
        extendfrac  = 0.1,
        rasterized  = True
    )
}
_default_config['VelFitErrSweepPlotter'] = VelFitErrSweepPlotter_config

##############################################################################

VelFitStdSweepPlotter_config = {
    'scale_factor': .7,
    'cbar_kw': dict(
        location='right',
        label='Mean $\sigma_{spd}$ (neurons/s)',
        shrink = 0.8,
        pad = 0.05,
        ticks=ti.MultipleLocator(5),
        extend='max', extendfrac=0.1
    )
}
_default_config['VelFitStdSweepPlotter'] = VelFitStdSweepPlotter_config

##############################################################################
