# import the modules
import matplotlib.pyplot as plt
import numpy as np
import scipy
from serial.tools import list_ports

def ripData():
    # Returns (x_data, y_data) of the function currently plotted in pyplot
    plot = (plt.gca()).lines[0]
    x_data = plot.get_data()[0]
    y_data = plot.get_data()[1]
    return x_data, y_data

# Get nanovna device automatically
# https://github.com/nanovna-v2/NanoVNA2-firmware/blob/master/python/nanovna.py
VIDPIDs = set([(0x0483, 0x5740), (0x04b4,0x0008)]);
def getport() -> str:
    device_list = list_ports.comports()
    for device in device_list:
        if (device.vid, device.pid) in VIDPIDs:
            return device.device
    raise OSError("device not found")

def extrapolatetodc(f,s):
    """Extrapolate s parameters to DC. Assumes the frequency difference between
    DC and the first point is equal to the frequency difference between adjacent
    points"""
    fwithDC = np.insert(f,0,0)
    swithDC = np.insert(s,0,0)
    print(len(f))
    print(len(s))
    phase = scipy.interpolate.interp1d(f, np.unwrap(np.angle(s)), axis=0,
    fill_value='extrapolate')(0)
    magnitude = scipy.interpolate.interp1d(f, np.abs(s), axis=0,
    fill_value='extrapolate')(0)
    swithDC[0] = np.real(magnitude*np.exp(-1j*phase))
    return fwithDC,swithDC

def calculateTDR(f,s,mode='lowpass_step',window='normal',electrical_delay=0.0):
    """Calculate the time domain step response from the frequency domain data.
    Uses the same window as the NanoVNA v2 firmware which can be found at
    https://github.com/nanovna-v2/NanoVNA-V2-firmware in the file main2.cpp
    in the function transform_domain() with option TD_FUNC_LOWPASS_STEP"""
    points = len(s)
    #the window is symmetric about the middle of the array
    #if mode is lowpass, made window twice and wide and apply only
    #the right half of the window to the data.
    if mode == 'lowpass_step' or mode == 'lowpass_impulse':
        window_size = 2*points
    else:
        window_size = points
    #apply a window to reduce high frequency noise and aliasing
    #use a kaiser window for consistency with NanoVNA firmware
    #beta = 6 for TD_WINDOW_NORMAL, 0 for TD_WINDOW_MINIMUM, and 13 for TD_WINDOW_MAXIMUM
    if window == 'minimum':
        beta = 0 #rectangular window in the frequency domain
    elif window == 'normal':
        beta = 6
    elif window == 'maximum':
        beta = 13
    else:
        raise Exception("Allowed window sizes are minimum, normal, or maximum")
    window_points = np.kaiser(window_size,beta)
    #if we are using one of the lowpass modes, apply only the right half
    #of the window to the data. otherwise apply the full window.
    if mode == 'lowpass_step' or mode == 'lowpass_impulse':
        snoDC = s*window_points[points:]
    else:
        snoDC = s*window_points
    #extrapolate the s parameters to DC
    fwithDC, swithDC = extrapolatetodc(f,snoDC)
    #we expect a real signal but we are only measuring positive frequencies.
    #append the complex conjugate (without the dc component to preserve conjugate symmetry)
    swithconj = np.concatenate((swithDC,np.conj(np.flip(snoDC))))
    ## same as above but zero padding
    # pad_width=1024-(2*points+1)
    # swithconj = np.concatenate((np.pad(swithDC,(0,pad_width)),np.pad(np.conj(np.flip(snoDC)),(pad_width,0))))
    #inverse fourier transform to get back into the time domain
    td = np.fft.ifft(swithconj)
    #take the cumulative sum to simulate the step response (rather than the impulse response)
    if mode == 'lowpass_step':
        td = np.cumsum(td)
        #calculate the time axis
        tmax = 1 / (f[1] - f[0])
        t = np.linspace(0, tmax, len(td))
    return t,td

def measureTDR(s11, f, mode='lowpass_step',window='normal',electrical_delay=0.0):
    return calculateTDR(f,s11,mode,window,electrical_delay)