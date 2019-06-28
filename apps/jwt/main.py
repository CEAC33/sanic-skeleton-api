from sanic_jwt import exceptions
from sanic.log import logger

from apps.utils.mongo_utils import save_to_mongo, get_from_mongo
from config import Config 


class User:

    def __init__(self, id, username, password):
        self.user_id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return "User(id='{}')".format(self.user_id)

    def to_dict(self):
        return {"user_id": self.user_id, "username": self.username}


async def authenticate(request, *args, **kwargs):
    username_sent = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username_sent or not password:
        raise exceptions.AuthenticationFailed("Missing username or password.")

    # load default config
    config = Config()
    await config.load_config()

    user = await get_from_mongo(config, 'users', username_sent, 'username')

    if user is None:
        raise exceptions.AuthenticationFailed("User not found.")

    if password != user['password']:
        raise exceptions.AuthenticationFailed("Password is incorrect.")

    return user

    