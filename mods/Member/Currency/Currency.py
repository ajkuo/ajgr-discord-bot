from module import Module
import discord
import config
import math, random, time
from datetime import datetime, timedelta
from utils.decorators import owner_only

class Currency(Module):

    def GetUserAssets(self, member):
        """
            回傳 User 的資產，res[0]: 現金
        """
        assets = self.bot.db.get_value("Users", "USER_MONEY", "USER_ID = {}".format(member.id))
        return assets[0]

    def GetUserAssetsRank(self, member):
        SQL = """ 
            SELECT member.RANK, server.COUNT
            FROM (
                SELECT USER_ID, USER_MONEY, @rank:=@rank+1 as RANK
                FROM Users, (SELECT @rank := 0) r
                ORDER BY USER_MONEY DESC, USER_ID ASC
            ) member, (
                SELECT COUNT(*) COUNT
                FROM Users
            ) server
            WHERE member.USER_ID = '{}';
        """.format(member.id)
        res = self.bot.db.execute_sql(SQL)
        return res[0]

    def SetUserMoney(self, usr, amount, change_type, sender="sys"):
        """
            改變使用者的滷幣現金
            依照 type 不同可分為:
            add: 增加
            sub: 減少
            cover: 改變為指定金額
            gift: 他人贈送 -> 要另外扣除贈送方的滷幣
        """
        change_type = change_type.lower()
        amount = math.floor(float(amount))
        balance = self.GetUserAssets(usr)[0]
        if change_type == "cover":
            balance = amount
        elif change_type == "add" or change_type == "gift":
            balance += amount
        elif change_type == "sub":
            balance -= amount

        if balance < 0:
            balance = 0

        self.bot.db.execute_sql("UPDATE Users SET USER_MONEY = {} WHERE USER_ID = '{}';".format(balance, usr.id))
        self.SetMoneyLog(usr, amount, change_type, sender)

    def SetMoneyLog(self, reciver, amount, change_type, sender):
        reciver = reciver.id
        amount = math.floor(float(amount))
        change_type = change_type.lower()
        self.bot.db.execute_sql("INSERT INTO Log_EarnMoney(SOURCE, USER_ID, EARN_MONEY, EARN_TIME, EARN_TYPE) VALUES('{}', '{}', {}, '{}', '{}');".format(sender, reciver, amount, datetime.now(), change_type))
          
    @owner_only
    async def cmd_setmoney(self, message):
        if not message.mentions:
            usr = message.author
            if len(message.content.strip().split(" ")) != 3:
                await self.bot.safe_send_message(message.channel, ":warning: 參數錯誤，使用方式為：`setmoney (mention) <add|sub|cover> <amount>`", expire_in=10)
                return                
        else:
            usr = message.mentions[0]

            if len(message.content.strip().split(" ")) != 4:
                await self.bot.safe_send_message(message.channel, ":warning: 參數錯誤，使用方式為：`setmoney (mention) <add|sub|cover> <amount>`", expire_in=10)
                return

        change_type = message.content.split(" ")[-2].strip()
        if change_type not in ["add", "sub", "cover"]:
            await self.bot.safe_send_message(message.channel, ":warning: 參數錯誤，只能使用 `add|sub|cover` 類型來改變金額。", expire_in=10)
            return

        amount = message.content.split(" ")[-1].strip()
        try:
            amount = math.floor(float(amount))

        except ValueError:
            await self.bot.safe_send_message(message.channel, ":warning: 參數錯誤，使用方式為：`setmoney (mention) <add|sub|cover> <amount>`", expire_in=10)
            return         

        self.SetUserMoney(usr, amount, change_type, sender=message.author)
        hint_str = {'add': '增加', 'sub': '減少', 'cover': '變為'}
        await self.bot.delete_message(message)
        await self.bot.safe_send_message(message.channel, "Done. `已經將 {} 的滷幣{} {} 個了。`".format(usr, hint_str[change_type], amount), expire_in=10)

    async def cmd_give(self, message):
        """
        使用方式:
            {command_prefix}give [金額] [@user]

        將滷幣贈送給其他成員。
        (※ 送出後無法收回，請謹慎使用。)
        """
        if not message.mentions:
            await self.bot.safe_send_message(message.channel, "👉 請指定您要將滷幣送給誰哦。")
        else:
            amount = message.content.split(" ")[-1].strip()
            try:
                amount = math.floor(float(amount))

            except ValueError:
                await self.bot.safe_send_message(message.channel, ":warning: 金額錯誤，請確定您輸入的是數字。", expire_in=10)
                return         

            usr = message.mentions[0]
            balance = self.GetUserAssets(message.author)[0]
            try:
                if amount > balance or balance == 0:
                    await self.bot.safe_send_message(message.channel, "👉 {0} 您的滷幣不足，您目前只有 🍢 {1} 個滷幣。".format(message.author.mention, balance))

                else:
                    self.SetUserMoney(message.author, amount, "sub")
                    self.SetUserMoney(usr, amount, "gift", message.author)

                    await self.bot.safe_send_message(message.channel, "👉 {0} 您已經將 🍢 {1} 個滷幣送給 {2} 了。".format(message.author.mention, amount, usr.mention))

            except Exception as e:
                raise exceptions.CommandError("Error:%s" % e, expire_in=10)

    async def cmd_rank(self, message):
        if not message.mentions:
            usr = message.author
        else:
            usr = message.mentions[0]
        member = self.bot.running_module.get("mods.Member.Member")
        embed = discord.Embed(colour=0xFFFF00, timestamp=datetime.now()-timedelta(hours=8))
        embed.set_thumbnail(url=usr.avatar_url)
        exp_rank = member.GetUserRank(usr)
        embed.add_field(name="會員", value="{}".format(usr), inline=True)
        embed.add_field(name="ID", value=usr.id, inline=True)
        exp = member.GetUserExp(usr)
        assets = self.GetUserAssets(usr)
        asset_rank = self.GetUserAssetsRank(usr)
        embed.add_field(name="目前等級", value="Lv. {:,}".format(member._get_level_from_exp(exp[2])), inline=True)
        embed.add_field(name="目前經驗值", value="{:,}/{:,} (Total: {:,})".format(exp[0], exp[1], exp[2]), inline=True)
        embed.add_field(name="{} 您的滷幣現金".format(config.CURRENCY_ICON), value="$`{:,}`".format(assets[0]), inline=True)
        embed.add_field(name="🏆 等級排行榜", value="{:,}/{:,}".format(int(exp_rank[0]), int(exp_rank[1])), inline=True)
        embed.add_field(name="💰 富豪排行榜", value="{:,}/{:,}".format(int(asset_rank[0]), int(asset_rank[1])), inline=True)
        create_date = (usr.created_at + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
        join_date = (usr.joined_at + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
        joined_days = (datetime.now() - datetime.strptime(join_date, '%Y-%m-%d %H:%M')).days

        text_info = "您是在 `{}` 加入 Discord 的，並且在 `{}` 加入 **{}**，至今已經 `{:,}` 天囉。".format(create_date, join_date, config.SERVER_NAME, joined_days)
        embed.add_field(name="相關資訊", value=text_info, inline=True)
        embed.set_footer(text="Powered by A.J. Group | 2012-{} ".format(datetime.today().year))
        embed.set_author(name="{}".format(config.SERVER_NAME), url="{}".format(config.SERVER_INVITE_URL), icon_url="{}".format(config.SERVER_ICON_URL))

        await self.bot.safe_send_message(message.channel, embed=embed)

    async def cmd_daily(self, message):

        # 每日獎勵的額外獎勵，不影響普通的每日獎勵
        if config.DAILY_BONUS_ENABLE:
            bonus_act_start = datetime.strptime(config.DAILY_BONUS_ACTIVITY_DATE_START, '%Y-%m-%d %H:%M:%S')
            bonus_act_end = datetime.strptime(config.DAILY_BONUS_ACTIVITY_DATE_END, '%Y-%m-%d %H:%M:%S')

            # 活動進行中
            if bonus_act_start <= datetime.now() and bonus_act_end >= datetime.now():
                BONUS_RATE = config.DAILY_BONUS_ACTIVITY_RATE
                BONUS_MIN = int(config.DAILY_BONUS_ACTIVITY_MIN)
                BONUS_MAX = int(config.DAILY_BONUS_ACTIVITY_MAX)

            # 正常情況
            else:
                BONUS_RATE = config.DAILY_BONUS_RATE
                BONUS_MIN = int(config.DAILY_BONUS_MIN)
                BONUS_MAX = int(config.DAILY_BONUS_MAX)

            BONUS_RATE = (BONUS_RATE * 100)
            if BONUS_RATE < 1:  BONUS_RATE = 1
            BONUS_LUCKY_NUM = random.sample(range(BONUS_RATE), BONUS_RATE)
            BONUS_RAND_NUM = random.randint(0, 10000 - 1)


        act_start = datetime.strptime(config.DAILY_ACTIVITY_DATE_START, '%Y-%m-%d %H:%M:%S')
        act_end = datetime.strptime(config.DAILY_ACTIVITY_DATE_END, '%Y-%m-%d %H:%M:%S')

        # 活動進行中
        if act_start <= datetime.now() and act_end >= datetime.now():
            DAILY_MIN = int(config.DAILY_ACTIVITY_MIN)
            DAILY_MAX = int(config.DAILY_ACTIVITY_MAX)
            DAILY_CD_TIME = int(config.DAILY_ACTIVITY_CD_TIME)
            IGNORE_TIME = config.DAILY_ACTIVITY_CD_IGNORE_TIME

        # 正常情況
        else:
            DAILY_MIN = int(config.DAILY_MIN)
            DAILY_MAX = int(config.DAILY_MAX)
            DAILY_CD_TIME = int(config.DAILY_CD_TIME)
            IGNORE_TIME = config.DAILY_CD_IGNORE_TIME

        res = self.bot.db.get_value("Users", "DAILY_TIME", "USER_ID = {}".format(message.author.id))
        dt_time = res[0][0]

        if IGNORE_TIME:
            # 忽略時間，若少於一天則以一天計
            days = int(DAILY_CD_TIME / 86400)
            if days <= 0:  days = 1
            if dt_time == None:
                dt_time = datetime.now() - timedelta(days=days)
            dt_next = dt_time + timedelta(days=days)
            dt_next = datetime.combine(dt_next.date(), datetime.min.time())
        else:
            if dt_time == None:
                dt_time = datetime.now() - timedelta(seconds=DAILY_CD_TIME)
            dt_next = dt_time + timedelta(seconds=DAILY_CD_TIME)

        # 冷卻時間到，順利領獎
        if datetime.now() >= dt_next:
            DAILY_COIN = random.randint(DAILY_MIN, DAILY_MAX)

            if config.DAILY_BONUS_ENABLE:
                if BONUS_RAND_NUM in BONUS_LUCKY_NUM:
                    BONUS_COIN = random.randint(BONUS_MIN, BONUS_MAX)
                    DAILY_COIN += BONUS_COIN
                    self.SetUserMoney(message.author, DAILY_COIN, "add", "Daily")
                    self.bot.db.execute_sql("UPDATE Users SET DAILY_TIME = '{}' WHERE USER_ID = '{}'".format(datetime.now(), message.author.id))

                    await self.bot.safe_send_message(message.channel, "{0} 狂賀！恭喜您抽中特別獎勵！！加上每日獎勵共 🍢 {1} 滷幣！".format(message.author.mention, DAILY_COIN))
                    return
                
            self.SetUserMoney(message.author, DAILY_COIN, "add", "Daily")
            self.bot.db.execute_sql("UPDATE Users SET DAILY_TIME = '{}' WHERE USER_ID = '{}'".format(datetime.now(), message.author.id))
            await self.bot.safe_send_message(message.channel, "{0} 恭喜您順利領取每日獎勵 🍢 {1} 滷幣！".format(message.author.mention, DAILY_COIN))
            
        # 冷卻時間尚未結束
        else:
            if (dt_next - datetime.now()).seconds <= 100:
                await self.bot.safe_send_message(message.channel, "{0} 再等一下下... 只剩 {1} 秒就可以領獎勵了 🤑".format(message.author.mention, (dt_next - datetime.now()).seconds) + 1)
            else:
                str_next = dt_next.strftime("%Y{0} %m{1} %d{2} %H{3} %M{4} %S{5}").format(*'年月日時分秒')
                await self.bot.safe_send_message(message.channel, "{0} 太著急囉，下次領 🍢 每日獎勵的時間是 {1} 哦 😙！".format(message.author.mention, str_next))

    async def cmd_lb(self, message):
        if not message.mentions:
            usr = message.author
        else:
            usr = message.mentions[0]
        usr_rank = 0
        total_usr = 0
        res = self.bot.db.get_value("Users", "USER_ID, USER_NAME, USER_MONEY", "1=1 ORDER BY TOTAL_MONEY DESC")

        embed = discord.Embed(colour=0xFFFF00, description="--", timestamp=datetime.now()-timedelta(hours=8))
        embed.set_author(name="A.J. Group 滷味小店 富豪排行榜", icon_url="{}".format(config.SERVER_ICON_URL))
        embed.set_thumbnail(url="{}".format(config.SERVER_ICON_URL))
        for idx, user in enumerate(res):
            total_usr += 1
            if idx < 5:
                embed.add_field(
                    name="第 {} 名：{}".format(idx+1, user[1]), 
                    value="共有 `${:,}` 元滷幣。".format(user[2]), inline=False
                )
            if user[0] == usr.id:
                usr_rank = idx+1

        embed.add_field(name="-", value="`{} 的排名為：第 {}/{} 名`\n\n".format(usr, usr_rank, total_usr), inline=False)
        embed.set_footer(text="Powered by A.J. Group | 2012-{} ".format(datetime.today().year))
        await self.bot.safe_send_message(message.channel, embed=embed)

    async def cmd_money(self, message):
        if not message.mentions:
            usr = message.author
            usr_name = "您"
        else:
            usr = message.mentions[0]
            usr_name = usr.name

        assets = self.GetUserAssets(usr)    
        embed = discord.Embed(colour=0xFFFF00, description="--", timestamp=datetime.now()-timedelta(hours=8))
        embed.set_author(name="A.J. Group 滷味小店 - {} 的財產一覽".format(usr.name), icon_url="{}".format(usr.avatar_url))
        embed.set_thumbnail(url="{}".format(config.SERVER_ICON_URL))
        embed.add_field(name="{} {}的滷幣".format(config.CURRENCY_ICON, usr_name), value="現金：$`{:,}`".format(assets[0]), inline=False)
        embed.set_footer(text="Powered by A.J. Group | 2012-{} ".format(datetime.today().year))
        await self.bot.safe_send_message(message.channel, embed=embed)

    async def on_message(self, message):
        pass

    async def on_member_join(self, member):
        pass
