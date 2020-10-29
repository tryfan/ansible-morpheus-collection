# Ansible Dynamic Inventory for Morpheus

## Installation

### Ansible <= 2.9
---
**NOTE**

This has been tested both with the EPEL and pip installed versions of Ansible, so
this method should be fairly portable.

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

Within Morpheus, the dynamic inventory plugin will query the API and return a set of targets based on your search and organaizational criteria.  In your Ansible integration repo, use an inventory file named `morpheusinv.yml` or `morpheusinv.yaml` to activate the plugin.

### Inventory Variables

|Name|Required|Description|
|---|---|---|
|plugin|yes|Use `morpheus_inventory` to activate the plugin|
|group|yes||List used for group definition|
|searchtype|yes|Search type for host matching.  Values: `label`, `name`|
|searchstring|yes|Search string|
|morpheus_api_key|no|Required for Morpheus versions <= 5.0.0|

---
**NOTE**

Morpheus versions <= 5.0.0  require an API token in the inventory file to provide access to the Morpheus API.  Look in the Examples section for an example using Ansible Vault.

## Examples

### Token Requirement Example

Since the inventory file will need to be stored in a git repository, we don't want to have it in plain text.  This method will encrypt the token with Ansible Vault and the password to the vault will be stored on the Morpheus server itself.

Acquire a token by going in your Morpheus user settings and clicking the API Access button.  Any entry will be sufficient.  Regenerate an Access Token and copy it.  On your Morpheus server command line, create a directory under `/var/opt/morpheus/morpheus-ui` to store the Ansible vault id file.  We can restrict permissions on this directory to the Morpheus user that runs Ansible:

```bash
install -o morpheus-local -g morpheus-local -m 0770 -d /var/opt/morpheus/morpheus-ui/ansiblevault
```

Create a file in that directory with the following [syntax](https://docs.ansible.com/ansible/latest/user_guide/vault.html#storing-passwords-in-files). Restrict permissions on the file to the same user and group as above:

```bash
tokenvaultid <somepassword>
```

Encrypt your token using the following command:

```bash
ansible-vault encrypt_string --vault-id tokenvaultid@/var/opt/morpheus/morpheus-ui/ansiblevault/<vaultfile> '<API Token>' --name morpheus_api_key
```

This will output a string similar to the following:

```yaml
morpheus_api_key: !vault |
          $ANSIBLE_VAULT;1.2;AES256;tokenvaultid
          66366331356462626531303738656437616337316636663561343938366466353939343264326330
          6233353538386634323966303566613034393463356333390a633162316637323062343739653966
          31623861643364363965613735323865393566383464316336653034353834616232356664323764
          3462623236353064330a373136333733633235663662626365303337373637396165643761613462
          38623931663166616338393236633837393830373832313636363830393635393965316665326563
          3562316436303138343662376536383131343565666635376133
```

Write the rest of your inventory file with the vaulted token above:

```yaml
plugin: morpheus_inventory
groups:
  - name: morphtest
    searchtype: label
    searchstring: whateverlabel
morpheus_url: <your morpheus url>
<morpheus_api_key from above>
```

When run, this will generate an inventory with a group `morpheusgroup` and hosts that have a label of `app_label`.
