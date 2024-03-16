import random
import time
from typing import Union

from faker import Faker

from models.user import User

fake = Faker("es_CO")


def mock_user(user_id: str | None) -> Union[None, User]:
    time.sleep(random.uniform(0.1, 0.9))
    if user_id is None:
        return None
    return User(id=user_id, name=fake.name(), email=fake.email(), phone_number=123456789)
