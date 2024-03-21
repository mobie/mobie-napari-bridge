"""
utility functions
"""

import os
import requests


# import metadata as mm

class MoBIEState(object):
    def __init__(self):
        self.project_root = None
        self.datasets = []
        self.dataset = None
        self.imported_dataset = None
        self.ds_name = ''
        self.views = []
        self.sources = []
        self.view = []
        self.allviews = dict()
        self.view_groups = []
        self.displays = []
        self.display = []

    def to_napari_layer_metadata(self):
        return {
            "project_root": self.project_root,
            "dataset": self.imported_dataset,
            "ds_name": self.ds_name,
            "view": self.view,
            "display": self.display
        }

    def update_napari_image_layer(self, layer):
        if 'imageDisplay' in self.display.keys():
            disp = self.display['imageDisplay']
            layer.contrast_limits = disp['contrastLimits']
            layer.opacity = disp['opacity']
            layer.visible = disp['visible']



def is_mobie_project(path: os.PathLike) -> (bool, str):
    """

    Parameters
    ----------
    path : os.PathLike

    Returns
    -------
    (bool, str)

    """

    if os.path.isdir(path):
        if 'project.json' in os.listdir(path):
            return True, ''
        elif os.path.isdir(os.path.join(path, 'data')):
            if 'project.json' in os.listdir(os.path.join(path, 'data')):
                return True, 'data'

    return False, ''


def s3link(indict):
    url = indict['s3Address']
    return url


def check_image_source(src_type, im_metadata, ds_path):
    if src_type not in im_metadata.keys():
        return None

    if src_type == 'ome.zarr.s3':
        if requests.get(s3link(im_metadata[src_type]) + '/.zattrs').ok:
            return s3link(im_metadata[src_type])

    elif src_type == 'ome.zarr':
        zpath = os.path.join(ds_path, im_metadata[src_type]['relativePath'])
        if os.path.exists(zpath):
            return zpath

    else:
        return None
