import inspect

class Module(object):
    def __init__(self, AJGRbot):
        self.bot = AJGRbot

    async def on_message(self, message):
        pass

    async def on_member_join(self, member):
        pass