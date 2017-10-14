import asyncio
import aiohttp
import discord
import inspect
import importlib
import os
import sys
import traceback
from discord.ext import commands
from datetime import datetime

import config
import exceptions
from database import Db
from module import Module
from utils.decorators import owner_only


class Response:
    def __init__(self, content, reply=False, delete_after=0):
        self.content = content
        self.reply = reply
        self.delete_after = delete_after

class AJGRbot(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aiosession = aiohttp.ClientSession(loop=self.loop)
        self.prefix = config.command_prefix
        self.module_list = config.DEFAULT_MODULES
        self.running_module_name = []
        self.running_module = {}
        self.db = Db()

    def run(self, *args):
        try:
            self.loop.run_until_complete(self.start(*args))

        except discord.errors.LoginFailure:
            # Add if token, else
            raise exceptions.HelpfulError(
                "Bot cannot login, bad credentials.",
                "Fix your Email or Password or Token in the options file.  "
                "Remember that each field should be on their own line.")

        finally:
            try:
                self._cleanup()
            except Exception as e:
                print("Error in cleanup:", e)

            self.loop.close()
            if self.exit_signal:
                raise self.exit_signal

    async def on_ready(self):
        try:
            os.system('cls')
            with open("welcome_ascii.txt") as text_file:
                print(text_file.read())
            print()
            for mod in self.module_list:
                try:
                    res = self.load_module(mod)
                    if res:
                        self.safe_print(" [v] Module '{}' is ready.".format(mod))
                    else:
                        self.safe_print(" [-] Module '{}' loading failed.".format(mod))
                        self.safe_print("   --- (Please check the parent module have been loading.)")

                except Exception as e:
                    self.safe_print(" [-] Module '{}' loading failed.".format(mod))
                    self.safe_print("   --- ({}: {})".format(type(e).__name__, e))
            print()
            self.safe_print(' [v] Bot information:')
            self.safe_print('   --- {} / {}'.format(self.user.id, self.user))
            self.safe_print('   --- Command prefix: {}'.format(self.prefix))
            print()
            await self.change_status()
            print()
            self.safe_print(' [v] {}  -- Connected. Enjoy it!'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            print()
                
        except Exception as e:
            print(type(e).__name__ + ': ' + str(e))

    async def on_error(self, event, *args, **kwargs):
        ex_type, ex, stack = sys.exc_info()

        if ex_type == exceptions.HelpfulError:
            print("Exception in", event)
            print(ex.message)

            await asyncio.sleep(2)  # don't ask
            await self.logout()

        elif issubclass(ex_type, exceptions.Signal):
            self.exit_signal = ex_type
            await self.logout()

        else:
            traceback.print_exc()

    async def on_member_join(self, member):
        for name in self.running_module:
            mod = self.running_module[name]
            self.loop.create_task(mod.on_member_join(member))

    async def on_message(self, message):
        # 檢查是否為 BOT 自己傳送的訊息
        if message.author == self.user:
            return
        
        # 檢查是否為其他 BOT 傳送的訊息
        if message.author.bot:
            return

        # 執行每個 Module 裡面的 on_message 事件 (放在這裡是因為不一定要輸入 prefix 才能執行, 也有可能有的模組可以回覆私人訊息)
        for name in self.running_module:
            mod = self.running_module[name]
            self.loop.create_task(mod.on_message(message))

        # 檢查是否為私人訊息 -> 如果某個模組需要用私訊，目前是放在該模組 on_message 事件來偵測，
        # 但是該模組執行完還是會繼續執行這邊的程式碼，所以目前把提示訊息隱藏，如果完全不會用到私訊功能，可以取消註解。
        if message.channel.is_private:
            # await self.safe_send_message(message.channel, "您的指令錯誤，或是目前無法回覆私人訊息哦。")
            return

        message_content = message.content.strip()
        if not message_content.startswith(self.prefix):
            return

        command, *args = message_content.split()  # Uh, doesn't this break prefixes with spaces in them (it doesn't, config parser already breaks them)
        command = command[len(self.prefix):].lower().strip()

        handler = getattr(self, 'cmd_%s' % command, None)
        if not handler:
            for name in self.running_module:
                mod = self.running_module[name]
                temp = getattr(mod, 'cmd_%s' % command, None)                 
                if temp:
                    handler = temp                  
            if not handler:
                return


        self.safe_print("[Command] {0.id}/{0} ({1})".format(message.author, command))

        argspec = inspect.signature(handler)
        params = argspec.parameters.copy()
        try:
            handler_kwargs = {}
            if params.pop('message', None):
                handler_kwargs['message'] = message

            args_expected = []
            for key, param in list(params.items()):
                doc_key = '[%s=%s]' % (key, param.default) if param.default is not inspect.Parameter.empty else key
                args_expected.append(doc_key)

                if not args and param.default is not inspect.Parameter.empty:
                    params.pop(key)
                    continue

                if args:
                    arg_value = args.pop(0)
                    handler_kwargs[key] = arg_value
                    params.pop(key)

            # if message.author.id != self.config.owner_id:
            #     raise exceptions.PermissionsError(
            #         "This command is not enabled for you.",
            #         expire_in=20)

            if params:
                docs = getattr(handler, '__doc__', None)
                if not docs:
                    docs = '使用方式: {}{} {}'.format(
                        self.prefix,
                        command,
                        ' '.join(args_expected)
                    )

                docs = '\n'.join(l.strip() for l in docs.split('\n'))
                await self.safe_send_message(
                    message.channel,
                    '```\n%s\n```' % docs.format(command_prefix=self.prefix),
                    expire_in=60
                )
                return

            response = await handler(**handler_kwargs)
            if response and isinstance(response, Response):
                content = response.content
                if response.reply:
                    content = '%s, %s' % (message.author.mention, content)

                sentmsg = await self.safe_send_message(
                    message.channel, content,
                    expire_in= 0,
                    also_delete= None
                )

        except (exceptions.CommandError, exceptions.HelpfulError, exceptions.ExtractionError) as e:
            print("{0.__class__}: {0.message}".format(e))

            expirein = e.expire_in if config.delete_messages else None
            alsodelete = message if config.delete_invoking else None

            await self.safe_send_message(
                message.channel,
                '```\n%s\n```' % e.message,
                expire_in=expirein,
                also_delete=alsodelete
            )
        except exceptions.Signal:
            raise
        except Exception as e:
            traceback.print_exc()
   
    async def change_status(self, status=config.default_status):
        """changes bots status"""
        try:
            if status != ():
                await self.ws.change_presence(game=discord.Game(name="{0}".format(status)))
                self.safe_print(' [v] Bot status now is "{}"'.format(status))
        except:
            pass

    def safe_print(self, content, *, end='\n', flush=True):
        sys.stdout.buffer.write((content + end).encode('utf-8', 'replace'))
        if flush:
            sys.stdout.flush()

    async def safe_send_message(self, dest, content=None, *, tts=False, expire_in=0, also_delete=None, quiet=False, embed=None):
        msg = None
        try:
            if embed != None:
                msg = await self.send_message(dest, embed=embed)
            elif content != None:
                msg = await self.send_message(dest, content, tts=tts)
            else:
                return

            if msg and expire_in:
                asyncio.ensure_future(self._wait_delete_msg(msg, expire_in))

            if also_delete and isinstance(also_delete, discord.Message):
                asyncio.ensure_future(self._wait_delete_msg(also_delete, expire_in))

        except discord.Forbidden:
            if not quiet:
                self.safe_print("Warning: Cannot send message to %s, no permission" % dest.name)

        except discord.NotFound:
            if not quiet:
                self.safe_print("Warning: Cannot send message to %s, invalid channel?" % dest.name)

        return msg

    async def safe_delete_message(self, message, *, quiet=False):
        try:
            return await self.delete_message(message)

        except discord.Forbidden:
            if not quiet:
                self.safe_print("Warning: Cannot delete message \"%s\", no permission" % message.clean_content)

        except discord.NotFound:
            if not quiet:
                self.safe_print("Warning: Cannot delete message \"%s\", message not found" % message.clean_content)

    async def safe_edit_message(self, message, new, *, send_if_fail=False, quiet=False):
        try:
            return await self.edit_message(message, new)

        except discord.NotFound:
            if not quiet:
                self.safe_print("Warning: Cannot edit message \"%s\", message not found" % message.clean_content)
            if send_if_fail:
                if not quiet:
                    print("Sending instead")
                return await self.safe_send_message(message.channel, new)

    async def _wait_delete_msg(self, message, after):
        await asyncio.sleep(after)
        await self.safe_delete_message(message)

    def load_module(self, name):
        if name in self.running_module:
            return False

        master_module_name = name.split("mods.")[1]
        if len(master_module_name.split(".")) > 1:
            if master_module_name.split(".")[-2] == master_module_name.split(".")[-1]:
                if len(master_module_name.split(".")) > 2:
                    for i in range(0, len(master_module_name.split(".")) - 2):
                        check_module_name = "mods." + ".".join(master_module_name.split(".")[:-2]) 
                        check_module_name += "." + master_module_name.split(".")[-3]
                        if check_module_name in self.running_module:
                            pass
                        else:
                            return False

            else:
                master_module_name = master_module_name.split(".")[-2]
                master_module_name = name[:name.rfind(master_module_name) + len(master_module_name)] + "." + master_module_name
                if master_module_name not in self.running_module:
                    return False

        lib = getattr(importlib.import_module(name), name.split(".")[-1])
        self.running_module[name] = lib(self)
        return True

    def unload_module(self, name):
        lib = self.running_module.get(name)
        if lib is None:
            return

        try:
            func = getattr(lib, 'teardown')

        except AttributeError:
            pass
        else:
            try:
                func(self)
            except:
                pass
        finally:
            IsMasterModule = False
            master_module_name = name.split("mods.")[1]
            if len(master_module_name.split(".")) > 1:
                if master_module_name.split(".")[-2] == master_module_name.split(".")[-1]:
                    master_module_name = master_module_name.split(".")[-2]
                    master_module_name = name[:master_module_name.rfind(master_module_name) - len(master_module_name)]
                    IsMasterModule = True

            if IsMasterModule:
                del_mod = []
                for mod in self.running_module:
                    if mod == name:
                        continue
                    if master_module_name in mod:
                        del_mod.append(mod)
                        del sys.modules[mod]
                        self.module_list.remove(mod)
                if len(del_mod) > 0:
                    for del_name in del_mod:
                        del self.running_module[del_name]

            del lib
            del self.running_module[name]
            del sys.modules[name]
            self.module_list.remove(name)

    async def logout(self):
        return await super().logout()

    def _cleanup(self):
        try:
            self.loop.run_until_complete(self.logout())
        except: # Can be ignored
            pass

        pending = asyncio.Task.all_tasks()
        gathered = asyncio.gather(*pending)

        try:
            gathered.cancel()
            self.loop.run_until_complete(gathered)
            gathered.exception()
        except: # Can be ignored
            pass

    @owner_only
    async def cmd_test(self, message):
        for module in self.running_module:
            await self.safe_send_message(message.channel, self.running_module[module])

    # 透過指令將模組上線，直接打模組名稱，前面不用加上 mods. -> 模組要放在 mods/
    @owner_only
    async def cmd_modload(self, message):
        module = message.content.split(' ')[1]
        module = "mods." + module
        if module not in self.running_module:
            try:
                msg = await self.safe_send_message(message.channel,"模組 `{0}` 載入中 ...".format(module))
                res = self.load_module(module)
                if res:
                    self.module_list.append(module)
                    await self.safe_edit_message(msg, "**完成。** 模組 `{0}` 已經順利掛載。".format(module))
                else:
                    await self.safe_edit_message(msg, "**失敗。** 模組 `{0}` 未掛載，可能是必要模組尚未掛載或是模組已在運行。".format(module))
            except Exception as e:
                await self.safe_edit_message(msg, "*:warning: **錯誤:** `{}`".format(str(e)))

        else:
            await self.safe_send_message(message.channel, ":warning: **錯誤:** `模組已經在模組清單內，請重新確認。`")

    # 透過指令將模組卸載
    @owner_only
    async def cmd_modunload(self, message):
        module = message.content.split(' ')[1]
        module = "mods." + module
        if module in self.running_module:
            try:
                msg = await self.safe_send_message(message.channel,"模組 `{0}` 卸載中 ...".format(module))
                self.unload_module(module)
                await self.safe_edit_message(msg, "**完成。** 模組 `{0}` 已經順利卸載。".format(module))
            except Exception as e:
                await self.safe_edit_message(msg, "*:warning: **錯誤:** `{}`".format(str(e)))

        else:
            await self.safe_send_message(message.channel, ":warning: **錯誤:** `{0}` 不在模組清單內。".format(module))

    # 顯示目前 BOT 執行的模組清單
    @owner_only
    async def cmd_showmod(self, message):
        try:
            text = "-\n\nNow running module(s):\n\n"
            for module in self.running_module:
                module = module.split('mods.')[1]
                text += "`{}`, ".format(module)
            if len(self.running_module) == 0:
                text += "`There is no module running.`" 
            else:
                text = text[:-2]
            await self.safe_send_message(message.channel, "{}".format(text))

        except Exception as e:
            await self.safe_send_message(message.channel, "*:warning: **錯誤:** `{}`".format(str(e)))

    # 更改 BOT 的顯示狀態
    @owner_only
    async def cmd_status(self, message):
        """changes bots status"""
        status = ' '.join(message.content.split(' ')[1:])

        if status == "":
            status = "A.J. Group"

        if len(status) > 100:
            status = status[:100]

        if status != ():
            await self.ws.change_presence(game=discord.Game(name="{0}".format(status)))
        
        await self.delete_message(message)
        await self.safe_send_message(message.channel, " 👌 BOT 狀態目前已經更改為 `{0}` 。".format(status), expire_in=10)

    # 更改 BOT 的大頭照
    @owner_only
    async def cmd_setavatar(self, message):
        url = message.content.split(" ")[1]
        try:
            if message.attachments:
                thing = message.attachments[0]['url']
            else:
                thing = url.strip('<>')

            with aiohttp.Timeout(10):
                async with self.aiosession.get(thing) as res:
                    await self.edit_profile(avatar=await res.read())

        except Exception as e:
            raise exceptions.CommandError(":warning: 錯誤: `%s`" % e, expire_in=20)

        return Response(":ok_hand:", delete_after=20)

    # 更改 BOT 的暱稱
    @owner_only
    async def cmd_setnick(self, message):
        """
        Usage:
            {command_prefix}setnick nick

        Changes the bot's nickname.
        """

        if not message.channel.permissions_for(message.server.me).change_nickname:
            raise exceptions.CommandError("Unable to change nickname: no permission.")

        nick = " ".join(message.content.split(" ")[1:])

        try:
            await self.change_nickname(message.server.me, nick)
        except Exception as e:
            raise exceptions.CommandError(e, expire_in=20)

        return Response(":ok_hand:", delete_after=20)

    # 更改 BOT 的會員名字 (每小時只能更改二次)
    @owner_only
    async def cmd_setname(self, message):
        """
        Usage:
            {command_prefix}setname name

        Changes the bot's username.
        Note: This operation is limited by discord to twice per hour.
        """

        name = " ".join(message.content.split(" ")[1:])

        try:
            await self.edit_profile(username=name)
        except Exception as e:
            raise exceptions.CommandError(e, expire_in=20)

        return Response(":ok_hand:", delete_after=20)

    @owner_only
    async def cmd_emojiid(self, message):
        emoji_str = ""
        for idx, emoji in enumerate(message.server.emojis):
            emoji_str += "`{0} - {1}: {2}`\n".format(str(idx+1).rjust(2, '0'), emoji.name, emoji.id)
        await self.safe_send_message(message.channel, emoji_str)

