import boto3
import os
import sys
import unittest
from botocore.stub import Stubber
from datetime import datetime, timedelta
from mock import *
from StringIO import StringIO
from time import time

sys.path.insert(0, os.path.abspath('lambda'))
import index


class TestLightsailAutoSnapshots(unittest.TestCase):
    def test_snapshot_instances(self):
        mock_time = MagicMock()
        mock_time.return_value = 1485044158
        logger = StringIO()
        client = boto3.client('lightsail')
        stubber = Stubber(client)
        stubber.add_response('get_instances', {'instances': [
            {'name': 'LinuxBox1'}]})
        stubber.add_response('create_instance_snapshot', {}, {
            'instanceName': 'LinuxBox1',
            'instanceSnapshotName': 'LinuxBox1-system-1485044158000-auto'})
        stubber.activate()

        index._snapshot_instances(client, mock_time, logger)

        stubber.assert_no_pending_responses()
        self.assertEqual(
            'Created Snapshot name="LinuxBox1-system-1485044158000-auto"',
            logger.getvalue().strip())

    def test_prune_snapshots(self):
        mock_dt = MagicMock()
        mock_dt.now.return_value = datetime(2016, 12, 2)
        logger = StringIO()
        client = boto3.client('lightsail')
        stubber = Stubber(client)
        stubber.add_response('get_instance_snapshots', {'instanceSnapshots': [
            {'name': 'new-snapshot-auto', 'createdAt': datetime(2016, 12, 1)},
            {'name': 'old-snapshot-auto', 'createdAt': datetime(2016, 10, 15)}
            ]})
        stubber.add_response('delete_instance_snapshot', {}, {
            'instanceSnapshotName': 'old-snapshot-auto'})
        stubber.activate()

        index._prune_snapshots(client, timedelta(days=5), mock_dt, logger)

        stubber.assert_no_pending_responses()
        self.assertEqual('Deleted Snapshot name="old-snapshot-auto"',
                         logger.getvalue().strip())

if __name__ == '__main__':
    unittest.main()
