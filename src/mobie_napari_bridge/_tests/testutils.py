from mobie import add_image
import os
import numpy as np

datasets = ['ds1', 'ds2']
def create_test_project(root, single_view_group=False):
    for ds in datasets:
        for im_name in ['im1', 'im2']:
            im = np.random.rand(128, 128)
            vg_name = 'menu_'+im_name
            if single_view_group:
                vg_name = 'bookmark'
            add_image(im, '', root, ds, im_name, [1, 1], [[1, 1]], [128, 128],
                      menu_name=vg_name, tmp_folder=os.path.join(root, 'tmp_'+ds+im_name))
