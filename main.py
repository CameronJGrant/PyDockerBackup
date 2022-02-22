from pydockerbackup import upload_file, delete_folder, get_bucket_contents
import subprocess
import os
from pathlib import Path
from datetime import datetime


def get_folder_dates():
    folders = []
    for folder in get_bucket_contents(path=backup_folder_name):
        key = folder.key
        date = key.split('/')[1]
        folders.append(date)
    return list(set(folders))


def check_if_exists():
    dates_already_done = get_folder_dates()

    if today in dates_already_done:
        raise Exception('Already Backed up today.')


def zip_files():
    sp = subprocess.call(['sh', './backup.sh'])

    if sp == 0:
        print('Compressed')
    else:
        raise Exception('Compression Failed')


def upload_zip_files():
    uploaded = None
    files = list(Path('/compressed').glob('*'))
    for counter, i in enumerate(files):
        size = i.stat().st_size
        unit = 'B'
        if size / 1e3 > 1:
            size /= 1000
            unit = 'KB'
        if size / 1e3 > 1:
            size /= 1000
            unit = 'MB'
        if size / 1e3 > 1:
            size /= 1000
            unit = 'GB'
        print(f"Uploading ({counter + 1}/{len(files)}): {i.name} {size:0.2f}{unit}")
        uploaded = upload_file(i, object_name=f"{backup_folder_name}/{today}/{i.name}")

    if uploaded:
        print("Files uploaded")
    else:
        raise Exception('Failed upload.')


def delete_old_backups():
    dates_in_s3 = [datetime.strptime(date, '%Y-%m-%d') for date in dates_in_s3_str]
    dates_in_s3.sort()
    num_folders = len(dates_in_s3)
    delete_to = num_folders - num_rolling_backups + 1  # +1 for new date just added.
    if delete_to > 0:
        dates_to_delete = [date.strftime('%Y-%m-%d') for date in dates_in_s3[:delete_to]]
        for folder_delete in dates_to_delete:
            delete_folder(f'{backup_folder_name}/{folder_delete}')
        print(f'Deleted {delete_to} old backups.')


if __name__ == '__main__':
    today = datetime.now().strftime('%Y-%m-%d')
    num_rolling_backups = int(os.environ['NUM_ROLLING_BACKUPS'])
    backup_folder_name = os.environ['BACKUP_NAME']

    if not backup_folder_name:
        raise Exception('Please specify folder name for backups. Set environment variable "BACKUP_NAME"')

    dates_in_s3_str = get_folder_dates()

    check_if_exists()

    print(f'Backing up ({today})...')
    zip_files()
    upload_zip_files()

    delete_old_backups()

    print('Done')
