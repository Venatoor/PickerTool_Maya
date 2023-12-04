from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui


class PickerToolLogic():

    def __init__(self):

        self.filePath = ""

    def CaptureImage(self, filePath):

        #looking through camera
        #changing file format
        #playblast

        panel = mc.getPanel(withFocus = True)
        camera = mc.modelPanel( panel, query = True, camera = True)

        if camera:

            mc.lookThru(camera)
            image_format = "png"
            mc.setAttr("defaultRenderGlobals.imageFormat",32)
            mc.playblast(format = "image", frame = mc.currentTime(q=True), filename = filePath, viewer = False)
            print(f"viewport image saved in {filePath}")

            self.filePath = filePath
            return filePath