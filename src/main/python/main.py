import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from fbs_runtime.application_context.PyQt5 import ApplicationContext

from PIL import Image, ImageFilter, ImageDraw
import numpy as np
import threading
import os
import face_recognition

import numpy.random.common
import numpy.random.bounded_integers
import numpy.random.entropy


lst = []
fastProcessing = True
blurness = 6
fastProcessingTemp = True
blurnessTemp = 6


# Drag and Drop Area
class Button(QPushButton):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.setAcceptDrops(True)
        self.setIcon(QIcon(imgIcon))
        self.setIconSize(QSize(67,34))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setStyleSheet('border: 2px dashed rgba(255,255,255,40); background-color: rgb(40,39,38); border-radius: 8px')


    def dragEnterEvent(self, e):
        m = e.mimeData()
        if m.hasUrls():
            self.setStyleSheet('border: 2px dashed rgba(255,255,255,40); background-color: rgb(52,50,49); border-radius: 8px')
            e.accept()
        else:
            e.ignore()

    def dragLeaveEvent(self, e):
        self.setStyleSheet('border: 2px dashed rgba(255,255,255,40); background-color: rgb(40,39,38); border-radius: 8px')


    def dropEvent(self, e):
        m = e.mimeData()
        self.setStyleSheet('border: 2px dashed rgba(255,255,255,40); background-color: rgb(40,39,38); border-radius: 8px')
        if m.hasUrls():
            for i in range(len(m.urls())):
                print(m.urls()[i].toLocalFile())
                filename, file_extension = os.path.splitext(m.urls()[i].toLocalFile())
                if '.jpg' in str(file_extension) or '.png' in str(file_extension) or '.jpeg' in str(file_extension) :
                    global lst
                    lst.extend([m.urls()[i].toLocalFile()]) 
            self.parent().label.setText(str(len(lst)) + ' images selected')



