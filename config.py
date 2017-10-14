# Discord Bot
SERVER_NAME = "A.J. Group 滷味小店"
SERVER_INVITE_URL = "https://discord.gg/aRy4Ydp"
SERVER_ICON_URL = "https://cdn.discordapp.com/icons/249577790976950272/9fdcc43f049064f8e4f777e67aa98b96.png"
_login_token = "Bot login token"
owner_id = "Bot owner id"
description = "AJGR Bot"
default_status = "✨ A.J. Group - 頻道網址：https://discord.gg/aRy4Ydp"
# 預設模組清單，如有子模組，請依照階層順序填寫
DEFAULT_MODULES = [
    'mods.Fun',
    'mods.Member.Member',
    'mods.Member.Currency.Currency', 
]

# Bot command
command_prefix = "." # 指令前綴字，指令前面加上此前綴字元即可呼叫 BOT
delete_messages = True
delete_invoking = False # 是否一併刪除發話者的訊息(用在某些指令出錯時)，預設為 False

# Database
DB_HOST = "Your database host"
DB_USER = "Your database username"
DB_PASSWORD = "Your database user password"
DB_NAME = "ajgr"
DB_PORT = 3306
DB_CHARSET = "utf8"

#====================================== Module Common Settings =============================
ALL_MODULE_ACTIVITY_ENABLE = False # [!]特別注意，此選項設置為 True 時，所有模組的活動日期皆下面兩個為主，Default: False
ALL_MODULE_ACTIVITY_DATE_START = "2017-10-10 00:00:00" 
ALL_MODULE_ACTIVITY_DATE_END = "2017-10-11 00:00:00"
# !!! 以上選項是用來開啟所有模組的活動，活動期間內模組的參數都會以該模組的 ACTIVITY 參數為主，
# !!! 請先確認模組活動參數都已經調整完畢。


#====================================== Member module ======================================
EXP_MIN = 15 #經驗系統每次增加最小值，Default: 15
EXP_MAX = 25 #經驗系統每次增加最大值，Default: 25
EXP_CD = 60 #經驗系統冷卻時間(秒)，Default: 60
EXP_ACTIVITY_DATE_START = "2017-10-10 00:00:00" if not ALL_MODULE_ACTIVITY_ENABLE else ALL_MODULE_ACTIVITY_DATE_START
EXP_ACTIVITY_DATE_END = "2017-10-11 00:00:00" if not ALL_MODULE_ACTIVITY_ENABLE else ALL_MODULE_ACTIVITY_DATE_END 
EXP_ACTIVITY_MIN = 15 * 1.2
EXP_ACTIVITY_MAX = 25 * 1.2
EXP_ACTIVITY_CD = 60


#====================================== Fun module ======================================
CONSOLE_SHOW_FUNNY_IMAGE = False #後臺是否要顯示呼叫關鍵字的命令，Default: True


#====================================== Currency module ======================================
CURRENCY_ICON = "🍢" #預設的金幣符號
DEFAULT_MONEY = 0 #會員初始金幣，Default: 0  ---> 好像暫時沒用到XD

DAILY_MIN = 1 #每日獎勵最小值，Default: 1
DAILY_MAX = 5 #每日獎勵最大值，Default: 5
DAILY_CD_TIME = 86400 #領取每日獎勵的冷卻時間(秒)，Default: 86400
DAILY_CD_IGNORE_TIME = True #是否只看日期(CD_TIME若小於86400，請False，否則以1天計) -> 即過 12 點就可以領，不用真的過 24+ 小時
DAILY_BONUS_ENABLE = True #是否開放每日獎勵的額外獎勵，Default: True
DAILY_BONUS_RATE = 2 #每日獎勵的額外獎勵機率(%)，輸入 100 即為 100 %，最小為0.01(萬分之一)，小於萬分之一以萬分之一計，Default: 2
DAILY_BONUS_MIN = 10 #每日獎勵的額外獎勵最小值，Default: 10
DAILY_BONUS_MAX = 10 #每日獎勵的額外獎勵最大值，Default: 10

DAILY_ACTIVITY_DATE_START = "2017-10-07 20:55:00" if not ALL_MODULE_ACTIVITY_ENABLE else ALL_MODULE_ACTIVITY_DATE_START #活動開始日期
DAILY_ACTIVITY_DATE_END = "2017-10-07 21:00:00" if not ALL_MODULE_ACTIVITY_ENABLE else ALL_MODULE_ACTIVITY_DATE_END #活動結束日期
DAILY_ACTIVITY_MIN = 1
DAILY_ACTIVITY_MAX = 5
DAILY_ACTIVITY_CD_TIME = 28800 #領取每日獎勵的冷卻時間(秒)
DAILY_ACTIVITY_CD_IGNORE_TIME = False #是否只看日期(CD_TIME若小於86400，請False，否則以1天計)

#以下為 [每日獎勵] 的活動設定，設定好活動日期和參數後，活動期間將以下面設定為主
DAILY_BONUS_ACTIVITY_DATE_START = "2017-10-07 20:55:00" if not ALL_MODULE_ACTIVITY_ENABLE else ALL_MODULE_ACTIVITY_DATE_START #活動開始日期
DAILY_BONUS_ACTIVITY_DATE_END = "2017-10-07 21:00:00" if not ALL_MODULE_ACTIVITY_ENABLE else ALL_MODULE_ACTIVITY_DATE_END #活動結束日期
DAILY_BONUS_ACTIVITY_RATE = 4 #每日獎勵的額外獎勵機率(%)，輸入 100 即為 100 %，最小為0.01(萬分之一)，小於萬分之一以萬分之一計
DAILY_BONUS_ACTIVITY_MIN = 10
DAILY_BONUS_ACTIVITY_MAX = 10
# --- [每日獎勵活動參數 結束] ---

