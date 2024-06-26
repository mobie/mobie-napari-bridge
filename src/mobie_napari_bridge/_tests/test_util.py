import os
import pytest
import numpy as np

from mobie_napari_bridge.util import (is_mobie_project, s3link, check_image_source,
                                      MoBIEState, find_same_extent, tmpdir)


def test_is_mobie_project(tmp_path):
    # create dummy project
    targetpath = os.path.join(tmp_path, 'testmobieproject', 'data')
    os.makedirs(targetpath)

    with open(os.path.join(targetpath, 'project.json'), 'w') as f:
        f.write('{}')

    # test non-existing path
    assert is_mobie_project(os.path.join(tmp_path, 'thispathdoesnotexists')) == (False, '', False)

    # test path without MoBIE project
    assert is_mobie_project(tmp_path) == (False, '', False)

    # test parent MoBIE path
    assert is_mobie_project(os.path.join(tmp_path, 'testmobieproject')) == (True, targetpath, False)

    # test full path
    assert is_mobie_project(targetpath, remote=True) == (True, targetpath, True)

    # test wrong github
    assert is_mobie_project('github.com/notexistingrepository') == (False, '', False)

    # test existing github but no MoBIE project
    url = 'https://github.com/mobie/mobie.io'
    assert is_mobie_project(url) == (False, '', False)

    # test good github
    url = 'https://github.com/mobie/clem-example-project'
    localdir = os.path.join(tmpdir,'data')
    assert is_mobie_project(url.lstrip('https://')) == (True, localdir, True)
    assert is_mobie_project(url) == (True, localdir, True)


def test_s3link():
    #     test wrong dict
    wrongdict = {'wrong_key': None}
    with pytest.raises(KeyError):
        __ = s3link(wrongdict)

    targetaddress = 'https://s3targetaddress/test/'
    gooddict = {'s3Address': targetaddress}

    assert s3link(gooddict) == targetaddress.rstrip('/')


def test_check_image_source(tmp_path):
    # test unsupported type
    assert check_image_source('n5', {'ome.zarr': {}}, '') is None

    # test not existing local directory:
    zpath = os.path.join(tmp_path, 'test.ome.zarr')
    local_metadata = {'ome.zarr': {'relativePath': './test.ome.zarr'}}

    assert check_image_source('ome.zarr', local_metadata, tmp_path) is None

    # test local OME-Zarr
    os.makedirs(zpath)
    with open(os.path.join(zpath, '.zattrs'), 'w') as f:
        f.write('{}')

    assert check_image_source('ome.zarr', local_metadata, tmp_path) == zpath

    # test remote OME-Zarr
    targetaddress = 'https://s3targetaddress/test/'
    remote_metadata = {'ome.zarr.s3': {'s3Address': targetaddress}}
    remote_metadata.update(local_metadata)

    assert check_image_source('ome.zarr.s3', remote_metadata, tmp_path) is None

    targetaddress = 'https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.1/6001240.zarr/'
    remote_metadata['ome.zarr.s3']['s3Address'] = targetaddress

    assert check_image_source('ome.zarr.s3', remote_metadata, tmp_path) == targetaddress.rstrip('/')


def test_mobiestate_to_napari_layer_metadata():
    mstate = MoBIEState()
    mstate.project_root = 'root'

    assert mstate.to_napari_layer_metadata() == {"MoBIE": {
        "project_root": 'root',
        "dataset": None,
        "ds_name": '',
        "view": {},
        "display": {}
    }
    }


def test_mobiestate_update_napari_image_layer(make_napari_viewer):
    mstate = MoBIEState()
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((100, 100)), name='testimage')

    mstate.display['imageDisplay'] = {'contrastLimits': [0, 255.],
                                      'opacity': 0.12345,
                                      'visible': False}

    # check contrast not being updated
    old_contrast = viewer.layers['testimage'].contrast_limits

    mstate.update_napari_image_layer(viewer.layers['testimage'])

    assert old_contrast == viewer.layers['testimage'].contrast_limits

    # check updated values
    mstate.display['imageDisplay']['contrastLimits'] = [0.1, 3.4567]
    mstate.update_napari_image_layer(viewer.layers['testimage'])

    assert viewer.layers['testimage'].contrast_limits == mstate.display['imageDisplay']['contrastLimits']
    assert viewer.layers['testimage'].opacity == mstate.display['imageDisplay']['opacity']
    assert viewer.layers['testimage'].visible == mstate.display['imageDisplay']['visible']


def test_find_same_extent(make_napari_viewer):
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((100, 100)), name='t0_100')
    viewer.add_image(np.random.random((100, 100)), name='t1_100')
    viewer.add_image(np.random.random((100, 100)), name='target_100')
    viewer.add_image(np.random.random((101, 101)), name='t0_101')

    assert find_same_extent(viewer.layers, 'target_100') == ['t0_100', 't1_100']
    assert find_same_extent(viewer.layers, 't0_101') == []
    with pytest.raises(KeyError):
        find_same_extent(viewer.layers, 'target_101')