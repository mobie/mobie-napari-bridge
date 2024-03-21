"""
utility functions to handle MoBIE projects in napari
"""

import os
import requests


class MoBIEState(object):
    """
    Necessary metadata to actively work within a MoBIE project.
    """
    def __init__(self):
        self.project_root = None
        self.datasets = []
        self.dataset = None
        self.imported_dataset = None
        self.ds_name = ''
        self.views = []
        self.sources = []
        self.view = {}
        self.allviews = dict()
        self.view_groups = []
        self.displays = []
        self.display = {}

    def to_napari_layer_metadata(self):
        """
        Generates relevant MoBIE metadata for serialized storage in a napari layer.

        Returns
        -------
        dict
        The metadata dictionary under the key "MoBIE".

        """
        return {"MoBIE": {
            "project_root": self.project_root,
            "dataset": self.imported_dataset,
            "ds_name": self.ds_name,
            "view": self.view,
            "display": self.display
        }
        }

    def update_napari_image_layer(self, layer):
        if 'imageDisplay' in self.display.keys():
            disp = self.display['imageDisplay']
            if disp['contrastLimits'] not in ([0, 255], [0, 65535]):
                layer.contrast_limits = disp['contrastLimits']
            layer.opacity = disp['opacity']
            layer.visible = disp['visible']


def is_mobie_project(path):
    """
    Checks if a given path contains a MoBIE project. Can be at top level or in the `data` sub-folder.

    Parameters
    ----------
    path : os.PathLike The path to check.

    Returns
    -------
    (bool, str)
    True if a MoBIE project structure is found and the complete path to the MoBIE project or if not: (False, '').
    """

    if os.path.isdir(path):
        if 'project.json' in os.listdir(path):
            return True, path
        elif os.path.isdir(os.path.join(path, 'data')):
            if 'project.json' in os.listdir(os.path.join(path, 'data')):
                return True, os.path.join(path, 'data')

    return False, ''


def s3link(indict):
    """

    Parameters
    ----------
    indict : dict The MoBIE definitions dictionary of an S3 source.

    Returns
    -------
    str
    The full URL to the source for an S3 reader to open.
    """
    url = indict['s3Address']
    return url


def check_image_source(src_type, im_metadata, ds_path):
    """

    Parameters
    ----------
    src_type : str Source type specifier
    im_metadata : dict image source dictionary defining the links to original data
    ds_path : str full path of the dataset (local file system).

    Returns
    -------
    (str, None)
    Path to the image that napari reader(s) can open or None if not possible.

    """
    if src_type not in im_metadata.keys():
        return None

    if src_type == 'ome.zarr.s3':
        if requests.get(s3link(im_metadata[src_type]) + '/.zattrs').ok:
            return s3link(im_metadata[src_type])

    elif src_type == 'ome.zarr':
        zpath = os.path.join(ds_path,
                             im_metadata[src_type]['relativePath'].lstrip('./').replace('/', os.pathsep))
        if os.path.exists(zpath) and os.path.exists(os.path.join(zpath, '.zattrs')):
            return zpath

    else:
        return None
