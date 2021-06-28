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
    def __init__(self, userSocket, userInfo):
        super().__init__()
        self.userSocket = userSocket
        self.isCurrentUserAdmin = userInfo['isAdmin']
        self.group_id = userInfo['Group ID']
        self.userName = userInfo['Username']
        self.HEADER = 4

        self.setWindowTitle("::  𝙎𝙮𝙣𝙘 𝙋𝙡𝙖𝙮 - 𝔸 𝕍𝕚𝕕𝕖𝕠 𝕊𝕪𝕟𝕔 𝔸𝕡𝕡𝕝𝕚𝕔𝕒𝕥𝕚𝕠𝕟  ::")
        self.setGeometry(0,0, 1900, 950)
        self.setWindowIcon(QIcon('images/window_icon.png'))
        palette = self.palette()
        palette.setColor(QPalette.Window, Qt.black)
        self.setPalette(palette)

        # if the client is not admin, the start the execution thread
        if not self.isCurrentUserAdmin:
            serverListeningThread = threading.Thread(target = self.execute_command_thread, args = (1,))
            serverListeningThread.start()

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
        
        # Creat (open file) Buttons
        openFileBtn = QPushButton('Open Video')
        openFileBtn.clicked.connect(self.open_file)
        openFileBtn.setStyleSheet('background-color:white;')
        hboxLayout.addWidget(openFileBtn)

        # View Box
        vboxLayout = QVBoxLayout()
        vboxLayout.setContentsMargins(10,0,10,20)

        if self.isCurrentUserAdmin:
        
            # Create play Button
            self.playBtn = QPushButton('Play')
            self.playBtn.setStyleSheet('background-color:white;')
            self.playBtn.setEnabled(False)
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.playBtn.clicked.connect(self.play_video)

            self.slider = QSlider(Qt.Horizontal)
            self.slider.setRange(0,0)
            self.slider.sliderMoved.connect(self.set_position)
            
            # Adding widgets to Horizontal layout
            hboxLayout.addWidget(self.playBtn)
            hboxLayout.addWidget(self.slider,0)

            # Heading Layout for Group Code
            header = QHBoxLayout()
            titleAlignmentLabel1 = QLabel()
            titleAlignmentLabel1.setFixedSize(200, 100)
            
            # Banner
            titleLabel = QLabel()
            titleLabel.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
            titleLabel.setText("𝙎𝙮𝙣𝙘 𝙋𝙡𝙖𝙮 - 𝔸 𝕍𝕚𝕕𝕖𝕠 𝕊𝕪𝕟𝕔 𝔸𝕡𝕡𝕝𝕚𝕔𝕒𝕥𝕚𝕠𝕟\n 𝐆𝐫𝐨𝐮𝐩 𝐈𝐃 - " + str(self.group_id))
            titleLabel.setStyleSheet('background-color: #000000; color: white;border: 2px solid black;font-size:15pt;')
            titleLabel.setAlignment(Qt.AlignCenter)
            titleLabel.setFixedSize(700, 100)
            
            titleAlignmentLabel2 = QLabel()
            titleAlignmentLabel2.setFixedSize(200, 100)
        
            header.addWidget(titleAlignmentLabel1)
            header.addWidget(titleLabel)
            header.addWidget(titleAlignmentLabel2)
            vboxLayout.addLayout(header)

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
            if self.isCurrentUserAdmin:
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

        adminAction ={
            'Play'  :   play,
            'Slider':   slider
        }
        
        msg = pickle.dumps(adminAction)
        msg = bytes(f'{len(msg):<{self.HEADER}}', 'utf-8') + msg
        self.userSocket.send(msg)

    # To execute the command sent from the Admin
    def execute_command_thread(self, flag):

        while(1):
            try:
                message_header = self.userSocket.recv(self.HEADER)
            except:
                continue
            if not len(message_header):
                continue
            if message_header == "":
                sys.exit(0)
            message_length = int(message_header.decode('utf-8').strip())

            command = pickle.loads(self.userSocket.recv(message_length))
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
        sys.exit(1)


# app = QApplication(sys.argv)
# window = Window(1)
# sys.exit(app.exec_())
