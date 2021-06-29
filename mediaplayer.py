# Authored By- Akash Kumar Bhagat
# Github Id - @charlie219
# Email - akashkbhagat221199@gmail.com
# Date - 26-6-2021


from PyQt5.QtWidgets import *
import sys
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtCore import *
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
            self.serverListeningThread()
        
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
        self.openFileBtn = QPushButton('Open Video')
        self.openFileBtn.clicked.connect(self.open_file)
        self.openFileBtn.setStyleSheet('background-color:white;')
        hboxLayout.addWidget(self.openFileBtn)

        # View Box
        vboxLayout = QVBoxLayout()
        vboxLayout.setContentsMargins(10,0,10,20)


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
        self.titleAlignmentLabel1 = QLabel()
        self.titleAlignmentLabel1.setFixedSize(200, 100)
        
        # Banner
        self.titleLabel = QLabel()
        self.titleLabel.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.titleLabel.setText("𝙎𝙮𝙣𝙘 𝙋𝙡𝙖𝙮 - 𝔸 𝕍𝕚𝕕𝕖𝕠 𝕊𝕪𝕟𝕔 𝔸𝕡𝕡𝕝𝕚𝕔𝕒𝕥𝕚𝕠𝕟\n 𝐆𝐫𝐨𝐮𝐩 𝐈𝐃 - " + str(self.group_id))
        self.titleLabel.setStyleSheet('background-color: #000000; color: white;border: 2px solid black;font-size:15pt;')
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.setFixedSize(700, 100)
        
        self.titleAlignmentLabel2 = QLabel()
        self.titleAlignmentLabel2.setFixedSize(200, 100)
    
        header.addWidget(self.titleAlignmentLabel1)
        header.addWidget(self.titleLabel)
        header.addWidget(self.titleAlignmentLabel2)
        vboxLayout.addLayout(header)

        # Media Signals
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

        if not self.isCurrentUserAdmin:
            self.playBtn.setVisible(False)
            self.slider.setVisible(False)
        

        # Show/Hide Group ID button
        self.showGroupIdBtn = QPushButton('Full Screen')
        self.showGroupIdBtn.setStyleSheet('background-color:white;')
        self.showGroupIdBtn.clicked.connect(self.titleLabelHandeler)
        hboxLayout.addWidget(self.showGroupIdBtn)

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

        file_extentions = "Video (*.mp4 *.mkv *.mov *.wmv *.avi *.avcdh *.flv *.f4v *.swf *.webm *.mpeq2 *.mp3)"
        filename, path = QFileDialog.getOpenFileName(self, "Open Video", "", file_extentions)
        self.filename = filename.split('/')[-1]
        print(self.filename)       
        if filename != '':
            self.openFileBtn.setText('Video Loaded')
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            self.playBtn.setEnabled(True)
    
    def titleLabelHandeler(self):

        #print('clicked', self.titleLabel.isVisible())
        if self.titleLabel.isVisible():
            self.showGroupIdBtn.setText('Show Group ID')
            self.titleLabel.setVisible(False)
            self.titleAlignmentLabel2.setVisible(False)
            self.titleAlignmentLabel1.setVisible(False)
        else:
            self.showGroupIdBtn.setText('Full Screen')
            self.titleLabel.setVisible(True)
            self.titleAlignmentLabel2.setVisible(True)
            self.titleAlignmentLabel1.setVisible(True)


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
    def serverListeningThread(self):
            self.recv_thread = ServerListeningThread(self.userSocket)
            self.recv_thread.commandSignal.connect(self.executeAdminCommand)
            self.recv_thread.start()
            self.recv_thread.finished.connect(self.AdminLeftMessage)

    def executeAdminCommand(self, command):
        
        if command['Play'] is not None:
            if command['Play']:
                self.mediaPlayer.play()
            else:
                self.mediaPlayer.pause()
        if command['Slider'] is not None:
            self.mediaPlayer.setPosition(command['Slider'])

    def AdminLeftMessage(self):

        self.mediaPlayer.pause()
        adminLeftMessageBox = QMessageBox()
        adminLeftMessageBox.setWindowTitle("Important")
        adminLeftMessageBox.setText("Admin Left the Group\n Click to continue watching without admin")
        adminLeftMessageBox.setIcon(QMessageBox.Warning)
        adminLeftMessageBox.setStandardButtons(QMessageBox.Ok)
        
        adminLeftMessageBox.exec_()

        # Providing play & slide controls if the admin left
        self.playBtn.setVisible(True)
        self.slider.setVisible(True)
        self.playBtn.setText('Pause')
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.mediaPlayer.play()

    def leave_group(self):

        # Close the Socket
        sys.exit(1)

class ServerListeningThread(QThread):

    commandSignal = pyqtSignal(dict)
    def __init__(self, userSocket):
        super().__init__()
        self.userSocket = userSocket
        self.HEADER = 4

    def run(self):
        while(1):
            try:
                message_header = self.userSocket.recv(self.HEADER)
            except:
                continue
            if not len(message_header):
                break
            
            message_length = int(message_header.decode('utf-8').strip())

            # If the admin has left the group
            if message_length == 5:
                self.userSocket.recv(message_length)
                break
            else:
                command = pickle.loads(self.userSocket.recv(message_length))
                self.commandSignal.emit(command)
                
        

# app = QApplication(sys.argv)
# window = Window(1)
# sys.exit(app.exec_())
