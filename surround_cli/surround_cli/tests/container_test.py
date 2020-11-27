import os
import unittest
import zipfile

from surround_cli.data import DataContainer
from surround_cli.data.container import MetadataNotFoundError

class TestDataContainer(unittest.TestCase):
    def setUp(self):
        os.mkdir("test_data/")
        os.mkdir('test_data/test_group')

        with open("test_data/test_file.csv", "w+") as f:
            f.write("ground_truth,predict_value\n")
            f.write('0,1')
            f.write('1,0')
            f.write('1,1')

        for i in range(20):
            with open("test_data/test_group/image%s.png" % i, "w+") as f:
                f.write("FAKE_DATA")

    def tearDown(self):
        os.unlink('test_data/test_file.csv')

        for i in range(20):
            os.unlink('test_data/test_group/image%i.png' % i)

        os.rmdir('test_data/test_group')
        os.rmdir('test_data')

        if os.path.exists('test_data_2'):
            os.unlink('test_data_2/test_file.csv')
            os.unlink('test_data_2/manifest.yaml')

            for i in range(20):
                os.unlink('test_data_2/test_group/image%i.png' % i)

            os.rmdir('test_data_2/test_group')
            os.rmdir('test_data_2')

        if os.path.exists('test-container.data.zip'):
            os.unlink('test-container.data.zip')

        if os.path.exists('test_file.csv'):
            os.unlink('test_file.csv')

        if os.path.exists('test_group'):
            os.unlink('test_group/image0.png')
            os.rmdir('test_group')

    def test_create_container(self):
        container = DataContainer()
        container.export('test-container.data.zip')

        self.assertTrue(os.path.exists('test-container.data.zip'))

        with zipfile.ZipFile('test-container.data.zip', 'r') as f:
            self.assertIn('manifest.yaml', f.namelist())

        os.unlink('test-container.data.zip')

    def test_open_corrupt_container(self):
        with self.assertRaises(FileNotFoundError):
            DataContainer('test-container.data.zip')

        with open("test-container.data.zip", "w+") as f:
            f.write("INVALID_ZIP_DATA")

        with self.assertRaises(zipfile.BadZipFile):
            DataContainer('test-container.data.zip')

        os.unlink('test-container.data.zip')

        with zipfile.ZipFile('test-container.data.zip', 'w') as f:
            f.writestr('bad.txt', 'BAD')

        with self.assertRaises(MetadataNotFoundError):
            DataContainer('test-container.data.zip')

        os.unlink('test-container.data.zip')

    def test_open_container(self):
        container = DataContainer()
        container.export('test-container.data.zip')

        container = DataContainer('test-container.data.zip')
        self.assertTrue(container.file_exists('manifest.yaml'))

        os.unlink('test-container.data.zip')

    def test_import_directory(self):
        container = DataContainer()
        container.import_directory('test_data')
        container.export('test-container.data.zip')

        self.assertIn('test_file.csv', container.get_files())
        self.assertIn('test_group/image0.png', container.get_files())
        self.assertTrue(container.file_exists('test_file.csv'))
        self.assertTrue(container.file_exists('test_group/image0.png'))
        self.assertIn('image/png', container.metadata['summary']['formats'])

        with zipfile.ZipFile('test-container.data.zip', 'r') as f:
            self.assertIn('manifest.yaml', f.namelist())
            self.assertIn('test_file.csv', f.namelist())
            self.assertIn('test_group/image0.png', f.namelist())

            with f.open('test_group/image0.png') as ff:
                self.assertEqual(ff.read().decode('utf-8'), 'FAKE_DATA')

        os.unlink('test-container.data.zip')

    def test_import_file(self):
        container = DataContainer()
        container.import_file('test_data/test_file.csv', 'test_file.csv')
        container.export('test-container.data.zip')

        self.assertIn('test_file.csv', container.get_files())
        self.assertTrue(container.file_exists('test_file.csv'))

        csv_in_meta = 'application/vnd.ms-excel' in container.metadata['summary']['formats']
        csv_in_meta |= 'text/csv' in container.metadata['summary']['formats']

        self.assertTrue(csv_in_meta)

        with zipfile.ZipFile('test-container.data.zip', 'r') as f:
            self.assertIn('manifest.yaml', f.namelist())
            self.assertIn('test_file.csv', f.namelist())

            with f.open('test_file.csv') as ff:
                self.assertEqual('ground_truth,predict_value', ff.readline().decode('utf-8').rstrip())

        os.unlink('test-container.data.zip')

    def test_import_data(self):
        container = DataContainer()
        container.import_data('FAKE_DATA', 'test_data.txt')
        container.export('test-container.data.zip')

        self.assertIn('test_data.txt', container.get_files())
        self.assertTrue(container.file_exists('test_data.txt'))
        self.assertIn('text/plain', container.metadata['summary']['formats'])
        self.assertIn('Text', container.metadata['summary']['types'])
        self.assertNotIn('StillImage', container.metadata['summary']['types'])

        with zipfile.ZipFile('test-container.data.zip', 'r') as f:
            with f.open('test_data.txt') as ff:
                self.assertEqual('FAKE_DATA', ff.read().decode('utf-8'))

        os.unlink('test-container.data.zip')

    def test_extract_metadata(self):
        container = DataContainer()
        container.import_directory('test_data')
        container.export('test-container.data.zip')

        container = DataContainer('test-container.data.zip')
        self.assertIn('image/png', container.metadata['summary']['formats'])
        self.assertIn('StillImage', container.metadata['summary']['types'])
        self.assertIn('Dataset', container.metadata['summary']['types'])

        os.unlink('test-container.data.zip')

    def test_extract_file(self):
        container = DataContainer()
        container.import_directory('test_data')
        container.export('test-container.data.zip')

        container = DataContainer('test-container.data.zip')
        container.extract_file('test_file.csv', '.')

        self.assertTrue(os.path.exists('test_file.csv'))
        self.assertTrue(os.path.isfile('test_file.csv'))

        with open('test_file.csv', 'rb') as f:
            self.assertEqual('ground_truth,predict_value', f.readline().decode('utf-8').rstrip())

        os.unlink('test_file.csv')
        os.unlink('test-container.data.zip')

    def test_extract_file_data(self):
        container = DataContainer()
        container.import_directory('test_data')
        container.export('test-container.data.zip')

        container = DataContainer('test-container.data.zip')
        contents = container.extract_file_bytes('test_file.csv')
        contents = contents.decode('utf-8').rstrip()

        self.assertIn('ground_truth,predict_value', contents)

        contents = container.extract_file_bytes('test_group/image0.png')
        contents = contents.decode('utf-8')

        self.assertEqual('FAKE_DATA', contents)

        os.unlink('test-container.data.zip')

    def test_extract_all_files(self):
        container = DataContainer()
        container.import_directory('test_data')
        container.export('test-container.data.zip')

        container = DataContainer('test-container.data.zip')
        container.extract_all('test_data_2')

        self.assertTrue(os.path.exists('test_data_2'))
        self.assertTrue(os.path.exists('test_data_2/test_file.csv'))
        self.assertTrue(os.path.exists('test_data_2/test_group'))
        self.assertTrue(os.path.exists('test_data_2/test_group/image0.png'))

        os.unlink('test_data_2/test_file.csv')
        os.unlink('test_data_2/manifest.yaml')

        for i in range(20):
            os.unlink('test_data_2/test_group/image%i.png' % i)

        os.rmdir('test_data_2/test_group')
        os.rmdir('test_data_2')

    def test_extract_files(self):
        container = DataContainer()
        container.import_directory('test_data')
        container.export('test-container.data.zip')

        container = DataContainer('test-container.data.zip')
        container.extract_files(['test_file.csv', 'test_group/image0.png'], '.')

        self.assertTrue(os.path.exists('test_file.csv'))
        self.assertTrue(os.path.exists('test_group/image0.png'))

        os.unlink('test_file.csv')
        os.unlink('test_group/image0.png')
        os.rmdir('test_group')

    def test_invalid_file_import(self):
        container = DataContainer()

        with self.assertRaises(FileNotFoundError):
            container.import_file('this_file_doesnt_exist.txt', 'file.txt')
            container.export('test-container.data.zip')

    def test_invalid_directory_import(self):
        container = DataContainer()

        with self.assertRaises(FileNotFoundError):
            container.import_directory('this_folder_doesnt_exist')
            container.export('test-container.data.zip')
