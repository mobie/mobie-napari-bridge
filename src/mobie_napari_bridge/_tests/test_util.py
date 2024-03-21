import os
import pytest

from mobie_napari_bridge.util import is_mobie_project, s3link, check_image_source, MoBIEState


def test_is_mobie_project(tmp_path):
    # create dummy project
    targetpath = os.path.join(tmp_path, 'testmobieproject', 'data')
    os.makedirs(targetpath)

    with open(os.path.join(targetpath, 'project.json'), 'w') as f:
        f.write('{}')

    # test non-existing path
    assert is_mobie_project(os.path.join(tmp_path, 'thispathdoesnotexists')) == (False, '')

    # test path without MoBIE project
    assert is_mobie_project(tmp_path) == (False, '')

    # test parent MoBIE path
    assert is_mobie_project(os.path.join(tmp_path, 'testmobieproject')) == (True, targetpath)

    # test full path
    assert is_mobie_project(targetpath) == (True, targetpath)


def test_s3link():
    #     test wrong dict
    wrongdict = {'wrong_key': None}
    with pytest.raises(KeyError):
        __ = s3link(wrongdict)

    targetaddress = 'https://s3targetaddress/test/'
    gooddict = {'s3Address': targetaddress}

    assert s3link(gooddict) == targetaddress


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
