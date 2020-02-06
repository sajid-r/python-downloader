import unittest
from unittest import mock
import os
from agoda_poc.source_crawlers import oneDrive, google, youtube, s3, http_ftp

destination = os.path.join(os.getcwd())

def calculate_md5(filename, block_size=2**20):
    """Returns MD% checksum for given file.
    """
    import hashlib

    md5 = hashlib.md5()
    try:
        with open(filename, 'rb') as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                md5.update(data)
    except IOError:
        print('File \'' + filename + '\' not found!')
        return None
    except:
        return None
    return md5.hexdigest()


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, data, status_code):
            self.data = data
            self.status_code = status_code
            self.url = 'http://someurl.com/test'
            self.headers = {'content-length':2, 'content-disposition':"attachment; filename*=UTF-8''testMockFile"}

        def json(self):
            return self.data
        
        def raise_for_status(self):
            return 200
        
        def iter_content(self,chunk_size):
            return [b'123', b'456', b'789']
        
        def close(self):
            return True

    return MockResponse(None, 404)



def mocked_requests_get_exception(*args, **kwargs):
    class MockResponse:
        def __init__(self, data, status_code):
            self.data = data
            self.status_code = status_code
            self.url = 'http://someurl.com/test'
            self.headers = {'content-length':2, 'content-disposition':"attachment; filename*=UTF-8''testMockFile"}

        def json(self):
            return self.data
        
        def raise_for_status(self):
            return 200
        
        def iter_content(self,chunk_size):
            return 200
        
        def close(self):
            return True

    return MockResponse(None, 404)


class TestHttpDownload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = []

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_mock_download_one_drive(self, mock_get):
        url = 'https://1drv.ms/b/s!AsC7cPKnf-69bOF8Bm88hS_0waU?e=VbFLVk'
        odDownloader = oneDrive.OneDriveDownloader(url, destination)
        self.files.append("testMockFile")
        payload, status_code = odDownloader.download()
        assert os.path.exists("testMockFile")
        with open("testMockFile", 'r') as f:
            content = f.readlines()
        assert content == ['123456789']


    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_mock_download_google_drive(self, mock_get):
        url = 'https://drive.google.com/file/d/0ByWGbOlDK-wac3RhcnRlcl9maWxl/view?usp=sharing'
        fileId = url.split('/')[5]
        gdDownloader = google.GoogleDriveDownloader(fileId, destination)
        self.files.append("testMockFile")
        payload, status_code = gdDownloader.download()
        assert os.path.exists("testMockFile")
        with open("testMockFile", 'r') as f:
            content = f.readlines()
        assert content == ['123456789']


    @mock.patch('requests.get', side_effect=mocked_requests_get_exception)
    def test_mock_download_google_drive_exception(self, mock_get):
        url = 'https://drive.google.com/file/d/0ByWGbOlDK-wac3RhcnRlcl9maWxl/view?usp=sharing'
        fileId = url.split('/')[5]
        gdDownloader = google.GoogleDriveDownloader(fileId, destination)
        self.files.append("testMockFile")
        payload, status_code = gdDownloader.download()
        assert not os.path.exists("testMockFile")


    @mock.patch('requests.get', side_effect=mocked_requests_get_exception)
    def test_mock_download_one_drive_exception(self, mock_get):
        url = 'https://1drv.ms/b/s!AsC7cPKnf-69bOF8Bm88hS_0waU?e=VbFLVk'
        odDownloader = oneDrive.OneDriveDownloader(url, destination)
        self.files.append("testMockFile")
        payload, status_code = odDownloader.download()
        assert not os.path.exists("testMockFile")


    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_mock_download_one_drive_stream(self, mock_get):
        url = 'https://1drv.ms/b/s!AsC7cPKnf-69bOF8Bm88hS_0waU?e=VbFLVk'
        odDownloader = oneDrive.OneDriveDownloader(url, destination)
        self.files.append("testMockFile")
        payload, status_code = odDownloader.downloadPartialStream()
        assert os.path.exists("testMockFile")
        with open("testMockFile", 'r') as f:
            content = f.readlines()
        assert content == ['123']


    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_mock_download_google_drive_stream(self, mock_get):
        url = 'https://drive.google.com/file/d/0ByWGbOlDK-wac3RhcnRlcl9maWxl/view?usp=sharing'
        fileId = url.split('/')[5]
        gdDownloader = google.GoogleDriveDownloader(fileId, destination)
        self.files.append("testMockFile")
        payload, status_code = gdDownloader.downloadPartialStream()
        assert os.path.exists("testMockFile")
        with open("testMockFile", 'r') as f:
            content = f.readlines()
        assert content == ['123']
    
    
    
    def tearDown(self):
        for file in self.files:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass


if __name__ == '__main__':
    unittest.main(verbosity=2)