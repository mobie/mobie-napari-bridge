import numpy as np
import os
from .testutils import create_test_project, datasets

from mobie_napari_bridge._widget import (
    QFileDialog, QMessageBox, QInputDialog,
    LoadSource
)


def test_loadsource(make_napari_viewer, capsys, monkeypatch, tmp_path):
    class MockQFileDialog:
        @staticmethod
        def exec_():
            pass

        def getExistingDirectory(self, __):
            return tmp_path

    class MockQMessageBox(QMessageBox):
        def exec(self):
            print(self.text())

    class MockQInputDialog(QInputDialog):
        def getText(self, __, title, label):
            print(label)
            return label, True


    # Monkeypatch the QFileDialog.exec_() method with our mock implementation
    monkeypatch.setattr(QFileDialog, 'exec_', MockQFileDialog.exec_)
    monkeypatch.setattr(QFileDialog, 'getExistingDirectory', MockQFileDialog.getExistingDirectory)

    monkeypatch.setattr(QMessageBox, 'exec', MockQMessageBox.exec)
    monkeypatch.setattr(QInputDialog, 'getText', MockQInputDialog.getText)

    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()

    # create our widget, passing in the viewer
    my_widget = LoadSource(viewer)

    # call our widget methods

    # --------------------------------------------------------------------------------------
    # load project button

    my_widget._project_folder_button_click()

    # read captured output and check that the MessageBox has appeared
    captured = capsys.readouterr()

    assert captured.out == 'No MoBIE project found here.\n'
    assert my_widget.ds_dropdown.isHidden()
    assert my_widget.ds_caption.isHidden()

    create_test_project(str(tmp_path))

    # clear MoBIE stdout and stderr
    __ = capsys.readouterr()

    my_widget._project_folder_button_click()

    assert my_widget.ds_dropdown.isHidden() is False
    assert my_widget.ds_caption.isHidden() is False
    assert my_widget.mobie.datasets == datasets
    assert my_widget.ds_dropdown.count() == len(datasets)

    for idx, ds in enumerate(datasets):
        assert my_widget.ds_dropdown.itemText(idx) == ds

    #     --------------------------------------------------------------
    #     remote repository button

    # reset visibility
    my_widget.ds_dropdown.setVisible(False)
    my_widget.ds_caption.setVisible(False)

    my_widget._remote_project_button_click(test_url='wronglocation')

    # read captured output and check that the DialogBox has appeared
    captured = capsys.readouterr()

    assert captured.out == 'Repository URL:\nNo MoBIE project found here.\n'

    assert my_widget.ds_dropdown.isHidden()
    assert my_widget.ds_caption.isHidden()

    # clear MoBIE stdout and stderr
    __ = capsys.readouterr()

    my_widget._remote_project_button_click(test_url=str(tmp_path))

    assert my_widget.ds_dropdown.isHidden() is False
    assert my_widget.ds_caption.isHidden() is False
    assert my_widget.mobie.datasets == datasets
    assert my_widget.ds_dropdown.count() == len(datasets)

    for idx, ds in enumerate(datasets):
        assert my_widget.ds_dropdown.itemText(idx) == ds

    #     --------------------------------------------------------------
    #     select dataset

    assert my_widget.ds_dropdown.currentText() == 'ds1'
    my_widget.ds_dropdown.setCurrentIndex(1)
    assert my_widget.ds_dropdown.currentText() == 'ds2'

    assert my_widget.vg_dropdown.isHidden() is False
    assert my_widget.vg_caption.isHidden() is False

    assert my_widget.vg_dropdown.count() == 3  # default view in addition
    assert len(my_widget.mobie.allviews.keys()) == 3
    assert my_widget.vg_dropdown.itemText(0) == 'bookmark'
    assert 'bookmark' in my_widget.mobie.allviews.keys()

    for idx in range(2):
        assert my_widget.vg_dropdown.itemText(idx+1) == 'menu_im' + str(idx+1)
        assert 'menu_im' + str(idx+1) in my_widget.mobie.allviews.keys()

    newpath = os.path.join(tmp_path, 'single_viewgroup')
    create_test_project(newpath, single_view_group=True)
    my_widget._remote_project_button_click(test_url=newpath)

    assert my_widget.vg_dropdown.isHidden()
    assert my_widget.vg_caption.isHidden()

    assert my_widget.v_dropdown.count() == len(my_widget.mobie.views)


    #     --------------------------------------------------------------
    #     select view group

    my_widget._remote_project_button_click(test_url=tmp_path)
    my_widget.vg_dropdown.setCurrentIndex(1)

    assert len(my_widget.mobie.views) == len(my_widget.mobie.allviews['menu_im1']) == my_widget.v_dropdown.count()

    for idx, view in enumerate(my_widget.mobie.allviews['menu_im1']):
        assert my_widget.v_dropdown.itemText(idx) == my_widget.mobie.views[idx] == view

    #     --------------------------------------------------------------
    #     select view

    my_widget.v_dropdown.setCurrentIndex(0)
    assert len(my_widget.mobie.sources) == my_widget.source_list.count()

    for idx, source in enumerate(my_widget.mobie.sources):
        assert my_widget.source_list.item(idx) == source



