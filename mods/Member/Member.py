from module import Module
import config
import discord
import exceptions
from utils.decorators import owner_only

import random
from datetime import datetime, timedelta


def check_add_role_perm(member, role, bot):
    permissions = bot.server_permissions
    return permissions.manage_roles # and bot.top_role > role

class Member(Module):

    @staticmethod
    def _get_level_exp(n):
        return 5*(n**2)+50*n+100

    @staticmethod
    def _get_level_from_exp(exp):
        remaining_exp = int(exp)
        level = 0
        while remaining_exp >= Member._get_level_exp(level):
            remaining_exp -= Member._get_level_exp(level)
            level += 1
        return level

    def GetUserExp(self, member):
        exp = self.bot.db.get_value("Users", "USER_EXP_NOW, USER_EXP_LEVEL, USER_EXP_TOTAL", "USER_ID = {}".format(member.id))
        return exp[0]

    def GetUserRank(self, member):
        SQL = """ 
            SELECT member.RANK, server.COUNT
            FROM (
                SELECT USER_ID, USER_EXP_TOTAL, @rank:=@rank+1 as RANK
                FROM Users, (SELECT @rank := 0) r
                ORDER BY USER_EXP_TOTAL DESC, USER_ID ASC
            ) member, (
                SELECT COUNT(*) COUNT
                FROM Users
            ) server
            WHERE member.USER_ID = '{}';
        """.format(member.id)
        res = self.bot.db.execute_sql(SQL)
        return res[0]

    async def CheckUserRecordExist(self, member):
        try:
            result = self.bot.db.get_value("Users", "count(*) ct", "USER_ID = {}".format(member.id))
            if result[0][0] == 0:
                self.bot.db.execute_sql("INSERT INTO Users(USER_ID, USER_NAME) VALUES('{}', '{}');".format(member.id, member))

            else:
                return
        except Exception as e:
            raise exceptions.CommandError("Error:%s" % e, expire_in=10)

    async def AddUserExp(self, message, member):
        check = False
        try:
            res = self.bot.db.get_value("Users", "USER_EXP_NOW, USER_EXP_LEVEL, USER_EXP_TOTAL, USER_EXP_CD", "USER_ID = {}".format(member.id))
            if res[0][3] == None:
                check = True
            else:
                if (datetime.now() - res[0][3]).total_seconds() > config.EXP_CD:
                    check = True

            if check:
                rand_exp = random.randint(config.EXP_MIN, config.EXP_MAX)
                now_exp = res[0][1]
                now_total_exp = res[0][2]
                new_total_exp = now_total_exp + rand_exp
                new_now_exp = res[0][0] + rand_exp

                now_lv = self._get_level_from_exp(now_total_exp)
                now_lv_exp = self._get_level_exp(now_lv)

                new_lv = self._get_level_from_exp(new_total_exp)
                new_lv_exp = self._get_level_exp(new_lv)

                if new_lv > now_lv:
                    new_now_exp = new_now_exp - now_lv_exp

                self.bot.db.execute_sql("UPDATE Users SET USER_EXP_NOW = {}, USER_EXP_LEVEL = {}, USER_EXP_TOTAL = {}, USER_LEVEL = {}, USER_EXP_CD = '{}' WHERE USER_ID = '{}';".format(new_now_exp, new_lv_exp, new_total_exp, new_lv, datetime.now(), member.id))


                if new_lv > now_lv:
                    await self.bot.safe_send_message(message.channel, "恭喜 {} 升到 {} 級!".format(member.mention, new_lv))


        except Exception as e:
            raise exceptions.CommandError("Error:%s" % e, expire_in=10)

    # 注意，如果有 Currency 模組，會以那邊的 rank 為主，如果有基本模板要更新，要另外過來這邊改寫。
    async def cmd_rank(self, message):
        if not message.mentions:
            usr = message.author
        else:
            usr = message.mentions[0]
        member = self.bot.running_module.get("mods.Member.Member")
        embed = discord.Embed(colour=0xFFFF00)
        embed.set_thumbnail(url=usr.avatar_url)
        rank = member.GetUserRank(usr)
        embed.add_field(name="會員", value="{}".format(usr), inline=True)
        embed.add_field(name="ID", value=usr.id, inline=True)
        exp = member.GetUserExp(usr)
        embed.add_field(name="目前等級", value="Lv. {}".format(self._get_level_from_exp(exp[2])), inline=True)
        embed.add_field(name="目前經驗值", value="{}/{} (Total: {})".format(exp[0], exp[1], exp[2]), inline=True)
        embed.add_field(name="等級排行榜", value="{}/{}".format(int(rank[0]), int(rank[1])), inline=True)
        create_date = (usr.created_at + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
        join_date = (usr.joined_at + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
        joined_days = (datetime.now() - datetime.strptime(join_date, '%Y-%m-%d %H:%M')).days

        text_info = "您是在 `{}` 加入 Discord 的，並且在 `{}` 加入 **{}**，至今已經 `{}` 天囉。".format(create_date, join_date, config.SERVER_NAME, joined_days)
        embed.add_field(name="相關資訊", value=text_info, inline=True)
        embed.set_footer(text="Powered by A.J. Group | 2012-{} | https://discord.gg/aRy4Ydp".format(datetime.today().year))
        embed.set_author(name="{}".format(config.SERVER_NAME), url="{}".format(config.SERVER_INVITE_URL), icon_url="{}".format(config.SERVER_ICON_URL))

        await self.bot.safe_send_message(message.channel, embed=embed)

    async def add_role(self, member, role, server):
        if check_add_role_perm(member, role, server.me):
            return await self.bot.add_roles(member, role)

    async def remove_role(self, member, role, server):
        if check_add_role_perm(member, role, server.me):
            return await self.bot.remove_roles(member, role)

    # 測試用，顯示伺服器內的所有用戶組 ID
    @owner_only
    async def cmd_roleid(self, message):
        role_str = ""
        for idx, role in enumerate(message.server.roles):
            role_str += "`{0} - {1}: {2}`\n".format(str(idx+1).rjust(2, '0'), role.name, role.id)
        await self.bot.safe_send_message(message.channel, role_str)


    async def on_message(self, message):
        member = message.author     
        await self.CheckUserRecordExist(member)
        await self.AddUserExp(message, member)

    async def on_member_join(self, member):
        self.CheckUserRecordExist(member)
