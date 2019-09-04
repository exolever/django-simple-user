import re

from django.conf import settings

from auth_uuid.jwt_helpers import _build_jwt

from .faker_factory import faker
from .faker_user_factory import FakeUserFactory


class AccountTestMixin:

    def setUp(self):
        super().setUp()
        self.create_super_user()
        self.create_user()

    def create_user(self, password=None):
        password = password or '123456'
        self.user = FakeUserFactory.create(
            is_superuser=False,
            is_active=True,
            password=password)
        return self.user

    def create_super_user(self, password=None):
        password = password or '123456'
        self.super_user = FakeUserFactory.create(
            is_superuser=True,
            is_active=True,
            password=password)
        return self.super_user

    def get_user(self, password=None):
        password = password or '123456'
        user = FakeUserFactory.create(
            is_superuser=False,
            is_active=True,
            password=password
        )
        return user

    def init_mock(self, mock):
        matcher = re.compile('{}/api/accounts/me/'.format(settings.EXOLEVER_HOST))
        mock.register_uri(
            'GET',
            matcher,
            json=mock_callback)

    def setup_credentials(self, user):
        token = _build_jwt(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def reset_credentials(self):
        self.client.credentials()

    def setup_username_credentials(self):
        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)


class AccountRequestMock:

    def __init__(self):
        self._requests = {}

    def reset(self):
        self._requests = {}

    def add_request(self, uuid, response):
        self._requests[uuid] = response

    def get_request(self, uuid):
        return self._requests.get(uuid)

    def add_mock(self, user, is_consultant=False, **kwargs):
        response = {
            'uuid': str(user.uuid),
            'shortName': faker.first_name(),
            'fullName': faker.name(),
            'email': faker.email(),
            'groups': kwargs.get('groups', []),
            'consultantId': 1 if is_consultant else None,
            'profilePicture': [
                [[settings.SMALL_IMAGE_SIZE, settings.SMALL_IMAGE_SIZE], faker.image_url()],
                [[settings.MEDIUM_IMAGE_SIZE, settings.MEDIUM_IMAGE_SIZE], faker.image_url()],
                [[settings.LARGE_IMAGE_SIZE, settings.LARGE_IMAGE_SIZE], faker.image_url()],
            ],
            'userTitle': faker.word(),
            'profileUrl': faker.uri(),
            'hubs': [{'_type': 'T'}] if is_consultant else [],
            'isActive': True,
            'isStaff': False,
            'isSuperuser': kwargs.get('is_superuser', False),
        }
        response.update(**kwargs)
        self.add_request(
            str(user.uuid),
            response=response)


account_request_mock = AccountRequestMock()


def mock_callback(request, context):
    uuid = request.path.split('/')[-2]
    return account_request_mock.get_request(uuid)
