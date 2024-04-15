"""
utility functions to handle MoBIE projects in napari
"""

import os
import shutil
import requests
import numpy as np
from git import Repo

from qtpy.QtWidgets import QMessageBox

tmpdir = os.path.join(os.getcwd(), 'tmp_MoBIE_project')


class MoBIEState(object):
    """
    Necessary metadata to actively work within a MoBIE project.
    """

    def __init__(self):
        self.project_root = None
        self.remote_root = None
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
            if disp['contrastLimits'] not in ([0, 255]):
                layer.contrast_limits = disp['contrastLimits']
            if 'opacity' in disp.keys():
                layer.opacity = disp['opacity']
            if 'visible' in disp.keys():
                layer.visible = disp['visible']


def is_mobie_project(path, remote=False):
    """
    Checks if a given path contains a MoBIE project. Can be at top level or in the `data` sub-folder.

    Parameters
    ----------
    path : str The path/URL to check.
    remote : bool whether the project resides on a remote (github)

    Returns
    -------
    (bool, str, bool)
    - True if a MoBIE project structure is found
    - the complete path to the MoBIE project or if not: (False, '').
    - True if remote repository
    """

    if os.path.isdir(path):
        if 'project.json' in os.listdir(path):
            return True, path, remote
        elif os.path.isdir(os.path.join(path, 'data')):
            if 'project.json' in os.listdir(os.path.join(path, 'data')):
                return True, os.path.join(path, 'data'), remote
        else:
            return False, '', False

    elif 'github.com' in path:
        if path.startswith('https:'):
            repo_url = path
        elif path.startswith('github.com'):
            repo_url = 'https://' + path
        else:
            return False, '', False

        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

        try:
            Repo.clone_from(repo_url, tmpdir,   depth=1, single_branch=True)
        except:
            return False, '', False

        return is_mobie_project(tmpdir, remote=True)

    else:
        return False, '', False


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
    url = indict['s3Address'].rstrip('/')
    return url


def check_image_source(src_type, im_metadata, ds_path):
    """

    Parameters
    ----------
    src_type : str Source type specifier
    im_metadata : dict image source dictionary defining the links to original data
    ds_path : str Full path of the dataset (local file system).

    Returns
    -------
    (str, None)
    Path to the image that napari reader(s) can open or None if not possible.

    """
    if src_type not in im_metadata.keys():
        return None

    if src_type == 'ome.zarr.s3':
        try:
            a = requests.get(s3link(im_metadata[src_type]) + '/.zattrs')
            if a.ok:
                return s3link(im_metadata[src_type])
        except:
            return None

    elif src_type == 'ome.zarr':
        zpath = os.path.join(ds_path,
                             im_metadata[src_type]['relativePath'].lstrip('./').replace('/', os.path.sep))
        if os.path.exists(zpath) and os.path.exists(os.path.join(zpath, '.zattrs')):
            return zpath

    else:
        return None


def get_link(im_links, ds_path, remote=False):
    """

    Parameters
    ----------
    im_links : dict The MoBIE source dictionary
    ds_path : str Path of dataset
    remote : object Whether remote sources are preferred.

    Returns
    -------
    object

    """
    if 'ome.zarr.s3' not in im_links.keys() and 'ome.zarr' not in im_links.keys():
        no_zarr = QMessageBox()
        no_zarr.setText("Import only possible for OME-Zarr sources.")
        no_zarr.exec()
        return None
        # raise ValueError('Wrong image format!')

    if remote:
        imlink = check_image_source('ome.zarr.s3', im_links, ds_path)
    else:
        imlink = check_image_source('ome.zarr', im_links, ds_path)

    # loop through all possible source paths if preferred one is not found
    idx = 0
    while (imlink is None and idx < len(im_links.keys())):
        link_type = list(im_links.keys())[idx]
        imlink = check_image_source(link_type, im_links, ds_path)
        idx += 1

    return imlink


def find_same_extent(layers, target_name):
    """

    Parameters
    ----------
    layers : napari.viewer.Viewer.layers The napari viewer layers to screen.
    target_name : str The layer name to find a match.

    Returns
    -------
    list(str)
    The matching layer(s) name(s).
    """

    extent = layers[target_name].extent
    result = list()

    for layer in layers:
        if all([np.all(layer.extent[i] == extent[i]) for i in range(len(extent))]):
            if layer.name != target_name:
                result.append(layer.name)

    return result
