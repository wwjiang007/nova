# Copyright 2016 Red Hat, Inc
# Copyright 2017 Rackspace Australia
#
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

"""Routines that bypass file-system checks."""

import os

from oslo_utils import fileutils

from nova import exception
import nova.privsep


@nova.privsep.sys_admin_pctxt.entrypoint
def readfile(path):
    if not os.path.exists(path):
        raise exception.FileNotFound(file_path=path)
    with open(path, 'r') as f:
        return f.read()


@nova.privsep.sys_admin_pctxt.entrypoint
def writefile(path, mode, content):
    if not os.path.exists(path):
        raise exception.FileNotFound(file_path=path)
    with open(path, mode) as f:
        f.write(content)


@nova.privsep.sys_admin_pctxt.entrypoint
def readlink(path):
    if not os.path.exists(path):
        raise exception.FileNotFound(file_path=path)
    return os.readlink(path)


@nova.privsep.sys_admin_pctxt.entrypoint
def chown(path, uid=-1, gid=-1):
    if not os.path.exists(path):
        raise exception.FileNotFound(file_path=path)
    return os.chown(path, uid, gid)


@nova.privsep.sys_admin_pctxt.entrypoint
def makedirs(path):
    fileutils.ensure_tree(path)


@nova.privsep.sys_admin_pctxt.entrypoint
def chmod(path, mode):
    if not os.path.exists(path):
        raise exception.FileNotFound(file_path=path)
    os.chmod(path, mode)


@nova.privsep.sys_admin_pctxt.entrypoint
def utime(path):
    if not os.path.exists(path):
        raise exception.FileNotFound(file_path=path)

    # NOTE(mikal): the old version of this used execute(touch, ...), which
    # would apparently fail on shared storage when multiple instances were
    # being launched at the same time. If we see failures here, we might need
    # to wrap this in a try / except.
    os.utime(path, None)


class path(object):
    @staticmethod
    @nova.privsep.sys_admin_pctxt.entrypoint
    def exists(path):
        return os.path.exists(path)
