from __future__ import print_function
import boto3
from datetime import datetime, timedelta
from os import getenv
from sys import stdout
from time import time

DEFAULT_RETENTION_DAYS = 30
AUTO_SNAPSHOT_SUFFIX = 'auto'


def handler(event, context):
    client = boto3.client('lightsail')
    retention_days = int(getenv('RETENTION_DAYS', DEFAULT_RETENTION_DAYS))
    retention_period = timedelta(days=retention_days)

    _snapshot_instances(client)
    _prune_snapshots(client, retention_period)


def _snapshot_instances(client, time=time, out=stdout):
    for page in client.get_paginator('get_instances').paginate():
        for instance in page['instances']:
            snapshot_name = '{}-system-{}-{}'.format(instance['name'],
                                                     int(time() * 1000),
                                                     AUTO_SNAPSHOT_SUFFIX)

            client.create_instance_snapshot(instanceName=instance['name'],
                                            instanceSnapshotName=snapshot_name)
            print('Created Snapshot name="{}"'.format(snapshot_name), file=out)


def _prune_snapshots(client, retention_period, datetime=datetime, out=stdout):
    for page in client.get_paginator('get_instance_snapshots').paginate():
        for snapshot in page['instanceSnapshots']:
            name, created_at = snapshot['name'], snapshot['createdAt']
            now = datetime.now(created_at.tzinfo)
            is_automated_snapshot = name.endswith(AUTO_SNAPSHOT_SUFFIX)
            has_elapsed_retention_period = now - created_at > retention_period

            if (is_automated_snapshot and has_elapsed_retention_period):
                client.delete_instance_snapshot(instanceSnapshotName=name)
                print('Deleted Snapshot name="{}"'.format(name), file=out)
