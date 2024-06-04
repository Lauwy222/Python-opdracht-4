import pyvisa
import numpy as np
import matplotlib.pyplot as plt

class Instrument:
    def __init__(self, pyvisa_instrument=None):
        self.instrument = pyvisa_instrument

    def send_write(self, cmd):
        self.instrument.write(cmd)

    def send_query(self, cmd):
        return self.instrument.query(cmd)


# Function gen CMDS
class FunctionGenerator(Instrument):
    def set_function(self, channel, value):
        self.instrument.write(":SOUR{}:FUNC {}".format(channel, value))

    def set_frequency(self, channel, value):
        self.instrument.write(":SOUR{}:FREQ {}".format(channel, value))

    def set_offset(self, channel, value):
        self.instrument.write(":SOUR{}:VOLT:OFFS {}".format(channel, value))

    def set_phase(self, channel, value):
        self.instrument.write(":SOUR{}:PHAS {}".format(channel, value))

    def set_amplitude(self, channel, value):
        self.instrument.write(":SOUR{}:VOLT {}".format(channel, value))

    def enable_outputs(self, channel, state):
        self.instrument.write(":OUTP{} {}".format(channel, state))


# Oscilloscope CMDS
class Oscilloscope(Instrument):
    def set_horizontal_scale(self, seconds_per_devision):
        self.instrument.write(":TIM:MAIN:SCAL {}".format(seconds_per_devision))

    def set_vertical_scale(self, channel, volts_per_devision):
        self.instrument.write(":CHAN{}:SCAL {}".format(channel, volts_per_devision))

    def get_max_voltage(self, channel):
        return self.instrument.query(":MEAS:ITEM? VMAX, CHAN{}".format(channel))


def plot_frequency_response(frequencies, amplitudes):
    gain_db = 20 * np.log10(amplitudes)
    plt.figure()
    plt.semilogx(frequencies, gain_db)
    plt.title("Frequency Response")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Gain (dB)")
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.show()

rm = pyvisa.ResourceManager()

print(rm.list_resources())

fg_found = False
scope_found = False

for name, info in rm.list_resources_info().items():
    if info.interface_type.name == "usb":
        resource = rm.open_resource(name)
        query_result = resource.query("*IDN?")
        if "DG1032Z" in query_result:
            fg_found = True
            fg_resource = resource
            Func = FunctionGenerator(resource)
        if "MSO1074" in query_result:
            scope_found = True
            scope_resource = resource
            Osci = Oscilloscope(resource)

if fg_found:
    print("Found DG1032Z")
else:
    print("No function generator found")
if scope_found:
    print("Found MSO1074")
else:
    print("No Oscilloscope found")

min_freq = 1e2
max_freq = 30e3
frequencies = np.logspace(start=np.log10(min_freq), stop=np.log10(max_freq), num=12)
r = 1.2e3
c = 100e-9
amplitudes = np.absolute(1 / (1 + 2 * np.pi * frequencies * r * c * 1j))

Func.set_function(1, "SIN")  #PULS OR SIN
Func.set_frequency(1, 1)
Func.set_amplitude(1, 1)
Func.set_offset(1, 0)
Func.set_phase(1, 0)
Func.enable_outputs(1, "ON")
Osci.set_horizontal_scale(0.5)
# Osci.setpos(1, 100)
Osci.set_vertical_scale(1, 1)

plot_frequency_response(frequencies, amplitudes)
