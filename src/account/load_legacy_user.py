import os.path
import pickle
import csv

from django.conf import settings

path = os.path.join(settings.BASE_DIR, 'account', 'legacy_user.csv')

with open(path, 'r') as file:
    reader = csv.DictReader(file)
    data_list = [dict(line) for line in reader]