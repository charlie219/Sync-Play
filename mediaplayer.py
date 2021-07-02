# Authored By- Akash Kumar Bhagat
# Github Id - @charlie219
# Email - akashkbhagat221199@gmail.com
# Date - 26-6-2021


from PyQt5.QtWidgets import *
import sys
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QPalette, QFont
from PyQt5.QtCore import *
import socket, pickle, threading, time


class Window(QWidget):
    def __init__(self, userSocket, userInfo):
        super().__init__()
        self.userSocket = userSocket
        self.isCurrentUserAdmin = userInfo['isAdmin']
        self.group_id = userInfo['Group ID']
        self.userName = userInfo['Username']
        self.filename = userInfo['Movie']
        self.groupMembers = []
        self.groupAdmin = userInfo['Group Admin']
        self.isAdminPlaying = False

        self.connection = True
        self.HEADER = 4

        self.setWindowTitle("::  𝙎𝙮𝙣𝙘 𝙋𝙡𝙖𝙮 -  𝔸 𝕍𝕚𝕕𝕖𝕠 𝕊𝕪𝕟𝕔 𝔸𝕡𝕡𝕝𝕚𝕔𝕒𝕥𝕚𝕠𝕟  ::")
        self.setGeometry(0,0, 1900, 950)
        self.setWindowIcon(QIcon('images/window_icon.png'))
        palette = self.palette()
        palette.setColor(QPalette.Window, Qt.black)
        self.setPalette(palette)

        self.ui()
        self.show()

        # If the file name is not chosen by the Admin, we'll disable openfileBtn 
        # if the client is not admin, the start the execution thread
        if not self.isCurrentUserAdmin:
            self.MemberInfoLabel.setVisible(False)
            self.MemberInfoTitleLabel.setVisible(False)
            if self.filename is None:
                self.openFileBtn.setEnabled(False)
            
            # If Admin has already Started the movie
            else:
                self.isAdminPlaying = True
                self.openFileButtonReady()
        self.serverListeningThread()

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

        #  Container Vertical box to store the videoVbox and sideVbox
        containerHBox = QHBoxLayout()

        # VideoWidget Horizontal box layout 
        videoVBox = QVBoxLayout()
        videoVBox.addWidget(videowidget, stretch = 3)


        # SideInfoLayout which will contain the group info
        sideVBoxLayout = QVBoxLayout()


        # Group Info Lable
        self.groupInfoLabel = QLabel()
        self.setGroupInfoLabel()
        sideVBoxLayout.addWidget(self.groupInfoLabel, stretch = 1)
        

        # Member Info for the Admin
        self.MemberInfoTitleLabel = QLabel("---- 𝙈𝙚𝙢𝙗𝙚𝙧 𝙇𝙞𝙨𝙩 ----")
        self.MemberInfoTitleLabel.setStyleSheet('color: white; font-size:15pt')
        sideVBoxLayout.addWidget(self.MemberInfoTitleLabel)
        
        self.MemberInfoLabel = QLabel()
        self.setMemberInfoLabel()
        sideVBoxLayout.addWidget(self.MemberInfoLabel, stretch = 5)
        containerHBox.addLayout(videoVBox, stretch = 1)
        containerHBox.addLayout(sideVBoxLayout)
        


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
        self.titleLabel.setText("𝙎𝙮𝙣𝙘 𝙋𝙡𝙖𝙮 \n 𝔸 𝕍𝕚𝕕𝕖𝕠 𝕊𝕪𝕟𝕔 𝔸𝕡𝕡𝕝𝕚𝕔𝕒𝕥𝕚𝕠𝕟")
        self.titleLabel.setStyleSheet('background-color: #000000; color: white;border: 2px solid black;font-size:18pt;')
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

        # Restricting Play and Slider for the Admin
        if not self.isCurrentUserAdmin:
            self.playBtn.setVisible(False)
            self.slider.setVisible(False)

        # Show/Hide Group ID button
        self.showGroupIdBtn = QPushButton('Full Screen')
        self.showGroupIdBtn.setStyleSheet('background-color:white;')
        self.showGroupIdBtn.clicked.connect(self.groupInfoHandeler)
        hboxLayout.addWidget(self.showGroupIdBtn)

        # Create Leave Button
        self.leaveBtn = QPushButton('Leave Group')
        self.leaveBtn.setStyleSheet('background-color:red; color : white')
        self.leaveBtn.clicked.connect(self.leave_group)
        hboxLayout.addWidget(self.leaveBtn)


        # Create viewbox layout
        vboxLayout.addLayout(containerHBox)
        vboxLayout.addLayout(hboxLayout)

        self.setLayout(vboxLayout)

        # Setting the videowidget to mediaplayer obj
        self.mediaPlayer.setVideoOutput(videowidget)

    def setMemberInfoLabel(self):
        memberStr = "\n"
        memberStr+= self.userName + "           (𝘈𝘥𝘮𝘪𝘯)"

        for member in self.groupMembers:
            memberStr += "\n" + member

        self.MemberInfoLabel.setText(memberStr)
        self.MemberInfoLabel.setAlignment(Qt.AlignLeft)
        self.MemberInfoLabel.setStyleSheet('color: white; padding-top : 1px;')
        self.MemberInfoLabel.setFont(QFont("Sanserif",14))

    def setGroupInfoLabel(self):
        if self.group_id:
            self.groupInfoLabel.setText(" 𝔾𝕣𝕠𝕦𝕡 𝕀𝔻 :- " + str(self.group_id) + " \n𝔸𝕕𝕞𝕚𝕟 :- " + self.groupAdmin)
        else:
            self.groupInfoLabel.setText(" 𝔾𝕣𝕠𝕦𝕡 𝕀𝔻 :- 𝒩𝑜𝓃𝑒\n𝔸𝕕𝕞𝕚𝕟 :- 𝒩𝑜𝓃𝑒 ")

        self.groupInfoLabel.setAlignment(Qt.AlignCenter)
        self.groupInfoLabel.setFont(QFont("Sanserif", 15))
        self.groupInfoLabel.setStyleSheet('background-color: black; color: white;border :3px solid blue;border-radius: 20px')

    def open_file(self):

        file_extentions = "Video (*.mp4 *.mkv *.mov *.wmv *.avi *.avcdh *.flv *.f4v *.swf *.webm *.mpeq2 *.mp3)"
        filename, path = QFileDialog.getOpenFileName(self, "Open Video", "", file_extentions)

        # If no File is Choosen
        if filename == "":
            return 
        # If the user is not admin and the chosen file is incorrect
        if not self.isCurrentUserAdmin and filename.split('/')[-1] != self.filename:
            self.incorrectFileNameMessageBox()
            
        else:
            self.openFileBtn.setText('Video Loaded')
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))

            # Ask the current status of the Admin
            self.send_message()

            self.playBtn.setEnabled(True)
            self.playBtn.setText('Play')
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

            if self.isCurrentUserAdmin:
                self.send_message(filename = filename.split('/')[-1])
    
    def sendUpdateToNewMember(self):
    
        # Send update about the Admins position play/pause and slider position to keep the members updated
        self.send_message(play = int(self.playBtn.text() == 'Pause'), slider = self.slider.sliderPosition())
            
    def groupInfoHandeler(self):

        if self.titleLabel.isVisible():
            self.showGroupIdBtn.setText('Show Group Info')
            self.titleLabel.setVisible(False)
            self.titleAlignmentLabel2.setVisible(False)
            self.titleAlignmentLabel1.setVisible(False)
            self.MemberInfoLabel.setVisible(False)
            self.MemberInfoTitleLabel.setVisible(False)
            self.groupInfoLabel.setVisible(False)
            
        else:
            self.showGroupIdBtn.setText('Full Screen')
            self.titleLabel.setVisible(True)
            self.titleAlignmentLabel2.setVisible(True)
            self.titleAlignmentLabel1.setVisible(True)
            self.groupInfoLabel.setVisible(True)
            if self.isCurrentUserAdmin:
                self.MemberInfoLabel.setVisible(True)
                self.MemberInfoTitleLabel.setVisible(True)


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

    # Message box to show incorrect filename message:
    def incorrectFileNameMessageBox(self):
        incorrectFileMessageBox = QMessageBox()
        incorrectFileMessageBox.setWindowTitle("Important")
        incorrectFileMessageBox.setText("Selected File is Incorrect\n Contact to the Admin for the Movie")
        incorrectFileMessageBox.setIcon(QMessageBox.Warning)
        incorrectFileMessageBox.setStandardButtons(QMessageBox.Ok)
        
        incorrectFileMessageBox.exec_()

    # To send the commmands to the server
    def send_message(self, play = None, slider = None, filename = None):

        adminAction ={
            'Play'  :   play,
            'Slider':   slider,
            'Movie' :   filename
        }
        
        msg = pickle.dumps(adminAction)
        msg = bytes(f'{len(msg):<{self.HEADER}}', 'utf-8') + msg
        self.userSocket.send(msg)

    # To execute the command sent from the Admin
    def serverListeningThread(self):
        self.recv_thread = ServerListeningThread(self.userSocket)
        self.recv_thread.inboundSignal.connect(self.diffrentiateMessage)
        self.recv_thread.start()
        self.recv_thread.finished.connect(self.AdminLeftMessage)

    # To distinguish between an UpdateMemberMessage(from Server to Admin)
    # or executeAdminCommand messahe (from Server to other members)
    def diffrentiateMessage(self, message):
        if self.isCurrentUserAdmin:
            if 'New Member' in message:
                self.sendUpdateToNewMember()
                if message['New Member'] != "":
                    self.groupMembers.append(message['New Member'])
            else:
                self.groupMembers.remove(message['Delete Member'])
            #print(self.groupMembers)
            self.setMemberInfoLabel()
        else:
            self.executeAdminCommand(message)
        
    def executeAdminCommand(self, command):
        
        if command['Play'] is not None:
            if command['Play']:
                self.mediaPlayer.play()
            else:
                self.mediaPlayer.pause()
        if command['Slider'] is not None:
            self.mediaPlayer.setPosition(command['Slider'])
        
        if command['Movie'] is not None:
            self.filename = command['Movie']

            # if Another movie is selected, then we will stop the previous video
            # set the mediaPlayer.setPosition to 0
            self.mediaPlayer.pause()
            self.mediaPlayer.setPosition(0)


            # MessageBox 
            self.openFileButtonReady()
            self.openFileBtn.setEnabled(True)

    
    # Message Box to notify that admin has selected the movie and open file button is ready
    def openFileButtonReady(self):
            openFileButtonReadyMessageBox = QMessageBox()
            openFileButtonReadyMessageBox.setWindowTitle("Important")
            openFileButtonReadyMessageBox.setText("Admin has Selected the movie\n Movie: -" + self.filename)
            openFileButtonReadyMessageBox.setIcon(QMessageBox.Information)
            openFileButtonReadyMessageBox.setStandardButtons(QMessageBox.Ok)
            openFileButtonReadyMessageBox.exec_()

            self.open_file()    

    def AdminLeftMessage(self):

        self.mediaPlayer.pause()
        adminLeftMessageBox = QMessageBox()
        adminLeftMessageBox.setWindowTitle("Important")
        adminLeftMessageBox.setText("Admin Left the Group\n Click to continue watching without admin")
        adminLeftMessageBox.setIcon(QMessageBox.Warning)
        adminLeftMessageBox.setStandardButtons(QMessageBox.Ok)
        
        adminLeftMessageBox.exec_()

        # Change the Group Info Label
        self.group_id = None
        self.groupAdmin = None
        self.setGroupInfoLabel()

        # Providing play & slide controls if the admin left
        self.playBtn.setVisible(True)
        self.slider.setVisible(True)
        self.playBtn.setText('Pause')
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.openFileBtn.setEnabled(True)
        self.mediaPlayer.play()

    def leave_group(self):

        # Close the Socket
        self.connection = False
        sys.exit(1)

class ServerListeningThread(QThread):

    # Signal from server
    inboundSignal = pyqtSignal(dict)
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
                self.inboundSignal.emit(command)
                                    


# app = QApplication(sys.argv)
# window = Window(1)
# sys.exit(app.exec_())
