# Python Downloader

### Downloads content from http, ftp, GoogleDrive, OneDrive, s3, YouTube
More connectors coming soon

## Installation

```
pip install -r requirements.txt
```

## Usage

### Direct url download

```
python source-crawler-dag.py --url https://www.youtube.com/watch?v=NZRc5IcxXZI
python source-crawler-dag.py --url ftp://speedtest.tele2.net/512KB.zip
python source-crawler-dag.py --url http://ovh.net/files/1Mb.dat
python source-crawler-dag.py --url https://1drv.ms/b/s!AsC7cPKnf-69bOF8Bm88hS_0waU?e=VbFLVk
python source-crawler-dag.py --url https://drive.google.com/file/d/0ByWGbOlDK-wac3RhcnRlcl9maWxl/view?usp=sharing
python source-crawler-dag.py --url s3://username:password@mybucket/location/to/file
```

### URLs in a file for bulk download

```
python source-crawler-dag.py --file input
```


## Test
Real Resource Test
```
python tester.py
```
Mock Resource Test
```
python tester_mock_request.py
```