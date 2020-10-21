# morpheus_inventory.py

from __future__ import (absolute_import, division, print_function)
import requests
import urllib3
import json
import os
import yaml
from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.errors import AnsibleError, AnsibleParserError

__metaclass__ = type

DOCUMENTATION = r'''
    name: morpheus_inventory
    plugin_type: inventory
    short_description: Returns Ansible inventory from Morpheus
    description: Returns Ansible inventory from Morpheus
    options:
        plugin:
            description: Morpheus Inventory
            required: true
            choices: ['morpheus_inventory']
        groups:
            description: whatever
            required: true
        searchtype:
            description: Search type
            required: false
        searchstring:
            description: Search term
            required: false
        morpheus_url:
            description: Morpheus URL
            required: false
        morpheus_api_key:
            description: Morpheus API Key - Can be a vault encrypted string
            required: false
'''


class InventoryModule(BaseInventoryPlugin):
    NAME = 'morpheus_inventory'

    def __init__(self):
        self.morpheus_env = False
        self.morpheus_url = ""
        self.morpheus_api = ""
        self.morpheus_token = ""
        self.morpheus_opt_args = {
            'token': "",
            # 'client_id': "morph-api",
            'sslverify': True
        }

    def _get_all_instances_from_morpheus(self):

        oauth_path = "/oauth/token?grant_type=password&scope=write"
        oauth_url = self.morpheus_url + oauth_path

        # if not optargs['sslverify']:
        #     urllib3.disable_warnings()

        authmethod = "token"
        headers = {'Authorization': "BEARER %s" % self.morpheus_token,
                   "Content-Type": "application/json"}

        path = "/instances"
        url = self.morpheus_api + path
        method = "get"
        verify = self.morpheus_opt_args['sslverify']
        r = getattr(requests, method)(url, headers=headers, verify=verify)
        return r.json()
        # import pdb; pdb.set_trace()

    def _get_containers_from_morpheus(self, instanceid):
        oauth_path = "/oauth/token?grant_type=password&scope=write"
        oauth_url = self.morpheus_url + oauth_path
        authmethod = "token"
        headers = {'Authorization': "BEARER %s" % self.morpheus_token,
                   "Content-Type": "application/json"}

        path = "/instances/%s/containers" % instanceid
        url = self.morpheus_api + path
        method = "get"
        verify = self.morpheus_opt_args['sslverify']
        r = getattr(requests, method)(url, headers=headers, verify=verify)
        return r.json()
        # import pdb; pdb.set_trace()

    def _set_morpheus_connection_vars(self, hostname, ip, containerid, noagent=None):
        if noagent == "null" or noagent == None:
            agent = True
        else:
            agent = False
        self.inventory.set_variable(hostname, 'ansible_host', ip)
        self.inventory.set_variable(hostname, 'ansible_user', 'morpheus-node')
        self.inventory.set_variable(hostname, 'ansible_ssh_private_key_file', self.morpheusprivatekeyfile)
        self.inventory.set_variable(hostname, 'ansible_morpheus_container_id', containerid)
        if agent:
            self.inventory.set_variable(hostname, 'ansible_connection', 'morpheus')

    def _filter_morpheus_output(self, rawresponse, group, searchtype, searchstring):
        output = {}
        if self.morpheus_env:
            try:
                for file in os.listdir(self.workspace):
                    if file.startswith("private-"):
                        self.morpheusprivatekeyfile = self.workspace + file
            except Exception as e:
                raise AnsibleParserError("Cannot find morpheus private key in workspace directory")
        if searchtype == "label":
            for instance in rawresponse['instances']:
                if searchstring in instance['tags']:
                    # raise AnsibleParserError(json.dumps(instance))
                    if len(instance['containers']) > 1:
                        containerdata = self._get_containers_from_morpheus(instance['id'])
                        for containerid in instance['containers']:
                            for container in containerdata['containers']:
                                # import pdb; pdb.set_trace()
                                if containerid == container['id']:
                                    self.inventory.add_host(
                                        host=container['externalHostname'],
                                        group=group
                                    )
                                    if self.morpheus_env:
                                        # raise AnsibleParserError(instance['noAgent'])
                                        self._set_morpheus_connection_vars(container['externalHostname'],
                                                                           container['ip'], containerid,
                                                                           instance['config']['noAgent'])
                                    else:
                                        self.inventory.set_variable(container['externalHostname'], 'ansible_host',
                                                                    container['ip'])
                    else:
                        self.inventory.add_host(
                            host=instance['hostName'],
                            group=group
                        )
                        if self.morpheus_env:
                            self._set_morpheus_connection_vars(instance)

    def verify_file(self, path):
        '''Return true/false if this is possibly a valid file for this plugin to
        consume
        '''
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('morpheusinv.yaml', 'morpheusinv.yml')):
                valid = True
        return valid

    def parse(self, inventory, loader, path, cache):
        '''Return dynamic inventory from source '''
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        if os.environ['PWD'].startswith('/var/opt/morpheus/morpheus-ui'):
            self.morpheus_env = True
        config_data = self._read_config_data(path)

        try:
            self.groups = config_data['groups']
            # self.searchtype = config_data['searchtype']
            # self.searchstring = config_data['searchstring']
            if self.morpheus_env:
                self.workspace = str(os.environ['ANSIBLE_LOOKUP_PLUGINS'])[:-51]
                # import pdb; pdb.set_trace()
                for file in os.listdir(self.workspace):
                    if file.startswith("extraVars-"):
                        morpheusextravarsfile = self.workspace + file
                with open(morpheusextravarsfile, 'r') as stream:
                    self.extravars = yaml.safe_load(stream)
                # raise AnsibleParserError(self.extravars)
                self.morpheus_url = self.extravars['morpheus']['morpheus']['applianceUrl']
                # self.morpheus_url = self.extravars['ansible_morpheus_url']
                # self.morpheus_token = self.extravars['ansible_morpheus_token']
                self.morpheus_token = config_data['morpheus_api_key']
                # else:
                #    #raise AnsibleParserError(config_data['morpheus_api_key'])
                #    self.morpheus_token = config_data['morpheus_api_key']
            else:
                self.morpheus_url = config_data['morpheus_url']
                self.morpheus_token = config_data['morpheus_api_key']

            self.morpheus_api = self.morpheus_url + "/api"
            if 'morpheus_client_id' in config_data:
                self.morpheus_opt_args['client_id'] = config_data['morpheus_client_id']
            if 'morpheus_ssl_verify' in config_data:
                if "true" or "True" in config_data['morpheus_ssl_verify']:
                    self.morpheus_opt_args['ssl_verify'] = True
                elif "false" or "False" in config_data['morpheus_ssl_verify']:
                    self.morpheus_opt_args['ssl_verify'] = False
                else:
                    raise AnsibleParserError('morpheus_ssl_verify must be set to "True" or "False"')
        except Exception as e:
            raise AnsibleParserError('Options missing: {}'.format(e))

        # import pdb; pdb.set_trace()
        for group in self.groups:
            self.inventory.add_group(group['name'])
            rawoutput = self._get_all_instances_from_morpheus()
            self._filter_morpheus_output(rawoutput, group['name'], group['searchtype'], group['searchstring'])
            # import pdb; pdb.set_trace()
