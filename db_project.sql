-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2025-05-20 05:23:12
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
-- 資料表結構 `announcement`
--

CREATE TABLE `announcement` (
  `id` int(11) NOT NULL,
  `p_id` varchar(20) NOT NULL,
  `n_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `announcement`
--

INSERT INTO `announcement` (`id`, `p_id`, `n_id`) VALUES
(1, 'D1212122', 1),
(2, 'D1212124', 2);

-- --------------------------------------------------------

--
-- 資料表結構 `blacklist`
--

CREATE TABLE `blacklist` (
  `p_id` varchar(20) NOT NULL,
  `s_id` varchar(20) NOT NULL,
  `text` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `blacklist`
--

INSERT INTO `blacklist` (`p_id`, `s_id`, `text`) VALUES
('D1212122', 'B1229021', '未依規定時間完成預約'),
('D1212124', 'B1229051', '多次未出席預約');

-- --------------------------------------------------------

--
-- 資料表結構 `notice`
--

CREATE TABLE `notice` (
  `id` int(11) NOT NULL,
  `text` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `notice`
--

INSERT INTO `notice` (`id`, `text`) VALUES
(1, '未依規定時間完成預約'),
(2, '期末考報告繳交期限到 6 月 20 日');

-- --------------------------------------------------------

--
-- 資料表結構 `person`
--

CREATE TABLE `person` (
  `u_id` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `dept` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `person`
--

INSERT INTO `person` (`u_id`, `name`, `password`, `dept`) VALUES
('Uab68e67854ff651a578c7918ae0b2aa1', '李大志', 'D0000146', '資工系'),
('Uab68e67854ff651a578c7918ae0b2aaa', '小滿', 'P123456', 'Admin'),
('Ucd68e67854ff651a578c7918ae0b2cc3', '張偉豪', 'D0000148', '電機系'),
('Ud759801d757d52e40195cffd858b5089', '黃一哲', '12345678', '資工系'),
('Udd68e63026ff651a578c7918ae0b1fd6', '黃星昊', 'B1229021', '資工系');

-- --------------------------------------------------------

--
-- 資料表結構 `professor`
--

CREATE TABLE `professor` (
  `u_id` varchar(50) NOT NULL,
  `p_id` varchar(20) NOT NULL,
  `position` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `professor`
--

INSERT INTO `professor` (`u_id`, `p_id`, `position`) VALUES
('Uab68e67854ff651a578c7918ae0b2aa1', 'D1212122', '助理教授'),
('Ucd68e67854ff651a578c7918ae0b2cc3', 'D1212124', '教授');

-- --------------------------------------------------------

--
-- 資料表結構 `report`
--

CREATE TABLE `report` (
  `u_id` varchar(50) NOT NULL,
  `r_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `report`
--

INSERT INTO `report` (`u_id`, `r_id`) VALUES
('Ud759801d757d52e40195cffd858b5089', 2),
('Udd68e63026ff651a578c7918ae0b1fd6', 1);

-- --------------------------------------------------------

--
-- 資料表結構 `report_table`
--

CREATE TABLE `report_table` (
  `id` int(11) NOT NULL,
  `text` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `report_table`
--

INSERT INTO `report_table` (`id`, `text`) VALUES
(1, '找不到教授'),
(2, '預約按鈕沒有反應'),
(3, '課表沒有正常載入'),
(4, '找不到教授'),
(5, '預約按鈕沒有反應'),
(6, '課表沒有正常載入');

-- --------------------------------------------------------

--
-- 資料表結構 `schedule`
--

CREATE TABLE `schedule` (
  `id` int(11) NOT NULL,
  `p_id` varchar(20) DEFAULT NULL,
  `s_id` varchar(20) DEFAULT NULL,
  `time_slot_id` int(11) DEFAULT NULL,
  `week_id` int(11) DEFAULT NULL,
  `text` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `schedule`
--

INSERT INTO `schedule` (`id`, `p_id`, `s_id`, `time_slot_id`, `week_id`, `text`) VALUES
(1, 'D1212122', 'B1229021', 1, 1, '資料結構輔導'),
(2, 'D1212122', 'B1229021', 3, 3, '演算法面試準備'),
(3, 'D1212124', 'B1229051', 2, 2, '電機原理實驗'),
(4, 'D1212124', 'B1229051', 5, 4, '自動控制系統討論');

-- --------------------------------------------------------

--
-- 資料表結構 `student`
--

CREATE TABLE `student` (
  `u_id` varchar(50) NOT NULL,
  `s_id` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `student`
--

INSERT INTO `student` (`u_id`, `s_id`) VALUES
('Udd68e63026ff651a578c7918ae0b1fd6', 'B1229021'),
('Ud759801d757d52e40195cffd858b5089', 'B1229051');

-- --------------------------------------------------------

--
-- 資料表結構 `time_slot`
--

CREATE TABLE `time_slot` (
  `id` int(11) NOT NULL,
  `time_start` time NOT NULL,
  `time_end` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `time_slot`
--

INSERT INTO `time_slot` (`id`, `time_start`, `time_end`) VALUES
(1, '08:00:00', '09:00:00'),
(2, '09:00:00', '10:00:00'),
(3, '10:00:00', '11:00:00'),
(4, '11:00:00', '12:00:00'),
(5, '12:00:00', '13:00:00'),
(6, '13:00:00', '14:00:00'),
(7, '14:00:00', '15:00:00'),
(8, '15:00:00', '16:00:00'),
(9, '16:00:00', '17:00:00');

-- --------------------------------------------------------

--
-- 資料表結構 `week_day`
--

CREATE TABLE `week_day` (
  `id` int(11) NOT NULL,
  `day` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `week_day`
--

INSERT INTO `week_day` (`id`, `day`) VALUES
(1, 'Monday'),
(2, 'Tuesday'),
(3, 'Wednesday'),
(4, 'Thursday'),
(5, 'Friday');

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `announcement`
--
ALTER TABLE `announcement`
  ADD PRIMARY KEY (`id`),
  ADD KEY `p_id` (`p_id`),
  ADD KEY `n_id` (`n_id`);

--
-- 資料表索引 `blacklist`
--
ALTER TABLE `blacklist`
  ADD PRIMARY KEY (`p_id`,`s_id`),
  ADD KEY `p_id` (`p_id`),
  ADD KEY `s_id` (`s_id`);

--
-- 資料表索引 `notice`
--
ALTER TABLE `notice`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `person`
--
ALTER TABLE `person`
  ADD PRIMARY KEY (`u_id`);

--
-- 資料表索引 `professor`
--
ALTER TABLE `professor`
  ADD PRIMARY KEY (`u_id`),
  ADD UNIQUE KEY `p_id` (`p_id`);

--
-- 資料表索引 `report`
--
ALTER TABLE `report`
  ADD PRIMARY KEY (`u_id`,`r_id`),
  ADD KEY `r_id` (`r_id`);

--
-- 資料表索引 `report_table`
--
ALTER TABLE `report_table`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `schedule`
--
ALTER TABLE `schedule`
  ADD PRIMARY KEY (`id`),
  ADD KEY `p_id` (`p_id`),
  ADD KEY `s_id` (`s_id`),
  ADD KEY `time_slot_id` (`time_slot_id`),
  ADD KEY `week_id` (`week_id`);

--
-- 資料表索引 `student`
--
ALTER TABLE `student`
  ADD PRIMARY KEY (`u_id`),
  ADD UNIQUE KEY `s_id` (`s_id`);

--
-- 資料表索引 `time_slot`
--
ALTER TABLE `time_slot`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `week_day`
--
ALTER TABLE `week_day`
  ADD PRIMARY KEY (`id`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `announcement`
--
ALTER TABLE `announcement`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `notice`
--
ALTER TABLE `notice`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `report_table`
--
ALTER TABLE `report_table`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `schedule`
--
ALTER TABLE `schedule`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `time_slot`
--
ALTER TABLE `time_slot`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `week_day`
--
ALTER TABLE `week_day`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- 已傾印資料表的限制式
--

--
-- 資料表的限制式 `announcement`
--
ALTER TABLE `announcement`
  ADD CONSTRAINT `announcement_ibfk_1` FOREIGN KEY (`p_id`) REFERENCES `professor` (`p_id`),
  ADD CONSTRAINT `announcement_ibfk_2` FOREIGN KEY (`n_id`) REFERENCES `notice` (`id`);

--
-- 資料表的限制式 `blacklist`
--
ALTER TABLE `blacklist`
  ADD CONSTRAINT `blacklist_ibfk_1` FOREIGN KEY (`p_id`) REFERENCES `professor` (`p_id`),
  ADD CONSTRAINT `blacklist_ibfk_2` FOREIGN KEY (`s_id`) REFERENCES `student` (`s_id`);

--
-- 資料表的限制式 `professor`
--
ALTER TABLE `professor`
  ADD CONSTRAINT `professor_ibfk_1` FOREIGN KEY (`u_id`) REFERENCES `person` (`u_id`);

--
-- 資料表的限制式 `report`
--
ALTER TABLE `report`
  ADD CONSTRAINT `report_ibfk_1` FOREIGN KEY (`u_id`) REFERENCES `person` (`u_id`),
  ADD CONSTRAINT `report_ibfk_2` FOREIGN KEY (`r_id`) REFERENCES `report_table` (`id`);

--
-- 資料表的限制式 `schedule`
--
ALTER TABLE `schedule`
  ADD CONSTRAINT `schedule_ibfk_1` FOREIGN KEY (`p_id`) REFERENCES `professor` (`p_id`),
  ADD CONSTRAINT `schedule_ibfk_2` FOREIGN KEY (`s_id`) REFERENCES `student` (`s_id`),
  ADD CONSTRAINT `schedule_ibfk_3` FOREIGN KEY (`time_slot_id`) REFERENCES `time_slot` (`id`),
  ADD CONSTRAINT `schedule_ibfk_4` FOREIGN KEY (`week_id`) REFERENCES `week_day` (`id`);

--
-- 資料表的限制式 `student`
--
ALTER TABLE `student`
  ADD CONSTRAINT `student_ibfk_1` FOREIGN KEY (`u_id`) REFERENCES `person` (`u_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
