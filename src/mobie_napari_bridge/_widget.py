"""

"""
import os

from typing import TYPE_CHECKING
from mobie_napari_bridge.util import is_mobie_project

from qtpy.QtWidgets import (QFileDialog, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel,
                            QPushButton, QWidget, QComboBox, QMessageBox)

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
        self.datasets = []
        self.dataset = None
        self.views = []

        self.loadproj_btn = QPushButton("Select MoBIE project Folder")
        self.loadproj_btn.clicked.connect(self._button_click)

        self.ds_caption = QLabel("Select dataset:")
        self.ds_caption.setVisible(False)
        self.ds_dropdown = QComboBox()
        self.ds_dropdown.currentTextChanged.connect(self._ds_select)
        self.ds_dropdown.setVisible(False)


        self.v_caption = QLabel("Select view:")
        self.v_caption.setVisible(False)
        self.v_dropdown = QComboBox()
        # self.v_dropdown.currentTextChanged.connect(self._ds_select)
        self.v_dropdown.setVisible(False)

        self.setLayout(QVBoxLayout())
        # self.setLayout(QGridLayout())
        # self.layout().setColumnStretch(1, 4)
        # self.layout().setColumnStretch(2, 1)
        self.layout().addWidget(self.loadproj_btn)
        self.layout().addWidget(self.ds_caption)
        self.layout().addWidget(self.ds_dropdown)
        self.layout().addWidget(self.v_caption)
        self.layout().addWidget(self.v_dropdown)

    def _button_click(self):
        import mobie.metadata as mm

        dlg1 = QFileDialog()
        self.project_root = dlg1.getExistingDirectory(None)

        isproject, subpath = is_mobie_project(self.project_root)
        self.project_root = os.path.join(self.project_root, subpath)

        if not isproject:
            no_proj = QMessageBox()
            no_proj.setText("No MoBIE project found here.")
            no_proj.exec()
        else:
            self.datasets = mm.get_datasets(self.project_root)
            self.ds_dropdown.show()
            self.ds_caption.show()
            self.ds_dropdown.clear()
            self.ds_dropdown.addItems(self.datasets)



    def _ds_select(self, ds_name):
        import mobie.metadata as mm

        self.dataset = mm.dataset_metadata.read_dataset_metadata(os.path.join(self.project_root, ds_name))

        self.views = list(self.dataset['views'].keys())
        self.v_dropdown.show()
        self.v_caption.show()
        self.v_dropdown.clear()
        self.v_dropdown.addItems(self.views)


