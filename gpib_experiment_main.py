"""

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

        self.setWindowTitle('Amp Connection Test')
        self.setMinimumSize(QSize(300, 300))

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

        # New labels
        self.lb_band_value = QLabel('')
        self.lb_lclrmt_value = QLabel('')
        self.lb_flt_value = QLabel('')
        self.lb_llo_value = QLabel('')

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
        status = self.ask_status()
        conn_error = False
        counter = 0

        while status[1] != 'BAND1':

            if self.amp.connect(tags.sim_addr):
                self.amp.write_command(cmd)
                self.amp.disconnect()
            else:
                conn_error = True
                break

            if(counter >= 5):
                conn_error = True
                break

            time.sleep(3)

            status = self.ask_status()

        if conn_error:
            self.lb_feedback.setText('Error setting Band 1')
            QTimer.singleShot(3000, lambda: self.lb_feedback.setText(''))
        else:
            self.lb_feedback.setText('Switched to Band 1')
            QTimer.singleShot(4000, lambda: self.lb_feedback.setText(''))

    def switch_band2(self):     ## todo: error handling einbauen wenn Konzept wie bei Band1 funktioniert
        cmd = 'BAND2'
        if self.amp.connect(tags.sim_addr):
            self.amp.write_command(cmd)
            self.amp.disconnect()
            self.lb_feedback.setText('Switched to Band 2')
            QTimer.singleShot(4000, lambda: self.lb_feedback.setText(''))
        else:
            self.lb_feedback.setText('Error: check GPIB connection')
            QTimer.singleShot(2000, lambda: self.lb_feedback.setText(''))

    def switch_band3(self):     ## todo: error handling einbauen wenn Konzept wie bei Band1 funktioniert
        cmd = 'BAND3'
        if self.amp.connect(tags.sim_addr):
            self.amp.write_command(cmd)
            self.amp.disconnect() 
            self.lb_feedback.setText('Switched to Band 3')
            QTimer.singleShot(4000, lambda: self.lb_feedback.setText(''))
        else:
            self.lb_feedback.setText('Error: check GPIB connection')
            QTimer.singleShot(2000, lambda: self.lb_feedback.setText(''))

    def reset_faults(self):
        cmd = 'RST'
        if self.amp.connect(tags.sim_addr):
            self.amp.write_command(cmd)
            self.amp.disconnect()
        else:
            return False        ## todo: kleinen Log-Eintrag schreiben
        
    def status_button(self):
        status = self.ask_status()
        self.display_status(status)

    def ask_status(self):
        cmd = 'STS'
        if self.amp.connect(tags.sim_addr):
            raw_status = self.amp.query_command(cmd)
            self.amp.disconnect()
            status = self.parse_status(raw_status)
            return status
        else:
            self.lb_status.setText('Error: check GPIB connection')
            QTimer.singleShot(2000, lambda: self.lb_status.setText(''))

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