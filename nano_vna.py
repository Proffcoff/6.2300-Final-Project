# import the modules
import matplotlib.pyplot as plt
import skrf
from skrf.vi.vna import nanovna
from skrf.calibration import OnePort
from skrf.calibration import SOLT
from nano_vna_funcs import *

c = 3e8 # speed of light [m/s]
v_f = 1 # velocity factor
cal_file = "nanovna_cal"

COM_Port = getport()[3:] # get rid of 'COM' before the com port number
instr = nanovna.NanoVNA('ASRL'+COM_Port+'::INSTR')
# Assign frequency range and number of points
instr.freq_start = 3e9
instr.freq_stop = 4e9
instr.npoints = 1024  # max number of points for nanovna

user_choice = input("Update Calibration? (y/n): ")
if user_choice == "y":
    # Calibrate
    input("Please connect a SHORT to port 1 at\nthe reference plane, then press enter:\n")
    s11_short, _ = instr.get_s11_s21()
    input("Please connect an OPEN to port 1 at\nthe reference plane, then press enter:\n")
    s11_open, _ = instr.get_s11_s21()
    input("Please connect a MATCHED LOAD to port 1\nat the reference plane, then press enter:\n")
    s11_match, _ = instr.get_s11_s21()
    
    input("Please connect a SHORT to port 2 at\nthe reference plane, then press enter:\n")
    _, s21_short = instr.get_s11_s21()
    input("Please connect an OPEN to port 2 at\nthe reference plane, then press enter:\n")
    _, s21_open = instr.get_s11_s21()
    input("Please connect a MATCHED LOAD to port 2\nat the reference plane, then press enter:\n")
    _, s21_match = instr.get_s11_s21()
    
    input("Please connect a Thru to port 1 & port 2\nat the reference plane, then press enter:\n")
    s11_thru, s21_thru = instr.get_s11_s21()

    shorts = skrf.two_port_reflect(s11_short, s21_short)
    opens = skrf.two_port_reflect(s11_open, s21_open)
    matches = skrf.two_port_reflect(s11_match, s21_match)
    thru = skrf.two_port_reflect(s11_thru, s21_thru)

    line = skrf.DefinedGammaZ0(frequency=s11_short.frequency, z0=50)
    # create and run the calibration
    new_cal = SOLT(ideals=[line.short(2), line.open(2), line.match(2), line.thru(2)],
                measured=[shorts, opens, matches, thru])
    new_cal.run()
    print("Calibration finished!")
    new_cal.name = cal_file
    new_cal.write()
    print("Calibration saved!")
# get calibration
cal = skrf.read(cal_file + ".cal")

# acquire a new trace & calibrate
input("Press enter to take measurement:\n")
s11, s21 = instr.get_s11_s21()
s = skrf.two_port_reflect(s11, s21)
s_cal = cal.apply_cal(s)

t1, td1 = plotBandpassTDR(s, sx1 = 's11')
plt.plot(t1*1e9, td1)
t2, td2 = plotBandpassTDR(s, sx1 = 's21')
plt.plot(t2*1e9, td2)

s11_peak_inds, s11_peak_vals = findPeaks(td1, 0.05)
print(f"s11 peak inds: {s11_peak_inds}\ns11 peak data: {s11_peak_vals}")
s21_peak_inds, s21_peak_vals = findPeaks(td2, 0.05)
print(f"s21 peak inds: {s21_peak_inds}\ns21 peak data: {s21_peak_vals}")

plt.xlabel("Time (ns)")
plt.ylabel("|s11|")
plt.show()