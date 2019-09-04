import factory

from django.contrib.auth import get_user_model
from django.utils.timezone import now

from .faker_factory import faker


class FakeUserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = get_user_model()

    email = factory.LazyAttribute(lambda x: faker.email())
    short_name = factory.LazyAttribute(lambda x: faker.first_name())
    full_name = factory.LazyAttribute(lambda x: '{} {}'.format(faker.first_name(), faker.last_name()))
    password = '123456'
    last_login = now()
    is_active = True
    is_superuser = False
    is_staff = False
