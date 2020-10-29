# Ansible Dynamic Inventory for Morpheus

## Installation

### Ansible <= 2.9
---
**NOTE**

This has been tested both with the EPEL and pip installed versions of Ansible, so this method should be fairly portable.

---

If it doesn't exist, create the directory `/usr/share/ansible/plugins/inventory`
```
mkdir -p /usr/share/ansible/plugins/inventory
```

Download the Ansible Morpheus Collection tarball

From the tarball, copy the `plugins/inventory/morpheus_inventory.py` file to the `/usr/share/ansible/plugins/inventory` directory.
```
cp plugins/inventory/morpheus_inventory.py /usr/share/ansible/plugins/inventory/
```

Run `ansible-doc` to confirm installation
```
ansible-doc -t inventory -l | grep morpheus
```

When using this module with Ansible <= 2.9, you will refer to the module in your YAML file as:
```
plugin: morpheus_inventory
```

### Ansible >= 2.10

Download the Ansible Morpheus Collection tarball

Install the collection through Ansible
```
ansible-galaxy collection install <tarball>
```

Run `ansible-doc` to confirm installation
```
ansible-doc -t inventory -l | grep morpheus
```

When using this module as a collection with Ansible >= 2.10, refer to the module in your YAML file as:
```
plugin: morpheusdata.morpheus.morpheus_inventory
```

## Usage

Within Morpheus, the dynamic inventory plugin will query the API and return a set of targets based on your search and organaizational criteria.

### Inventory Variables

|Name|Required|Description|
|---|---|---|
|plugin|yes|Use `morpheus_inventory` to activate the plugin|
|group|yes||List used for group definition|
|searchtype|yes|Search type for host matching.  Values: `label`, `name`, `app`|
|searchstring|yes|Search string - the app type uses this as a list, otherwise it is a string|
|morpheus_url|yes|Morpheus URL|
|morpheus_api_key|yes|Required for Morpheus versions <= 5.0.0|

---
**NOTE**

Morpheus versions <= 5.0.0  require an API token in the inventory file to provide access to the Morpheus API.  Look in the Examples section for an example using Ansible Vault.

## Examples

### Use in Morpheus

Create an Ansible Task in Morpheus and specify the playbook you wish to run.  Set the `Execute Target` to `Local`.

In `Command Options` specify `-i <relative path>/morpheusinv.yml`

This will process `morpheusinv.yml` as a dynamic inventory using the specified plugin.

#### Name or Label

In your git repo, place this file as morpheusinv.yml

```yaml
plugin: morpheus_inventory
groups:
  - name: morphtest
    searchtype: label
    searchstring: whateverlabel
morpheus_url: <your morpheus URL>
morpheus_api_key: <your API key>
```

This will create a group `morphtest` and add any instances that have the label `whateverlabel` applied in Morpheus.

#### App

In your git repo, place this file as morpheusinv.yml

```yaml
plugin: morpheus_inventory
groups:
  - name: ui
    searchtype: app
    searchstring:
      appname: 2tier
      apptier: UI
  - name: db
    searchtype: app
    searchstring:
      appname: 2tier
      apptier: Database
morpheus_url: <your morpheus URL>
morpheus_api_key: <your API key>
```

This will create two groups: `ui` and `db`.
`ui` will contain instances from the `UI` tier of the `2tier` application that was deployed in Morpheus from a blueprint.
`db` will contain instances from the `Database` tier of the `2tier` application.

### Token Requirement

Since the inventory file will need to be stored in a git repository, it is not advised to store it in plain text.

We suggest encrypting the API token with Ansible Vault with the vault password stored in a file on the Morpheus UI server(s).

Acquire a token by going in your Morpheus user settings and clicking the API Access button.
Any entry will be sufficient.  Regenerate an Access Token and copy it.

On your Morpheus server, create a directory under `/var/opt/morpheus/morpheus-ui` to store the Ansible vault password.
Restrict permissions on this directory to the Morpheus user that runs Ansible: `morpheus-local`
```bash
install -o morpheus-local -g morpheus-local -m 0770 -d /var/opt/morpheus/morpheus-ui/ansiblevault
```

In your task, specify `--vault-password-file /var/opt/morpheus/morpheus-ui/ansiblevault/<file>` in order to use the password.

Information on encrypting strings and variables for ansible is located [HERE](https://docs.ansible.com/ansible/latest/user_guide/vault.html)