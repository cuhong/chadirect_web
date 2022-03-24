from django.utils import timezone


def lunar_age(birthdate):
    now = timezone.localdate()
    birthdate_of_this_year = birthdate.replace(year=now.year)
    year = now.year - birthdate.year
    if now < birthdate_of_this_year:
        year -= 1
    return year