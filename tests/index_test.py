import boto3
import os
import sys
import unittest
from botocore.stub import Stubber
from datetime import datetime, timedelta
from mock import *
from StringIO import StringIO
from test.test_support import EnvironmentVarGuard
from time import time

sys.path.insert(0, os.path.abspath('lambda'))
import index


class TestLightsailAutoSnapshots(unittest.TestCase):
    def test_snapshot_instances(self):
        """
        Tests instance snapshotting by stubbing one instance in the response to
        the get_instances call and verifying the create_instance_snapshot API
        endpoint is called with the expected parameters and verifying the
        output.
        """
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
        """
        Tests snapshot pruning by providing three snapshots - one manual and
        two automatic of which one is has an elapsed retention period. The
        test asserts that only the eligible snapshot is pruned via stubbing
        the API call to delete_instance_snapshot and verifying the output.
        """
        mock_dt = MagicMock()
        mock_dt.now.return_value = datetime(2016, 12, 2)
        logger = StringIO()
        client = boto3.client('lightsail')
        stubber = Stubber(client)
        stubber.add_response('get_instance_snapshots', {'instanceSnapshots': [
            {'name': 'snapshot-manual', 'createdAt': datetime(2016, 12, 1)},
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

    def test_pagination(self):
        """
        Tests pagination by returning three pages of results and asserts each
        request is made with the expected pageToken.
        """
        client = boto3.client('lightsail')
        stubber = Stubber(client)
        stubber.add_response('get_instance_snapshots', {'instanceSnapshots': [
            {'name': 'snapshot1', 'createdAt': datetime(2016, 12, 1)},
            ], 'nextPageToken': 'token1'})
        stubber.add_response('get_instance_snapshots', {'instanceSnapshots': [
            {'name': 'snapshot2', 'createdAt': datetime(2016, 12, 2)},
            ], 'nextPageToken': 'token2'}, {'pageToken': 'token1'})
        stubber.add_response('get_instance_snapshots', {'instanceSnapshots': [
            {'name': 'snapshot2', 'createdAt': datetime(2016, 12, 3)},
            ]}, {'pageToken': 'token2'})
        stubber.activate()

        index._prune_snapshots(client, timedelta(days=5))

        stubber.assert_no_pending_responses()

    @patch('index._prune_snapshots')
    @patch('index._snapshot_instances')
    def test_handler(self, snapshot_instances_mock, prune_snapshots_mock):
        """
        Tests that the handler honors the value of RENTENTION_DAYS and calls
        the snapshot and prune functions with the expected values.
        """
        self.env = EnvironmentVarGuard()
        self.env.set('RETENTION_DAYS', '90')

        client = Mock()

        with patch('boto3.client', return_value=client):
            with self.env:
                index.handler(Mock(), Mock())

        snapshot_instances_mock.assert_called_with(client)
        prune_snapshots_mock.assert_called_with(client, timedelta(days=90))

if __name__ == '__main__':
    unittest.main()
