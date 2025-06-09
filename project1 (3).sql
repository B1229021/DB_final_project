-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2025-06-09 04:41:29
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
-- 資料庫： `project1`
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
(3, '健康 / 運動'),
(4, '戶外 / 旅遊'),
(5, '社交 / 聯誼'),
(6, '專業 / 商務'),
(7, '市集 / 展覽'),
(8, '志工 / 公益'),
(17, '室內 / 運動');

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
(17, 40, '撞球');

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
(130, 'jre82jd02ls6gwsnx5reww5oosh', NULL, NULL, NULL),
(130, 'U33f883009491ea75dc9fcac06fd4e113', NULL, NULL, NULL),
(130, 'U7c9d00039cc39a0d21e985f798460e48', NULL, NULL, NULL),
(130, 'U8917d798951962ee0ca582d4fc1d46d2', NULL, NULL, NULL),
(130, 'Ua06201dec88a97574d4c3662142a89f0', NULL, NULL, NULL),
(130, 'Udd68e63026ff651a578c7918ae0b1fd6', NULL, NULL, NULL),
(133, 'jre82jd02ls6gwsnx5reww5oosh', NULL, '我們的感情好像跳樓機', -1),
(138, '123', NULL, NULL, NULL),
(140, '123', '跳樓機', '我們的感情好像跳樓機', 1),
(140, 'jre82jd02ls6gwsnx5reww5oosh', '跳樓機2', '讓我忽然地升空又急速落地', 1),
(141, 'Ua06201dec88a97574d4c3662142a89f0', NULL, NULL, NULL),
(142, 'U7c9d00039cc39a0d21e985f798460e48', NULL, NULL, NULL),
(144, 'Udd68e63026ff651a578c7918ae0b1fd6', '測試測試', '我很好', 1),
(277, 'Udd68e63026ff651a578c7918ae0b1fd6', '123456', NULL, 1),
(279, 'Udd68e63026ff651a578c7918ae0b1fd6', '456789', NULL, 1),
(282, 'jre82jd02ls6gwsnx5reww5oosh', NULL, NULL, NULL),
(283, 'jre82jd02ls6gwsnx5reww5oosh', NULL, NULL, NULL),
(284, 'jre82jd02ls6gwsnx5reww5oosh', NULL, NULL, NULL),
(285, 'jre82jd02ls6gwsnx5reww5oosh', NULL, NULL, NULL),
(286, 'Udd68e63026ff651a578c7918ae0b1fd6', NULL, NULL, NULL),
(287, 'Udd68e63026ff651a578c7918ae0b1fd6', NULL, NULL, NULL),
(290, 'Ud759801d757d52e40195cffd858b5089', NULL, NULL, NULL);

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
(130, '123', '築間', '2025-06-05 12:00:00', '2025-06-06 00:00:00', '', 10, '已成立', 21, 1, 5, 5, 5, 3),
(133, '123', '我家', '2025-06-03 00:58:00', '2025-06-03 00:59:00', '', 1, '已結束', 40, 0, 0, 0, 0, 0),
(138, 'Ua06201dec88a97574d4c3662142a89f0', '123', '2025-06-03 01:49:00', '2025-06-03 01:50:00', '', 1, '已結束', 27, 0, 0, 0, 0, 0),
(140, 'Ua06201dec88a97574d4c3662142a89f0', '123', '2025-06-03 01:51:00', '2025-06-03 01:56:00', '', 2, '已結束', 27, 0, 0, 0, 0, 0),
(141, '123', '123', '2025-06-06 01:57:00', '2025-06-12 01:57:00', '', 1, '已成立', 13, 0, 0, 0, 0, 0),
(142, 'Ua06201dec88a97574d4c3662142a89f0', '築間', '2025-06-13 02:03:00', '2025-06-20 02:03:00', '', 1, '已成立', 13, 0, 0, 0, 0, 0),
(144, 'Ua06201dec88a97574d4c3662142a89f0', '你好', '2025-06-03 14:31:00', '2025-07-03 14:30:00', '', 2, '已結束', 40, 0, 0, 0, 0, 0),
(277, 'rehg8923njasd9srftgnjrs43hgsdjnrs6uj', '我家', '2025-06-03 19:53:00', '2025-06-04 19:52:00', '', 1, '已結束', 12, 0, 0, 0, 0, 0),
(279, 'rehg8923njasd9srftgnjrs43hgsdjnrs6uj', '我家', '2025-06-03 19:56:00', '2025-06-04 19:52:00', '', 1, '已結束', 12, 0, 0, 0, 0, 0),
(282, 'Udd68e63026ff651a578c7918ae0b1fd6', '我家', '2025-06-04 17:32:00', '2025-06-04 17:34:00', '', 2, '待確認', 12, 0, 0, 0, 0, 0),
(283, 'Udd68e63026ff651a578c7918ae0b1fd6', '我家', '2025-06-04 17:35:00', '2025-06-04 17:36:00', '', 2, '待確認', 12, 0, 0, 0, 0, 0),
(284, 'Udd68e63026ff651a578c7918ae0b1fd6', '我家', '2025-06-04 17:41:00', '2025-06-04 17:43:00', '', 2, '待確認', 12, 0, 0, 0, 0, 0),
(285, 'Udd68e63026ff651a578c7918ae0b1fd6', '我家', '2025-06-04 17:45:00', '2025-06-04 17:46:00', '', 2, '已隱藏', 12, 0, 0, 0, 0, 0),
(286, 'jre82jd02ls6gwsnx5reww5oosh', '我家', '2025-06-04 17:46:00', '2025-06-04 17:47:00', '', 2, '待確認', 16, 0, 0, 0, 0, 0),
(287, 'Ud759801d757d52e40195cffd858b5089', '直至', '2025-06-04 17:53:00', '2025-06-04 17:54:00', '', 2, '已隱藏', 22, 0, 0, 0, 0, 0),
(290, 'Udd68e63026ff651a578c7918ae0b1fd6', '我家', '2025-06-04 17:58:00', '2025-06-04 17:59:00', '', 2, '已隱藏', 16, 0, 0, 0, 0, 0);

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
('123', '我好棒', '陶春嬌', '女', '2025-06-01', 'None', 0, '0000000000', 'A000000000'),
('f8dh3ld8bnwe3bfx8hre3jt7b01gvd', '星予', '陳欣妤', '女', '2025-05-23', '予是三聲，妤是二聲', 0, '0912345678', 'B123456789'),
('g8hl30shd2gg78nfdol3iixye6sio62xuue', '俊傑哥', '林俊傑傑', '男', '2025-05-23', '我是歌手0000', 0, '0987654321', 'C123456789'),
('gjhdri4h509ah1h73h2hsdlo3', '資工二系學會長', '林威宇', '男', '2025-05-23', '歡迎妹子來找我', 0, '0923456789', 'D123456789'),
('gsd8fgl3vx0dh3g3h36h6h0az1he0f1h', '我喜歡句號', '黃逗號', '男', '2025-05-23', NULL, 0, '0934567890', 'E123456789'),
('jre82jd02ls6gwsnx5reww5oosh', '王小明', '王曉明', '女', '2025-05-23', '我真的是曉', 0, '045678901', 'F123456789'),
('rehg8923njasd9srftgnjrs43hgsdjnrs6uj', '檸檬', '楊思涵', '女', '2005-04-04', NULL, 0, '0967890123', 'H123456789'),
('rfaedg8912bnwg83b2', '黃星昊', '黃星昊', '男', '2005-01-01', '可惜我不是句號', 1, '0902030405', 'A987654320'),
('th902jms0dg2j347tt4njksdfgbb', '句號', '林靖', '女', '2006-07-07', '你好~', 0, '0978901234', 'I123456789'),
('U12eb6fda512d63001b90bbc685545029', '小滿', '滿天星', '女', '2007-01-16', NULL, 0, '0988684397', 'H111222333'),
('U33f883009491ea75dc9fcac06fd4e113', '陳紅魚', '陳紅魚', '女', '2025-02-14', NULL, 0, '0912345678', 'A123456789'),
('U39dcd62eb2c540c39909faa8c70a66ae', 'dang', 'y', '男', '2025-06-03', NULL, 0, '0900000001', 'A123456789'),
('U3f8756ec543740b8d56ad6e60a9e73a6', '歪屁屁', 'YP', '男', '2020-01-01', NULL, 0, '0912345678', 'A123456789'),
('U79a550e384e288066138caa3048993c4', '🧂', '陳語嫻', '女', '2005-05-25', NULL, 0, '0973308053', 'R123456789'),
('U7c9d00039cc39a0d21e985f798460e48', 'uuri', '政維', '男', '2004-09-02', NULL, 0, '0988888888', 'F131830203'),
('U8917d798951962ee0ca582d4fc1d46d2', '我修院', '我修院 達也', '男', '2025-05-14', NULL, 0, '0900114514', 'A114514114'),
('Ua06201dec88a97574d4c3662142a89f0', '均', '陳泓均', '男', '2025-05-01', '你好', 1, '0000000001', 'A000000000'),
('Ua0b3af57ce325778c619db3502d01323', '洪偉城', '洪偉城', '男', '2025-05-01', NULL, 0, '0912345678', 'A123456789'),
('Ub0d4b9a0c3b7f78ac7a3f5954975211e', 'Yves', 'Yp', '男', '1977-09-01', NULL, 0, '0912345678', 'A123456789'),
('Ub0d7ce3026fc3c8e599b5943b86b8be0', '可以', '不可以', '男', '2025-06-02', NULL, 0, '0444444444', 'O044444444'),
('Ubf273d35b61e075a0e464cc89208c6a4', '阿拉花瓜', '阿花', '女', '2000-06-12', NULL, 0, '0999999999', 'A112345677'),
('Ucd3d6e26e35f5353d5c886126f5402f0', 'bella', 'Abc', '女', '2025-05-14', NULL, 0, '0912345678', 'F123456789'),
('Ud759801d757d52e40195cffd858b5089', '哲', '黃一哲', '男', '2025-06-03', NULL, 1, '0968377533', 'D121222323'),
('Udd68e63026ff651a578c7918ae0b1fd6', 'Ooo', 'Tt', '女', '2025-06-02', NULL, 1, '0984578084', 'A127342764'),
('Ue13ee7f77244893b7f39a10cf8b70582', 'Aaa', 'Abc', '男', '1997-07-03', NULL, 0, '0988123456', 'A111222333'),
('Ufa31432987c129d11abf2af141b510be', 'test', 'ooo', '男', '2004-01-20', NULL, 0, '0912232165', 'J122345676');

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
  MODIFY `categories_id` int(4) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `order_detail`
--
ALTER TABLE `order_detail`
  MODIFY `orderid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=291;

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
  ADD CONSTRAINT `involvement_ibfk_2` FOREIGN KEY (`uid`) REFERENCES `user` (`uid`) ON DELETE CASCADE ON UPDATE CASCADE;

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
