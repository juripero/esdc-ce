from logging import getLogger

from api.node.sshkey.tasks import node_authorized_keys_sync
# noinspection PyProtectedMember
from api.node.image.tasks import node_img_sources_sync

logger = getLogger(__name__)


# noinspection PyUnusedLocal
def dc_node_settings_changed_handler(task_id, dc, old_settings, new_settings):
    """
    Handle changes in the DC settings; triggered by dc_settings_changed signal
    """
    old_keys = old_settings.get('VMS_NODE_SSH_KEYS_DEFAULT', [])
    new_keys = new_settings.get('VMS_NODE_SSH_KEYS_DEFAULT', [])
    # if there is difference between SSH keys in original and new settings; sync keys
    if old_keys != new_keys:
        logger.info('Updating SSH keys on compute nodes because DC settings have changed')
        node_authorized_keys_sync.call(task_id)

    # imgadm sources need to be updated on all compute nodes if there is a difference
    # between old/new Image server or old/new Image server NIC ID or old/new additional imgadm sources
    img_settings_changed = any(old_settings.get(opt, None) != new_settings.get(opt, None)
                               for opt in ('VMS_IMAGE_VM', 'VMS_IMAGE_VM_NIC', 'VMS_IMAGE_SOURCES'))

    if img_settings_changed:
        logger.info('Updating imgadm sources on all compute nodes because DC settings have changed')
        node_img_sources_sync.call(task_id)
