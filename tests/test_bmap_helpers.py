# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 et ai si
#
# Copyright (c) 2012-2014 Intel, Inc.
# License: GPLv2
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

"""
This test verifies 'BmapHelpers' module functionality.
"""

import os
import tempfile


from bmaptools import BmapHelpers
from backports import tempfile as btempfile
from mock import patch, MagicMock


# This is a work-around for Centos 6
try:
    import unittest2 as unittest  # pylint: disable=F0401
except ImportError:
    import unittest


class TestBmapHelpers(unittest.TestCase):
    """The test class for these unit tests."""

    def test_get_file_system_type(self):
        with tempfile.NamedTemporaryFile("r", prefix="testfile_",
                                         delete=True, dir=".", suffix=".img") as f:
            type = BmapHelpers.get_file_system_type(f.name)
            self.assertTrue(type)

    def test_get_file_system_type_nofstypefound(self):
        d = os.path.dirname(__file__)
        f = os.path.join(d, 'BmapHelpers/file/does/not/exist')
        with self.assertRaises(BmapHelpers.UnexpectedStateError):
            BmapHelpers.get_file_system_type(f)

    def test_get_file_system_type_symlink(self):
        with btempfile.TemporaryDirectory(prefix="testdir_", dir=".") as d:
            f = tempfile.NamedTemporaryFile("r", prefix="testfile_", delete=False,
                                            dir=d, suffix=".img")
            lnk = os.path.join(d, 'test_symlink')
            os.symlink(f.name, lnk)
            type = BmapHelpers.get_file_system_type(lnk)
            self.assertTrue(type)

    @patch.object(BmapHelpers, 'get_zfs_compat_param_path')
    def test_is_zfs_compatible_enabled(self, mock_zfs_param_path):
        with tempfile.NamedTemporaryFile("w+", prefix="testfile_",
                                         delete=True, dir=".", suffix=".img") as f:
            f.write("1")
            f.flush()
            mock_zfs_param_path.return_value = f.name
            self.assertTrue(BmapHelpers.is_zfs_compatible())

    @patch.object(BmapHelpers, 'get_zfs_compat_param_path')
    def test_is_zfs_compatible_disabled(self, mock_zfs_param_path):
        with tempfile.NamedTemporaryFile("w+", prefix="testfile_",
                                         delete=True, dir=".", suffix=".img") as f:
            f.write("0")
            f.flush()
            mock_zfs_param_path.return_value = f.name
            self.assertFalse(BmapHelpers.is_zfs_compatible())

    @patch.object(BmapHelpers, 'get_zfs_compat_param_path')
    def test_is_zfs_compatible_notinstalled(self, mock_zfs_param_path):
        d = os.path.dirname(__file__)
        mock_zfs_param_path.return_value = os.path.join(
            d, 'BmapHelpers/file/does/not/exist')
        self.assertFalse(BmapHelpers.is_zfs_compatible())

    @patch.object(BmapHelpers, 'get_file_system_type', return_value="zfs")
    @patch.object(BmapHelpers, 'get_zfs_compat_param_path')
    def test_is_compatible_file_system_zfs_valid(self, mock_zfs_param_path, mock_get_fs_type):
        with tempfile.NamedTemporaryFile("w+", prefix="testfile_",
                                         delete=True, dir=".", suffix=".img") as f:
            f.write("1")
            f.flush()
            mock_zfs_param_path.return_value = f.name
            self.assertTrue(BmapHelpers.is_compatible_file_system(f.name))

    @patch.object(BmapHelpers, 'get_file_system_type', return_value="zfs")
    @patch.object(BmapHelpers, 'get_zfs_compat_param_path')
    def test_is_compatible_file_system_zfs_invalid(self, mock_zfs_param_path, mock_get_fs_type):
        with tempfile.NamedTemporaryFile("w+", prefix="testfile_",
                                         delete=True, dir=".", suffix=".img") as f:
            f.write("0")
            f.flush()
            mock_zfs_param_path.return_value = f.name
            self.assertFalse(BmapHelpers.is_compatible_file_system(f.name))

    @patch.object(BmapHelpers, 'get_file_system_type', return_value="ext4")
    def test_is_compatible_file_system_ext4(self, mock_get_fs_type):
        with tempfile.NamedTemporaryFile("w+", prefix="testfile_",
                                         delete=True, dir=".", suffix=".img") as f:

            self.assertTrue(BmapHelpers.is_compatible_file_system(f.name))


    def test_get_mount_point(self):
         with tempfile.NamedTemporaryFile("w+", prefix="testfile_",
                                         delete=True, dir=".", suffix=".img") as f:
            f = BmapHelpers.get_mount_point(f.name)
            self.assertIsNotNone(f)
            self.assertTrue(f.strip())