class Form(QWidget):

    def __init__(self):
        super().__init__()

        # 1 - create Worker and Thread inside the Form
        self.obj = Worker()  # no parent!
        self.thread = QThread()  # no parent!

        # 2 - Connect Worker`s Signals to Form method slots to post data.
        self.obj.intReady.connect(self.onIntReady)

        # 3 - Move the Worker object to the Thread object
        self.obj.moveToThread(self.thread)

        # 4 - Connect Worker Signals to the Thread slots
        self.obj.finished.connect(self.thread.quit)

        # 5 - Connect Thread started signal to Worker operational slot method
        self.thread.started.connect(self.obj.procCounter)

        # 6 - Start the form
        self.initUI()

    def initUI(self):


        #####################
        #### Main Window ####
        #####################


        # Title
        title = QLabel('Detect and blur faces in any picture')
        title.setSizePolicy(QtWidgets.QSizePolicy.Preferred,QtWidgets.QSizePolicy.Preferred)
        title.setStyleSheet('QLabel {color: rgba(255, 255 , 255, 255); font-size: 12px;}')
        title.setFixedHeight(20)

        # Settings Button
        settingsButton = QPushButton('')
        settingsButton.setIcon(QIcon(settingsIcon))
        settingsButton.setIconSize(QSize(15,15))
        settingsButton.setStyleSheet('QPushButton {border: none; color: rgba(255, 255 , 255, 255); width: 25px; text-align: right}')

        #Drag and drop area
        dragAndDropButton = Button("",self)

        # Info label
        self.label = QLabel("")
        self.label.setText("Drag and drop or manually select images")
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("QLabel {background-color: transparent; font-size: 15px; color:white}")
        self.label.setFixedHeight(60)

        # Upload Button
        button = QPushButton('Select Images')
        button.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Preferred)
        button.setStyleSheet('QPushButton {border:1px solid rgb(225, 225 , 93); max-height: 35px; color: rgb(225,225,93); }' 'QPushButton:pressed {background-color: rgb(225,225,93); color: rgb(52,50,49)}')
       
        # Process Button
        button2 = QPushButton('Start Processing')
        button2.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Preferred)
        button2.setStyleSheet('QPushButton {border:1px solid rgb(113, 195 , 148); max-height: 35px; color: rgb(113,195,148);}' 'QPushButton:pressed {background-color: rgb(113,195,148); color: rgb(52,50,49)}')

        # Create main window layout
        grid = QGridLayout()
        self.setLayout(grid)


        # Add Widgets to grid
        grid.addWidget(title,0,0, 1 , 7)
        grid.addWidget(settingsButton,0,7, 1 ,1)
        grid.addWidget(dragAndDropButton,1,0, 1 ,8) #Logo
        grid.addWidget(self.label, 2,0, 1 ,8)
        grid.addWidget(button, 3, 0, 1, 4)
        grid.addWidget(button2, 3, 4, 1, 4)

        ###############
        #### Modal ####
        ###############

        # Efficiency label 
        Efficiency = QLabel(self)
        Efficiency.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        Efficiency.setStyleSheet('font-size: 14px; color: rgba(255,255,255,255); background-color: rgb(55,55,55); margin-top: 30px}')
        Efficiency.setText("Efficiency")

        # Slider -  Low
        Sliderlabel1 = QLabel(self)
        Sliderlabel1.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        Sliderlabel1.setStyleSheet('QLabel {font-size: 12px; color: rgba(255,255,255,180); background-color: rgb(55,55,55)}')
        Sliderlabel1.setText("Low")
    
        # Slider -  Bar
        slider = QtWidgets.QSlider()
        slider.setOrientation(QtCore.Qt.Horizontal)
        slider.setMaximum(10)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setTickInterval(1)
        slider.setSingleStep(1)
        slider.setValue(blurness)

        # Blur Intensity Label
        Blurlabel = QLabel(self)
        Blurlabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        Blurlabel.setStyleSheet('font-size: 14px; color: rgba(255,255,255,255); background-color: rgb(55,55,55)')
        Blurlabel.setText("Blur Intensity")
        Blurlabel.setFixedHeight(20)

        # Slider - High
        Sliderlabel2 = QLabel(self)
        Sliderlabel2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        Sliderlabel2.setStyleSheet('QLabel {font-size: 12px; color: rgba(255,255,255,180); background-color: rgb(55,55,55)}')
        Sliderlabel2.setText("High")

        # HOC Button
        toggle1 = QPushButton('Faster')
        toggle1.setSizePolicy(QtWidgets.QSizePolicy.Preferred,QtWidgets.QSizePolicy.Preferred)
        toggle1.setStyleSheet('QPushButton {border:1px solid rgb(40,39,38);color: rgba(255, 255 , 255, 255); background-color: rgb(40,39,38); font-size: 10px}')
        toggle1.setFixedHeight(35)

        # CNN Button
        toggle2 = QPushButton('More Accurate')
        toggle2.setSizePolicy(QtWidgets.QSizePolicy.Preferred,QtWidgets.QSizePolicy.Preferred)
        toggle2.setStyleSheet('QPushButton {border:1px solid rgb(40,39,38); color: rgba(255, 255 , 255, 80); background-color:transparent; font-size: 10px}')
        toggle2.setFixedHeight(35)

        # Spacer Label
        Spacer = QLabel(self)
        Spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        Spacer.setStyleSheet('background-color: rgb(55,55,55)')
        Spacer.setText("")

        # Close Modal Button
        closeButton = QPushButton('CANCEL')
        closeButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Preferred)
        closeButton.setStyleSheet('QPushButton {border: none; color: rgba(255,255 ,255,180); font-size: 12px; background-color: transparent}' 'QPushButton:pressed {color: rgba(255,255 ,255,255)}')
        closeButton.setFixedHeight(25)

        # Save settings Modal Button
        saveButton = QPushButton('OK')
        saveButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Preferred)
        saveButton.setStyleSheet('QPushButton {border: 1px solid rgb(113, 195 , 148); color: rgb(113, 195 , 148); font-size: 12px; background-color: transparent}' 'QPushButton:pressed {color: rgba(55,55,55,255); background-color: rgb(113, 195 , 148)}')
        saveButton.setFixedHeight(25)

        # Create Modal Layout
        my_dialog = QDialog(self) 
        my_dialog.setModal(True)
        my_dialog.setFixedSize(250, 300)
        my_dialog.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        modalGrid = QGridLayout()
        modalGrid.setVerticalSpacing(15)
        my_dialog.setLayout(modalGrid)
        my_dialog.setStyleSheet("QDialog {background-color:rgb(55,55,55); border: 1px solid rgba(255,255,255,20);}")
        my_dialog.draggable = True
        my_dialog.dragging_threshould = 5

        # Add Widgets to Modal
        modalGrid.addWidget(Blurlabel, 0, 0, 1 ,6)
        modalGrid.addWidget(Sliderlabel1, 1, 0, 1, 1)
        modalGrid.addWidget(slider, 1, 1, 1 ,4)
        modalGrid.addWidget(Sliderlabel2, 1, 5, 1, 1)
        modalGrid.addWidget(Efficiency, 2, 0, 1 ,6)
        modalGrid.addWidget(toggle1, 3, 0, 1, 3)
        modalGrid.addWidget(toggle2, 3, 3, 1, 3)
        modalGrid.addWidget(Spacer, 4, 0, 1, 6)
        modalGrid.addWidget(closeButton, 5,0,1,3)
        modalGrid.addWidget(saveButton, 5,3,1,3)

        ##########################
        #### Show Main Window ####
        ##########################

        # Manage App Window
        self.move(100, 100)
        self.setWindowTitle('Faceblur')
        self.setFixedSize(400, 350)
        self.setStyleSheet("QWidget {background-color:rgb(52,50,49);}")
        self.show()


        ########################
        #### Buttons events ####
        ########################

        def closeModal():
            my_dialog.close()

        def saveModal():
            global blurnessTemp, fastProcessingTemp, blurness, fastProcessing
            blurness = blurnessTemp
            fastProcessing = fastProcessingTemp
            my_dialog.close()

        def openModal():
            sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
            if(sizeObject.width() - getXCoordinates() - 400 > 250 ):
                x = getXCoordinates() + 350
            else :
                x = getXCoordinates() - 200

            if(sizeObject.height() - getYCoordinates() > 350 ):
                y = getYCoordinates() + 50
            else :
                y = getYCoordinates() - 300

            my_dialog.move(x, y)
            slider.setValue(blurness)
            HOGpressed() if fastProcessing == True else CNNpressed()
            my_dialog.exec_()

        def getXCoordinates():
            return self.geometry().getCoords()[0]

        def getYCoordinates():
            return self.geometry().getCoords()[1]

        def uploadImages():
            print('clicked')
            dialog = QFileDialog()
            filenames = dialog.getOpenFileNames(None,"Select Images", "", "Images (*.png *.jpg *.jpeg)")
            global lst
            lst = lst + list(filenames[0])
            print('got the names')
            self.label.setText(str(len(lst)) + " images selected")

        def startProcessing():
            if len(lst) > 0:
                self.thread.start()
            else:
                 self.label.setText('No images were selected')

        def HOGpressed():
            global fastProcessingTemp
            fastProcessingTemp = True
            toggle1.setStyleSheet('QPushButton {border:1px solid rgb(40,39,38);  color: rgba(255, 255 , 255, 255); background-color: rgb(40,39,38); font-size: 10px}' )
            toggle2.setStyleSheet('QPushButton {border:1px solid rgb(40,39,38);  color: rgba(255, 255 , 255, 80); background-color: transparent; font-size: 10px}' )


        def CNNpressed():
            global fastProcessingTemp
            fastProcessingTemp = False
            toggle1.setStyleSheet('QPushButton {border:1px solid rgb(40,39,38); color: rgba(255, 255 , 255, 80);  background-color: transparent; font-size: 10px}')
            toggle2.setStyleSheet('QPushButton {border:1px solid rgb(40,39,38); color: rgba(255, 255 , 255, 255); background-color: rgb(40,39,38); font-size: 10px}')

        def setBlur():
            global blurnessTemp
            blurnessTemp = slider.value()

        # Connects Events to Buttons
        button.clicked.connect(uploadImages)
        button2.clicked.connect(startProcessing)
        toggle1.clicked.connect(HOGpressed)
        toggle2.clicked.connect(CNNpressed)
        slider.sliderReleased.connect(setBlur)
        settingsButton.clicked.connect(openModal)
        closeButton.clicked.connect(closeModal)
        saveButton.clicked.connect(saveModal)


    def onIntReady(self, i):
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setText(i)



