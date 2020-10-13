# Ansible Dynamic Inventory for Morpheus

## Usage

Within Morpheus, the dynamic inventory plugin will query the API and return a set of targets based on your search and organaizational criteria.  In your Ansible integration repo, use an inventory file named `morpheusinv.yml` or `morpheusinv.yaml` to activate the plugin.

### Inventory Variables

|Name|Required|Description|
|---|---|---|
|plugin|yes|Use `morpheus_inventory` to activate the plugin|
|group|yes||Array used for group definition|
|searchtype|yes|Search type for host matching.  Values: `label`, `name`|
|searchstring|yes|Search string|
|morpheus_api_key|no|Required for 4.2.3 and 5.0.0|

### Notes

#### Morpheus versions under 4.2.3 and 5.0.0

These versions require an API token in the inventory file to provide access to the Morpheus API.  Look in the Examples section for an example using Ansible Vault.

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
groupname: morpheusgroup
searchtype: label
searchstring: app_label
<morpheus_api_key from above>
```

When run, this will generate an inventory with a group `morpheusgroup` and hosts that have a label of `app_label`.