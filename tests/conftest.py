import pytest
from telegram import User

from ptbtest import UserGenerator

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture
def test_user(request) -> User:
    return UserGenerator().get_user(user_id=771940,
                                    username="ringo_starr",
                                    first_name="Ringo",
                                    last_name="Starr")