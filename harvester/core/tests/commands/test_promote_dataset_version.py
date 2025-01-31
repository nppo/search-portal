from unittest.mock import patch

from django.test import TestCase, override_settings
from django.core.management import call_command, CommandError

from core.tests.mocks import get_elastic_client_mock


class TestPromoteDatasetVersion(TestCase):

    fixtures = ["datasets-history", "index-history"]
    elastic_client = get_elastic_client_mock(has_history=True)

    def setUp(self):
        super().setUp()
        self.elastic_client.indices.put_alias.reset_mock()
        self.elastic_client.indices.create.reset_mock()
        self.elastic_client.indices.delete.reset_mock()

    def assert_index_promoted(self):
        # Indices should not get recreated
        self.assertEqual(self.elastic_client.indices.delete.call_count, 0)
        self.assertEqual(self.elastic_client.indices.create.call_count, 0)
        # Latest alias should update
        self.assertEqual(self.elastic_client.indices.put_alias.call_count, 2)
        for args, kwargs in self.elastic_client.indices.put_alias.call_args_list:
            index_name, version, language, id = kwargs["index"].split("-")
            self.assertEqual(index_name, "test")
            self.assertEqual(version, "001")
            self.assertIn(kwargs["name"], ["latest-nl", "latest-en"])

    @override_settings(VERSION="0.0.1")
    @patch("core.models.search.get_es_client", return_value=elastic_client)
    def test_promote_dataset(self, get_es_client):
        get_es_client.reset_mock()
        call_command("promote_dataset_version", "--dataset=test")
        self.assert_index_promoted()

        get_es_client.reset_mock()
        call_command("promote_dataset_version", "--dataset=test", "--harvester-version=0.0.1")
        self.assert_index_promoted()

    @patch("core.models.search.get_es_client", return_value=elastic_client)
    def test_promote_dataset_version(self, get_es_client):
        get_es_client.reset_mock()
        call_command("promote_dataset_version", "--dataset-version=1")
        self.assert_index_promoted()

    def test_promote_invalid(self):
        try:
            call_command("promote_dataset_version")
            self.fail("Expected promote_dataset_version to fail with dataset and dataset_version unspecified")
        except CommandError:
            pass
        try:
            call_command("promote_dataset_version", "--dataset=test", "--harvester-version=0.0.2")
            self.fail("Expected promote_dataset_version to fail with invalid harvester version specified")
        except CommandError:
            pass
