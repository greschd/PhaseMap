"""
Helper fixtures for plot tests.
"""
# pylint: disable=unused-argument,redefined-outer-name

import tempfile

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.testing.compare import compare_images
import pytest


@pytest.fixture()
def disable_diff_save(monkeypatch):
    """
    Do not save the diff of images if the test fails.
    """

    def do_nothing(*args, **kwargs):
        pass

    monkeypatch.setattr(
        matplotlib.testing.compare, 'save_diff_image', do_nothing
    )


@pytest.fixture
def assert_image_equal(disable_diff_save, pytestconfig, test_name):
    """
    Save the current figure to a temporary file and check that it's the same as the reference image of the given name.
    """

    def inner(tol=1e-6):
        path = './reference_plots/' + test_name + '.png'
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            plt.savefig(path)
            raise ValueError('Reference plot did not exist.')
        else:
            with tempfile.NamedTemporaryFile(suffix='.png') as temp_file:
                plt.savefig(temp_file.name)
                assert compare_images(
                    path, temp_file.name, tol=tol, in_decorator=True
                ) is None

    return inner
