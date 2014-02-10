#
#   image.py
#
#   Image analysis fitting - rateMaps, generic image analysis for GridCells,
#   etc.
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
from abc import ABCMeta, abstractmethod
import collections
import logging

from scipy    import weave

import numpy as np
import scipy.optimize

from . import spikes

__all__ = ['Position2D', 'remapTwistedTorus', 'fitGaussianTT',
        'fitGaussianBumpTT']

logger = logging.getLogger(__name__)

class Position2D(object):

    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    def __str__(self):
        return "Position2D: x: " + str(self.x) + ", y: " + str(self.y)



class FittingParams(object):
    __meta__ = ABCMeta

    @abstractmethod
    def __init__(self):
        raise NotImplementedError()



class SymmetricGaussianFit(FittingParams):
    def __init__(self, A, mu_x, mu_y, sigma, err):
        self.A = A
        self.mu_x = mu_x
        self.mu_y = mu_y
        self.sigma = sigma
        self.err = err



class GaussianInitParams(object):
    def __init__(self):
        self.A0      = 10.0
        self.mu0_x   = 1.0
        self.mu0_y   = 1.0
        self.sigma0  = 1.0




## Remap a distance between 'a' and others on a twisted torus
#
# Take 'a' which is a 2D position and others, which is a vector of 2D positions
# and compute the distances between them based on the topology of the twisted
# torus, mainly its dimensions.
# 
# If you just want to remap a function of (X, Y), set a==[[0, 0]].
#
# @param a  An array of shape (1, 2) that specifies a position on the twisted
#           torus.
# @param others An array of shape (N, 2) that gives the positions on the twisted
#               torus to compute distance from.
# @param x_dim  X dimension of the torus
# @param y_dim  Y dimension of the torus
# @return       An array of shape (N, ) with all the distances
#
def remapTwistedTorus(a, others, dim):

    a_x = float(a.x)
    a_y = float(a.y)
    others_x = others.x
    others_y = others.y
    szO = others.x.shape[0]
    x_dim = float(dim.x)
    y_dim = float(dim.y)

    ret = np.ndarray((szO,))

    code = '''
    #define SQ(x) ((x) * (x))
    #define MIN(x1, x2) ((x1) < (x2) ? (x1) : (x2))

    for (int i = 0; i < szO; i++)
    {
        double o_x = others_x(i);
        double o_y = others_y(i);

        double d1 = sqrt(SQ(a_x - o_x            ) + SQ(a_y - o_y        ));
        double d2 = sqrt(SQ(a_x - o_x - x_dim    ) + SQ(a_y - o_y        ));
        double d3 = sqrt(SQ(a_x - o_x + x_dim    ) + SQ(a_y - o_y        ));
        double d4 = sqrt(SQ(a_x - o_x + 0.5*x_dim) + SQ(a_y - o_y - y_dim));
        double d5 = sqrt(SQ(a_x - o_x - 0.5*x_dim) + SQ(a_y - o_y - y_dim));
        double d6 = sqrt(SQ(a_x - o_x + 0.5*x_dim) + SQ(a_y - o_y + y_dim));
        double d7 = sqrt(SQ(a_x - o_x - 0.5*x_dim) + SQ(a_y - o_y + y_dim));

        ret(i) = MIN(d7, MIN(d6, MIN(d5, MIN(d4, MIN(d3, MIN(d2, d1))))));
    }
    '''
    
    weave.inline(code,
        ['others_x', 'others_y', 'szO', 'ret', 'a_x', 'a_y', 'x_dim', 'y_dim'],
        type_converters=weave.converters.blitz,
        compiler='gcc',
        extra_compile_args=['-O3'],
        verbose=2)

    return ret



##############################################################################
#                      Image analysis/manipulation functions
##############################################################################



