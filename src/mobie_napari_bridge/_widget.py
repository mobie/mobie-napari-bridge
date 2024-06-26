"""

"""
import os
import copy

from typing import TYPE_CHECKING
from mobie_napari_bridge.util import is_mobie_project, MoBIEState, find_same_extent, get_link

from qtpy.QtWidgets import (QFileDialog, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QInputDialog,
                            QPushButton, QWidget, QListWidget, QComboBox, QMessageBox, QAbstractItemView)

if TYPE_CHECKING:
    import napari

from napari import layers


class LoadSource(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # use a type annotation of 'napari.viewer.Viewer' for any parameter

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.mobie = MoBIEState()

        self.loadproj_btn = QPushButton("Select MoBIE project Folder")
        self.loadproj_btn.clicked.connect(self._project_folder_button_click)

        self.remote_proj_btn = QPushButton("Select MoBIE repository")
        self.remote_proj_btn.clicked.connect(self._remote_project_button_click)

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

        self.setLayout(QVBoxLayout())

        self.layout().addWidget(self.loadproj_btn)
        self.layout().addWidget(self.remote_proj_btn)
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

    def _project_folder_button_click(self):
        import mobie.metadata as mm

        dlg1 = QFileDialog()
        self.mobie.project_root = dlg1.getExistingDirectory(None)

        isproject, self.mobie.project_root, __ = is_mobie_project(self.mobie.project_root)

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

    def _remote_project_button_click(self, test_url=None):
        import mobie.metadata as mm

        dlg2 = QInputDialog()
        inurl, ok = dlg2.getText(self, 'Open MoBIE repository', 'Repository URL:')

        if test_url:
            inurl = test_url

        if not ok:
            return

        isproject, self.mobie.project_root, isremote = is_mobie_project(inurl)

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

            if isremote:
                self.mobie.remote_root = inurl

    def _ds_select(self, ds_name):
        import mobie.metadata as mm

        self.mobie.dataset = mm.dataset_metadata.read_dataset_metadata(os.path.join(self.mobie.project_root, ds_name))
        self.mobie.ds_name = ds_name

        self.mobie.allviews = dict()
        self.mobie.view_groups = []

        self.vg_dropdown.hide()
        self.vg_caption.hide()

        if 'views' not in self.mobie.dataset.keys():  # pragma: no cover
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
            self.vg_dropdown.show()
            self.vg_caption.show()
            self.vg_dropdown.clear()
            self.vg_dropdown.addItems(self.mobie.view_groups)

        else:
            self.mobie.views = list(self.mobie.dataset['views'].keys())

            self.vg_dropdown.hide()
            self.vg_caption.hide()
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
        if view_name not in self.mobie.dataset['views'].keys():  # pragma: no cover
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

            if thissource not in self.mobie.dataset['sources'].keys():  # pragma: no cover
                raise ValueError('Wrong dataset!')

            s_meta = self.mobie.dataset['sources'][thissource]
            ds_path = os.path.join(self.mobie.project_root, self.mobie.ds_name)

            if 'image' in s_meta.keys():
                im_links = s_meta['image']['imageData']

                imlink = get_link(im_links, ds_path, remote=any((self.remote_checkbox.isChecked(),
                                                                 self.mobie.remote_root is not None)))

                if imlink is not None:
                    self.mobie.display = thisdisp
                    self.viewer.open(imlink, plugin="napari-ome-zarr",
                                     name=thissource,
                                     metadata=self.mobie.to_napari_layer_metadata())
                    self.mobie.update_napari_image_layer(self.viewer.layers[thissource])

            elif 'segmentation' in s_meta.keys():
                im_links = s_meta['segmentation']['imageData']

                imlink = get_link(im_links, ds_path, remote=self.remote_checkbox.isChecked())

                if imlink is not None:
                    self.mobie.display = thisdisp
                    self.viewer.open(imlink, plugin="napari-ome-zarr",
                                     name=thissource,
                                     metadata=self.mobie.to_napari_layer_metadata(),
                                     layer_type="labels")
                    pass

            self.mobie.imported_sources = sel_sources

class Layer2MoBIE(QWidget):

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer

        self.add_btn = QPushButton("Add selected layer(s) to MoBIE project")
        self.add_btn.clicked.connect(self._addbtn_click)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.add_btn)

    def _addbtn_click(self):
        import mobie.metadata as mm

        if len(self.viewer.layers.selection) < 1:
            no_layer = QMessageBox()
            no_layer.setText("No layer(s) selected.")
            no_layer.exec()
            return

        newlayers = list()

        for layer in list(self.viewer.layers.selection):
            if 'MoBIE' not in layer.metadata.keys():
                p_layers = find_same_extent(self.viewer.layers, layer.name)

                if len(p_layers) < 1:
                    continue
                else:
                    layer.metadata['MoBIE'] = copy.deepcopy(self.viewer.layers[p_layers[0]].metadata['MoBIE'])
                    view = layer.metadata['MoBIE']['view']
                    ds_path = os.path.join(layer.metadata['MoBIE']['project_root'], layer.metadata['MoBIE']['ds_name'])
                    if type(layer) is layers.labels.labels.Labels:
                        mm.add_regions_to_dataset(ds_path, layer.name, layer.features) # WHY IS THE FEATURES EMPTY FOR PAINTED LAYERS?

                    elif type(layer) is layers.image.image.Image:
                        pass
                    else:
                        no_supplayer = QMessageBox()
                        no_supplayer.setText("Layer " + layer.names + " not of supported type!")
                        no_supplayer.exec()
                        continue

                    newlayers.append(layer)

        if len(newlayers) < 1:
            no_nlayer = QMessageBox()
            no_nlayer.setText("No new layer(s) selected or no parent imported MoBIE layers found.")
            no_nlayer.exec()
            return
