#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os

import mock
from oslo_concurrency import processutils

from nova.tests.unit.virt.libvirt.volume import test_volume
from nova import utils
from nova.virt.libvirt import utils as libvirt_utils
from nova.virt.libvirt.volume import glusterfs


class LibvirtGlusterfsVolumeDriverTestCase(
        test_volume.LibvirtVolumeBaseTestCase):

    @mock.patch.object(libvirt_utils, 'is_mounted', return_value=False)
    def test_libvirt_glusterfs_driver(self, mock_is_mounted):
        mnt_base = '/mnt'
        self.flags(glusterfs_mount_point_base=mnt_base, group='libvirt')

        libvirt_driver = glusterfs.LibvirtGlusterfsVolumeDriver(self.fake_host)
        export_string = '192.168.1.1:/volume-00001'
        export_mnt_base = os.path.join(mnt_base,
                utils.get_hash_str(export_string))

        connection_info = {'data': {'export': export_string,
                                    'name': self.name}}
        libvirt_driver.connect_volume(connection_info, self.disk_info,
                                      mock.sentinel.instance)
        libvirt_driver.disconnect_volume(connection_info, "vde",
                                         mock.sentinel.instance)

        device_path = os.path.join(export_mnt_base,
                                   connection_info['data']['name'])
        self.assertEqual(connection_info['data']['device_path'], device_path)
        expected_commands = [
            ('mkdir', '-p', export_mnt_base),
            ('mount', '-t', 'glusterfs', export_string, export_mnt_base),
            ('umount', export_mnt_base)]
        self.assertEqual(expected_commands, self.executes)
        self.assertTrue(mock_is_mounted.called)

    def test_libvirt_glusterfs_driver_get_config(self):
        mnt_base = '/mnt'
        self.flags(glusterfs_mount_point_base=mnt_base, group='libvirt')

        libvirt_driver = glusterfs.LibvirtGlusterfsVolumeDriver(self.fake_host)
        export_string = '192.168.1.1:/volume-00001'
        export_mnt_base = os.path.join(mnt_base,
                                       utils.get_hash_str(export_string))
        file_path = os.path.join(export_mnt_base, self.name)

        # Test default format - raw
        connection_info = {'data': {'export': export_string,
                                    'name': self.name,
                                    'device_path': file_path}}
        conf = libvirt_driver.get_config(connection_info, self.disk_info)
        tree = conf.format_dom()
        self._assertFileTypeEquals(tree, file_path)
        self.assertEqual('raw', tree.find('./driver').get('type'))

        # Test specified format - qcow2
        connection_info = {'data': {'export': export_string,
                                    'name': self.name,
                                    'device_path': file_path,
                                    'format': 'qcow2'}}
        conf = libvirt_driver.get_config(connection_info, self.disk_info)
        tree = conf.format_dom()
        self._assertFileTypeEquals(tree, file_path)
        self.assertEqual('qcow2', tree.find('./driver').get('type'))

    @mock.patch.object(libvirt_utils, 'is_mounted', return_value=True)
    def test_libvirt_glusterfs_driver_already_mounted(self, mock_is_mounted):
        mnt_base = '/mnt'
        self.flags(glusterfs_mount_point_base=mnt_base, group='libvirt')

        libvirt_driver = glusterfs.LibvirtGlusterfsVolumeDriver(self.fake_host)
        export_string = '192.168.1.1:/volume-00001'
        export_mnt_base = os.path.join(mnt_base,
                utils.get_hash_str(export_string))

        connection_info = {'data': {'export': export_string,
                                    'name': self.name}}
        libvirt_driver.connect_volume(connection_info, self.disk_info,
                                      mock.sentinel.instance)
        libvirt_driver.disconnect_volume(connection_info, "vde",
                                         mock.sentinel.instance)

        expected_commands = [
            ('umount', export_mnt_base)]
        self.assertEqual(expected_commands, self.executes)

    @mock.patch.object(glusterfs.utils, 'execute')
    @mock.patch.object(glusterfs.LOG, 'debug')
    @mock.patch.object(glusterfs.LOG, 'exception')
    def test_libvirt_glusterfs_driver_umount_error(self, mock_LOG_exception,
                                        mock_LOG_debug, mock_utils_exe):
        export_string = '192.168.1.1:/volume-00001'
        connection_info = {'data': {'export': export_string,
                                    'name': self.name}}
        libvirt_driver = glusterfs.LibvirtGlusterfsVolumeDriver(self.fake_host)
        mock_utils_exe.side_effect = processutils.ProcessExecutionError(
            None, None, None, 'umount', 'umount: target is busy.')
        libvirt_driver.disconnect_volume(connection_info, "vde",
                                         mock.sentinel.instance)
        self.assertTrue(mock_LOG_debug.called)

    @mock.patch.object(libvirt_utils, 'is_mounted', return_value=False)
    def test_libvirt_glusterfs_driver_with_opts(self, mock_is_mounted):
        mnt_base = '/mnt'
        self.flags(glusterfs_mount_point_base=mnt_base, group='libvirt')

        libvirt_driver = glusterfs.LibvirtGlusterfsVolumeDriver(self.fake_host)
        export_string = '192.168.1.1:/volume-00001'
        options = '-o backupvolfile-server=192.168.1.2'
        export_mnt_base = os.path.join(mnt_base,
                utils.get_hash_str(export_string))

        connection_info = {'data': {'export': export_string,
                                    'name': self.name,
                                    'options': options}}
        libvirt_driver.connect_volume(connection_info, self.disk_info,
                                      mock.sentinel.instance)
        libvirt_driver.disconnect_volume(connection_info, "vde",
                                         mock.sentinel.instance)

        expected_commands = [
            ('mkdir', '-p', export_mnt_base),
            ('mount', '-t', 'glusterfs',
             '-o', 'backupvolfile-server=192.168.1.2',
             export_string, export_mnt_base),
            ('umount', export_mnt_base),
        ]
        self.assertEqual(expected_commands, self.executes)
        self.assertTrue(mock_is_mounted.called)

    @mock.patch.object(libvirt_utils, 'is_mounted', return_value=False)
    def test_libvirt_glusterfs_libgfapi(self, mock_is_mounted):
        self.flags(qemu_allowed_storage_drivers=['gluster'], group='libvirt')
        libvirt_driver = glusterfs.LibvirtGlusterfsVolumeDriver(self.fake_host)
        export_string = '192.168.1.1:/volume-00001'
        name = 'volume-00001'

        connection_info = {'data': {'export': export_string, 'name': name}}

        disk_info = {
            "dev": "vde",
            "type": "disk",
            "bus": "virtio",
        }

        libvirt_driver.connect_volume(connection_info, disk_info,
                                      mock.sentinel.instance)
        conf = libvirt_driver.get_config(connection_info, disk_info)
        tree = conf.format_dom()
        self.assertEqual('network', tree.get('type'))
        self.assertEqual('raw', tree.find('./driver').get('type'))

        source = tree.find('./source')
        self.assertEqual('gluster', source.get('protocol'))
        self.assertEqual('volume-00001/volume-00001', source.get('name'))
        self.assertEqual('192.168.1.1', source.find('./host').get('name'))
        self.assertEqual('24007', source.find('./host').get('port'))
        self.assertFalse(mock_is_mounted.called)

        libvirt_driver.disconnect_volume(connection_info, "vde",
                                         mock.sentinel.instance)
