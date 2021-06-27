from PyQt5.QtWidgets import *
import sys
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtCore import Qt, QRect, QUrl
import socket
import pickle
import threading


class Window(QWidget):
    def __init__(self, sock, client_info):
        super().__init__()
        self.sock = sock
        self.isAdmin = client_info['isAdmin']
        self.group_id = client_info['Group ID']
        self.uname = client_info['Username']
        self.HEADER = 4

        self.setWindowTitle("::  𝙎𝙮𝙣𝙘 𝙋𝙡𝙖𝙮 - 𝔸 𝕍𝕚𝕕𝕖𝕠 𝕊𝕪𝕟𝕔 𝔸𝕡𝕡𝕝𝕚𝕔𝕒𝕥𝕚𝕠𝕟  ::")
        self.setGeometry(0,0, 1900, 950)
        self.setWindowIcon(QIcon('images/window_icon.png'))
        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)

        # if the client is not admin, the start the execution thread
        if not self.isAdmin:
            command_thread = threading.Thread(target = self.execute_command_thread, args = (1,))
            command_thread.start()

        self.ui()
        self.show()


    def ui(self):

        # Create MediaPlayer object to play video content 
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # Create Horizontal box layout
        hboxLayout = QHBoxLayout()
        hboxLayout.setContentsMargins(0, 0, 0, 0)
        
        # Creat video Widget object
        videowidget = QVideoWidget()
        

        # Creat open the file Buttons
        openBtn = QPushButton('Open Video')
        openBtn.clicked.connect(self.open_file)
        openBtn.setStyleSheet('background-color:white;')
        hboxLayout.addWidget(openBtn)

        # View Box
        vboxLayout = QVBoxLayout()
        vboxLayout.setContentsMargins(10,0,10,20)

        if self.isAdmin:
        
            # Create play Button
            self.playBtn = QPushButton('Play')
            self.playBtn.setStyleSheet('background-color:white;')
            self.playBtn.setEnabled(False)
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.playBtn.clicked.connect(self.play_video)

            # Create Slider for the 
            self.slider = QSlider(Qt.Horizontal)
            self.slider.setRange(0,0)
            self.slider.sliderMoved.connect(self.set_position)
            
            # Adding widgets to Horizontal layout
            hboxLayout.addWidget(self.playBtn)
            hboxLayout.addWidget(self.slider,0)

            # Heading Layout for Group Code
            head = QHBoxLayout()
            align_label = QLabel()
            align_label.setFixedSize(200, 100)
            
            # Banner
            topLabel = QLabel()
            topLabel.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
            topLabel.setText("𝙎𝙮𝙣𝙘 𝙋𝙡𝙖𝙮 - 𝔸 𝕍𝕚𝕕𝕖𝕠 𝕊𝕪𝕟𝕔 𝔸𝕡𝕡𝕝𝕚𝕔𝕒𝕥𝕚𝕠𝕟\n 𝐆𝐫𝐨𝐮𝐩 𝐈𝐃 - " + str(self.group_id))
            topLabel.setStyleSheet('background-color: #000000; color: white;border: 2px solid black;font-size:15pt;')
            topLabel.setAlignment(Qt.AlignCenter)
            topLabel.setFixedSize(700, 100)
            
            align_label2 = QLabel()
            align_label2.setFixedSize(200, 100)
        
            head.addWidget(align_label)
            head.addWidget(topLabel)
            head.addWidget(align_label2)
            vboxLayout.addLayout(head)

            # Media Signals
            self.mediaPlayer.positionChanged.connect(self.position_changed)
            self.mediaPlayer.durationChanged.connect(self.duration_changed)


        # Create Leave Button
        self.leaveBtn = QPushButton('Leave Group')
        self.leaveBtn.setStyleSheet('background-color:red; color : white')
        self.leaveBtn.clicked.connect(self.leave_group)
        hboxLayout.addWidget(self.leaveBtn)

        # Create viewbox layout
        vboxLayout.addWidget(videowidget)
        vboxLayout.addLayout(hboxLayout)

        self.setLayout(vboxLayout)

        # Setting the videowidget to mediaplayer obj
        self.mediaPlayer.setVideoOutput(videowidget)
            

    def open_file(self):

        filename, path = QFileDialog.getOpenFileName(self, "Open Video")         
        if filename != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            if self.isAdmin:
                self.playBtn.setEnabled(True)

    def position_changed(self, position):
        self.slider.setValue(position)
 
    def duration_changed(self, duration):
        self.slider.setRange(0, duration)
 
 
    def set_position(self, position):
        self.mediaPlayer.setPosition(position)
        self.send_message(slider = position)

    def play_video(self):
        
        # If the media player is already playing, we will make it pause
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playBtn.setText('Play')
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.mediaPlayer.pause()
            self.send_message(play = 0)
        
        # If it is not playing/ paused, we will play the mediaplayer
        else:
            self.playBtn.setText('Pause')
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.mediaPlayer.play()
            self.send_message(play = 1)

    # To send the commmands to the server
    def send_message(self, play = None, slider = None):

        command_payload ={
            'Play'  :   play,
            'Slider':   slider
        }
        
        msg = pickle.dumps(command_payload)
        msg = bytes(f'{len(msg):<{self.HEADER}}', 'utf-8') + msg
        self.sock.send(msg)

    # To execute the command sent from the Admin
    def execute_command_thread(self, flag):

        while(1):
            message_header = self.sock.recv(self.HEADER)
            if not len(message_header):
                continue
            message_length = int(message_header.decode('utf-8').strip())

            command = pickle.loads(self.sock.recv(message_length))
            if command['Play'] is not None:
                if command['Play']:
                    self.mediaPlayer.play()
                else:
                    self.mediaPlayer.pause()
            if command['Slider'] is not None:
                self.mediaPlayer.setPosition(command['Slider'])
            
            # Continnue the thread
    
    def leave_group(self):
        
        # Close the Socket
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        sys.exit(1)


# app = QApplication(sys.argv)
# window = Window(1)
# sys.exit(app.exec_())
