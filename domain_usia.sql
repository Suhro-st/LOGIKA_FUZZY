-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Sep 20, 2026 at 11:11 AM
-- Server version: 9.1.0
-- PHP Version: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `logika_fuzzy`
--

-- --------------------------------------------------------

--
-- Table structure for table `domain_usia`
--

DROP TABLE IF EXISTS `domain_usia`;
CREATE TABLE IF NOT EXISTS `domain_usia` (
  `id_domain` int NOT NULL AUTO_INCREMENT,
  `kategori` varchar(50) NOT NULL,
  `batas_bawah` decimal(5,2) NOT NULL,
  `a` decimal(5,2) NOT NULL,
  `b` decimal(5,2) NOT NULL,
  `c` decimal(5,2) NOT NULL,
  `d` decimal(5,2) NOT NULL,
  `batas_atas` decimal(5,2) NOT NULL,
  PRIMARY KEY (`id_domain`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `domain_usia`
--

INSERT INTO `domain_usia` (`id_domain`, `kategori`, `batas_bawah`, `a`, `b`, `c`, `d`, `batas_atas`) VALUES
(1, 'Bayi/Anak Usia Dini', 0.00, 0.00, 2.00, 3.00, 5.00, 5.00),
(2, 'Anak-anak', 6.00, 6.00, 8.00, 9.00, 11.00, 11.00),
(3, 'Remaja', 10.00, 10.00, 14.00, 15.00, 19.00, 19.00),
(4, 'Pemuda', 15.00, 15.00, 19.00, 20.00, 24.00, 24.00),
(5, 'Dewasa', 20.00, 20.00, 42.00, 43.00, 65.00, 65.00),
(6, 'Lanjut Usia', 60.00, 60.00, 70.00, 80.00, 90.00, 90.00);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

