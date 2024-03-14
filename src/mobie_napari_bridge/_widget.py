"""

"""
from typing import TYPE_CHECKING

from magicgui import magic_factory
from magicgui.widgets import CheckBox, Container, create_widget
from qtpy.QtWidgets import QFileDialog, QHBoxLayout, QPushButton, QWidget, QComboBox
from skimage.util import img_as_float

if TYPE_CHECKING:
    import napari


class ExampleQWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer

        btn = QPushButton("Click me!")
        btn.clicked.connect(self._on_click)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(btn)

    def _on_click(self):
        print("napari has", len(self.viewer.layers), "layers")


class TestBrowse(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.project_root = None

        self.loadproj_btn = QPushButton("Select MoBIE project Folder")
        self.loadproj_btn.clicked.connect(self._button_click)

        self.ds_dropdown = QComboBox()

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.loadproj_btn)

    def _button_click(self):
        dlg1 = QFileDialog()
        self.project_root = dlg1.getExistingDirectory(None)

        self.ds_dropdown.addItems(['1', '2'])
        self.layout().addWidget(self.ds_dropdown)

        print(self.project_root)
