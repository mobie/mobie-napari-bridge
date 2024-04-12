import numpy as np

from mobie_napari_bridge._widget import (
    LoadSource
)

def test_loadsource(make_napari_viewer, capsys):
    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()

    # create our widget, passing in the viewer
    my_widget = LoadSource(viewer)

    # call our widget method
    my_widget._button_click()



