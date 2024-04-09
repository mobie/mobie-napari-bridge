"""

"""
import os
import copy

from typing import TYPE_CHECKING
from mobie_napari_bridge.util import is_mobie_project, check_image_source, MoBIEState, find_same_extent

from qtpy.QtWidgets import (QFileDialog, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox,
                            QPushButton, QWidget, QListWidget, QComboBox, QMessageBox, QAbstractItemView)

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


class LoadSource(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # use a type annotation of 'napari.viewer.Viewer' for any parameter

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.mobie = MoBIEState()

        self.loadproj_btn = QPushButton("Select MoBIE project Folder")
        self.loadproj_btn.clicked.connect(self._button_click)

        self.ds_caption = QLabel("Select dataset:")
        self.ds_caption.setVisible(False)
        self.ds_dropdown = QComboBox()
        self.ds_dropdown.currentTextChanged.connect(self._ds_select)
        self.ds_dropdown.setVisible(False)

        self.vg_caption = QLabel("Select view group:")
        self.vg_caption.setVisible(False)
        self.vg_dropdown = QComboBox()
        self.vg_dropdown.currentTextChanged.connect(self._vg_select)
        self.vg_dropdown.setVisible(False)

        self.v_caption = QLabel("Select view:")
        self.v_caption.setVisible(False)
        self.v_dropdown = QComboBox()
        self.v_dropdown.currentTextChanged.connect(self._v_select)
        self.v_dropdown.setVisible(False)

        self.sl_caption = QLabel("Select source(s):")
        self.sl_caption.setVisible(False)
        self.source_list = QListWidget()
        self.source_list.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )
        self.source_list.setVisible(False)
        self.source_btn = QPushButton("Load selected source(s) in napari")
        self.source_btn.clicked.connect(self._srcbtn_click)
        self.source_btn.setVisible(False)

        self.remote_checkbox = QCheckBox('Prefer remote data if available')
        self.remote_checkbox.setVisible(False)

        self.add_btn = QPushButton("Add selected layer(s) to MoBIE project")
        self.add_btn.clicked.connect(self._addbtn_click)
        self.add_btn.setVisible(False)

        self.setLayout(QVBoxLayout())

        self.layout().addWidget(self.loadproj_btn)
        self.layout().addWidget(self.ds_caption)
        self.layout().addWidget(self.ds_dropdown)
        self.layout().addWidget(self.vg_caption)
        self.layout().addWidget(self.vg_dropdown)
        self.layout().addWidget(self.v_caption)
        self.layout().addWidget(self.v_dropdown)
        self.layout().addWidget(self.sl_caption)
        self.layout().addWidget(self.source_list)
        self.layout().addWidget(self.source_btn)
        self.layout().addWidget(self.remote_checkbox)
        self.layout().addWidget(self.add_btn)

    def _button_click(self):
        import mobie.metadata as mm

        dlg1 = QFileDialog()
        self.mobie.project_root = dlg1.getExistingDirectory(None)

        isproject, self.mobie.project_root = is_mobie_project(self.mobie.project_root)

        if not isproject:
            no_proj = QMessageBox()
            no_proj.setText("No MoBIE project found here.")
            no_proj.exec()
        else:
            self.mobie.datasets = mm.get_datasets(self.mobie.project_root)
            self.ds_dropdown.show()
            self.ds_caption.show()
            self.ds_dropdown.clear()
            self.ds_dropdown.addItems(self.mobie.datasets)

    def _ds_select(self, ds_name):
        import mobie.metadata as mm

        self.mobie.dataset = mm.dataset_metadata.read_dataset_metadata(os.path.join(self.mobie.project_root, ds_name))
        self.mobie.ds_name = ds_name

        self.mobie.allviews = dict()
        self.mobie.view_groups = []

        self.vg_dropdown.hide()
        self.vg_caption.hide()

        if 'views' not in self.mobie.dataset.keys():
            self.v_dropdown.hide()
            self.v_caption.hide()
            return

        for viewname, view in self.mobie.dataset['views'].items():
            if view['uiSelectionGroup'] not in self.mobie.view_groups:
                self.mobie.view_groups.append(view['uiSelectionGroup'])
                self.mobie.allviews[view['uiSelectionGroup']] = [viewname]
            else:
                self.mobie.allviews[view['uiSelectionGroup']].append(viewname)

        if len(self.mobie.view_groups) != 1:
            self.v_dropdown.hide()
            self.v_caption.hide()

            self.vg_dropdown.show()
            self.vg_caption.show()
            self.vg_dropdown.clear()
            self.vg_dropdown.addItems(self.mobie.view_groups)

        else:
            self.mobie.views = list(self.mobie.dataset['views'].keys())

            self.v_dropdown.show()
            self.v_caption.show()
            self.v_dropdown.clear()
            self.v_dropdown.addItems(self.mobie.views)

    def _vg_select(self, vg_name):
        if vg_name not in self.mobie.view_groups:
            return

        self.mobie.views = list(self.mobie.allviews[vg_name])

        self.v_dropdown.show()
        self.v_caption.show()
        self.v_dropdown.clear()
        self.v_dropdown.addItems(self.mobie.views)

    def _v_select(self, view_name):
        if view_name not in self.mobie.dataset['views'].keys():
            return

        self.mobie.sources = []
        self.mobie.displays = []
        self.mobie.view = self.mobie.dataset['views'][view_name]

        for disp in self.mobie.view['sourceDisplays']:
            if 'imageDisplay' in disp.keys():
                sources = disp['imageDisplay']['sources']

            elif 'regionDisplay' in disp.keys():
                sources = [item for entry in disp['regionDisplay']['sources'].values() for item in entry]

            elif 'segmentationDisplay' in disp.keys():
                sources = disp['segmentationDisplay']['sources']

            else:
                sources = []

            for source in sources:
                if source not in self.mobie.sources:
                    self.mobie.sources.append(source)
                    self.mobie.displays.append(disp)

        self.source_list.show()
        self.sl_caption.show()

        self.source_btn.show()
        self.remote_checkbox.show()
        self.add_btn.show()

        self.source_list.clear()
        self.source_list.addItems(self.mobie.sources)

    def _srcbtn_click(self):
        sel_source_items = self.source_list.selectedIndexes()

        if len(sel_source_items) < 1:
            no_src = QMessageBox()
            no_src.setText("No source(s) selected.")
            no_src.exec()
            return

        sel_sources = []
        self.mobie.imported_dataset = copy.deepcopy(self.mobie.dataset)

        for item in sel_source_items:
            thissource = item.data()
            thisdisp = self.mobie.displays[item.row()]

            sel_sources.append(thissource)

            if thissource not in self.mobie.dataset['sources'].keys():
                raise ValueError('Wrong dataset!')

            s_meta = self.mobie.dataset['sources'][thissource]
            ds_path = os.path.join(self.mobie.project_root, self.mobie.ds_name)

            if 'image' in s_meta.keys():
                im_links = s_meta['image']['imageData']

                if 'ome.zarr.s3' not in im_links.keys() and 'ome.zarr' not in im_links.keys():
                    no_zarr = QMessageBox()
                    no_zarr.setText("Import only possible for OME-Zarr sources.")
                    no_zarr.exec()
                    continue
                    # raise ValueError('Wrong image format!')

                if self.remote_checkbox.isChecked():
                    imlink = check_image_source('ome.zarr.s3', im_links, ds_path)
                else:
                    imlink = check_image_source('ome.zarr', im_links, ds_path)

                # loop through all possible source paths if preferred one is not found
                idx = 0
                while imlink is None and idx < len(im_links.keys()):
                    link_type = list(im_links.keys())[idx]
                    imlink = check_image_source(link_type, im_links, ds_path)
                    idx += 1

                if imlink is not None:
                    self.mobie.display = thisdisp
                    self.viewer.open(imlink, plugin="napari-ome-zarr",
                                     name=thissource,
                                     metadata=self.mobie.to_napari_layer_metadata())
                    self.mobie.update_napari_image_layer(self.viewer.layers[thissource])

    def _addbtn_click(self):
        if len(self.viewer.layers.selection) < 1:
            no_layer = QMessageBox()
            no_layer.setText("No layer(s) selected.")
            no_layer.exec()
            return

        newlayers = list()

        for layer in self.viewer.layers.selection:
            if 'MoBIE' not in layer.metadata.keys():
                p_layers = find_same_extent(self.viewer.layers, layer.name)

                if len(p_layers) < 1:
                    continue
                else:
                    layer.metadata['MoBIE'] = copy.deepcopy(self.viewer.layers[p_layers[0]].metadata['MoBIE'])
                    newlayers.append(layer)



        if len(newlayers) < 1:
            no_nlayer = QMessageBox()
            no_nlayer.setText("No new layer(s) selected or no parent imported MoBIE layers found.")
            no_nlayer.exec()
            return