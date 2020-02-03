from datetime import datetime, timedelta
import json, os
from agoda_poc.source_crawlers import oneDrive, google, youtube, s3, http_ftp
from base64 import b64encode as b64e
from dotenv import load_dotenv
import argparse

load_dotenv('agoda-poc-config')
tempDownloadFolder = os.getenv('tempDownloadFolder')


def consume_source(url, destination):

    if url[:3] == 'ftp':
        ftp_handler(url=url, destination=destination)
    elif url.split('/')[2] == '1drv.ms':
        one_drive_handler(url=url, destination=destination)
    elif url.split('/')[2] == 'drive.google.com':
        google_drive_handler(url=url, destination=destination)
    elif url.split('/')[2] == 'www.youtube.com':
        youtube_handler(url=url, destination=destination)
    elif url[:2] == 's3':
        s3_handler(url=url, destination=destination)
    else:
        http_handler(url=url, destination=destination)

def s3_handler(**kwargs):
    url = kwargs['url']
    destination = kwargs['destination']

    if '@' in url:
        username = url.split('/')[2].split(':')[0]
        password = url.split('@')[0].replace(f's3://{username}:','')
        url = url.replace(f'{username}:{password}@','')
        # print(username, password, url)
        bucket = url.split('/')[2]
        key = '/'.join(url.split('/')[3:])
        s3Downloader = s3.S3Downloader(bucket, key, 
                            aws_id=username, 
                            aws_key=password,
                            destPathPrefix=destination)
        payload, status_code = s3Downloader.download()


    if status_code:
        print(f"Downloaded {payload} to {destination}", end= ' ')
        print (u'\u2713')


def google_drive_handler(**kwargs):
    url = kwargs['url']
    destination = kwargs['destination']
    fileId = url.split('/')[5]
    gdDownloader = google.GoogleDriveDownloader(fileId, destination)
    payload, status_code = gdDownloader.download()

    if status_code:
        print(f"Downloaded {payload} to {destination}", end= ' ')
        print (u'\u2713')


def one_drive_handler(**kwargs):
    url = kwargs['url']
    destination = kwargs['destination']
    odDownloader = oneDrive.OneDriveDownloader(url, destination)
    payload, status_code = odDownloader.download()

    if status_code:
        print(f"Downloaded {payload} to {destination}", end= ' ')
        print (u'\u2713')


def youtube_handler(**kwargs):
    url = kwargs['url']
    destination = kwargs['destination']
    ytDownloader = youtube.YoutubeDownloader(url, destination)
    ytDownloader.download()


def http_handler(**kwargs):
    url = kwargs['url']
    destination = kwargs['destination']
    down = http_ftp.Download(url)
    payload, status_code = down.download(destPathPrefix=destination)

    if status_code:
        print(f"Downloaded {payload} to {destination}", end= ' ')
        print (u'\u2713')
        


def ftp_handler(**kwargs):
    url = kwargs['url']
    destination = kwargs['destination']
    if '@' in url:
        username = url.split('/')[2].split(':')[0]
        password = url.split('/')[2].split(':')[1].split('@')[0]
        url = url.replace(f'{username}:{password}@','')
        down = http_ftp.Download(url, auth=(username, password))
        payload, status_code = down.download(destPathPrefix=destination)
    else:
        down = http_ftp.Download(url)
        payload, status_code = down.download(destPathPrefix=destination)

    if status_code:
        print(f"Downloaded {payload} to {destination}", end= ' ')
        print (u'\u2713')



def run(argv = None):
    parser = argparse.ArgumentParser()

    parser.add_argument('--url',
                        type=str,
                        help='The URL to the resource you want to download.')

    parser.add_argument('--output',
                        type=str,
                        default=tempDownloadFolder,
                        help='Path to the destination download folder. Default value can be configured in the config file.')


    parser.add_argument('--file',
                        type=str,
                        help='Location of the file containing the list of URLs')


    args = parser.parse_args(argv)

    if args.file == None and args.url == None:
        print("Please enter url using --url or the location of the file containing urls using --file")
    elif not os.path.isdir(args.output):
        print("Destination path is not a directory. Please enter valid directory path and make sure you have access.")
    else:
        if args.url != None:
            consume_source(args.url, args.output)
        else:
            try:
                with open(args.file, 'r') as file:
                    for line in file:
                        print(line)
                        consume_source(line, args.output)
                file.close()
            except FileNotFoundError:
                print("File not found. Check the file path.")

    
if __name__ == "__main__":
    print(f"Downloading file to {tempDownloadFolder}")
    run()