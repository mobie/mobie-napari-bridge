"""
utility functions
"""

import os

# import mobie.metadata as mm


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

