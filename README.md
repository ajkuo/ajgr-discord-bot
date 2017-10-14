# ajgr-discord-bot
  
此為 Discord BOT 的基本雛形款(Python 3)，此 BOT 可以在執行過程使用指令動態添加或移除模組，方便管理各模組。  
歡迎加入 **「A.J. Group 滷味小店」** 頻道交流，頻道邀請連結：[https://discord.gg/aRy4Ydp](https://discord.gg/aRy4Ydp)  
  
## 模組的介紹
本 BOT 將各功能性指令劃分為不同模組管理，並藉由模組階層的方式來連動，方便管理 BOT 的模組。

目前包含 3 個基本模組作為示範：  
1. Fun  
2. Member.Member  
3. Member.Currency.Currency  

舉例而言，若您的 BOT 只需要簡單指令功能，不用會員、經驗、貨幣等系統，那你只需要在 config.py 內留下 Fun 模組即可，無需其他設定。

#### 模組階層性
模組之間具階層性，透過目錄階層來管理，最上層的 mods 資料夾放置的模組一律都是獨立模組(例如：Fun)，與其他模組無關聯性，故可以獨立放在最上層目錄。  
  
由於模組階層性的關係，若您載入子模組時，上層模組尚未載入，將會載入失敗。舉例而言：若您載入 Member.Currnecy.Currency 模組時，Member.Member 並未執行，則會顯示上層模組並未存在的錯誤訊息，此時請先載入 Member.Member 模組，再重新載入即可。  
  
而當您卸載上層模組時，將會一併將其連帶的子模組全部卸載。舉例而言：當您卸載 Member.Member 模組時，凡名為 Member.* 的模組皆會被一併卸載，以上面的範例而言， Member.Currency.Currency 便會一併被卸載。  
  
#### 模組的擴充
舉例而言， Member 模組因考慮到未來的會員系統可以用更多模組擴充，因此將其視為一個子模組。  
**子模組需要放在一個與模組名稱相同的子目錄下，例如子模組「Member」就必須放在「Member」目錄底下**，並且在 config.py 內使用"資料夾.模組名"的方式載入。
  
#### 子模組的擴充
子模組擴充可分為兩種：  
  
1. 單純使用到子模組功能且未來不會有更多擴充的模組。  
2. 使用到子模組功能，且未來還可以基於此新模組延伸更多功能。  
  
第一類的模組，只要跟子模組放在同一層目錄下即可。舉例而言，若只是單純想基於 Member 模組開發經驗值的應用，則只要將新模組放置在「Member」目錄底下即可，並在 config.py 內使用「Member.模組名」的方式載入。  
  
第二類的模組，則是在子模組目錄內，再新增一個與新模組同名的目錄，即範例內的 Currency 模組。此類型模組即基於會員模組(Member)開發的貨幣模組，且貨幣模組本身可以再衍生出其他基於貨幣的模組擴充，因此使用第二類的子模組擴充。而此類模組的指令若與上層模組相同，則優先使用下層子模組的指令。  
  
  
## 基本指令
預設的指令前綴字元為「.」，執行以下指令時請在 Discord 使用「. + 指令」即可，例如「.sleep」。  

#### 管理員專用
(基本 BOT 指令)  
1. showmod - 顯示目前執行中的模組清單。  
2. modload / modunload <模組名稱(不用最前面的 mods.> - 載入 or 移除模組。  
3. status <狀態名稱> - 將 BOT 的狀態改為指定內容。  
4. setavater <圖片網址> - 將 BOT 的大頭照改為指定圖片。  
5. setnick <BOT暱稱> - 將 BOT 的暱稱改為指定內容。  
6. setname <BOT名字> - 將 BOT 的名字改為指定內容，每小時只能使用 2 次，沒特別需求建議使用 setnick 就好。  
  
( Fun 模組)
1. addkeyword <關鍵字> - 新增聊天關鍵字，需要搭配下面的指令新增對應內容。  
2. addkeyurl <關鍵字|同義詞> <對應內容> - 新增指定關鍵字的對應內容。新增完畢之後，在聊天時只要句子有出現關鍵字，BOT便會自動回應對應內容。(對應內容不一定要是網址，可以是文字、圖片連結、影片連結......任何內容皆可自由搭配。)  
3. addvicekey <關鍵字|同義詞> <新同義詞> - 新增指定關鍵字的同義詞，當出現同義詞時，BOT也會做出相同回應，請注意系統並不會檢查同義詞是否重複。  
  
( Currency 模組)  
1. setmoney <@user> <add|sub|cover> <金額> - 用來調整用戶的現金，若未標記使用者，則調整自身金額。add為增加指定金額、sub為減少指定金額、cover為直接將用戶的現金變更為指定金額。  
  
#### 通用指令
( Fun 模組)  
1. e <表情符號> - 可將指定表情符號放大顯示。
2. sleep - 讓 BOT 幫你跟大家說聲晚安。  
3. keywords - 可以顯示目前頻道已經建立的關鍵字清單。
  
( Member 模組)  
1. rank <@user> - 顯示目前用戶資訊 (若有載入 Currency 模組，則以 Currency 模組的同名指令優先)  
  
( Currency 模組)  
1. daily - 領取每日獎勵。  
2. rank <@user> - 顯示目前用戶資訊，包含現金資訊，可查詢指定用戶。  
3. money <@user> - 顯示現金資訊，可查詢指定用戶。  
4. give <@user> <金額> - 將指定金額轉帳給指定用戶。  
5. lb <@user> - 查詢資產排名前 5 名的用戶及指定用戶的目前排名。 
  
--  
BOT 參考資料:  
[1] NotSoBot - https://github.com/NotSoSuper/NotSoBot  
[2] Mee6 - https://github.com/cookkkie/mee6  
[3] MusicBot - https://github.com/Just-Some-Bots/MusicBot  
[4] Twitter, twemoji - https://github.com/twitter/twemoji