class Worker(QObject):
    intReady = pyqtSignal(str)
    finished = pyqtSignal()
    @pyqtSlot()
    def procCounter(self): # A slot takes no params
        print('started image processing')
        global lst
        index = 0
        for i in lst:
            self.intReady.emit(str(index) + ' of ' + str(len(lst)) + ' images processed')
            index = index + 1
            filename = i
            img = Image.open(filename)

            if img is None:
                print("Could not read input image")
                self.intReady.emit('Something went wrong!')
                exit()

            imagep = face_recognition.load_image_file(filename)
            if(fastProcessing):
                faces_locations = face_recognition.face_locations(imagep, number_of_times_to_upsample=2)
            else:
                faces_locations = face_recognition.face_locations(imagep, number_of_times_to_upsample=0, model="cnn")

            for face in faces_locations:
                x = face[3]
                y = face[0]
                w = face[1] - x
                h = face[2] - y

                # Crop square around the face
                cropped_image = img.crop((x,y,x+w,y+h))

                # Blur it
                global blurness
                blurred_image = cropped_image.filter(ImageFilter.GaussianBlur(radius=blurness))

                # Open the input image as numpy array
                npImage=np.array(blurred_image)
                q,t=blurred_image.size

                # Create same size alpha layer with circle
                alpha = Image.new('L', blurred_image.size,0)
                draw = ImageDraw.Draw(alpha)
                draw.pieslice([0,0,q,t],0,360,fill=255) 

                # Convert alpha Image to numpy array
                npAlpha=np.array(alpha)

                # Add alpha layer to RGB
                npImage=np.dstack((npImage,npAlpha))
                final_crop = Image.fromarray(npImage)
                
                # Paste cropped image over original
                img.paste(final_crop, (x,y), final_crop)


            file_name, file_extension = os.path.splitext(i)
            img.save(str(file_name) + '_blurred' + file_extension)
        self.intReady.emit('Image processing completed')
        self.finished.emit()
        lst = []



appctxt = ApplicationContext()
imgIcon = appctxt.get_resource('dropIcon.png')
settingsIcon = appctxt.get_resource('settingsIcon.png')
form = Form()
exit_code = appctxt.app.exec_()  
sys.exit(exit_code)
