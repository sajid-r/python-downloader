import unittest
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


class TestHttpDownload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = []

    def test_download(self):
        down = http_ftp.Download("http://ovh.net/files/1Mb.dat")
        self.files.append("1Mb.dat")
        down.download(destPathPrefix=destination)
        assert os.path.exists("1Mb.dat")
        assert calculate_md5("1Mb.dat") == "62501d556539559fb422943553cd235a"


    def test_check_exists(self):
        down = http_ftp.Download("http://ovh.net/files/1Mb.dat")
        exists = down.check_exists()
        self.assertTrue(exists)
        down = http_ftp.Download("http://ovh.net/files/not_exists.dat")
        exists = down.check_exists()
        self.assertFalse(exists)

    def test_ftp_download(self):
        down = http_ftp.Download("ftp://speedtest.tele2.net/512KB.zip")
        self.files.append("512KB.zip")
        down.download(destPathPrefix=destination)
        assert os.path.exists("512KB.zip")
        assert calculate_md5("512KB.zip") == "59071590099d21dd439896592338bf95"

    def test_ftp_download_password(self):
        down = http_ftp.Download("ftp://test.rebex.net/readme.txt", auth=("demo", "password"))
        self.files.append("readme.txt")
        down.download(destPathPrefix=destination)
        assert os.path.exists("readme.txt")
        assert calculate_md5("readme.txt") == "d1f2b721bf97a3b6ae0c7975f5a0a11b"

    def test_youtube(self):
        ytDownloader = youtube.YoutubeDownloader("https://www.youtube.com/watch?v=NZRc5IcxXZI", destination)
        self.files.append("Happy Lunar New Year 2020 - Agodawebm.mkv")
        ytDownloader.download()
        assert os.path.exists("Happy Lunar New Year 2020 - Agodawebm.mkv")

    def test_googledrive(self):
        url = 'https://drive.google.com/file/d/0ByWGbOlDK-wac3RhcnRlcl9maWxl/view?usp=sharing'
        fileId = url.split('/')[5]
        gdDownloader = google.GoogleDriveDownloader(fileId, destination)
        self.files.append("How to get started with Drive.pdf")
        payload, status_code = gdDownloader.download()
        assert os.path.exists("How to get started with Drive.pdf")

    def test_onedrive(self):
        url = 'https://1drv.ms/b/s!AsC7cPKnf-69bOF8Bm88hS_0waU?e=VbFLVk'
        odDownloader = oneDrive.OneDriveDownloader(url, destination)
        self.files.append("Getting started with OneDrive.pdf")
        payload, status_code = odDownloader.download()
        assert os.path.exists("Getting started with OneDrive.pdf")

    def tearDown(self):
        for file in self.files:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass


if __name__ == '__main__':
    unittest.main(verbosity=2)