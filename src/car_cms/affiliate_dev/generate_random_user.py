import random

from faker import Faker
from tqdm import tqdm

from account.models import Organization, User

faker = Faker('ko_KR')

organization = Organization.objects.get(id=4)

email_list = list(set([faker.email() for i in range(500)]))

user_list = [
    {
        "email": email, "name": faker.name(), "cellphone": "".join([s for s in str(faker.phone_number()) if s.isdigit()]), "organization": organization,
        "is_organization_admin": True if random.random() < 0.05 else False, "password": "p@assword1!"
    } for email in tqdm(email_list)
]

for user in tqdm(user_list):
    created_user = User.objects.create_user(**user)