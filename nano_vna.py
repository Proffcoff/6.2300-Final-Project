# import the modules
import matplotlib.pyplot as plt
import skrf
from skrf.vi.vna import nanovna
from skrf.calibration import OnePort
from nano_vna_funcs import *

c = 3e8 # speed of light [m/s]
v_f = 1 # velocity factor

COM_Port = getport()[3:] # get rid of 'COM' before the com port number
instr = nanovna.NanoVNA('ASRL'+COM_Port+'::INSTR')
# Assign frequency range and number of points
instr.freq_start = 3e9
instr.freq_stop = 4e9
instr.npoints = 1024  # max number of points for nanovna

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

t, td = plotBandpassTDR(s11_cal)
plt.plot(t*1e9, td)
plt.xlabel("Time (ns)")
plt.ylabel("|s11|")

peak_inds, peak_vals = findPeaks(td, 0.03)
print(f"peak inds: {peak_inds}\npeak data: {peak_vals}")

plt.show()