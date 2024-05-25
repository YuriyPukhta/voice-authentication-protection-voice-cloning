import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen, QPixmap, QBitmap, QCursor,  QLinearGradient
from PyQt5.QtCore import Qt, QRect, QPoint
import sounddevice as sd
import soundfile as sf


class RoundButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(100, 40)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRect(0, 0, self.width(), self.height())

        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0.0, QColor("#ffffff"))
        gradient.setColorAt(1.0, QColor("#d3d3d3"))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(rect)

        font_metrics = painter.fontMetrics()
        text_rect = font_metrics.boundingRect(self.text())
        text_rect.moveCenter(rect.center())
        painter.setPen(Qt.black)
        painter.drawText(text_rect, Qt.AlignCenter, self.text())


class RecorderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Recorder")
        self.setGeometry(100, 100, 300, 100)

        self.record_button = RoundButton('Record', self)
        self.record_button.setGeometry(100, 30, 100, 40)
        self.record_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.record_button.setStyleSheet("background-color: #ffffff; color: #000000;")

        self.recording = False

    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.recording = True
        self.record_button.setText('Stop Recording')
        self.record_audio()

    def stop_recording(self):
        self.recording = False
        self.record_button.setText('Record')

    def record_audio(self):
        duration = 10  # record for 10 seconds (you can adjust this)
        fs = 44100  # sample rate
        try:
            with sf.SoundFile('output.wav', mode='x', samplerate=fs, channels=2) as file:
                print("Recording...")
                data = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='float32')
                sd.wait()
                file.write(data)
                print("Recording finished")
        except Exception as e:
            print("Error:", e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RecorderApp()
    window.show()
    sys.exit(app.exec_())