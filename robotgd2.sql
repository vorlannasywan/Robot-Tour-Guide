-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jul 16, 2025 at 04:38 AM
-- Server version: 8.0.30
-- PHP Version: 8.3.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `robotgd2`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `username` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(100) COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`username`, `password`) VALUES
('dika', 'dikahdmi');

-- --------------------------------------------------------

--
-- Table structure for table `lantai`
--

CREATE TABLE `lantai` (
  `id` int NOT NULL,
  `nomor` int NOT NULL,
  `deskripsi` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `lantai`
--

INSERT INTO `lantai` (`id`, `nomor`, `deskripsi`) VALUES
(1, 1, 'Laboratorium dan ruang kerja'),
(2, 2, 'Tempat Dosen'),
(3, 3, 'Ruang kelas'),
(4, 4, 'Laboratorium');

-- --------------------------------------------------------

--
-- Table structure for table `robot_usage`
--

CREATE TABLE `robot_usage` (
  `id` int NOT NULL,
  `event_type` enum('activation','question') COLLATE utf8mb4_general_ci NOT NULL,
  `ruangan_id` int DEFAULT NULL,
  `timestamp` datetime NOT NULL,
  `details` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `robot_usage`
--

INSERT INTO `robot_usage` (`id`, `event_type`, `ruangan_id`, `timestamp`, `details`) VALUES
(92, 'question', 8, '2025-07-11 23:21:08', 'ruang dosen'),
(93, 'question', 6, '2025-07-11 23:21:22', 'ruang bengkel'),
(94, 'question', 6, '2025-07-11 23:21:36', 'ruang bengkel'),
(95, 'question', 7, '2025-07-11 23:21:55', 'ruang tu'),
(99, 'question', 5, '2025-07-11 23:22:20', 'ruang ict'),
(101, 'question', 6, '2025-07-11 23:22:35', 'ruang bengkel'),
(102, 'question', 8, '2025-07-11 23:22:48', 'ruang dosen'),
(103, 'question', 8, '2025-07-11 23:23:05', 'ruang dosen'),
(104, 'question', 8, '2025-07-11 23:23:17', 'ruang dosen'),
(109, 'question', 6, '2025-07-11 23:24:15', 'ruang bengkel'),
(110, 'question', 8, '2025-07-11 23:24:38', 'ruang dosen'),
(111, 'question', 8, '2025-07-11 23:24:56', 'ruang dosen'),
(113, 'question', 4, '2025-07-11 23:26:43', 'ruang iwi'),
(114, 'question', 4, '2025-07-11 23:27:52', 'ruang iwill'),
(115, 'question', 8, '2025-07-14 12:37:16', 'ruang dosen'),
(116, 'question', 6, '2025-07-14 12:37:33', 'ruang bengkel');

-- --------------------------------------------------------

--
-- Table structure for table `ruangan`
--

CREATE TABLE `ruangan` (
  `id` int NOT NULL,
  `nomor` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `nama` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `lantai_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `ruangan`
--

INSERT INTO `ruangan` (`id`, `nomor`, `nama`, `lantai_id`) VALUES
(1, '2101', 'laboratorium utama', 1),
(2, '2102', 'ruang staff', 1),
(3, '2103', 'alat alat laboratorium', 1),
(4, '2104', 'ruang iwill', 1),
(5, '2105', 'ruang ict', 1),
(6, '2106', 'ruang bengkel', 1),
(7, '2201', 'ruang tu', 2),
(8, '2202', 'ruang dosen', 2),
(9, '2203', 'ruang sidang', 2),
(10, '2204', 'ruang kaprodi', 2),
(11, '2301', 'ruang kelas 1', 3),
(12, '2302', 'ruang kelas 2', 3),
(13, '2303', 'ruang kelas 3', 3),
(14, '2304', 'ruang kelas 4', 3),
(15, '2305', 'ruang kelas 5', 3),
(16, '2306', 'ruang kelas 6', 3),
(17, '2401', 'laboratorium komputer', 4),
(18, '2402', 'laboratorium elektronika', 4),
(19, '2403', 'laboratorium mekatronika', 4),
(20, '2404', 'laboratorium riset', 4);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `lantai`
--
ALTER TABLE `lantai`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nomor` (`nomor`);

--
-- Indexes for table `robot_usage`
--
ALTER TABLE `robot_usage`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ruangan_id` (`ruangan_id`);

--
-- Indexes for table `ruangan`
--
ALTER TABLE `ruangan`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nomor` (`nomor`),
  ADD KEY `lantai_id` (`lantai_id`),
  ADD KEY `idx_nama_ruangan` (`nama`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `lantai`
--
ALTER TABLE `lantai`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `robot_usage`
--
ALTER TABLE `robot_usage`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=117;

--
-- AUTO_INCREMENT for table `ruangan`
--
ALTER TABLE `ruangan`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `robot_usage`
--
ALTER TABLE `robot_usage`
  ADD CONSTRAINT `robot_usage_ibfk_1` FOREIGN KEY (`ruangan_id`) REFERENCES `ruangan` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `ruangan`
--
ALTER TABLE `ruangan`
  ADD CONSTRAINT `ruangan_ibfk_1` FOREIGN KEY (`lantai_id`) REFERENCES `lantai` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
