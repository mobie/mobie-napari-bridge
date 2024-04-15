import numpy as np
import os
from .testutils import create_test_project, datasets

from mobie_napari_bridge._widget import (
    QFileDialog, QMessageBox,
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

    # Monkeypatch the QFileDialog.exec_() method with our mock implementation
    monkeypatch.setattr(QFileDialog, 'exec_', MockQFileDialog.exec_)
    monkeypatch.setattr(QFileDialog, 'getExistingDirectory', MockQFileDialog.getExistingDirectory)

    monkeypatch.setattr(QMessageBox, 'exec', MockQMessageBox.exec)

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



