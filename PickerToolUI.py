from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

from PickerTool import PickerToolLogic

import maya.cmds as mc
import maya.OpenMayaUI as omui
import os
import sys

def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class TabWidget():

    def __init__(self, tabs, ref):
        self.tabs = tabs
        self.ref = ref


class Tab():

    def __init__(self, ref, graphicZone):
        self.pickers = []
        self.graphicZone = graphicZone
        self.graphicScene = None
        self.ref = ref
        self.imageRef = None
        graphicZone.setSceneRect(0, 0, 341, 661)

    def bind_graphicScene(self):

        self.graphicZone.setScene(self.graphicScene)

    def create_graphicScene(self):

        self.graphicScene = QtWidgets.QGraphicsScene()

    def addMouseEventHandler(self):
        handler = MouseEventHandler()
        self.graphicZone.viewport().installEventFilter(handler)


class Picker():

    def __init__(self, color, height, width, text, position, ref):
        self.color = color
        self.height = height
        self.width = width
        self.text = text
        self.position = position
        self.ref = ref

        self.redValue = 0
        self.greenValue = 0
        self.blueValue = 0

class MouseEventHandler(QtCore.QObject):
    def eventFilter(self, obj, event):
        if obj is self.view.viewport() and event.type() == event.MouseButtonPress:
            pos = self.view.mapToScene(event.pos())
            item = self.scene.itemAt(pos, self.view.transform())
            if isinstance(item, QtWidgets.QGraphicsRectItem):
                print("Clicked on QGraphicsRectItem:", item)
        return False


