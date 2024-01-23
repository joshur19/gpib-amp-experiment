"""

"""

import amp_interface
import tags

from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtWidgets import(
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGroupBox,
    QMainWindow,
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
        layout_status = QVBoxLayout()

        self.bt_status = QPushButton('Statusabfrage')
        self.lb_status = QLabel('                 ')
        self.lb_interpretation = QLabel('Interpretation Status')
        self.lb_band = QLabel('Aktuelles Band:')
        self.lb_lclrmt = QLabel('Local/Remote:')
        self.lb_flt = QLabel('Fault:')
        self.lb_llo = QLabel('Local Lockout:')

        layout_status.addWidget(self.bt_status)
        layout_status.addWidget(self.lb_status)
        layout_status.addWidget(self.lb_interpretation)
        layout_status.addWidget(self.lb_band)
        layout_status.addWidget(self.lb_lclrmt)
        layout_status.addWidget(self.lb_flt)
        layout_status.addWidget(self.lb_llo)

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
        self.bt_status.clicked.connect(self.ask_status)
    
    def switch_band1(self):
        cmd = 'BAND1'
        if self.amp.connect(tags.sim_addr):
            self.amp.write_command(cmd)
            self.amp.disconnect() 
            self.lb_feedback.setText('Switched to Band 1')
            QTimer.singleShot(4000, lambda: self.lb_feedback.setText(''))
        else:
            self.lb_feedback.setText('Error: check GPIB connection')
            QTimer.singleShot(2000, lambda: self.lb_feedback.setText(''))

    def switch_band2(self):
        cmd = 'BAND2'
        if self.amp.connect(tags.sim_addr):
            self.amp.write_command(cmd)
            self.amp.disconnect()
            self.lb_feedback.setText('Switched to Band 2')
            QTimer.singleShot(4000, lambda: self.lb_feedback.setText(''))
        else:
            self.lb_feedback.setText('Error: check GPIB connection')
            QTimer.singleShot(2000, lambda: self.lb_feedback.setText(''))

    def switch_band3(self):
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
            return False        ## todo 

    def ask_status(self):
        cmd = 'STS'
        if self.amp.connect(tags.sim_addr):
            status = self.amp.query_command(cmd)
            self.amp.disconnect()
            #self.lb_status.setText('Statusantwort: ' + status)
        else:
            self.lb_status.setText('Error: check GPIB connection')
            QTimer.singleShot(2000, lambda: self.lb_status.setText(''))
    
if __name__ == "__main__":
    
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()