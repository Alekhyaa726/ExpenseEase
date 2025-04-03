-- MySQL dump 10.13  Distrib 8.0.36, for Linux (x86_64)
--
-- Host: localhost    Database: personal_finance
-- ------------------------------------------------------
-- Server version	8.0.36-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Account`
--

DROP TABLE IF EXISTS `Account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Account` (
  `acc_num` int NOT NULL,
  `acc_type` varchar(20) DEFAULT NULL,
  `balance` int DEFAULT NULL,
  `user` varchar(20) NOT NULL,
  PRIMARY KEY (`acc_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Account`
--

LOCK TABLES `Account` WRITE;
/*!40000 ALTER TABLE `Account` DISABLE KEYS */;
/*!40000 ALTER TABLE `Account` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Displays`
--

DROP TABLE IF EXISTS `Displays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Displays` (
  `NotificationID` int NOT NULL,
  `user` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`NotificationID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Displays`
--

LOCK TABLES `Displays` WRITE;
/*!40000 ALTER TABLE `Displays` DISABLE KEYS */;
/*!40000 ALTER TABLE `Displays` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Expense`
--

DROP TABLE IF EXISTS `Expense`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Expense` (
  `expenseID` int NOT NULL,
  `amount` int DEFAULT NULL,
  `category` varchar(20) DEFAULT NULL,
  `date_of_txn` date DEFAULT NULL,
  `mode` varchar(20) DEFAULT NULL,
  `user` varchar(20) NOT NULL,
  PRIMARY KEY (`expenseID`,`user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Expense`
--

LOCK TABLES `Expense` WRITE;
/*!40000 ALTER TABLE `Expense` DISABLE KEYS */;
INSERT INTO `Expense` VALUES (1,1000,'Food','2024-03-16','Debit','hello'),(1,100,'Food','2024-03-14','UPI','prabhav'),(2,65002,'Food','2024-03-13','Debit','hello'),(2,100,'Food','2024-03-14','NetBanking','prabhav'),(3,1200,'Food','2024-03-15','NetBanking','hello'),(3,123,'Beverages','2024-03-14','Debit','prabhav'),(4,200,'Beverages','2024-03-13','Cash','hello'),(4,200,'Education','2024-03-07','Cash','prabhav'),(5,569,'Food','2024-03-13','Credit','hello'),(5,1000,'Food','2024-03-09','Debit','prabhav');
/*!40000 ALTER TABLE `Expense` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Income`
--

DROP TABLE IF EXISTS `Income`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Income` (
  `amount` int DEFAULT NULL,
  `description` varchar(30) DEFAULT NULL,
  `incomeNum` int DEFAULT NULL,
  `user` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Income`
--

LOCK TABLES `Income` WRITE;
/*!40000 ALTER TABLE `Income` DISABLE KEYS */;
/*!40000 ALTER TABLE `Income` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Loan`
--

DROP TABLE IF EXISTS `Loan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Loan` (
  `loan_num` int NOT NULL,
  `loan_amount` int DEFAULT NULL,
  `interest` int DEFAULT NULL,
  `balance` int DEFAULT NULL,
  `endDate` date DEFAULT NULL,
  `startDate` date DEFAULT NULL,
  `type` varchar(20) DEFAULT NULL,
  `dueDate` date DEFAULT NULL,
  `user` varchar(20) NOT NULL,
  PRIMARY KEY (`loan_num`,`user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Loan`
--

LOCK TABLES `Loan` WRITE;
/*!40000 ALTER TABLE `Loan` DISABLE KEYS */;
INSERT INTO `Loan` VALUES (1,1000,12,1000,'2024-03-07','2024-03-14','Personal','2024-03-26','hello'),(1,100000,15,20000,'2024-03-29','2022-02-12','Home','2024-03-13','prabhav');
/*!40000 ALTER TABLE `Loan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Maintains`
--

DROP TABLE IF EXISTS `Maintains`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Maintains` (
  `AccNo` int DEFAULT NULL,
  `user` varchar(20) DEFAULT NULL,
  KEY `AccNo` (`AccNo`),
  CONSTRAINT `Maintains_ibfk_1` FOREIGN KEY (`AccNo`) REFERENCES `Account` (`acc_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Maintains`
--

LOCK TABLES `Maintains` WRITE;
/*!40000 ALTER TABLE `Maintains` DISABLE KEYS */;
/*!40000 ALTER TABLE `Maintains` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Notification`
--

DROP TABLE IF EXISTS `Notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Notification` (
  `notify_id` int NOT NULL,
  `nType` varchar(20) DEFAULT NULL,
  `user` varchar(20) NOT NULL,
  `content` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`notify_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Notification`
--

LOCK TABLES `Notification` WRITE;
/*!40000 ALTER TABLE `Notification` DISABLE KEYS */;
INSERT INTO `Notification` VALUES (1,'ADD EXPENSE','hello','Added an expense'),(2,'ADD EXPENSE','hello','Added an expense of amount 200'),(3,'ADD LOAN','hello','Added a loan of amount 1000 at an interest rate of 12%'),(4,'ADD EXPENSE','hello','Added an expense of amount 569');
/*!40000 ALTER TABLE `Notification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Records`
--

DROP TABLE IF EXISTS `Records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Records` (
  `AccNo` int DEFAULT NULL,
  `Expense` float DEFAULT NULL,
  `incomeID` int DEFAULT NULL,
  `notifyID` int DEFAULT NULL,
  `user` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Records`
--

LOCK TABLES `Records` WRITE;
/*!40000 ALTER TABLE `Records` DISABLE KEYS */;
/*!40000 ALTER TABLE `Records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `holds`
--

DROP TABLE IF EXISTS `holds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `holds` (
  `AccNum` int NOT NULL,
  `incomeID` int DEFAULT NULL,
  PRIMARY KEY (`AccNum`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `holds`
--

LOCK TABLES `holds` WRITE;
/*!40000 ALTER TABLE `holds` DISABLE KEYS */;
/*!40000 ALTER TABLE `holds` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profile`
--

DROP TABLE IF EXISTS `profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `profile` (
  `Name` varchar(30) DEFAULT NULL,
  `Phone` varchar(20) NOT NULL,
  `emailID` varchar(30) NOT NULL,
  `budget` int DEFAULT NULL,
  `notify_id` int DEFAULT NULL,
  `incomeID` int DEFAULT NULL,
  `expenseID` int DEFAULT NULL,
  `user` varchar(20) NOT NULL,
  PRIMARY KEY (`emailID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profile`
--

LOCK TABLES `profile` WRITE;
/*!40000 ALTER TABLE `profile` DISABLE KEYS */;
INSERT INTO `profile` VALUES ('hello','8310232245','dhruvsai1708@gmail.com',65000,NULL,NULL,NULL,'hello'),('Prabhav','8762449430','prabhavbk5112@gmail.com',20000,NULL,NULL,NULL,'prabhav');
/*!40000 ALTER TABLE `profile` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-04-01 16:10:48