## Fit a 2D Gaussian function to a 2D signal using a least squares method.
#
# The Gaussian is not generic - sigmax = sigmay = sigma, i.e. it is circular
# only.
#
# The function fitted looks like this:
#     fun = A*exp(-||X - mu||^2 / (2*sigma^2))
#
# The initialisation parameters are A, mu_x, mu_y, sigma
#
#
# @param sig_f  Signal function value - this is fitted, use the Position2D class
# @param i      A struct with initialisation values
# @param dim    Dimensions of the twisted torus (Position2D)
# @return Estimated values in the order specified above for A...sigma
#
def fitGaussianTT(sig_f, i, dim):
    X, Y = np.meshgrid(np.arange(dim.x), np.arange(dim.y))
    others = Position2D()
    others.x = X.flatten()
    others.y = Y.flatten()

    a = Position2D()
    def gaussDiff(x):
        a.x = x[1] # mu_x
        a.y = x[2] # mu_y
        dist = remapTwistedTorus(a, others, dim)
        #dist = np.sqrt((others.x - a.x)**2 + (others.y - a.y)**2)
        #print "A:", x[0], a, "sigma:", x[3]
        return np.abs(x[0]) * np.exp( -dist**2/2./ x[3]**2 ) - sig_f
#                       |                            |
#                       A                          sigma

    x0 = np.array([i.A0, i.mu0_x, i.mu0_y, i.sigma0])

    xest,ierr = scipy.optimize.leastsq(gaussDiff, x0)
    err = gaussDiff(xest)
    return xest, err**2



## Fit a 2D Gaussian onto a (potential) firing rate bump. On Twisted torus
#
# @param sig    Firing rate map to fit - a 2D numpy array
# @param dim    Dimensions of the twisted torus (Position2D)
# @return Estimated values for the Gaussian (see Position2D)
def fitGaussianBumpTT(sig, dim):
    '''
    Fit a Gaussian to a rate map, using least squares method.
    '''
    init = GaussianInitParams()
    init.mu0_y, init.mu0_x  = np.unravel_index(np.argmax(sig), sig.shape)
    init.A0 = sig[init.mu0_y, init.mu0_x]
    init.sigma0  = np.max([dim.x, dim.y]) / 2.0
    
    return fitGaussianTT(sig.flatten(), init, dim)






class SingleBumpPopulation(spikes.TwistedTorusSpikes):
    '''
    A population of neurons that is supposed to form a bump on a twisted torus.

    This class contains methods for processing  the population activity over
    time.
    '''

    class BumpFitList(collections.Sequence):
        def __init__(self,
                AList=[],
                mu_xList=[],
                mu_yList=[],
                sigmaList=[],
                err=[],
                times=[]):
            self._A     = AList
            self._mu_x  = mu_xList
            self._mu_y  = mu_yList
            self._sigma = sigmaList
            self._err   = err
            self._times = times

            if not self._consistent():
                raise ValueError('All input arguments mus have same length')


        def _consistent(self):
            return \
                len(self.A) == len(self.mu_x) and   \
                len(self.A) == len(self.mu_y) and   \
                len(self.A) == len(self.sigma) and  \
                len(self.A) == len(self.err) and    \
                len(self.A) == len(self.t)


        def getA(self): return self._A
        def getMu_x(self): return self._mu_x
        def getMu_y(self): return self._mu_y
        def getSigma(self): return self._sigma
        def getErr(self): return self._err
        def getT(self): return self._times
        A     = property(getA)
        mu_x  = property(getMu_x)
        mu_y  = property(getMu_y)
        sigma = property(getSigma)
        err   = property(getErr)
        t     = property(getT)


        def _appendData(self, A, mu_x, mu_y, sigma, err, t):
            self._A.append(A)
            self._mu_x.append(mu_x)
            self._mu_y.append(mu_y)
            self._sigma.append(sigma)
            self._err.append(err)
            self._times.append(t)


        def __getitem__(self, key):
            return SymmetricGaussianFit(self._A[key], self._mu_x[key],
                    self._mu_y[key], self._sigma[key], self._err[key]), \
                            self._times[key]

        def __len__(self):
            return len(self._A) # All same length



    def __init__(self, senders, times, sheetSize):
        super(SingleBumpPopulation, self).__init__(senders, times, sheetSize)



    def bumpPosition(self, tStart, tEnd, dt, winLen, fullErr=True):
        '''
        Estimate bump positions during the simulation time:
        
            1. Use :py:meth:`~.slidingFiringRate`

            2. Apply the bump position estimation procedure to each of the
               population activity items.

        **Parameters**

            tStart, tEnd, dt, winLen : as in :py:meth:`~.slidingFiringRate`.
            fullErr : bool
                If ``True``, save the full error of fit. Otherwise a sum only.

        **Output*
            
            A list of estimation result objects
        '''
        F, Ft = self.slidingFiringRate(tStart, tEnd, dt, winLen)
        dims = Position2D(self.Nx, self.Ny)
        res = self.BumpFitList()
        for tIdx in xrange(len(Ft)):
            logger.debug('Bump fitting: %s/%s', tIdx+1, len(Ft))
            (A, mu_x, mu_y, sigma), err2 = fitGaussianBumpTT(F[:, :, tIdx],
                    dims)
            
            err = np.sqrt(err2)
            if fullErr == False:
                err = np.sum(err)

            res._appendData(A, mu_x, mu_y, sigma, err, Ft[tIdx])
        return res
            





