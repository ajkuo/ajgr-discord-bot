from ajgr import AJGRbot
import config

bot = AJGRbot(
    description=config.description
)

bot.run(config._login_token)