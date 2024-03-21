import os

from mobie_napari_bridge.util import is_mobie_project, check_image_source, MoBIEState


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


def test_check_image_source(tmp_path):
    pass