##############################################################################
#                           Tests
##############################################################################

def remapAndPlot(a, dims):
    X, Y = np.meshgrid(np.arange(dims.x), np.arange(dims.y))
    others = Position2D()
    others.x = X.flatten()
    others.y = Y.flatten()
    dist = remapTwistedTorus(a, others, dims)
    plt.figure()
    plt.pcolormesh(np.reshape(dist, (dims.y, dims.x)))
    plt.title('a:(x, y): ' + str(a.x) + ', ' + str(a.y) + ', x_dim:' + str(dims.x) +
            ', y_dim: ' + str(dims.y))
    plt.axis('equal')


if (__name__ == '__main__'):

    import matplotlib.pyplot as plt
    from matplotlib.pyplot import *

    dims = Position2D()
    dims.x = 34
    dims.y = 34
    a = Position2D()
    a.x = 0; a.y = 0
    remapAndPlot(a, dims)

    a.x = dims.x/2.
    a.y = 0
    remapAndPlot(a, dims)

    a.x = dims.x - 1;
    a.y = 0
    remapAndPlot(a, dims)

    a.x = 0
    a.y = dims.y/2.0
    remapAndPlot(a, dims)

    a.x = dims.x/2.0
    a.y = dims.y/2.0
    remapAndPlot(a, dims)

    a.x = dims.x - 1
    a.y = dims.y/2.0
    remapAndPlot(a, dims)

    a.x = 0
    a.y = dims.y - 1
    remapAndPlot(a, dims)

    a.x = dims.x/2.0
    a.y = dims.y - 1
    remapAndPlot(a, dims)

    a.x = dims.x - 1
    a.y = dims.y - 1
    remapAndPlot(a, dims)

    show()


    ###################################################################### 
    # Gaussian bump fitting on a twisted torus
    dims = Position2D()
    dims.x = 100
    dims.y = 100

    X, Y = np.meshgrid(np.arange(dims.x), np.arange(dims.y))

    pos = Position2D()
    pos.x = X.flatten()
    pos.y = Y.flatten()

    A       = 20.0
    mu_x    = 99
    mu_y    = 50.0
    sigma   = 20

    a0 = Position2D()
    a0.x = mu_x
    a0.y = mu_y
    dist = remapTwistedTorus(a0, pos, dims)
    rateMap = A*np.exp(- dist**2 / (2*sigma**2))
    rateMap += A*0.2*np.random.randn(rateMap.shape[0])
    rateMap[rateMap < 0] = 0
    rateMap = np.reshape(rateMap, (dims.y, dims.x))
  
    figure()
    pcolormesh(np.reshape(dist, (dims.y, dims.x))); colorbar()
    figure()
    pcolormesh(X, Y, rateMap); colorbar()
  
    param_est = fitGaussianBumpTT(rateMap, dims)
    Aest, muxest, muyest, sigmaest = param_est

    print param_est
    
    show()
