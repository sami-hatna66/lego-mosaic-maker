from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2
import sys
import os
import math

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.CentralWidget = QWidget()
        self.setCentralWidget(self.CentralWidget)

        self.MainLayout = QHBoxLayout()
        self.CentralWidget.setLayout(self.MainLayout)

        self.setGeometry(300, 200, 800, 500)

        self.InitUI()

        self.show()

    def InitUI(self):
        self.PictureLayout = QVBoxLayout()
        self.MainLayout.addLayout(self.PictureLayout, stretch = 3)

        self.PictureWidget = ImageWidget()
        self.PictureWidget.PartsCollected.connect(self.PartsCollectedSlot)
        self.PictureWidget.SetTableSelection.connect(self.SelectColourSlot)
        self.PictureLayout.addWidget(self.PictureWidget)

        self.UploadImageBTN = QPushButton("Upload Image")
        self.UploadImageBTN.clicked.connect(self.UploadImage)
        self.PictureLayout.addWidget(self.UploadImageBTN)

        self.ControlsLayout = QVBoxLayout()
        self.ControlsLayout.setAlignment(Qt.AlignTop)
        self.MainLayout.addLayout(self.ControlsLayout, stretch = 2)

        self.SelectedImageLBL = QLabel("No image uploaded")
        self.ControlsLayout.addWidget(self.SelectedImageLBL)

        self.ControlsLayout.addSpacing(20)

        self.ControlsLayout.addWidget(QLabel("Width (in studs)"))

        self.WidthHBL = QHBoxLayout()
        self.ControlsLayout.addLayout(self.WidthHBL)

        self.WidthSlider = QSlider()
        self.WidthSlider.setEnabled(False)
        self.WidthSlider.valueChanged.connect(self.ChangeSliderVal)
        self.WidthSlider.setOrientation(Qt.Horizontal)
        self.WidthHBL.addWidget(self.WidthSlider)

        self.WidthSpinBox = QSpinBox()
        self.WidthSpinBox.setEnabled(False)
        self.WidthSpinBox.valueChanged.connect(self.ChangeSpinBoxVal)
        self.WidthSpinBox.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.WidthHBL.addWidget(self.WidthSpinBox)

        self.WarningLBL = QLabel("WARNING: It may take a while to generate larger mosaics")
        self.WarningLBL.setWordWrap(True)
        self.WarningLBL.setStyleSheet("color: red")
        self.ControlsLayout.addWidget(self.WarningLBL)
        self.WarningLBL.hide()

        self.ResultsTable = QTableWidget()
        self.ControlsLayout.addWidget(self.ResultsTable)
        self.ResultsTable.setColumnCount(3)
        self.ResultsTable.setShowGrid(False)
        self.ResultsTable.setColumnWidth(0, 50)
        self.ResultsTable.setColumnWidth(2, 70)
        self.ResultsTable.setSelectionBehavior(QTableView.SelectRows)
        self.ResultsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ResultsTable.setStyleSheet("QTableWidget::item{ selection-background-color: rgb(221,220,220); selection-color: black; }")
        self.ResultsTable.verticalHeader().setDefaultSectionSize(40)
        self.ResultsTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.ResultsTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ResultsTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.ResultsTable.verticalHeader().setVisible(False)
        self.ResultsTable.setHorizontalHeaderLabels(["", "Name", "Amount"])

        self.GenerateBTN = QPushButton("Generate Mosaic")
        self.GenerateBTN.setEnabled(False)
        self.GenerateBTN.clicked.connect(lambda: self.PictureWidget.Redraw(self.WidthSlider.value()))
        self.ControlsLayout.addWidget(self.GenerateBTN)

    def SelectColourSlot(self, Colour):
        Search = self.ResultsTable.findItems(Colour, Qt.MatchExactly)
        if Search:
            self.ResultsTable.selectRow(Search[0].row())

    def PartsCollectedSlot(self, PartList):
        print(PartList)
        self.ResultsTable.setRowCount(0)
        self.ResultsTable.setRowCount(len(PartList))
        for x in range(0, len(PartList)):
            ImageLBL = QLabel()
            ImageLBL.setAlignment(Qt.AlignCenter)
            try:
                PM = QPixmap("Colours/" + PartList[x][0])
            except:
                PM = QPixmap("Colours/" + PartList[x][0] + ".png")
            ImageLBL.setPixmap(PM)
            self.ResultsTable.setCellWidget(x, 0, ImageLBL)

            NameItem = QTableWidgetItem(PartList[x][0])
            self.ResultsTable.setItem(x, 1, NameItem)

            AmountLBL = QLabel(str(PartList[x][1]))
            AmountLBL.setAlignment(Qt.AlignCenter)
            self.ResultsTable.setCellWidget(x, 2, AmountLBL)

    def ChangeSliderVal(self):
        self.WidthSpinBox.setValue(self.WidthSlider.value())
        self.ShowHideWarning()

    def ChangeSpinBoxVal(self):
        self.WidthSlider.setValue(self.WidthSpinBox.value())
        self.ShowHideWarning()

    def ShowHideWarning(self):
        if self.WidthSlider.maximum() == 200 and self.WidthSlider.value() >= 125:
            self.WarningLBL.show()
        elif self.WidthSlider.maximum() == 400 and self.WidthSlider.value() >= 200:
            self.WarningLBL.show()
        else:
            self.WarningLBL.hide()

    def UploadImage(self):
        self.FileName, _ = QFileDialog.getOpenFileName(self, "Open Image File", os.path.abspath(os.sep), "Image files (*.png *.jpg *.tiff *.bmp, *.webp)")
        if self.FileName:
            self.SelectedImageLBL.setText("Selected " + QUrl.fromLocalFile(self.FileName).fileName()[:20] + "...")
            self.Image = cv2.imread(self.FileName)
            self.Rows, self.Columns, self.Channels = self.Image.shape
            self.PictureWidget.SetImage(self.Image)
            self.WidthSpinBox.setEnabled(True)
            self.WidthSlider.setEnabled(True)
            if self.PictureWidget.Orientation == "portrait":
                self.WidthSlider.setMaximum(200)
                self.WidthSlider.setMinimum(10)
                self.WidthSpinBox.setMaximum(200)
                self.WidthSpinBox.setMinimum(10)
            else:
                self.WidthSlider.setMaximum(400)
                self.WidthSlider.setMinimum(20)
                self.WidthSpinBox.setMaximum(400)
                self.WidthSpinBox.setMinimum(20)
            self.GenerateBTN.setEnabled(True)


