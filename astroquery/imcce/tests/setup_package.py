# Licensed under a 3-clause BSD style license - see LICENSE.rst


import os


def get_package_data():
    paths = [os.path.join('data', '*.dat'),
             os.path.join('data', '*.vot')]

    return {'astroquery.imcce.tests': paths}
