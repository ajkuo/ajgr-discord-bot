SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `Keywords`
-- ----------------------------
DROP TABLE IF EXISTS `Keywords`;
CREATE TABLE `Keywords` (
  `SN` bigint(20) NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`SN`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4;


-- ----------------------------
-- Table structure for `KeywordURLs`
-- ----------------------------
DROP TABLE IF EXISTS `KeywordURLs`;
CREATE TABLE `KeywordURLs` (
  `SN` bigint(20) NOT NULL AUTO_INCREMENT,
  `Keyword_SN` int(11) NOT NULL,
  `URL` varchar(2000) DEFAULT NULL,
  PRIMARY KEY (`SN`)
) ENGINE=InnoDB AUTO_INCREMENT=89 DEFAULT CHARSET=utf8mb4;


-- ----------------------------
-- Table structure for `Log_EarnMoney`
-- ----------------------------
DROP TABLE IF EXISTS `Log_EarnMoney`;
CREATE TABLE `Log_EarnMoney` (
  `SN` bigint(20) NOT NULL AUTO_INCREMENT,
  `SOURCE` varchar(64) DEFAULT NULL,
  `USER_ID` varchar(255) DEFAULT NULL,
  `EARN_MONEY` int(11) DEFAULT NULL,
  `EARN_TIME` datetime DEFAULT NULL,
  `EARN_TYPE` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`SN`)
) ENGINE=InnoDB AUTO_INCREMENT=152 DEFAULT CHARSET=utf8mb4;


-- ----------------------------
-- Table structure for `Users`
-- ----------------------------
DROP TABLE IF EXISTS `Users`;
CREATE TABLE `Users` (
  `SN` int(11) NOT NULL AUTO_INCREMENT,
  `USER_ID` varchar(64) DEFAULT NULL,
  `USER_NAME` varchar(200) DEFAULT NULL,
  `USER_EXP_NOW` int(11) DEFAULT '0',
  `USER_EXP_LEVEL` int(11) DEFAULT '0',
  `USER_EXP_TOTAL` int(11) DEFAULT '0',
  `USER_EXP_CD` datetime DEFAULT NULL,
  `USER_LEVEL` int(11) DEFAULT '0',
  `USER_MONEY` int(11) DEFAULT '0',
  `USER_SAVE` int(11) DEFAULT '0',
  `USER_GOLD` int(11) DEFAULT '0',
  `USER_CONT` int(11) DEFAULT '0',
  `DAILY_TIME` datetime DEFAULT NULL,
  `BONUS_TIME` datetime DEFAULT NULL,
  PRIMARY KEY (`SN`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4;


-- ----------------------------
-- Table structure for `Users_Save`
-- ----------------------------
DROP TABLE IF EXISTS `Users_Save`;
CREATE TABLE `Users_Save` (
  `SN` bigint(20) NOT NULL AUTO_INCREMENT,
  `USER_ID` varchar(255) NOT NULL,
  `AMOUNT` int(11) NOT NULL DEFAULT '0',
  `RATE` float NOT NULL DEFAULT '0',
  `SAVE_DATE` datetime NOT NULL,
  `EXPIRE_DATE` datetime NOT NULL,
  `RECEIVE` bit(1) NOT NULL DEFAULT b'0',
  `TOTAL_INTEREST` int(11) NOT NULL DEFAULT '0',
  `DAYS` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`SN`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4;


-- ----------------------------
-- Table structure for `ViceKeywords`
-- ----------------------------
DROP TABLE IF EXISTS `ViceKeywords`;
CREATE TABLE `ViceKeywords` (
  `SN` bigint(11) NOT NULL AUTO_INCREMENT,
  `Keyword_SN` bigint(11) DEFAULT NULL,
  `Name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`SN`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4;
