-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2025-05-18 18:09:39
-- 伺服器版本： 10.4.32-MariaDB
-- PHP 版本： 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `project`
--

-- --------------------------------------------------------

--
-- 資料表結構 `notice`
--

CREATE TABLE `notice` (
  `id` int(11) NOT NULL,
  `p_id` varchar(10) NOT NULL,
  `text` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `professor`
--

CREATE TABLE `professor` (
  `u_id` varchar(100) NOT NULL,
  `p_id` varchar(10) NOT NULL,
  `department` varchar(5) DEFAULT NULL,
  `password` varchar(20) DEFAULT NULL,
  `name` varchar(5) DEFAULT NULL,
  `position` varchar(5) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `professor`
--

INSERT INTO `professor` (`u_id`, `p_id`, `department`, `password`, `name`, `position`) VALUES
('DF45126455', 'D1212121', '資工系', 'D1212121', '王小明', '教授');

-- --------------------------------------------------------

--
-- 資料表結構 `schedule`
--

CREATE TABLE `schedule` (
  `id` int(11) NOT NULL,
  `s_id` varchar(10) NOT NULL,
  `p_id` varchar(10) NOT NULL,
  `week_id` int(11) NOT NULL,
  `time_slot_id` int(11) NOT NULL,
  `text` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `student`
--

CREATE TABLE `student` (
  `u_id` varchar(100) NOT NULL,
  `s_id` varchar(10) NOT NULL,
  `department` varchar(5) DEFAULT NULL,
  `password` varchar(20) DEFAULT NULL,
  `name` varchar(5) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `student`
--

INSERT INTO `student` (`u_id`, `s_id`, `department`, `password`, `name`) VALUES
('U12eb6fda512d63001b90bbc685545029', 'B0153120', '藥妝系', 'B0153120', '小滿'),
('Ud759801d757d52e40195cffd858b5089', 'B1229051', '資工系', '12345678', '黃一哲'),
('Udd68e63026ff651a578c7918ae0b1fd6', 'B1229021', '資工系', 'B1229021', '黃星昊');

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
  `name` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `week_day`
--

INSERT INTO `week_day` (`id`, `name`) VALUES
(1, 'Monday'),
(2, 'Tuesday'),
(3, 'Wednesday'),
(4, 'Thursday'),
(5, 'Friday');

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `notice`
--
ALTER TABLE `notice`
  ADD PRIMARY KEY (`id`),
  ADD KEY `p_id` (`p_id`);

--
-- 資料表索引 `professor`
--
ALTER TABLE `professor`
  ADD PRIMARY KEY (`u_id`),
  ADD UNIQUE KEY `p_id` (`p_id`);

--
-- 資料表索引 `schedule`
--
ALTER TABLE `schedule`
  ADD PRIMARY KEY (`id`),
  ADD KEY `s_id` (`s_id`),
  ADD KEY `p_id` (`p_id`),
  ADD KEY `week_id` (`week_id`),
  ADD KEY `time_slot_id` (`time_slot_id`);

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
-- 使用資料表自動遞增(AUTO_INCREMENT) `notice`
--
ALTER TABLE `notice`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `schedule`
--
ALTER TABLE `schedule`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

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
-- 資料表的限制式 `notice`
--
ALTER TABLE `notice`
  ADD CONSTRAINT `notice_ibfk_1` FOREIGN KEY (`p_id`) REFERENCES `professor` (`p_id`);

--
-- 資料表的限制式 `schedule`
--
ALTER TABLE `schedule`
  ADD CONSTRAINT `schedule_ibfk_1` FOREIGN KEY (`s_id`) REFERENCES `student` (`s_id`),
  ADD CONSTRAINT `schedule_ibfk_2` FOREIGN KEY (`p_id`) REFERENCES `professor` (`p_id`),
  ADD CONSTRAINT `schedule_ibfk_3` FOREIGN KEY (`week_id`) REFERENCES `week_day` (`id`),
  ADD CONSTRAINT `schedule_ibfk_4` FOREIGN KEY (`time_slot_id`) REFERENCES `time_slot` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