class ImageWidget(QGraphicsView):
    PartsCollected = pyqtSignal(list)
    SetTableSelection = pyqtSignal(str)
    def __init__(self):
        super(ImageWidget, self).__init__()
        self.Image = None
        self.Rows = None
        self.Columns = None
        self.Zoom = 0
        self.First = True
        self.Previous = None
        self.PrevPos = None
        self.ColourMap = []

        self.Scene = QGraphicsScene()
        self.setScene(self.Scene)

        self.setMouseTracking(True)

        self.Colours = ((248, 207, 70, "bright yellow", 24), (254, 245, 139, "cool yellow", 226), (230, 131, 59, "bright orange", 106),
                        (239, 174, 66, "flame yellowish orange", 191), (203, 52, 46, "bright red", 21), (217, 102, 160, "bright purple", 221),
                        (235, 176, 204, "light purple", 222), (166, 45, 122, "bright reddish violet", 124), (116, 30, 32, "new dark red", 154),
                        (146, 118, 176, "medium lavender", 324), (185, 167, 205, "lavender", 325), (73, 48, 141, "medium lilac", 268),
                        (46, 106, 177, "bright blue", 23), (96, 156, 202, "medium blue", 102), (136, 189, 230, "light royal blue", 212),
                        (109, 129, 149, "sand blue", 135), (22, 56, 91, "earth blue", 140), (73, 160, 213, "dark azur", 321),
                        (85, 187, 208, "medium azur", 322), (209, 224, 159, "yellowish green", 326), (200, 227, 218, "aqua", 323),
                        (79, 172, 88, "bright green", 37), (119, 147, 124, "sand green", 151), (64, 144, 79, "dark green", 28),
                        (30, 73, 47, "earth green", 141), (164, 201, 84, "bright yellowish green", 119), (130, 131, 89, "olive green", 330),
                        (98, 49, 27, "reddish brown", 192), (218, 197, 149, "brick yellow", 5), (145, 127, 99, "sand yellow", 138),
                        (166, 119, 78, "medium nougat", 312), (56, 26, 16, "dark brown", 308), (211, 143, 103, "nougat", 18),
                        (244, 197, 163, "light nougat", 283), (156, 87, 46, "dark orange"), (255, 255, 255, "white", 1),
                        (160, 161, 159, "medium stone grey", 194), (101, 103, 101, "dark stone grey", 199), (0, 0, 0, "black", 26),
                        (66, 66, 62, "metallic titanium", 316), (189, 153, 73, "warm gold", 297), (136, 141, 143, "metallic silver", 315))

    def SetImage(self, NewImg):
        if NewImg.shape[1] > NewImg.shape[0]:
            self.Orientation = "landscape"
        else:
            self.Orientation = "portrait"
        self.OriginalImage = NewImg

    def NearestColour(self, subjects, query):
        return min(subjects, key=lambda subject: sum((s - q) ** 2 for s, q in zip(subject, query)))

    def Redraw(self, Width):
        self.PartList = []
        self.ColourMap = []
        self.Scene.clear()
        self.Previous = None
        self.Image = cv2.resize(self.OriginalImage, (Width, int(self.OriginalImage.shape[0] / (self.OriginalImage.shape[1] / Width))), cv2.INTER_LANCZOS4)
        self.Rows, self.Columns, Channels = self.Image.shape
        Pen = QPen(Qt.NoPen)
        for i in range(0, self.Rows - 1):
            self.ColourMap.append([])
            for j in range(0, self.Columns - 1):
                Colour = self.Image[i, j]
                ColourApproximation = self.NearestColour(self.Colours, (Colour[2], Colour[1], Colour[0]))
                Brush = QBrush(QColor(ColourApproximation[0], ColourApproximation[1], ColourApproximation[2]))
                Found = False
                for entry in self.PartList:
                    if entry[0] == ColourApproximation[3]:
                        entry[1] += 1
                        Found = True
                if not Found:
                    self.PartList.append([ColourApproximation[3], 1])
                self.Scene.addRect(j, i, 1, 1, Pen, Brush)
                self.ColourMap[i].append([ColourApproximation[0], ColourApproximation[1], ColourApproximation[2], ColourApproximation[3]])

        self.PartsCollected.emit(self.PartList)
        self.CenterImage()
        print(self.ColourMap)
        if self.First:
            self.InstructionLBL = QLabel(" Use the + and – keys to zoom ", self)
            self.InstructionLBL.setStyleSheet("font-size: 10px; background-color: black; color: white")
            self.InstructionLBL.move(self.viewport().rect().width() - 145, self.viewport().rect().height() - 10)
            self.InstructionLBL.show()
            QTimer.singleShot(3000, self.InstructionLBL.hide)
            self.First = False

    def keyPressEvent(self, event):
        Factor = 1
        if event.key() == Qt.Key_Equal:
            Factor = 1.25
        elif event.key() == Qt.Key_Minus:
            Factor = 0.8
        self.scale(Factor, Factor)

    def CenterImage(self):
        Rect = QRectF(0, 0, self.Columns, self.Rows)
        self.setSceneRect(Rect)
        unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
        self.scale(1 / unity.width(), 1 / unity.height())
        viewrect = self.viewport().rect()
        scenerect = self.transform().mapRect(Rect)
        factor = min(viewrect.width() / scenerect.width(),
                     viewrect.height() / scenerect.height())
        self.scale(factor, factor)

    def contextMenuEvent(self, event):
        ContextMenu = QMenu(self)
        SaveImage = ContextMenu.addAction("Save Image")
        ZoomIn = ContextMenu.addAction("Zoom In")
        ZoomOut = ContextMenu.addAction("Zoom Out")
        Action = ContextMenu.exec_(self.mapToGlobal(event.pos()))
        if Action == SaveImage:
            pass
        if Action == ZoomIn:
            self.scale(1.25, 1.25)
        if Action == ZoomOut:
            self.scale(0.8, 0.8)

    def mousePressEvent(self, event):
        LocalPoint = self.mapFromGlobal(event.globalPos())
        PixelCoord = self.mapToScene(LocalPoint)
        XPos = math.floor(PixelCoord.x())
        YPos = math.floor(PixelCoord.y())
        if len(self.ColourMap) != 0:
            if 0 <= XPos < len(self.ColourMap[0]) and 0 <= YPos < len(self.ColourMap):
                self.SetTableSelection.emit(self.ColourMap[YPos][XPos][3])
                Pen = QPen(Qt.red)
                Pen.setWidth(0)
                Draw = True
                if self.Previous is not None:
                    self.Scene.removeItem(self.Previous)
                    if XPos == self.PrevPos[0] and YPos == self.PrevPos[1]:
                        Draw = False
                if Draw:
                    self.Previous = QGraphicsRectItem(XPos, YPos, 1, 1)
                    self.PrevPos = [XPos, YPos]
                    self.Previous.setPen(Pen)
                    self.Previous.setBrush(QBrush(Qt.NoBrush))
                    self.Scene.addItem(self.Previous)

if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    sys.exit(App.exec())