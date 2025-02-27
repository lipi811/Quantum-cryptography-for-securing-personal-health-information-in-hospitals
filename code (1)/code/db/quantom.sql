-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               5.0.17-nt - MySQL Community Edition (GPL)
-- Server OS:                    Win32
-- HeidiSQL Version:             9.4.0.5174
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- Dumping database structure for quantumcrypt
CREATE DATABASE IF NOT EXISTS `quantumcrypt` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `quantumcrypt`;

-- Dumping structure for table quantumcrypt.patient
CREATE TABLE IF NOT EXISTS `patient` (
  `id` int(11) NOT NULL auto_increment,
  `name` blob NOT NULL,
  `age` blob NOT NULL,
  `gender` blob NOT NULL,
  `phone` blob NOT NULL,
  `address` blob NOT NULL,
  `disease_type` blob NOT NULL,
  `medical_image` blob NOT NULL,
  `did` int(11) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `FK_patient_user` (`did`),
  CONSTRAINT `FK_patient_user` FOREIGN KEY (`did`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Dumping data for table quantumcrypt.patient: ~1 rows (approximately)
/*!40000 ALTER TABLE `patient` DISABLE KEYS */;
INSERT INTO `patient` (`id`, `name`, `age`, `gender`, `phone`, `address`, `disease_type`, `medical_image`, `did`) VALUES
	(1, _binary 0xA334750F55B0DD011FADAF453B96B27C6BB23C9CA423FDBCC12D765BB6E90892, _binary 0x67CF4942F16E18670519152EE18B3D431BEB88C2F7049777617C223F6D0A3C9C, _binary 0x4EA3B630771EC895115932B1388A7B46F0E5A227F0D256093BB4B2F04C4A7B99, _binary 0x1E9C74A303AC8208F52F48B412E23E67F0B5E876EC5E624EFAEE67AB5009E95B, _binary 0x210EBE61C541A92610F74A6C1FB6A3CE90C245A9AD3391B0B85F97005EC4FB9C, _binary 0xAD00C9C944F489FA890A63FB20346F4B9696737ED36D6F047D73A2C6B6F1FAE5, _binary 0x7374617469632F75706C6F6164735C656E637279707465645F54652D676C5F303031302E6A7067, 2);
/*!40000 ALTER TABLE `patient` ENABLE KEYS */;

-- Dumping structure for table quantumcrypt.patientlogin
CREATE TABLE IF NOT EXISTS `patientlogin` (
  `id` int(11) NOT NULL auto_increment,
  `email` varchar(150) NOT NULL default '0',
  `password` varchar(150) NOT NULL default '0',
  `pid` int(11) NOT NULL default '0',
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Dumping data for table quantumcrypt.patientlogin: ~1 rows (approximately)
/*!40000 ALTER TABLE `patientlogin` DISABLE KEYS */;
INSERT INTO `patientlogin` (`id`, `email`, `password`, `pid`) VALUES
	(1, 'arun@gmail.com', '2840', 1);
/*!40000 ALTER TABLE `patientlogin` ENABLE KEYS */;

-- Dumping structure for table quantumcrypt.signatures
CREATE TABLE IF NOT EXISTS `signatures` (
  `id` int(11) NOT NULL auto_increment,
  `name` text NOT NULL,
  `age` text NOT NULL,
  `gender` text NOT NULL,
  `phone` text NOT NULL,
  `address` text NOT NULL,
  `diseasetype` text NOT NULL,
  `img` text NOT NULL,
  `pid` int(11) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `FK_signatures_patient` (`pid`),
  CONSTRAINT `FK_signatures_patient` FOREIGN KEY (`pid`) REFERENCES `patient` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Dumping data for table quantumcrypt.signatures: ~1 rows (approximately)
/*!40000 ALTER TABLE `signatures` DISABLE KEYS */;
INSERT INTO `signatures` (`id`, `name`, `age`, `gender`, `phone`, `address`, `diseasetype`, `img`, `pid`) VALUES
	(1, '5fa4ee7624ac205554673a4b8d38bae65688fc185fbcfeaf9aaeb01ad5fef110', 'aa99c13b6d9d8a701f22f8be45939487fc655c2faa317635edef348c378f6aaf', 'd24c0e316d8a876fa50f8ff19153621cf4ba695f43d0bb2b88d4f6abf38572cb', '29f2678480b38ecfe1580dbff6d896e9d35c4fe2913753ce90031dc8767307a5', '9b9e128797cff5da2eac373f7c161956ad57dc0b84fe1bfa9116e278d3df931c', 'caf3faad6099ed0900d241c832330f03aae0c30df2ac10da02a7adaa9367fdd1', '4d589cccc6a280e4abdafc02f92d185bd65629dbbb5cc416c551ff660d3127f8', 1);
/*!40000 ALTER TABLE `signatures` ENABLE KEYS */;

-- Dumping structure for table quantumcrypt.user
CREATE TABLE IF NOT EXISTS `user` (
  `id` int(11) NOT NULL auto_increment,
  `email` varchar(150) NOT NULL default '0',
  `password` varchar(150) NOT NULL default '0',
  `role` varchar(150) NOT NULL default '0',
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Dumping data for table quantumcrypt.user: ~2 rows (approximately)
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` (`id`, `email`, `password`, `role`) VALUES
	(1, 'shri@gmail.com', '123', 'radiologist'),
	(2, 'doc@gmail.com', '123', 'doctor');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
