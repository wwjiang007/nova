# Copyright 2016 Cloudbase Solutions Srl
# All Rights Reserved.
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

from nova.policies import base


POLICY_ROOT = 'os_compute_api:os-flavor-extra-specs:%s'


flavor_extra_specs_policies = [
    base.create_rule_default(
        POLICY_ROOT % 'show',
        base.RULE_ADMIN_OR_OWNER,
        "Show an extra spec for a flavor",
        [
            {
                'path': '/flavors/{flavor_id}/os-extra_specs/'
                        '{flavor_extra_spec_key}',
                'method': 'GET'
            }
        ]
    ),
    base.create_rule_default(
        POLICY_ROOT % 'create',
        base.RULE_ADMIN_API,
        "Create extra specs for a flavor",
        [
            {
                'path': '/flavors/{flavor_id}/os-extra_specs/',
                'method': 'POST'
            }
        ]
    ),
    base.create_rule_default(
        POLICY_ROOT % 'update',
        base.RULE_ADMIN_API,
        "Update an extra spec for a flavor",
        [
            {
                'path': '/flavors/{flavor_id}/os-extra_specs/'
                        '{flavor_extra_spec_key}',
                'method': 'PUT'
            }
        ]
    ),
    base.create_rule_default(
        POLICY_ROOT % 'delete',
        base.RULE_ADMIN_API,
        "Delete an extra spec for a flavor",
        [
            {
                'path': '/flavors/{flavor_id}/os-extra_specs/'
                        '{flavor_extra_spec_key}',
                'method': 'DELETE'
            }
        ]
    ),
    base.create_rule_default(
        POLICY_ROOT % 'index',
        base.RULE_ADMIN_OR_OWNER,
        "List extra specs for a flavor",
        [
            {
                'path': '/flavors/{flavor_id}/os-extra_specs/',
                'method': 'GET'
            }
        ]
    ),
]


def list_rules():
    return flavor_extra_specs_policies
