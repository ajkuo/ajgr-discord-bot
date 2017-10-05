import asyncio
from functools import wraps
from discord.ext.commands.bot import _get_variable

import config
import exceptions

def owner_only(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Only allow the owner to use these commands
        orig_msg = _get_variable('message')

        if not orig_msg or orig_msg.author.id == config.owner_id:
            return await func(*args, **kwargs)
        else:
            raise exceptions.PermissionsError("需要管理員權限。", expire_in=30)
    return wrapper