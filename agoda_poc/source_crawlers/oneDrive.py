import requests
import os
import re
import urllib
from base64 import b64encode as b64e
import json
from urllib.parse import unquote
from alive_progress import alive_bar
import math

class OneDriveDownloader:
    def __init__(self, shareLink, destPathPrefix):
        self.shareLink = shareLink
        self.destPathPrefix = destPathPrefix
        if not os.path.isdir(self.destPathPrefix):
            os.makedirs(self.destPathPrefix)

    def getFilename(self, s):
        fname = re.findall("filename\*=([^;]+)", s, flags=re.IGNORECASE)
        if not fname:
            fname = re.findall("filename=([^;]+)", s, flags=re.IGNORECASE)
        if "utf-8''" in fname[0].lower():
            fname = re.sub("utf-8''", '', fname[0], flags=re.IGNORECASE)
            fname = unquote(fname)
        else:
            fname = fname[0]
        # clean space and double quotes
        return fname.strip().strip('"')

    def getEncodedSharingUrl(self):
        encoded = self.shareLink.encode()
        return 'u!'+b64e(encoded).decode().rstrip('=').replace('/','_').replace('+','-')

    def downloadFileInChunks(self, downloadUrl):
        r = requests.get(downloadUrl, stream=True)
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        block_size = 8192

        with open(self.destPathPrefix+'/tempFile', 'wb') as f:
            with alive_bar(math.ceil(total_size/block_size)) as bar:
                try:
                    for chunk in r.iter_content(chunk_size=8192): 
                        if chunk: # filter out keep-alive new chunks
                            f.write(chunk)
                            bar()
                except Exception as e:
                    if os.path.exists(f"{self.destPathPrefix}/tempFile"):
                        os.remove(f"{self.destPathPrefix}/tempFile")
                        return None
        
        cd = r.headers['content-disposition']
        fname=self.getFilename(cd)
        print(fname)
        os.rename(f"{self.destPathPrefix}/tempFile", f"{self.destPathPrefix}/{fname}")
        r.close()
        return fname


    def downloadFileInChunksPartialStream(self, downloadUrl):
        r = requests.get(downloadUrl, stream=True)
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        block_size = 8192

        with open(self.destPathPrefix+'/tempFile', 'wb') as f:
            with alive_bar(math.ceil(total_size/block_size)) as bar:
                try:
                    for chunk in r.iter_content(chunk_size=8192): 
                        if chunk: # filter out keep-alive new chunks
                            f.write(chunk)
                            bar()
                            break
                except Exception as e:
                    if os.path.exists(f"{self.destPathPrefix}/tempFile"):
                        os.remove(f"{self.destPathPrefix}/tempFile")
                        return None
        
        cd = r.headers['content-disposition']
        fname=self.getFilename(cd)
        print(fname)
        os.rename(f"{self.destPathPrefix}/tempFile", f"{self.destPathPrefix}/{fname}")
        r.close()
        return fname

    def download(self):
        encodedSharingUrl = self.getEncodedSharingUrl()
        downloadUrl = f"https://api.onedrive.com/v1.0/shares/{encodedSharingUrl}/root/content"
        fname = self.downloadFileInChunks(downloadUrl)
        return fname, True

    def downloadPartialStream(self):
        encodedSharingUrl = self.getEncodedSharingUrl()
        downloadUrl = f"https://api.onedrive.com/v1.0/shares/{encodedSharingUrl}/root/content"
        fname = self.downloadFileInChunksPartialStream(downloadUrl)
        return fname, True
