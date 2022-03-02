import os.path
import pickle

from django.conf import settings

path = os.path.join(settings.BASE_DIR, 'account', 'legacy_user.txt')

with open(path, 'rb') as file:
    user_data_list = pickle.load(file)