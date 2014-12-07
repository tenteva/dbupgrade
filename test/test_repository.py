from dbupgrade.repository.file_repository import FileRepository, RepositoryException
from dbupgrade.common import StepVersion

__author__ = 'vincent'

import unittest


class FileRepositoryCase(unittest.TestCase):
    def setUp(self):
        self.repo = FileRepository('repository', 'app2')

    def test_list_applications(self):
        apps = FileRepository.list_applications('repository')
        self.assertEqual(['app1', 'app2'], apps)

    def test_list_versions(self):
        assert_versions = [
            StepVersion('4.0.1'),
            StepVersion('4.0.1.2'),
            StepVersion('4.5.0'),
            StepVersion('4.10.0'),
        ]
        versions = self.repo.list_versions()

        self.assertEqual(versions, assert_versions)

    def test_path_to_version(self):
        with self.assertRaises(RepositoryException):
            self.repo.path_to_version(version_from=StepVersion('7.0.0'))

        with self.assertRaises(RepositoryException):
            self.repo.path_to_version(version_to=StepVersion('7.0.0'))

        self.assertEqual(
            self.repo.path_to_version(version_from=StepVersion('4.5.0'), version_to=StepVersion('4.5.0')),
            []
        )

        self.assertEqual(
            self.repo.path_to_version(),
            [
                StepVersion('4.0.1'),
                StepVersion('4.0.1.2'),
                StepVersion('4.5.0'),
                StepVersion('4.10.0'),
            ]
        )

        # Upgrade
        self.assertEqual(
            self.repo.path_to_version(version_to=StepVersion('4.5.0')),
            [
                StepVersion('4.0.1'),
                StepVersion('4.0.1.2'),
                StepVersion('4.5.0'),
            ]
        )

        self.assertEqual(
            self.repo.path_to_version(version_from=StepVersion('4.0.1.2')),
            [
                StepVersion('4.5.0'),
                StepVersion('4.10.0'),
            ]
        )

        self.assertEqual(
            self.repo.path_to_version(version_from=StepVersion('4.0.1.2'), version_to=StepVersion('4.5.0')),
            [
                StepVersion('4.5.0'),
            ]
        )

        # Downgrade
        self.assertEqual(
            self.repo.path_to_version(version_from=StepVersion('4.5.0'), version_to=StepVersion('4.0.1.2')),
            [
                StepVersion('4.5.0'),
            ]
        )

        self.assertEqual(
            self.repo.path_to_version(version_from=StepVersion('4.10.0'), version_to=StepVersion('4.0.1')),
            [
                StepVersion('4.10.0'),
                StepVersion('4.5.0'),
                StepVersion('4.0.1.2'),

            ]
        )

    def test_get_migration(self):
        # Upgrade

        steps = self.repo.get_migration(version_from=StepVersion('4.0.1'), version_to=StepVersion('4.10.0'))
        self.assertEquals(steps.content_steps(),
                          (
                              'CREATE TABLE test_first (INTEGER a,VARCHAR b);',
                              'CREATE TABLE test_second (INTEGER a,VARCHAR b);',
                              'ALTER TABLE testfirst ADD COLUMN INTEGER C;',
                          )
        )

        # Downgrade
        steps = self.repo.get_migration(version_from=StepVersion('4.10.0'), version_to=StepVersion('4.0.1'))
        self.assertEquals(steps.content_steps(),
                          (
                              'ALTER TABLE testfirst DROP COLUMN C;',
                              'DROP TABLE test_second;',
                              'DROP TABLE test_first;',
                          )
        )


if __name__ == '__main__':
    unittest.main()