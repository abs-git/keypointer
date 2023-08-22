import os.path
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import resources_rc

__appname__ = 'UtilityAI'

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle(__appname__)
        self.setWindowIcon(QIcon(":logo"))

        self.statusBar()
        self.statusBar().showMessage('Ready')
        

        self.toolbarBox = QToolBar(self)
        self.form_widget = FormWidget(self)
        self.setCentralWidget(self.form_widget)
        
        self.setGeometry(500, 500, 500, 500)

        openImageAction = self.initAction(":open", "Open Image Directory", "Ctrl+O")
        openKeypointAction = self.initAction(":open", "Open KeyPoint Directory", "Ctrl+K")
        prevAction = self.initAction(":prev", "Prev Image", "A")
        nextAction = self.initAction(":next", "Next Image", "D")
        saveAction = self.initAction(":open", "Save Image", "S")

        #왼쪽 메뉴 바부터 시작
        self.toolbarBox.addAction(openImageAction)
        self.toolbarBox.addAction(openKeypointAction)
        self.toolbarBox.addAction(prevAction)
        self.toolbarBox.addAction(nextAction)
        self.toolbarBox.addAction(saveAction)

        for index, value in enumerate(self.form_widget.vesselType):
            toolButton = QToolButton(self)
            toolButton.setCheckable(True)
            toolButton.setObjectName(self.form_widget.vesselType[index])
            toolButton.setText(f'{self.form_widget.vesselType[index]}({index + 1})')
            self.toolbarBox.addWidget(toolButton)
        
        self.toolbarBox.setIconSize(QSize(100, 60))
        self.addToolBar(Qt.LeftToolBarArea, self.toolbarBox)

        openImageAction.triggered.connect(self.form_widget.openDirClicked)
        openKeypointAction.triggered.connect(self.form_widget.openDirKeyPointClicked)
        prevAction.triggered.connect(self.form_widget.filePrevEvent)
        nextAction.triggered.connect(self.form_widget.fileNextEvent)
        saveAction.triggered.connect(self.form_widget.imageSaveEvent)

    def initAction(self, icon, toolTip, shortcut):
        action = QAction(QIcon(icon), toolTip, self)
        action.setShortcut(shortcut)
        action.setStatusTip(toolTip)
        return action

    def keyPressEvent(self, event):
        self.form_widget.keyPressEvent(event)

    def mousePressEvent(self, event):
        self.form_widget.mousePressEvent(event)


class FormWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.mainWindow = parent
        self.imageViewerWidget = QLabel() 
        self.imageViewerWidget.mousePressEvent = self.mousePressEvent
        self.imageListWidget = QListWidget()
        self.imageListWidget.setFixedWidth(300)

        self.txtListWidget = QLabel() 
        self.txtListWidget = QListWidget()
        self.txtListWidget.setFixedWidth(300)

        h_box_control = QHBoxLayout()
        h_box_control.addWidget(self.imageViewerWidget)

        mainBox = QVBoxLayout()
        mainBox.addLayout(h_box_control)

        self.setLayout(mainBox)
        self.resize(1600, 900)
        self.currIndex = 0
        self.initPoints()
        self.initStatic()

        self.openDirClicked()
        self.openDirKeyPointClicked()

    def openDirClicked(self):
        self.imageDirpath = QFileDialog.getExistingDirectory(self, self.tr("Open Data files"), "./", QFileDialog.ShowDirsOnly) #'D:\Sources\Python\KeyPointer\images_jpg' 
        self.mImgList = self.scanAllItems(self.imageDirpath)
        for imgPath in self.mImgList:
            item = QListWidgetItem(imgPath)
            self.imageListWidget.addItem(item)
        self.imageOpenEvent(0)

    def openDirKeyPointClicked(self):
        self.keypointDirpath = QFileDialog.getExistingDirectory(self, self.tr("Open Data files"), "./", QFileDialog.ShowDirsOnly) #"'D:\Sources\Python\KeyPointer\gt' "
        self.txtOpenEvent()
        self.refreshPaint()

    def scanAllItems(self, folderPath):
        item = []
        for root, dirs, files in os.walk(folderPath):
            for file in files:
                relativePath = os.path.join(root, file)
                path = str(os.path.abspath(relativePath))
                item.append(path)
        return item

    def filePrevEvent(self):
        self.imageOpenEvent(-1)

    def fileNextEvent(self):
        self.imageOpenEvent(1)

    def imageSaveEvent(self):
        exportPath =  self.keypointDirpath
        exportData = ""
        tempData = ""

        f = open(exportPath + "\\" + self.imageFile + '.txt', 'w')
        for line in self.points:
            tempData = ""
            for index, item in enumerate(line):
                if index == 0 or index == 1:
                    item = int(item * self.reverseRatio)
                tempData = tempData + str(item) + ","
            exportData = exportData + tempData[0:len(tempData) - 1] + "\n"
        f.write(exportData[0:len(exportData) - 1])
        f.close()

    def imageOpenEvent(self, index):
        self.initPoints()
        self.currIndex = self.currIndex + index
        self.filename = self.mImgList[self.currIndex]
        self.oriPixmap = QPixmap(self.filename)
        self.txtOpenEvent()
        self.refreshPaint()

        self.mainWindow.setWindowTitle(__appname__ + " / " + self.filename)

        

    def setImage(self):
        self.pixmap = self.oriPixmap
        oriWidth, oriHeight = self.pixmap.width(), self.pixmap.height()
        resizeWidth, resizeHeight = self.scaledImageSize()
        
        # if resizeWidth > oriWidth or resizeHeight > oriHeight:
        #     self.pixmap = self.pixmap.scaledToWidth(oriWidth)
        #     self.sizeRatio = 1
        #     self.reverseRatio = 1
        if oriWidth >= oriHeight:
            self.pixmap = self.pixmap.scaledToWidth(resizeWidth)
            self.sizeRatio = resizeWidth / oriWidth
            self.reverseRatio = oriWidth / resizeWidth
        else:
            self.sizeRatio = resizeWidth / oriWidth
            self.reverseRatio = oriHeight / resizeHeight
            self.pixmap = self.pixmap.scaledToHeight(int(oriHeight * self.sizeRatio))
        return self.pixmap

    
    def txtOpenEvent(self):
        if self.keypointDirpath == None:
            return
        
        self.mTxtList = self.scanAllItems(self.keypointDirpath)
        for txtPath in self.mTxtList:
            item = QListWidgetItem(txtPath)
            self.txtListWidget.addItem(item)

        if self.txtListWidget.count() == 0:
            return
        
        txtList = []
        for item in self.mTxtList:
            self.imageFile = self.filename[self.filename.rfind("\\") + 1:self.filename.rfind("\.") - 3]
            self.txtFile = item[item.rfind("\\") + 1 : item.rfind("\.") - 3]
            if self.imageFile == self.txtFile:
                f = open(item)
                lines = f.readlines()
                for index, line in enumerate(lines):
                    line = list(map(int, line.strip().split(',')))
                    line[0] = int(line[0] * self.sizeRatio)
                    line[1] = int(line[1] * self.sizeRatio)
                    txtList.append(line)
                break

        self.refreshPaint()
        
        if len(txtList) == 0:
            return

        for index, value in enumerate(txtList):
            self.points[index] = value

    def initPoints(self):
        self.points = []
        self.points.append([0, 0, 0, 0, 1])
        self.points.append([0, 0, 1, 0, 1])
        self.points.append([0, 0, 2, 0, 1])
        self.points.append([0, 0, 3, 0, 1])
        self.points.append([0, 0, 4, 0, 1])
        self.points.append([0, 0, 5, 0, 1])
        self.points.append([0, 0, 6, 0, 1])
        self.points.append([0, 0, 7, 0, 1])
        self.points.append([0, 0, 8, 0, 1])
        # self.points.append([0, 0, 9, 0, 1])
        # self.points.append([0, 0, 10, 0, 1])
        # self.points.append([0, 0, 11, 0, 1])
        # self.points.append([0, 0, 12, 0, 1])
        self.keyPoint = 0

    def initStatic(self):
        self.connectLine = [
            [0,1],
            [1,2],
            [2,3],
            [4,1],
            [5,2],
            [5,6],
            [5,7],
            [5,8],
        #   [9,10],
        #   [9,11],
        #   [11,12],
        #   [10,3],
        #   [12,3],
    	]

        self.vesselType = [
            'Head_Center',			# 1
            'Fore_Mast_Central_Axis_Point',	# 2
            'Main_Mast_Central_Axis_Point', # 3
            'Stern_Center',			# 4
            'Fore_Mast',			# 5
            'Mast_Across',          # 6
            'Bridge_Wing_Right',	# 7
            'Bridge_wing_Left',		# 8
            'Main_Mast',            # 9
            # 'Head_Starboard',     # 10
            # 'Head_Port',          # 11
            # 'Stern_Starboard',    # 12
            # 'Stern_Port',         # 13
        ]

        self.keypointDirpath = ""

    def paintEvent(self, event):
        if self._paintFlag:
            pixmap = self.setImage()
            self.painter = QPainter(pixmap)

            #point 찍기
            for index, value in enumerate(self.points):
                point = QPoint(value[0], value[1])
                if point != QPoint(0, 0):
                    self.painter.setPen(QPen(self.paintColor(value[4]), 3))
                    self.painter.setRenderHint(QPainter.Antialiasing, True)
                    self.painter.drawPoint(point)
                    pSize = 20
                    pt = QRectF(point.x() - pSize / 2, point.y() - pSize / 2, pSize, pSize)
                    self.painter.drawEllipse(pt)

                    #메인 윈도우 왼쪽 메뉴 활성화
                    for item in self.mainWindow.toolbarBox.findChildren(QToolButton):
                        if self.vesselType[index] == item.objectName():
                            item.setChecked(True)
                else:
                    for item in self.mainWindow.toolbarBox.findChildren(QToolButton):
                        if self.vesselType[index] == item.objectName():
                            item.setChecked(False)
            #line 그리기
            for item in self.connectLine:
                pointX, pointY = item
                if self.points[pointX][0] == 0 or self.points[pointX][1] == 0 or self.points[pointY][0] == 0 or self.points[pointY][1] == 0:
                    continue
                startX, startY = int(self.points[pointX][0]), int(self.points[pointX][1])
                endX, endY = int(self.points[pointY][0]), int(self.points[pointY][1])
                self.painter.setPen(QPen(Qt.blue, 3))
                self.painter.setRenderHint(QPainter.Antialiasing, True)
                self.painter.drawLine(startX, startY, endX, endY)            

            self.painter.end()
            self.imageViewerWidget.setPixmap(self.pixmap)
            self.imageViewerWidget.update()

    def paintColor(self, value):
        if value == 1:
            return Qt.blue
        else:
            return Qt.red

    def refreshPaint(self):
        self._paintFlag = True
        self.paintEvent(None)
        self._paintFlag = False

    def scaledImageSize(self):
        w = self.frameGeometry().width() - 44
        h = self.frameGeometry().height() - 200
        return w, h

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_1:
            self.keyPoint = 0
        elif e.key() == Qt.Key_2:
            self.keyPoint = 1
        elif e.key() == Qt.Key_3:
            self.keyPoint = 2
        elif e.key() == Qt.Key_4:
            self.keyPoint = 3
        elif e.key() == Qt.Key_5:
            self.keyPoint = 4
        elif e.key() == Qt.Key_6:
            self.keyPoint = 5
        elif e.key() == Qt.Key_7:
            self.keyPoint = 6
        elif e.key() == Qt.Key_8:
            self.keyPoint = 7
        elif e.key() == Qt.Key_9:
            self.keyPoint = 8
        # elif e.key() == Qt.Key_Q:
        #     self.keyPoint = 9
        # elif e.key() == Qt.Key_W:
        #     self.keyPoint = 10
        # elif e.key() == Qt.Key_E:
        #     self.keyPoint = 11
        # elif e.key() == Qt.Key_R:
        #     self.keyPoint = 12

        self.mainWindow.statusBar().showMessage(str(self.vesselType[self.keyPoint]))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.points[self.keyPoint][4] = 1
        elif event.button() == Qt.RightButton:
            self.points[self.keyPoint][4] = 2

        self.points[self.keyPoint][0] = event.x()
        self.points[self.keyPoint][1] = event.y()
        self.refreshPaint()

    def resizeEvent(self, event):
        self.refreshPaint()
        self.txtOpenEvent()
        return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    windowExample = MainWindow()
    windowExample.show()
    sys.exit(app.exec_())
