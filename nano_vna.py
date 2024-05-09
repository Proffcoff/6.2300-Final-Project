# import the modules
import matplotlib.pyplot as plt
import skrf
from skrf import Frequency
from skrf.vi.vna import nanovna
from skrf.calibration import OnePort
from serial.tools import list_ports
from scipy import signal

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

COM_Port = getport()[3] # get rid of 'COM' before the com port number
instr = nanovna.NanoVNA('ASRL'+COM_Port+'::INSTR')
# Assign frequency range and number of points
instr.freq_start = 2.4e9
instr.freq_stop = 3e9
instr.npoints = 100

# Calibrate
input("Please connect a SHORT to port 1 at\nthe reference plane, then press enter:\n")
s11_short, _ = instr.get_s11_s21()
input("Please connect an OPEN to port 1 at\nthe reference plane, then press enter:\n")
s11_open, _ = instr.get_s11_s21()
input("Please connect a MATCHED LOAD to port 1\nat the reference plane, then press enter:\n")
s11_match, _ = instr.get_s11_s21()

line = skrf.DefinedGammaZ0(frequency=s11_short.frequency, z0=50)

# create and run the calibration
cal = OnePort(ideals=[line.short(), line.open(), line.match()],
            measured=[s11_short, s11_open, s11_match])
cal.run()
print("Calibration finished!")

# acquire a new trace
input("Press enter to take measurement:\n")
s11, _ = instr.get_s11_s21()

# apply the calibration
s11_cal = cal.apply_cal(s11)

# plot the calibrated s11
s11_cal.plot_s_db()
plt.title("s_db freq")
plt.show()

#print(f"calibrated s_db_time matrix: {s11.s_time_db}")
#s11.plot_s_db_time()
#plt.title("Uncalibrated db vs time")
#plt.show()

s11_cal.plot_s_db_time()
plt.title("Calibrated db vs time")
x_data, y_data = ripData()
print(f"x_data: {x_data}")
print(f"y_data: {y_data}")
peak_inds, _ = signal.find_peaks(y_data, height=-3)
peak_vals = [y_data[ind] for ind in peak_inds]
print(f"peak inds: {peak_inds}\npeak data: {peak_vals}")
plt.show()

#s11.plot_s_time_mag()
#plt.title("Uncalibrated mag vs time")
#plt.show()

#s11_cal.plot_s_time_mag()
#plt.title("Calibrated mag vs time")
#plt.show()
