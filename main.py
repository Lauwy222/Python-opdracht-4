import pyvisa


class Instrument:
    def __init__(self, pyvisa_instrument=None):
        self.instrument = pyvisa_instrument

    def send_write(self, cmd):
        self.instrument.write(cmd)

    def send_query(self, cmd):
        return self.instrument.query(cmd)


class FunctionGenerator(Instrument):
    def set_function(self, channel, value):
        self.instrument.write(":SOUR{}:FUNC {}".format(channel, value))
        pass
    def set_frequency(self, channel, value):
        self.instrument.write(":SOUR{}:FREQ {}".format(channel, value))
        pass
    def set_offset(self, channel, value):
        self.instrument.write(":SOUR{}:VOLT:OFFS {}".format(channel, value))
        pass

    def set_phase(self, channel, value):
        self.instrument.write(":SOUR{}:PHAS {}".format(channel, value))
        pass

    def set_amplitude(self, channel, value):
        self.instrument.write(":SOUR{}:VOLT {}".format(channel, value))
        pass

    def enable_outputs(self, channel, state):
        self.instrument.write(":OUTP{} {}".format(channel,state))
        pass


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
if fg_found:
    print("Found DG1032Z")
else:
    print("No function generator found")
if scope_found:
    print("Found MSO1074")
else:
    print("No Oscilloscope found")

Func.set_function(1,"SIN") #PULS OR SIN
Func.set_frequency(1, 69)
Func.set_amplitude(1, 3)
Func.set_offset(1, 3)
Func.set_phase(1, 0)
Func.enable_outputs(1, "ON")
