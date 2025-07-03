import os
import time
import datetime
import socket
import mimetypes

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
from log_utils import log_console

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

        self._validate_env()
        self.s3_client = self._init_r2_client()

    def _validate_env(self):
        missing_env_vars = []
        if not self.CF_ACCOUNT_ID:
            missing_env_vars.append("CF_ACCOUNT_ID")
        if not self.CF_R2_ACCESS_KEY_ID:
            missing_env_vars.append("CF_R2_ACCESS_KEY_ID")
        if not self.CF_R2_SECRET_ACCESS_KEY:
            missing_env_vars.append("CF_R2_SECRET_ACCESS_KEY")
        if not self.CF_R2_BUCKET_NAME:
            missing_env_vars.append("CF_R2_BUCKET_NAME")
        if missing_env_vars:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing_env_vars)}")

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
        except Exception as e:
            log_console(f"Unexpected error during R2 client setup: {e}", "ERROR")
            raise

    def check_internet_connection(self, host="www.google.com", port=80, timeout=3):
        """
        Checks for an active internet connection by attempting to create a socket connection.
        Uses 'www.google.com' on port 80 (HTTP) as a test target.
        Includes a timeout to prevent indefinite hanging.
        """
        try:
            ip_address = socket.gethostbyname(host)
            with socket.create_connection((ip_address, port), timeout=timeout):
                return True
        except socket.gaierror:
            print(f"WARNING: Internet check failed - Could not resolve hostname '{host}'. (DNS issue?)")
        except socket.timeout:
            print(f"WARNING: Internet check failed - Connection to {host}:{port} timed out.")
        except ConnectionRefusedError:
            print(f"WARNING: Internet check failed - Connection to {host}:{port} refused. (Firewall or service down on target?)")
        except OSError as e:
            print(f"WARNING: Internet check failed for {host}:{port}. Details: {e}")
        except Exception as e:
            print(f"ERROR: An unexpected error occurred during internet check: {e}")
        return False

    def get_r2_object_metadata(self, r2_key):
        """Gets metadata (like last modified time and size) for an object in R2."""
        try:
            response = self.s3_client.head_object(Bucket=self.CF_R2_BUCKET_NAME, Key=r2_key)
            return response['LastModified'].timestamp(), response['ContentLength']
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == 'NoSuchKey' or e.response['ResponseMetadata']['HTTPStatusCode'] == 404:
                return None, None
            elif error_code == 'AccessDenied':
                print(f"ERROR: Access denied to get metadata for '{r2_key}'. Check R2 API token permissions (e.g., 's3:HeadObject').")
                return None, None
            else:
                print(f"ERROR: R2 Metadata Error for '{r2_key}': {error_code}")
                return None, None
        except Exception as e:
            print(f"ERROR: Unexpected error getting R2 metadata for '{r2_key}': {e}")
            return None, None

    def upload_file_to_r2(self, local_path, r2_key):
        """Uploads a single file to R2."""
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
            print(f"[UPLOADED] '{local_path}' -> R2 as '{r2_key}' (Type: {content_type})")
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            error_message = e.response.get("Error", {}).get("Message")
            print(f"[FAILED UPLOAD] '{local_path}' to '{r2_key}'. R2 Error: {error_code}")
            if error_code == 'AccessDenied':
                print("  HINT: Check your R2 API token permissions for 's3:PutObject' action on this bucket.")
            elif error_code == 'NoSuchBucket':
                print(f"  HINT: The specified R2 bucket '{CF_R2_BUCKET_NAME}' does not exist or you don't have access.")
            return False
        except FileNotFoundError:
            print(f"[SKIPPED] Local file not found: '{local_path}'. It might have been deleted before upload.")
            return False
        except Exception as e:
            print(f"[FAILED UPLOAD] An unexpected error occurred for '{local_path}': {e}")
            return False

    def sync_once(self):
        """Synchronizes the local folder with the R2 bucket."""
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n--- Starting synchronization at {current_time} ---")

        if not os.path.isdir(self.LOCAL_FOLDER_TO_SYNC):
            print(f"CRITICAL ERROR: The local folder to sync ('{self.LOCAL_FOLDER_TO_SYNC}') does not exist.")
            print("Please create this folder or adjust 'LOCAL_FOLDER_TO_SYNC' in the script and restart.")
            return

        for root, _, files in os.walk(self.LOCAL_FOLDER_TO_SYNC):
            for file_name in files:
                local_file_full_path = os.path.join(root, file_name)
                r2_object_key = os.path.relpath(local_file_full_path, self.LOCAL_FOLDER_TO_SYNC).replace(os.sep, '/')

                try:
                    local_mod_time = os.path.getmtime(local_file_full_path)
                    local_file_size = os.path.getsize(local_file_full_path)
                except OSError as e:
                    print(f"WARNING: Could not access local file '{local_file_full_path}'. Skipping. Error: {e}")
                    continue

                r2_mod_time, r2_file_size = self.get_r2_object_metadata(r2_object_key)

                if r2_mod_time is None:
                    print(f"[NEW FILE] '{r2_object_key}' detected.")
                    self.upload_file_to_r2(local_file_full_path, r2_object_key)
                elif local_mod_time > r2_mod_time or local_file_size != r2_file_size:
                    print(f"[CHANGED] '{r2_object_key}' is newer or different size. Uploading update.")
                    self.upload_file_to_r2(local_file_full_path, r2_object_key)
                else:
                    print(f"[UP-TO-DATE] '{r2_object_key}'. Skipping.")

        print(f"--- Synchronization finished at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

    def start_sync_loop(self):
        """Starts the synchronization loop, checking the internet connection and syncing at regular intervals."""
        try:
            while True:
                if self.check_internet_connection():
                    print("Internet connection active. Proceeding with sync.")
                    self.sync_once()
                else:
                    print("No internet connection detected. Waiting to retry...")

                time.sleep(self.SYNC_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print("Sync loop stopped by user.")
        except Exception as e:
            log_console(f"Error during sync: {e}", "ERROR")

# Example usage from another script:
# from sync_r2 import R2FolderSync
# syncer = R2FolderSync(local_folder="example", sync_interval=5)
# syncer.sync_once()  # For one-time sync
# syncer.start_sync_loop()  # For continuous sync