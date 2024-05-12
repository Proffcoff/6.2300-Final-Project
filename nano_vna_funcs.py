# import the modules
import matplotlib.pyplot as plt
import skrf
import numpy as np
from serial.tools import list_ports
from scipy import signal

def ripData():
    # Returns (x_data, y_data) of the function currently plotted in pyplot
    plot = (plt.gca()).lines[0]
    x_data = plot.get_data()[0]
    y_data = plot.get_data()[1]
    return x_data, y_data

def findPeaks(y_data, min_height):
    peak_inds, _ = signal.find_peaks(y_data, height=min_height)
    peak_vals = [y_data[ind] for ind in peak_inds]
    return peak_inds, peak_vals

# Get nanovna device automatically
# https://github.com/nanovna-v2/NanoVNA2-firmware/blob/master/python/nanovna.py
VIDPIDs = set([(0x0483, 0x5740), (0x04b4,0x0008)])
def getport() -> str:
    device_list = list_ports.comports()
    for device in device_list:
        if (device.vid, device.pid) in VIDPIDs:
            return device.device
    raise OSError("device not found")

def plotBandpassTDR(s: skrf.Network, sx1 = 's11', window = 'normal'):
    """Returns (x_axis, y_axis) of Bandpass impulse response plot given frequency data"""
    npoints = len(s.f)  # number of data points

    # Select s11 or s21
    if sx1 == 's11':
        freq_data = s.s[:,0,0]
    elif sx1 == 's21':
        freq_data = s.s[:,1,0]
    else:
        raise Exception("Must select 's11' or 's21' for frequency data")
    
    # Select window
    if window == 'minimum':
        beta = 0 #rectangular window in the frequency domain
    elif window == 'normal':
        beta = 6
    elif window == 'maximum':
        beta = 13
    else:
        raise Exception("Allowed window sizes are minimum, normal, or maximum")
    window_points = np.kaiser(npoints,beta)

    # Window,then take ifft
    s_windowed = freq_data*window_points
    td = np.fft.ifft(s_windowed)

    # make axes
    td = np.absolute(td)
    tmax = 1 / (s.f[1] - s.f[0])
    t = np.linspace(0, tmax, len(td))
    return t, td

    