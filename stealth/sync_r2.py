import os
import time
import mimetypes
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv

class R2FolderSync:
    def __init__(self, local_folder=None, sync_interval=5):
        load_dotenv()
        self.CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
        self.CF_R2_ACCESS_KEY_ID = os.getenv("CF_R2_ACCESS_KEY_ID")
        self.CF_R2_SECRET_ACCESS_KEY = os.getenv("CF_R2_SECRET_ACCESS_KEY")
        self.CF_R2_BUCKET_NAME = os.getenv("CF_R2_BUCKET_NAME")
        self.R2_ENDPOINT_URL = f"https://{self.CF_ACCOUNT_ID}.r2.cloudflarestorage.com"
        self.LOCAL_FOLDER_TO_SYNC = local_folder or "example"
        self.SYNC_INTERVAL_SECONDS = sync_interval

        if not all([self.CF_ACCOUNT_ID, self.CF_R2_ACCESS_KEY_ID, self.CF_R2_SECRET_ACCESS_KEY, self.CF_R2_BUCKET_NAME]):
            return  # Fail silently

        self.s3_client = self._init_r2_client()

    def _init_r2_client(self):
        try:
            client = boto3.client(
                's3',
                endpoint_url=self.R2_ENDPOINT_URL,
                aws_access_key_id=self.CF_R2_ACCESS_KEY_ID,
                aws_secret_access_key=self.CF_R2_SECRET_ACCESS_KEY,
                config=Config(signature_version='s3v4'),
                region_name='auto'
            )
            return client
        except Exception:
            return None

    def check_internet_connection(self, host="www.google.com", port=80, timeout=3):
        import socket
        try:
            ip_address = socket.gethostbyname(host)
            with socket.create_connection((ip_address, port), timeout=timeout):
                return True
        except Exception:
            return False

    def get_r2_object_metadata(self, r2_key):
        try:
            response = self.s3_client.head_object(Bucket=self.CF_R2_BUCKET_NAME, Key=r2_key)
            return response['LastModified'].timestamp(), response['ContentLength']
        except Exception:
            return None, None

    def upload_file_to_r2(self, local_path, r2_key):
        try:
            content_type, _ = mimetypes.guess_type(local_path)
            if content_type is None:
                content_type = 'application/octet-stream'
            self.s3_client.upload_file(
                local_path,
                self.CF_R2_BUCKET_NAME,
                r2_key,
                ExtraArgs={'ContentType': content_type}
            )
            return True
        except Exception:
            return False

    def sync_once(self):
        if not os.path.isdir(self.LOCAL_FOLDER_TO_SYNC):
            return
        for root, _, files in os.walk(self.LOCAL_FOLDER_TO_SYNC):
            for file_name in files:
                local_file_full_path = os.path.join(root, file_name)
                r2_object_key = os.path.relpath(local_file_full_path, self.LOCAL_FOLDER_TO_SYNC).replace(os.sep, '/')
                try:
                    local_mod_time = os.path.getmtime(local_file_full_path)
                    local_file_size = os.path.getsize(local_file_full_path)
                except Exception:
                    continue
                r2_mod_time, r2_file_size = self.get_r2_object_metadata(r2_object_key)
                if r2_mod_time is None:
                    self.upload_file_to_r2(local_file_full_path, r2_object_key)
                elif local_mod_time > r2_mod_time or local_file_size != r2_file_size:
                    self.upload_file_to_r2(local_file_full_path, r2_object_key)
                else:
                    continue

    def start_sync_loop(self):
        try:
            while True:
                if self.check_internet_connection():
                    self.sync_once()
                time.sleep(self.SYNC_INTERVAL_SECONDS)
        except (KeyboardInterrupt, SystemExit):
            pass
        except Exception:
            pass