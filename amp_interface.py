"""

"""

import pyvisa
import tags

class AmpInterface:
    def __init__(self):
        print(tags.amp_tag + 'Instance of interface created.')
        self.rm = pyvisa.ResourceManager()
        self.instr = None

    def connect(self, visa_resourcename):
        try:
            self.instr = self.rm.open_resource(visa_resourcename)
            self.instr.write_termination = '\r\n'
            self.instr.read_termination = '\r\n'
            print(tags.amp_tag + 'Succesfully connected to AMP.')
            return True
        except:
            print(tags.amp_tag + 'Error connecting to AMP.')
            return False
        
    def disconnect(self):
        self.instr.close()
        print(tags.amp_tag + 'Connection with AMP closed.')

    def write_command(self, command):
        print(tags.amp_tag + 'Command sent to AMP: ' + command)
        return self.instr.write(command)
    
    def query_command(self, command):
        print(tags.amp_tag + 'Command sent to AMP: ' + command)
        self.instr.write(command)
        result = self.instr.read_bytes(1024)
        print(tags.amp_tag + 'Answer from device: ' + len(result) + ' byte long answer')
        print(result)
        return result