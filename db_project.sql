-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2025-05-23 10:06:27
-- 伺服器版本： 10.4.32-MariaDB
-- PHP 版本： 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `db_project`
--

-- --------------------------------------------------------

--
-- 資料表結構 `categories`
--

CREATE TABLE `categories` (
  `categories_id` int(4) NOT NULL,
  `content` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `categories`
--

INSERT INTO `categories` (`categories_id`, `content`) VALUES
(1, '娛樂 / 表演'),
(2, '教育 / 課程'),
(3, '健康 / 運動'),
(4, '戶外 / 旅遊'),
(5, '社交 / 聯誼'),
(6, '專業 / 商務'),
(7, '市集 / 展覽'),
(8, '志工 / 公益'),
(9, '親子 / 家庭'),
(10, '體育 / 活動');

-- --------------------------------------------------------

--
-- 資料表結構 `event`
--

CREATE TABLE `event` (
  `categories_id` int(4) NOT NULL,
  `event_id` int(4) NOT NULL,
  `content` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `event`
--

INSERT INTO `event` (`categories_id`, `event_id`, `content`) VALUES
(10, 0, '打籃球'),
(1, 1, '音樂會 / 演唱會'),
(1, 2, '舞台劇 / 戲劇'),
(1, 3, '喜劇 / 脫口秀'),
(1, 4, '電影放映'),
(1, 5, '藝文展覽'),
(2, 6, '語言學習'),
(2, 7, '程式設計 / 科技'),
(2, 8, '財經 / 理財'),
(2, 9, '創業 / 行銷'),
(2, 10, '藝術 / 手作'),
(2, 11, '親子教育'),
(3, 12, '瑜伽 / 伸展'),
(3, 13, '跑步 / 馬拉松'),
(3, 14, '健身 / 重訓'),
(3, 15, '健康講座'),
(4, 16, '登山 / 健行'),
(4, 17, '露營'),
(4, 18, '一日遊 / 導覽'),
(4, 19, '寵物活動'),
(4, 20, '環保志工'),
(5, 21, '交友活動'),
(5, 22, '桌遊聚會'),
(5, 23, '同好社團'),
(5, 24, '單身派對'),
(5, 25, '品酒會 / 美食聚會'),
(6, 26, '產業論壇'),
(6, 27, '科技年會'),
(6, 28, '招聘會 / 就業博覽'),
(6, 29, '商業講座'),
(6, 30, 'B2B 推介會'),
(7, 31, '創意市集'),
(7, 32, '文創展'),
(7, 33, '寵物展'),
(7, 34, '車展'),
(7, 35, '書展'),
(8, 36, '公益市集'),
(8, 37, '街頭募款'),
(8, 38, '社區服務'),
(8, 39, '資源回收活動'),
(9, 40, '兒童劇場'),
(9, 41, '親子手作'),
(9, 42, '親子戶外活動'),
(9, 43, '媽媽教室');

-- --------------------------------------------------------

--
-- 資料表結構 `involvement`
--

CREATE TABLE `involvement` (
  `orderid` int(11) NOT NULL,
  `uid` varchar(50) NOT NULL,
  `eval_to_booker` varchar(200) DEFAULT NULL,
  `booker_eval` varchar(200) DEFAULT NULL,
  `evaluation` int(1) DEFAULT NULL COMMENT '讚:1，倒讚:-1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `involvement`
--

INSERT INTO `involvement` (`orderid`, `uid`, `eval_to_booker`, `booker_eval`, `evaluation`) VALUES
(1, 'gjhdri4h509ah1h73h2hsdlo3', NULL, NULL, 1),
(1, 'gsd8fgl3vx0dh3g3h36h6h0az1he0f1h', NULL, NULL, 1),
(2, 'jre82jd02ls6gwsnx5reww5oosh', '講話很大聲，沒頭沒腦', '不尊重人', -1),
(2, 'rehg8923njasd9srftgnjrs43hgsdjnrs6uj', '很聒噪的人', '很安靜的人', 1);

-- --------------------------------------------------------

--
-- 資料表結構 `order_detail`
--

CREATE TABLE `order_detail` (
  `orderid` int(11) NOT NULL,
  `booker` varchar(50) NOT NULL,
  `location` varchar(100) NOT NULL,
  `deadtime` datetime NOT NULL,
  `start_time` datetime NOT NULL DEFAULT current_timestamp(),
  `annotation` varchar(200) DEFAULT NULL,
  `participants` int(2) NOT NULL DEFAULT 1,
  `state` varchar(4) NOT NULL,
  `event_id` int(4) DEFAULT NULL,
  `gender_limit` tinyint(1) NOT NULL DEFAULT 0,
  `male_limit` int(2) DEFAULT NULL,
  `female_limit` int(2) DEFAULT NULL,
  `male_num` int(2) NOT NULL DEFAULT 0,
  `female_num` int(2) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `order_detail`
--

INSERT INTO `order_detail` (`orderid`, `booker`, `location`, `deadtime`, `start_time`, `annotation`, `participants`, `state`, `event_id`, `gender_limit`, `male_limit`, `female_limit`, `male_num`, `female_num`) VALUES
(1, 'g8hl30shd2gg78nfdol3iixye6sio62xuue', '台北市信義區市府路5段', '2025-06-06 10:00:00', '2025-05-23 14:29:30', '放假第一天，出去玩，上午十點集合', 3, '已滿人', 31, 0, NULL, NULL, 3, 0),
(2, 'f8dh3ld8bnwe3bfx8hre3jt7b01gvd', '台北市中山區南京西路12號', '2025-05-11 14:28:41', '2025-05-23 14:29:30', '母親節打折，去逛街，下午一點集合!!!', 4, '已結束', 1, 1, 0, 4, 0, 3),
(3, 'wergea78gewahr592kzx0xfhw3fddbad', '桃園市龜山區文化一路259號', '2025-06-03 13:00:00', '2025-06-03 14:00:00', '哪個大神來救我的資料庫啊', 5, '已成立', 7, 0, NULL, NULL, 2, 0);

-- --------------------------------------------------------

--
-- 資料表結構 `user`
--

CREATE TABLE `user` (
  `uid` varchar(50) NOT NULL,
  `username` varchar(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `gender` varchar(1) NOT NULL,
  `birthday` date DEFAULT NULL,
  `self_introduction` varchar(200) DEFAULT NULL,
  `isadmin` tinyint(1) DEFAULT 0,
  `phone` varchar(10) NOT NULL,
  `identify_ID` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `user`
--

INSERT INTO `user` (`uid`, `username`, `name`, `gender`, `birthday`, `self_introduction`, `isadmin`, `phone`, `identify_ID`) VALUES
('ergse9gwq42lsd7gjl478wshnjsjklfd', '尊', '朱玉恩', '男', '1998-08-08', '哈樓大家好我是尊', 0, '0956789012', 'G123456789'),
('f8dh3ld8bnwe3bfx8hre3jt7b01gvd', '星予', '陳欣妤', '女', '2025-05-23', '予是三聲，妤是二聲', 0, '0912345678', 'B123456789'),
('g8hl30shd2gg78nfdol3iixye6sio62xuue', '俊傑哥', '林俊傑', '男', '2025-05-23', '我是歌手', 0, '0987654321', 'C123456789'),
('gjhdri4h509ah1h73h2hsdlo3', '資工二系學會長', '林威宇', '男', '2025-05-23', '歡迎妹子來找我', 0, '0923456789', 'D123456789'),
('gsd8fgl3vx0dh3g3h36h6h0az1he0f1h', '我喜歡句號', '黃逗號', '男', '2025-05-23', NULL, 0, '0934567890', 'E123456789'),
('jre82jd02ls6gwsnx5reww5oosh', '王小明', '王曉明', '女', '2025-05-23', '我真的是曉', 0, '045678901', 'F123456789'),
('rehg8923njasd9srftgnjrs43hgsdjnrs6uj', '檸檬', '楊思涵', '女', '2005-04-04', NULL, 0, '0967890123', 'H123456789'),
('rfaedg8912bnwg83b2', '黃星昊', '黃星昊', '男', '2005-01-01', '可惜我不是句號', 1, '0902030405', 'A987654320'),
('th902jms0dg2j347tt4njksdfgbb', '句號', '林靖', '女', '2006-07-07', '你好~', 0, '0978901234', 'I123456789'),
('wergea78gewahr592kzx0xfhw3fddbad', '星辰', '陳泓均', '男', '2004-10-10', NULL, 1, '0901020304', 'A987654321');

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `categories`
--
ALTER TABLE `categories`
  ADD PRIMARY KEY (`categories_id`);

--
-- 資料表索引 `event`
--
ALTER TABLE `event`
  ADD PRIMARY KEY (`event_id`),
  ADD KEY `categories_id` (`categories_id`);

--
-- 資料表索引 `involvement`
--
ALTER TABLE `involvement`
  ADD PRIMARY KEY (`orderid`,`uid`),
  ADD KEY `uid` (`uid`);

--
-- 資料表索引 `order_detail`
--
ALTER TABLE `order_detail`
  ADD PRIMARY KEY (`orderid`),
  ADD KEY `booker` (`booker`),
  ADD KEY `event_id` (`event_id`);

--
-- 資料表索引 `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`uid`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `categories`
--
ALTER TABLE `categories`
  MODIFY `categories_id` int(4) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `order_detail`
--
ALTER TABLE `order_detail`
  MODIFY `orderid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- 已傾印資料表的限制式
--

--
-- 資料表的限制式 `event`
--
ALTER TABLE `event`
  ADD CONSTRAINT `event_ibfk_1` FOREIGN KEY (`categories_id`) REFERENCES `categories` (`categories_id`);

--
-- 資料表的限制式 `involvement`
--
ALTER TABLE `involvement`
  ADD CONSTRAINT `involvement_ibfk_1` FOREIGN KEY (`orderid`) REFERENCES `order_detail` (`orderid`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `involvement_ibfk_2` FOREIGN KEY (`uid`) REFERENCES `user` (`uid`);

--
-- 資料表的限制式 `order_detail`
--
ALTER TABLE `order_detail`
  ADD CONSTRAINT `order_detail_ibfk_1` FOREIGN KEY (`booker`) REFERENCES `user` (`uid`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `order_detail_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `event` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
