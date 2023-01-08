from pathlib import Path
import os, json
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def get_confidential(confidential_file_name, k):
        confidential_path = os.path.join(BASE_DIR, confidential_file_name)
        with open(confidential_path, 'r') as f:
            confidential_file = json.loads(f.read())
            
        try:
            return confidential_file[k]
        except KeyError:
            error_msg = "Set the {} environment variable".format(k)
            raise ImproperlyConfigured(error_msg)