class PickerToolController(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(PickerToolController, self).__init__(parent)

        self.updateSignal = QtCore.Signal()

        self.tabWidget = None
        self.hasValuesChanged = False

        self.setWindowTitle("PickerTool")
        self.setMinimumWidth(705)
        self.setMinimumHeight(705)

        self.currentPickers = []
        self.tabsDictionary = {}

        self.visualisationSquare = None
        self.currentPickerText = ""
        self.currentPickerHeight = 0
        self.currentPickerWidth = 0
        self.tabCurrentIndex = 0

        self.pickerTool = PickerToolLogic.PickerToolLogic()

        self.init_ui()
        self.prepare_objects()

        self.create_layout()
        self.create_connections()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_selection_list())
        self.timer.start(500)

    def init_ui(self):
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load("D:\Animations\Qt\PickerTool.ui", parentWidget=None)

        self.pickerViewScene = QtWidgets.QGraphicsScene()
        self.ui.pickerViewGV.setScene(self.pickerViewScene)

    def prepare_objects(self):
        self.tabWidget = TabWidget(tabs = [], ref= self.ui.tabWidget)

        self.tab1 = Tab(ref = self.ui.picker1T, graphicZone= self.ui.picker1GV)
        self.tab2 = Tab(ref = self.ui.picker2T, graphicZone= self.ui.picker2GV)

        self.tab1.create_graphicScene()
        self.tab2.create_graphicScene()

        self.tab1.bind_graphicScene()
        self.tab2.bind_graphicScene()

        self.tab1.addMouseEventHandler()
        self.tab2.addMouseEventHandler()

        self.tab1.graphicZone.setSceneRect(0, 0, 341, 661)
        self.tab2.graphicZone.setSceneRect(0, 0, 341, 661)

        self.tabWidget.tabs = [self.tab1, self.tab2]

        self.set_current_tab()
        self.setMouseTracking(True)  # Enable mouse tracking to receive mouse events


    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.ui)

    def create_connections(self):
        self.ui.capturePB.clicked.connect(self.on_capture_image)
        self.ui.addTabPB.clicked.connect(self.add_tab)

        # CRUD pickers

        self.ui.createPickerPB.clicked.connect(self.create_picker)
        self.ui.deletePickerPB.clicked.connect(self.delete_picker)
        self.ui.updatePickerPB.clicked.connect(self.update_picker)

        self.ui.previewPickerPB.clicked.connect(self.visualise_picker)

        # VISUALISATION OF PICKER

        self.ui.textLE.editingFinished.connect(self.on_text_changed)
        self.ui.heightS.valueChanged.connect(self.on_height_changed)
        self.ui.widthS.valueChanged.connect(self.on_width_changed)
        self.ui.loadImagePB.clicked.connect(self.load_image)
        # self.ui.previewPickerPB.clicked.connect(self.visualise_picker())

        # Tab_clicked

    def load_Image(self):
        pass

    def on_capture_image(self):
        # specifing file path
        self.filePathUI = "D:\Animations\Qt\PickerToolImages\PickerToolImage"
        # linking queried image to current tab
        filePath = self.pickerTool.CaptureImage(self.filePathUI)

        correctedFilePath = "D:\Animations\Qt\PickerToolImages\PickerToolImage.0000.png"
        if os.path.exists(correctedFilePath):
            pixmap = QtGui.QPixmap(correctedFilePath)
            pixmap_item = QtWidgets.QGraphicsPixmapItem(pixmap)
            current_tab_index = self.tabWidget.ref.currentIndex()
            current_tab_widget = self.tabWidget.ref.widget(current_tab_index)

            current_tab = self.tabWidget.tabs[current_tab_index]

            #Verifying if tab contains already a png file
            if  current_tab.imageRef is not None:
                print("removed")
                current_tab.graphicScene.removeItem(current_tab.imageRef)

            current_tab.imageRef = pixmap_item
            current_tab.graphicScene.addItem(pixmap_item)

            print("Success")
            os.remove(correctedFilePath)


        # matching it's size to tab height and width
        # deleting image

    def create_picker(self):

        current_tab_index = self.tabWidget.ref.currentIndex()
        current_tab_widget = self.tabWidget.ref.widget(current_tab_index)

        current_tab = self.tabWidget.tabs[current_tab_index]

        ref = QtWidgets.QGraphicsRectItem(0, 0, self.currentPickerWidth, self.currentPickerHeight)

        picker = Picker(color = (self.redValue,self.greenValue,self.blueValue), height = self.currentPickerHeight, width= self.currentPickerWidth,
                        ref= ref, position = (0,0), text = "")


        picker.ref.setBrush(QtGui.QColor(int(self.redValue), int(self.greenValue), int(self.blueValue)))
        picker.ref.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)

        current_tab.graphicScene.addItem(picker.ref)

        current_tab.pickers.append(picker)


    def delete_picker(self):
        pass

    def update_picker(self):
        pass

    def get_picker_informations(self):
        self.currentPickerText = self.ui.textLE.text()
        # adding height
        # adding weight

    # Tab logic

    def add_tab(self):

        new_tab = QtWidgets.QWidget()
        graphics_view = QtWidgets.QGraphicsView()

        tab = Tab(ref = new_tab, graphicZone= graphics_view)
        tab.create_graphicScene()
        tab.bind_graphicScene()
        tab.addMouseEventHandler()


        tab_layout = QtWidgets.QVBoxLayout()
        tab_layout.addWidget(graphics_view)
        tab.ref.setLayout(tab_layout)

        self.tabWidget.tabs.append(tab)
        self.tabWidget.ref.addTab(new_tab, f"Tab{self.ui.tabWidget.count() + 1}")
        # TODO adding a name here instead of index

        # updating view to display tab's graphicsview

    def get_current_tab(self):
        return self.tabCurrentIndex

    def set_current_tab(self):
        self.tabCurrentIndex = self.ui.tabWidget.currentIndex()

    # Picker visualisation delegates
    def on_text_changed(self):
        self.currentPickerText = str(self.ui.textLE.text())
        # if ( self.hasValuesChanged):
        # self.destroy_picker()

    def on_height_changed(self):
        self.currentPickerHeight = self.ui.heightS.value()
        # if (self.hasValuesChanged):
        # self.destroy_picker()

    def on_width_changed(self):
        self.currentPickerWidth = self.ui.widthS.value()
        # if (self.hasValuesChanged):
        # self.destroy_picker()

    def visualise_picker(self):
        self.destroy_picker()
        self.visualisationSquare = QtWidgets.QGraphicsRectItem(0, 0, self.currentPickerWidth, self.currentPickerHeight)
        self.redValue = self.ui.RedLE.text()
        self.greenValue = self.ui.GreenLE.text()
        self.blueValue = self.ui.BlueLE.text()
        self.visualisationSquare.setBrush(QtGui.QColor(int(self.redValue), int(self.greenValue), int(self.blueValue)))
        self.pickerViewScene.addItem(self.visualisationSquare)
        #

    def destroy_picker(self):
        self.pickerViewScene.removeItem(self.visualisationSquare)
        print("square destroyed")

    """
    #OVERRIDE
    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())  # Get the item at the click position
        if isinstance(item, QtWidgets.QGraphicsRectItem):
            print("Clicked on QGraphicsRectItem:", item)
    """
    def load_image(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter("Images (*.png *.jpg *.bmp)")
        file_dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            pixmap = QtGui.QPixmap(file_path)

            if not pixmap.isNull():
                pixmap_item = QtWidgets.QGraphicsPixmapItem(pixmap)
                current_tab_index = self.tabWidget.ref.currentIndex()
                current_tab_widget = self.tabWidget.ref.widget(current_tab_index)

                current_tab = self.tabWidget.tabs[current_tab_index]

                current_tab.imageRef = pixmap_item
                current_tab.graphicScene.addItem(pixmap_item)

    def create_connection(self):
        pass

    def populate_list_view(self):
        selected_objects = mc.ls(selection=True)

        model = QtCore.QStringListModel(selected_objects)

        self.ui.selectionLV.setModel(model)

    def update_selection_list(self):
        # Get the currently selected objects in Maya
        selected_objects = mc.ls(selection=True)

        # Check if the selected objects have changed
        current_model = self.ui.selectionLV.model()
        if current_model is not None and current_model.stringList() != selected_objects:
            self.update_signal.emit()


    def save_to_json(self):
        pass

    def load_from_json(self):
        pass


if __name__ == "__main__":
    pickerToolUI = PickerToolController()
    pickerToolUI.show()
