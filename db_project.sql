-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2025-05-21 13:51:55
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
-- 資料表結構 `admin`
--

CREATE TABLE `admin` (
  `uid` varchar(50) NOT NULL,
  `account` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `admin`
--

INSERT INTO `admin` (`uid`, `account`, `password`) VALUES
('gGd8go3Axfg89FDrhnGSRFeHrbg4b', 'banban', '123456789'),
('rkne8sw7dhsHfFBdfkD89frgsdUJfdD', 'pizza@gmail.com', '123456789');

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
(9, '親子 / 家庭');

-- --------------------------------------------------------

--
-- 資料表結構 `event`
--

CREATE TABLE `event` (
  `categories_id` int(4) NOT NULL,
  `event_id` int(4) NOT NULL,
  `content` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `event`
--

INSERT INTO `event` (`categories_id`, `event_id`, `content`) VALUES
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
(3, 16, '心理成長'),
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
  `uid` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `involvement`
--

INSERT INTO `involvement` (`orderid`, `uid`) VALUES
(1, 'gjhdri4h509ah1h73h2hsdlo3'),
(1, 'gsd8fgl3vx0dh3g3h36h6h0az1he0f1h'),
(2, 'jre82jd02ls6gwsnx5reww5oosh');

-- --------------------------------------------------------

--
-- 資料表結構 `order_detail`
--

CREATE TABLE `order_detail` (
  `orderid` int(11) NOT NULL,
  `booker` varchar(50) NOT NULL,
  `location` varchar(100) NOT NULL,
  `gender_limit` varchar(1) DEFAULT NULL,
  `deadtime` datetime NOT NULL,
  `annotation` varchar(200) DEFAULT NULL,
  `participants` int(2) NOT NULL DEFAULT 1,
  `state` varchar(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `order_detail`
--

INSERT INTO `order_detail` (`orderid`, `booker`, `location`, `gender_limit`, `deadtime`, `annotation`, `participants`, `state`) VALUES
(1, 'g8hl30shd2gg78nfdol3iixye6sio62xuue', '台北市信義區市府路5段', NULL, '2025-06-06 10:00:00', '放假第一天，出去玩，上午十點集合', 2, '已預約'),
(2, 'f8dh3ld8bnwe3bfx8hre3jt7b01gvd', '台北市中山區南京西路12號', '女', '2025-05-11 14:28:41', '母親節打折，去逛街，下午一點集合!!!', 4, '已結束');

-- --------------------------------------------------------

--
-- 資料表結構 `user`
--

CREATE TABLE `user` (
  `uid` varchar(50) NOT NULL,
  `account` varchar(100) NOT NULL,
  `password` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `gender` varchar(1) NOT NULL,
  `good` int(4) DEFAULT NULL,
  `bad` int(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `user`
--

INSERT INTO `user` (`uid`, `account`, `password`, `name`, `gender`, `good`, `bad`) VALUES
('f8dh3ld8bnwe3bfx8hre3jt7b01gvd', 'thisishowtobeaheartbreaker@gmail.com', 'heartbreaker', '陳欣妤', '女', NULL, NULL),
('g8hl30shd2gg78nfdol3iixye6sio62xuue', 'fentorisu@yahoo.com.tw', '123456789', '林俊傑', '男', NULL, NULL),
('gjhdri4h509ah1h73h2hsdlo3', 'B1229099@cgu.edu.tw', 'B229099', '林威宇', '男', NULL, NULL),
('gsd8fgl3vx0dh3g3h36h6h0az1he0f1h', 'banana001@gmail.com', '987654321', '黃逗號', '男', NULL, NULL),
('jre82jd02ls6gwsnx5reww5oosh', 'pizzahahahahaha@gmail.com', '123456789', '王曉明', '女', NULL, NULL);

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`uid`);

--
-- 資料表索引 `categories`
--
ALTER TABLE `categories`
  ADD PRIMARY KEY (`categories_id`);

--
-- 資料表索引 `event`
--
ALTER TABLE `event`
  ADD PRIMARY KEY (`categories_id`,`event_id`);

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
  ADD KEY `booker` (`booker`);

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
  MODIFY `categories_id` int(4) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `order_detail`
--
ALTER TABLE `order_detail`
  MODIFY `orderid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 已傾印資料表的限制式
--

--
-- 資料表的限制式 `event`
--
ALTER TABLE `event`
  ADD CONSTRAINT `event_ibfk_1` FOREIGN KEY (`categories_id`) REFERENCES `categories` (`categories_id`) ON DELETE CASCADE ON UPDATE CASCADE;

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
  ADD CONSTRAINT `order_detail_ibfk_1` FOREIGN KEY (`booker`) REFERENCES `user` (`uid`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
