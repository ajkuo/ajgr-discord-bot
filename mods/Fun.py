from module import Module
import aiohttp
import json
import random, requests
import os, sys
import re
import exceptions
from io import BytesIO

import config
from utils.decorators import owner_only

class Object(object):
    pass

def discord_path(self, path):
    return os.path.join(os.getenv('discord_path', '~/discord/'), path)

def files_path(self, path):
    return os.path.join(os.getenv('files_path', 'files/'), path)

async def bytes_download(self, link:str):
    with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            data = await resp.read()
            b = BytesIO(data)
            b.seek(0)
            return b

class Fun(Module):

    async def on_message(self, message):
        await self.CheckKeywords(message)

    async def cmd_sleep(self, message):
        await self.bot.safe_send_message(message.channel, "各 位 觀 眾 ！ 沒事，我先睡了。   `Sent from {}`".format(message.author))

    async def cmd_e(self, message):
        """
        使用方式:
            {command_prefix}e [表情符號]

        將表情符號放大顯示。
        (※ 請適度使用，若惡意洗頻將會被禁止發言。)
        """
        # 有可能傳很多個表情，用空格分開
        emote_regex = re.compile(r"<:(.*):([0-9]+)>", re.IGNORECASE)
        ems = " ".join(message.content.split(" ")[1:])
        ems = ems.split(" ")
        #await self.safe_send_message(channel, "TEST: {0}".format(ems[0]), expire_in=10, also_delete=ems)                 
        #del ems[0]

        try:
            if len(ems) == 1:
                em = ems[0]
                em = em.lower()
                em = em.encode("unicode_escape").decode()
                if "\\U000" in em and em.count("\\U000") == 1:
                    em = em.replace("\\U000", '')
                elif em.count("\\U000") == 2:
                    em = em.split("\\U000")
                    em = '{0}-{1}'.format(em[1], em[2])
                else:
                    em = em.replace("\\u", '')
                path = files_path(self, 'emoji/{0}.png'.format(em))
                if em == ':b1:':
                    path = files_path(self, 'b1.png')
                if os.path.isfile(path) == False:
                    match = emote_regex.match(ems[0])
                    if match == None or len(match.groups()) == 0:
                        await self.bot.safe_send_message(message.channel, ":warning: `錯誤: 表情錯誤或是圖片不存在。", expire_in=10, also_delete=ems)
                        return
                    emote = 'https://cdn.discordapp.com/emojis/{0}.png'.format(str(match.group(2)))
                    path = await bytes_download(self, emote)
                    if sys.getsizeof(path) == 88:
                        await self.bot.safe_send_message(message.channel, ":warning: `錯誤: 表情錯誤或是圖片不存在。`", expire_in=10, also_delete=ems)
                        return
                await self.bot.delete_message(message)
                await self.bot.send_file(message.channel, path, filename='emoji.png')
                await self.bot.safe_send_message(message.channel, "`Sent from {0}`".format(message.author))
            else:
                list_imgs = []
                count = -1
                for em in ems:
                    count += 1
                    em = em.lower()
                    em = em.encode("unicode_escape").decode()
                    if "\\U000" in em and em.count("\\U000") == 1:
                        em = em.replace("\\U000", '')
                    elif em.count("\\U000") == 2:
                        em = em.split("\\U000")
                        em = '{0}-{1}'.format(em[1], em[2])
                    else:
                        em = em.replace("\\u", '')
                    path = files_path(self, 'emoji/{0}.png'.format(em))
                    if os.path.isfile(path) == False:
                        match = emote_regex.match(ems[count])
                        emote = 'https://cdn.discordapp.com/emojis/{0}.png'.format(str(match.group(2)))
                        path = await bytes_download(self, emote)
                        if sys.getsizeof(path) == 88:
                            continue
                    list_imgs.append(path)
                imgs = [PIL.Image.open(i).convert('RGBA') for i in list_imgs]
                min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
                imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))
                imgs_comb = PIL.Image.fromarray(imgs_comb)
                png_info = imgs[0].info
                b = BytesIO()
                imgs_comb.save(b, 'png', **png_info)
                b.seek(0)
                try:
                    await self.bot.delete_message(message)
                    await self.bot.send_file(message.channel, b, filename='merged_emotes.png')
                    await self.bot.safe_send_message(message.channel, "`Sent from {0}`".format(message.author))
                except:
                    await self.bot.safe_send_message(message.channel, ":cold_sweat: `抱歉，圖片太大了，無法上傳。`", expire_in=10, also_delete=ems)
        except Exception as e:
            raise exceptions.CommandError("Error:%s" % e, expire_in=10)
    
    # 遇到關鍵字自動呼叫內容
    async def CheckKeywords(self, message):
        text = message.content.strip().upper()
        keywordList = self.bot.db.execute_sql("SELECT Name, SN FROM Keywords UNION SELECT Name, Keyword_SN FROM ViceKeywords")
        imgList = []
        for keyword in keywordList:
            if str(keyword[0]).upper() in text:
                imgList = self.bot.db.get_value("KeywordURLs tbURL", "URL, SN", "tbURL.Keyword_SN = {}".format(keyword[1]))
                break

        if (imgList is not None) and (len(imgList) > 0):
            idx = random.randint(0, len(imgList) - 1)
            if config.CONSOLE_SHOW_FUNNY_IMAGE:
                self.bot.safe_print("[FunnyImage] {0.id}/{0.name} @ #{1} ({2})".format(message.author, message.channel.name, text))
            await self.bot.safe_send_message(message.channel, "`[{0}]` {1}".format(imgList[idx][1], str(imgList[idx][0])))
            return

    def check_KeywordExist(self, keyword):
        SQL = """
            SELECT (tbKey.Count + tbVice.Count) Count
            FROM
            (
                SELECT COUNT(*) Count
                FROM Keywords 
                WHERE Name = '{}'
            ) tbKey,
            (
                SELECT COUNT(*) Count
                FROM ViceKeywords 
                WHERE Name = '{}'
            ) tbVice
        """.format(keyword, keyword)
        count = self.bot.db.execute_sql(SQL)[0][0]

        if count == 0:
            return True
        
        else:
            return False

    async def cmd_keywords(self, message):
        publish_str = " 📗 ` 關鍵字清單 ` \n\n"
        keywordList = self.bot.db.get_value("Keywords", "Name, SN")         
        if (keywordList is not None) and (len(keywordList) > 0):
            publish_str += "```"
            for idx, keyword in enumerate(keywordList):
                publish_str += "[{}] {}".format(str(idx+1).rjust(3, '0'), keyword[0])
                viceList = self.bot.db.get_value("ViceKeywords", "Name", "Keyword_SN = {}".format(keyword[1]))
                if (viceList is not None) and (len(viceList) > 0):
                    publish_str += ", "
                    for vice in viceList:
                        publish_str += "{}, ".format(vice[0])
                    publish_str = publish_str[:-2]
                    publish_str += "\n"

                else:
                    publish_str += "\n"
            publish_str += "```"

        else:                
            publish_str += " 👉 目前尚無任何關鍵字。"

        if message.channel.id == "251041379336192000":
            await self.bot.safe_send_message(message.channel, "{}".format(publish_str))
        else:
            await self.bot.delete_message(message)
            await self.bot.safe_send_message(message.channel, "{}\n\n:warning: **非 `#bot-test` 頻道，10秒後自動刪除此訊息。**".format(publish_str), expire_in= 10)

    @owner_only
    async def cmd_addkeyword(self, message):
        try:
            keyword = message.content.split(' ')[1]
            if self.check_KeywordExist(keyword):
                self.bot.db.execute_sql("INSERT INTO Keywords(Name) VALUES('{}')".format(keyword))
                await self.bot.safe_send_message(message.channel, " 👌 關鍵字 `{}` 新增成功。".format(keyword))
            
            else:
                await self.bot.safe_send_message(message.channel, " 👉 關鍵字 `{}` 已經存在。".format(keyword))
                return

        except Exception:
            await self.bot.safe_send_message(message.channel, " ⚠ 請輸入正確參數 `{}addkeyword <關鍵字>` 。".format(config.command_prefix), expire_in=10)

    @owner_only
    async def cmd_addkeyurl(self, message):
        try:
            keyword = message.content.split(' ')[1]
            url = " ".join(message.content.split(' ')[2:])
            if not self.check_KeywordExist(keyword):
                SQL = """
                    SELECT SN
                    FROM Keywords
                    WHERE Name = '{}'
                    UNION
                    SELECT Keyword_SN
                    FROM ViceKeywords tbVice
                    WHERE Name = '{}'
                """.format(keyword, keyword)
                keywordSN = self.bot.db.execute_sql(SQL)[0][0]
                self.bot.db.execute_sql("INSERT INTO KeywordURLs(Keyword_SN, URL) VALUES({}, '{}')".format(keywordSN, url))              
                await self.bot.delete_message(message)
                await self.bot.safe_send_message(message.channel, " 👌 關鍵字 `{}` 圖片網址新增成功。".format(keyword), expire_in=10)
            else:
                await self.bot.safe_send_message(message.channel, " ⚠ 關鍵字 `{}` 不存在。".format(keyword), expire_in=10)            

        except Exception as e:
            self.bot.safe_print(str(e))
            await self.bot.safe_send_message(message.channel, " ⚠ 請輸入正確參數 `{}addkeyurl <關鍵字> <對應內容>` 。".format(config.command_prefix), expire_in=10)

    @owner_only
    async def cmd_addvicekey(self, message):
        try:
            keyword = message.content.split(' ')[1]
            vice = message.content.split(' ')[2]
            if not self.check_KeywordExist(keyword):
                SQL = """
                    SELECT SN
                    FROM Keywords
                    WHERE Name = '{}'
                    UNION
                    SELECT Keyword_SN
                    FROM ViceKeywords tbVice
                    WHERE Name = '{}'
                """.format(keyword, keyword)
                keywordSN = self.bot.db.execute_sql(SQL)[0][0]
                self.bot.db.execute_sql("INSERT INTO ViceKeywords(Keyword_SN, Name) VALUES({}, '{}')".format(keywordSN, vice))             
                await self.bot.delete_message(message)
                await self.bot.safe_send_message(message.channel, " 👌 關鍵字 `{}` 的同義詞 `{}` 新增成功。".format(keyword, vice), expire_in=10)
            else:
                await self.bot.safe_send_message(message.channel, " ⚠ 關鍵字 `{}` 不存在。".format(keyword), expire_in=10)            

        except Exception:
            await self.bot.safe_send_message(message.channel, " ⚠ 請輸入正確參數 `{}addvicekey <關鍵字> <同義詞>` 。".format(config.command_prefix), expire_in=10)


