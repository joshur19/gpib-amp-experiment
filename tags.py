"""
file: tags (setup) file for log styling and storing device address
author: josh
last updated: 30/01/2024
"""

import datetime

sim_addr = 'GPIB0::3::INSTR'
sps_addr = 'GPIB0::7::INSTR'
amp_tag = f"{datetime.datetime.now().strftime("%H:%M:%S")} -- LOG -- AMP: "
main_tag = f'{datetime.datetime.now().strftime("%H:%M:%S")} -- LOG -- main: '