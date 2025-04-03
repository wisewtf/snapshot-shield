from pyVim import connect
from pyVmomi import vim
from datetime import datetime
import requests
import tomli

def configurator(section, value):

    with open("/app/config.toml", "rb") as f:
        toml_data = tomli.load(f)

    configuration = toml_data[section][value]
    return configuration

vcenter_host = configurator('vcenter', 'host')
vcenter_user = configurator('vcenter', 'user')
vcenter_password = configurator('vcenter', 'password')
mattermost_webhook_url = configurator('mattermost', 'url')

def get_snapshot_count(snapshot):
    if snapshot.childSnapshotList:
        count = 0
        for child_snapshot in snapshot.childSnapshotList:
            count += 1 + get_snapshot_count(child_snapshot)
        return count
    else:
        return 0

def get_vm_snapshots(vcenter_host, vcenter_user, vcenter_password, vcenter_port=443):
    try:
        service_instance = connect.SmartConnect(
            host=vcenter_host,
            user=vcenter_user,
            pwd=vcenter_password,
            port=vcenter_port,
            disableSslCertValidation=True
        )

        content = service_instance.RetrieveContent()

        vm_snapshots = []
        container_view = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.VirtualMachine], True
        )

        for vm in container_view.view:
            vm_moid = vm._moId
            vm_name = vm.name

            if vm.snapshot is not None and vm.snapshot.rootSnapshotList is not None:
                snapshots = vm.snapshot.rootSnapshotList
                for snapshot in snapshots:
                    create_time = datetime.strftime(snapshot.createTime, "%Y-%m-%d %H:%M:%S")
                    snapshot_count = get_snapshot_count(snapshot)
                    snapshot_info = {
                        'VM Name': vm_name,
                        'VM MoID': vm_moid,
                        'Snapshot Name': snapshot.name,
                        'Snapshot MoID': snapshot.snapshot._moId,
                        'Creation Time': create_time,
                        'Snapshot Count': snapshot_count
                    }
                    vm_snapshots.append(snapshot_info)

        connect.Disconnect(service_instance)

        return vm_snapshots

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

vm_snapshots = get_vm_snapshots(vcenter_host, vcenter_user, vcenter_password)

def send_to_teams(webhook_url, message):
    headers = {'Content-Type': 'application/json'}
    payload = {'text': message}
    response = requests.post(webhook_url, json=payload, headers=headers)
    return response.status_code

def send_to_mattermost(webhook_url, message):
    headers = {'Content-Type': 'application/json'}
    payload = {'text': message}
    response = requests.post(webhook_url, json=payload, headers=headers)
    return response.status_code

if vm_snapshots:
    markdown_table = "| VM Name | VM MoID | Snapshot Name | Snapshot MoID | Creation Time | Snapshot Count |\n" \
                     "|---------|---------|----------------|----------------|----------------|-----------------|\n"
    for snapshot in vm_snapshots:
        markdown_table += f"| {snapshot['VM Name']} | {snapshot['VM MoID']} | {snapshot['Snapshot Name']} | {snapshot['Snapshot MoID']} | {snapshot['Creation Time']} | {snapshot['Snapshot Count']+1} |\n"

    mattermost_status_code = send_to_mattermost(mattermost_webhook_url, markdown_table)

else:
    exit