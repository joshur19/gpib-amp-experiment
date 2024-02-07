"""
file: main file that creates UI with Qt and defines the logic behind the view elements
author: josh
last updated: 07/02/2024
"""

import amp_interface
import tags
import time

from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtWidgets import(
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGroupBox,
    QMainWindow,
    QGridLayout,
    QLabel,
    QApplication
)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.amp = amp_interface.AmpInterface()

        self.setWindowTitle('RF Amplifier Remote Connection')
        self.setMinimumSize(QSize(350, 300))

        self.build_layout()
        self.connect_layout()
        
    def build_layout(self):
        layout_main = QVBoxLayout()

        ## band switching
        gv_bands = QGroupBox('band switching')
        layout_bands = QVBoxLayout()

        self.bt_band1 = QPushButton('Band 1 - 0-200MHz')
        self.bt_band2 = QPushButton('Band 2 - 200-400MHz')
        self.bt_band3 = QPushButton('Band 3 - 400-1000MHz')
        self.lb_feedback = QLabel('              ')

        layout_bands.addWidget(self.bt_band1)
        layout_bands.addWidget(self.bt_band2)
        layout_bands.addWidget(self.bt_band3)
        layout_bands.addWidget(self.lb_feedback)

        gv_bands.setLayout(layout_bands)
        layout_main.addWidget(gv_bands)

        ## status abfragen
        gv_status = QGroupBox('status')
        layout_status = QGridLayout()

        self.bt_status = QPushButton('Statusabfrage')
        self.lb_status = QLabel('                 ')
        self.lb_interpretation = QLabel('Interpretation Status')
        self.lb_band = QLabel('Aktuelles Band:')
        self.lb_lclrmt = QLabel('Local/Remote:')
        self.lb_flt = QLabel('Fault:')
        self.lb_llo = QLabel('Local Lockout:')
        self.lb_spsmode = QLabel('SPS Mode: ')

        self.lb_band_value = QLabel('')
        self.lb_lclrmt_value = QLabel('')
        self.lb_flt_value = QLabel('')
        self.lb_llo_value = QLabel('')
        self.lb_spsmode_value = QLabel('')

        layout_status.addWidget(self.bt_status, 0, 0, 1, 2)
        layout_status.addWidget(self.lb_status, 1, 0, 1, 2)
        layout_status.addWidget(self.lb_interpretation, 2, 0, 1, 2)
        layout_status.addWidget(self.lb_band, 3, 0)
        layout_status.addWidget(self.lb_band_value, 3, 1)
        layout_status.addWidget(self.lb_lclrmt, 4, 0)
        layout_status.addWidget(self.lb_lclrmt_value, 4, 1)
        layout_status.addWidget(self.lb_flt, 5, 0)
        layout_status.addWidget(self.lb_flt_value, 5, 1)
        layout_status.addWidget(self.lb_llo, 6, 0)
        layout_status.addWidget(self.lb_llo_value, 6, 1)
        layout_status.addWidget(self.lb_spsmode, 7, 0)
        layout_status.addWidget(self.lb_spsmode_value, 7, 1)

        gv_status.setLayout(layout_status)
        layout_main.addWidget(gv_status)

        ## reset flts button
        self.bt_rst = QPushButton('Reset Faults')
        layout_main.addWidget(self.bt_rst)

        ## combine everything
        central_widget = QWidget()
        central_widget.setLayout(layout_main)
        self.setCentralWidget(central_widget)

    def connect_layout(self):
        self.bt_band1.clicked.connect(self.switch_band1)
        self.bt_band2.clicked.connect(self.switch_band2)
        self.bt_band3.clicked.connect(self.switch_band3)
        self.bt_rst.clicked.connect(self.reset_faults)
        self.bt_status.clicked.connect(self.status_button)
    
    def switch_band1(self):
        cmd = 'BAND1'
        conn_error = True
        self.reset_faults()     # vor dem ersten STS Befehl wird ein RST durchgeschickt um den STS Fehler zu vermeiden
        counter = 0     # wie oft der Versuch des Bandwechsels wiederholt werden soll
        status = self.ask_status()      # initiale Statusabfrage

        ## status fehler
        if status == False:
            self.lb_feedback.setText('Error computing status while switching bands')
            QApplication.processEvents()
            QTimer.singleShot(2000, lambda: self.lb_feedback.setText(''))
            return

        ## wenn Band schon gewählt ist das auch so ausgeben
        if status[1] == 'BAND1':
            self.lb_feedback.setText('Already in Band 1')
            QApplication.processEvents()
            QTimer.singleShot(2000, lambda: self.lb_feedback.setText(''))
            return

        ## wenn connection hergestellt werden kann
        if self.amp.connect(tags.sim_addr):

            conn_error = False
            
            self.lb_feedback.setText('Switching to Band 1...')
            QApplication.processEvents()

            while status[1] != 'BAND1' and conn_error == False:
                
                if(counter >= 6):   # hier Abbruchbedingung Anzahl an Wiederholungen setzen
                    conn_error = True

                self.amp.write_command(cmd)
                time.sleep(2)
                status = self.ask_status_conn()     # Statusabfrage ohne wiederholte connection

                if(status == False):
                    conn_error = True

                counter = counter+1

            self.amp.disconnect()

        ## keine connection zum Gerät
        else:
            self.lb_status.setText('Error: check GPIB connection')
            QTimer.singleShot(2000, lambda: self.lb_status.setText(''))

        ## wenn maximale Versuche oder Statusantwort illegal dann conn_error = True
        if conn_error:
            self.lb_feedback.setText('Error setting Band 1')
            QTimer.singleShot(3000, lambda: self.lb_feedback.setText(''))
        
        else:   # erfolgreicher Bandwechsel

            # SPS auf OPR Modus bringen
            if self.amp.connect(tags.sps_addr):
                try:
                    self.amp.write_command('STBY')
                    time.sleep(1)
                    self.amp.write_command('OPER')      ## todo: gucken ob das auch erfolgreich war
                except:
                    print(tags.main_tag + 'Error setting SPS to OPR-Mode')
                    self.lb_spsmode_value.setText('ERR')
                self.amp.disconnect()

            self.lb_feedback.setText('Switched to Band 1')
            QApplication.processEvents()
            self.display_status(status)
            self.lb_spsmode_value.setText('OPR')
            QTimer.singleShot(4000, lambda: self.lb_feedback.setText(''))

    def switch_band2(self):     
        cmd = 'BAND2'
        conn_error = True
        self.reset_faults()
        counter = 0     # wie oft der Versuch des Bandwechsels wiederholt werden soll
        status = self.ask_status()

        ## status fehler
        if status == False:
            self.lb_feedback.setText('Error computing status while switching bands')
            QApplication.processEvents()
            QTimer.singleShot(2000, lambda: self.lb_feedback.setText(''))
            return

        ## wenn Band schon gewählt ist das auch so ausgeben
        if status[1] == 'BAND2':
            self.lb_feedback.setText('Already in Band 2')
            QApplication.processEvents()
            QTimer.singleShot(2000, lambda: self.lb_feedback.setText(''))
            return

        ## wenn connection hergestellt werden kann
        if self.amp.connect(tags.sim_addr):

            conn_error = False
            
            self.lb_feedback.setText('Switching to Band 2...')
            QApplication.processEvents()

            while status[1] != 'BAND2' and conn_error == False:
                
                if(counter >= 6):
                    conn_error = True

                self.amp.write_command(cmd)
                time.sleep(2)
                status = self.ask_status_conn()

                if(status == False):
                    conn_error = True

                counter = counter+1

            self.lb_spsmode_value.setText('STBY')   # sobald der SPS BAND command erkennt wechselt er

            self.amp.disconnect()

        ## keine connection zum Gerät
        else:
            self.lb_status.setText('Error: check GPIB connection')
            QTimer.singleShot(2000, lambda: self.lb_status.setText(''))

        ## wenn maximale Versuche oder Statusantwort illegal dann conn_error = True
        if conn_error:
            self.lb_feedback.setText('Error setting Band 2')
            QTimer.singleShot(3000, lambda: self.lb_feedback.setText(''))
        else:   # erfolgreicher Bandwechsel
            self.lb_feedback.setText('Switched to Band 2')
            QApplication.processEvents()
            self.display_status(status)
            QTimer.singleShot(4000, lambda: self.lb_feedback.setText(''))

    def switch_band3(self):
        cmd = 'BAND3'
        conn_error = True
        self.reset_faults()
        counter = 0     # wie oft der Versuch des Bandwechsels wiederholt werden soll
        status = self.ask_status()

        ## status fehler
        if status == False:
            self.lb_feedback.setText('Error computing status while switching bands')
            QApplication.processEvents()
            QTimer.singleShot(2000, lambda: self.lb_feedback.setText(''))
            return

        ## wenn Band schon gewählt ist das auch so ausgeben
        if status[1] == 'BAND3':
            self.lb_feedback.setText('Already in Band 3')
            QApplication.processEvents()
            QTimer.singleShot(2000, lambda: self.lb_feedback.setText(''))
            return

        ## wenn connection hergestellt werden kann
        if self.amp.connect(tags.sim_addr):

            conn_error = False
            
            self.lb_feedback.setText('Switching to Band 3...')
            QApplication.processEvents()

            while status[1] != 'BAND3' and conn_error == False:
                
                if(counter >= 6):
                    conn_error = True

                self.amp.write_command(cmd)
                time.sleep(2)
                status = self.ask_status_conn()

                if(status == False):
                    conn_error = True

                counter = counter+1

            self.lb_spsmode_value.setText('STBY')   # sobald der SPS BAND command erkennt wechselt er

            self.amp.disconnect()

        ## keine connection zum Gerät
        else:
            self.lb_status.setText('Error: check GPIB connection')
            QTimer.singleShot(2000, lambda: self.lb_status.setText(''))

        ## wenn maximale Versuche oder Statusantwort illegal dann conn_error = True
        if conn_error:
            self.lb_feedback.setText('Error setting Band 3')
            QTimer.singleShot(3000, lambda: self.lb_feedback.setText(''))
        else:   # erfolgreicher Bandwechsel
            self.lb_feedback.setText('Switched to Band 3')
            QApplication.processEvents()
            self.display_status(status)
            QTimer.singleShot(4000, lambda: self.lb_feedback.setText(''))

    def reset_faults(self):
        cmd = 'RST'
        if self.amp.connect(tags.sim_addr):
            self.amp.write_command(cmd)
            self.amp.disconnect()
        else:
            print(tags.main_tag + 'Error connecting to AMP.')
        
    def status_button(self):
        status = self.ask_status()
        if status != False:
            self.display_status(status)
        else:
            self.lb_status.setText('Error setting status')
            QTimer.singleShot(2000, lambda: self.lb_status.setText(''))

    def ask_status_conn(self):
        cmd = 'STS'
        try:
            raw_status = self.amp.query_command(cmd)
            status = self.parse_status(raw_status)
            return status
        except:
            print(tags.main_tag + 'Error in STS call')
            return False

    def ask_status(self):
        cmd = 'STS'
        if self.amp.connect(tags.sim_addr):
            try:
                raw_status = self.amp.query_command(cmd)
                status = self.parse_status(raw_status)
                self.amp.disconnect()
                return status
            except:
                print(tags.main_tag + 'Error in STS call')
                self.amp.disconnect()
                return False
        else:
            self.lb_status.setText('Error: check GPIB connection')
            QTimer.singleShot(2000, lambda: self.lb_status.setText(''))
            return False

    def parse_status(self, raw_result):

        ## get relevant information from raw status response
        decoded_status = raw_result.decode('ascii')
        cleaned_status = decoded_status.split('\n')
        cleaned_status = [elem.strip('\r') for elem in cleaned_status]

        filtered_status = []
        for elem in cleaned_status:
            try:
                int_elem = int(elem)
                filtered_status.append(int_elem)
            except ValueError:
                continue

        total_sum = sum(filtered_status)
        num_elem = len(filtered_status)

        status_decimal = total_sum // num_elem

        print(tags.main_tag + f'Dezimalantwort: {status_decimal}')

        status_binary = f'{status_decimal:08b}'

        ## parse information from binary number
        if status_binary[3] == '0' and status_binary[4] == '0':
            band = 'BAND1'
        elif status_binary[3] == '0' and status_binary[4] == '1':
            band = 'BAND2'
        elif status_binary[3] == '1' and status_binary[4] == '0':
            band = 'BAND3'

        lcl_rem = 'LOCAL' if status_binary[5] == '0' else 'REMOTE'
        flt = 'FAULT' if status_binary[6] == '1' else 'NO FAULT'
        llo = 'LOCKOUT' if status_binary[7] == '1' else 'NO LOCKOUT'

        return [status_binary, band, lcl_rem, flt, llo]     ## todo: als map überarbeiten für bessere übersicht beim Zugriff
          
    def display_status(self, status):
        self.lb_status.setText('Statusantwort: ' + status[0])
        self.lb_band_value.setText(status[1])
        self.lb_lclrmt_value.setText(status[2])
        self.lb_flt_value.setText(status[3])
        self.lb_llo_value.setText(status[4])


    
if __name__ == "__main__":
    
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()