import boto3
from datetime import datetime, timedelta
from os import getenv
from time import time

DEFAULT_RETENTION_DAYS = 30
AUTO_SNAPSHOT_SUFFIX = 'auto'


def handler(event, context):
    client = boto3.client('lightsail')
    retention_days = int(getenv('RETENTION_DAYS', DEFAULT_RETENTION_DAYS))
    retention_period = timedelta(days=retention_days)

    _snapshot_instances(client)
    _prune_snapshots(client, retention_days)


def _snapshot_instances(client):
    instances = _get_paginated_collection(client.get_instances, 'instances')

    for instance in instances:
        _create_snapshot(client, instance['name'])


def _prune_snapshots(client, retention_period):
    snapshots = _get_paginated_collection(client.get_instance_snapshots,
                                          'instanceSnapshots')

    for snapshot in snapshots:
        now = datetime.now().replace(tzinfo=snapshot['createdAt'].tzinfo)
        time_elapsed = now - snapshot['createdAt']

        if (snapshot['name'].endswith(AUTO_SNAPSHOT_SUFFIX) and
                time_elapsed > retention_period):
            _delete_snapshot(client, snapshot['name'], snapshot['createdAt'])


def _get_paginated_collection(function, key, page_token=None, collection=None):
    kwargs = dict()

    if page_token is not None:
        kwargs['pageToken'] = page_token

    if collection is None:
        collection = list()

    response = function(**kwargs)
    collection += response[key]

    if 'nextPageToken' in response:
        __get_paginated_collection(function, key, collection=collection,
                                 page_token=response['nextPageToken'])

    return collection


def _create_snapshot(client, instance_name):
    snapshot_name = '{}-system-{}-{}'.format(instance_name, int(time() * 1000),
                                             AUTO_SNAPSHOT_SUFFIX)

    client.create_instance_snapshot(instanceName=instance_name,
                                    instanceSnapshotName=snapshot_name)
    print('Created Snapshot name="{}"'.format(snapshot_name))


def _delete_snapshot(client, name, created_at):
    client.delete_instance_snapshot(instanceSnapshotName=name)
    print('Deleted Snapshot name="{}" createdAt="{}"'.format(name, created_at))
