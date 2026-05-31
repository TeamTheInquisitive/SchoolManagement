Warning: A partial dump from a server that has GTIDs will by default include the GTIDs of all transactions, even those that changed suppressed parts of the database. If you don't want to restore GTIDs, pass --set-gtid-purged=OFF. To make a complete dump, pass --all-databases --triggers --routines --events. 
Warning: A dump from a server that has GTIDs enabled will by default include the GTIDs of all transactions, even those that were executed during its extraction and might not be represented in the dumped data. This might result in an inconsistent data dump. 
In order to ensure a consistent backup of the database, pass --single-transaction or --lock-all-tables or --source-data. 
-- MySQL dump 10.13  Distrib 9.6.0, for macos26.4 (arm64)
--
-- Host: localhost    Database: SchoolManagement
-- ------------------------------------------------------
-- Server version	9.6.0

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
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '0f86c1ac-5739-11f1-a1a7-1d959425008f:1-961';

--
-- Table structure for table `academic_years`
--

DROP TABLE IF EXISTS `academic_years`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `academic_years` (
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `is_current` tinyint(1) NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_academic_years_school_name` (`school_id`,`name`),
  KEY `ix_academic_years_school_id` (`school_id`),
  KEY `ix_academic_years_is_active` (`is_active`),
  CONSTRAINT `fk_academic_years_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `ck_academic_years_chk_academic_years_dates` CHECK ((`end_date` > `start_date`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `academic_years`
--

LOCK TABLES `academic_years` WRITE;
/*!40000 ALTER TABLE `academic_years` DISABLE KEYS */;
INSERT INTO `academic_years` VALUES ('2025-2026','2025-06-01','2026-03-31',1,'0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `academic_years` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `activities`
--

DROP TABLE IF EXISTS `activities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activities` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `activity_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `role` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `achievement` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `certificate_url` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `recorded_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_activities_academic_year_id_academic_years` (`academic_year_id`),
  KEY `fk_activities_recorded_by_staff` (`recorded_by`),
  KEY `ix_activities_school_id` (`school_id`),
  KEY `idx_activities_type` (`school_id`,`academic_year_id`,`activity_type`),
  KEY `idx_activities_student` (`student_id`,`academic_year_id`),
  KEY `ix_activities_is_active` (`is_active`),
  CONSTRAINT `fk_activities_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_activities_recorded_by_staff` FOREIGN KEY (`recorded_by`) REFERENCES `staff` (`id`),
  CONSTRAINT `fk_activities_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_activities_student_id_students` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activities`
--

LOCK TABLES `activities` WRITE;
/*!40000 ALTER TABLE `activities` DISABLE KEYS */;
INSERT INTO `activities` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4823e6f0-69e2-4a1c-a0ff-1fb9653767d5','Sports','Cricket Club',NULL,'Member','2025-07-01',NULL,NULL,NULL,NULL,'Active','14da24aa-d949-45c7-ad0f-59c52d70c7b5','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','d4145bca-3b08-489a-a80d-c8141b3ce925','Academic','Science Club',NULL,'Member','2025-07-01',NULL,NULL,NULL,NULL,'Active','1dedbb7e-a668-4891-84aa-ec5edcde2eb6','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','13118271-a690-4bd5-a38b-4cc13334f292','Cultural','Art Club',NULL,'Member','2025-07-01',NULL,NULL,NULL,NULL,'Active','c0ad7358-0d34-413e-b4db-924a79019c29','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `activities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `adhoc_classes`
--

DROP TABLE IF EXISTS `adhoc_classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `adhoc_classes` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `staff_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `class_section_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `subject_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `date` date NOT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `duration_minutes` int DEFAULT NULL,
  `type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `original_staff_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `topic` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `student_count` int NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_adhoc_classes_academic_year_id_academic_years` (`academic_year_id`),
  KEY `fk_adhoc_classes_subject_id_subjects` (`subject_id`),
  KEY `fk_adhoc_classes_original_staff_id_staff` (`original_staff_id`),
  KEY `ix_adhoc_classes_is_active` (`is_active`),
  KEY `idx_adhoc_classes_class` (`class_section_id`,`date`),
  KEY `idx_adhoc_classes_date` (`school_id`,`date`),
  KEY `idx_adhoc_classes_status` (`school_id`,`academic_year_id`,`status`),
  KEY `ix_adhoc_classes_school_id` (`school_id`),
  KEY `idx_adhoc_classes_staff` (`staff_id`,`date`),
  CONSTRAINT `fk_adhoc_classes_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_adhoc_classes_class_section_id_class_sections` FOREIGN KEY (`class_section_id`) REFERENCES `class_sections` (`id`),
  CONSTRAINT `fk_adhoc_classes_original_staff_id_staff` FOREIGN KEY (`original_staff_id`) REFERENCES `staff` (`id`),
  CONSTRAINT `fk_adhoc_classes_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_adhoc_classes_staff_id_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`),
  CONSTRAINT `fk_adhoc_classes_subject_id_subjects` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `adhoc_classes`
--

LOCK TABLES `adhoc_classes` WRITE;
/*!40000 ALTER TABLE `adhoc_classes` DISABLE KEYS */;
INSERT INTO `adhoc_classes` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','7794dcaf-e97c-41cb-83f8-c5ec057f8bd0','8f4911ac-187b-41a2-8866-1fc178a4343d','92d8d000-6478-4270-9a18-77b9d802885d','2025-11-12','09:45:00','10:30:00',45,'Substitute','Regular teacher on leave','f0bc267d-4453-40bf-9bcf-f3c888fcb48c',NULL,NULL,30,'Completed',NULL,'3cdd5a73-cb3b-4f46-9212-84857c1dd64f','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `adhoc_classes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('407b8e4db72e');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assignment_submissions`
--

DROP TABLE IF EXISTS `assignment_submissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assignment_submissions` (
  `assignment_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `submitted_at` datetime DEFAULT NULL,
  `comments` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `file_urls` json DEFAULT NULL,
  `marks` decimal(6,2) DEFAULT NULL,
  `feedback` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `graded_at` datetime DEFAULT NULL,
  `graded_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_late` tinyint(1) NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_assignment_submissions_school_assignment_student` (`school_id`,`assignment_id`,`student_id`),
  KEY `fk_assignment_submissions_graded_by_staff` (`graded_by`),
  KEY `ix_assignment_submissions_school_id` (`school_id`),
  KEY `ix_assignment_submissions_is_active` (`is_active`),
  KEY `idx_assignment_submissions_assignment` (`assignment_id`,`status`),
  KEY `idx_assignment_submissions_student` (`student_id`),
  CONSTRAINT `fk_assignment_submissions_assignment_id_assignments` FOREIGN KEY (`assignment_id`) REFERENCES `assignments` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_assignment_submissions_graded_by_staff` FOREIGN KEY (`graded_by`) REFERENCES `staff` (`id`),
  CONSTRAINT `fk_assignment_submissions_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_assignment_submissions_student_id_students` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assignment_submissions`
--

LOCK TABLES `assignment_submissions` WRITE;
/*!40000 ALTER TABLE `assignment_submissions` DISABLE KEYS */;
INSERT INTO `assignment_submissions` VALUES ('75e87e65-79e3-440b-bc85-054744ef4479','3778f4c0-2c67-479d-9dd2-4f84f696a1dc','Submitted','2025-11-18 14:00:00',NULL,'[]',NULL,NULL,NULL,NULL,1,'0830b014-1ac2-42d5-9a0e-98b3d3f02504','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('3575d3f8-f3c5-498a-b12e-a00df03db860','d4145bca-3b08-489a-a80d-c8141b3ce925','Pending',NULL,NULL,'[]',NULL,NULL,NULL,NULL,0,'1f2251c8-4267-4082-afeb-026ab242ad37','{}','2026-05-26 12:23:30','2026-05-26 12:23:30',1,NULL,NULL,'ca4bb6bf-ab10-4153-b8c2-734560dc7c8b',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('75e87e65-79e3-440b-bc85-054744ef4479','13118271-a690-4bd5-a38b-4cc13334f292','Graded','2025-11-18 12:00:00',NULL,'[]',85.00,NULL,NULL,NULL,0,'4eca3f26-bf82-4705-a2cc-4a9ada2c3ffc','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('3575d3f8-f3c5-498a-b12e-a00df03db860','13118271-a690-4bd5-a38b-4cc13334f292','Pending',NULL,NULL,'[]',NULL,NULL,NULL,NULL,0,'8e5e9e13-c998-4899-99cd-ada6f843c8f4','{}','2026-05-26 12:23:30','2026-05-26 12:23:30',1,NULL,NULL,'ca4bb6bf-ab10-4153-b8c2-734560dc7c8b',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('75e87e65-79e3-440b-bc85-054744ef4479','d4145bca-3b08-489a-a80d-c8141b3ce925','Graded','2025-11-18 11:00:00',NULL,'[]',80.00,NULL,NULL,NULL,0,'90820e76-74bb-47c5-878b-d7d427a2daec','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('75e87e65-79e3-440b-bc85-054744ef4479','394ceb26-22f3-4d34-8881-53472e29ad43','Submitted','2025-11-18 13:00:00',NULL,'[]',NULL,NULL,NULL,NULL,0,'962060e2-9b32-4b1c-8162-f79c9f0e8a39','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('3575d3f8-f3c5-498a-b12e-a00df03db860','4823e6f0-69e2-4a1c-a0ff-1fb9653767d5','Pending',NULL,NULL,'[]',NULL,NULL,NULL,NULL,0,'a79f2d05-6f71-4b43-a994-081952e283af','{}','2026-05-26 12:23:30','2026-05-26 12:23:30',1,NULL,NULL,'ca4bb6bf-ab10-4153-b8c2-734560dc7c8b',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('75e87e65-79e3-440b-bc85-054744ef4479','4823e6f0-69e2-4a1c-a0ff-1fb9653767d5','Graded','2025-11-18 10:00:00',NULL,'[]',75.00,NULL,NULL,NULL,0,'b45b459a-b22c-4097-91dc-a436f9b7448e','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `assignment_submissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assignments`
--

DROP TABLE IF EXISTS `assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assignments` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `class_section_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `subject_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `staff_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `due_date` date NOT NULL,
  `max_marks` decimal(6,2) DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `assigned_date` date NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_assignments_academic_year_id_academic_years` (`academic_year_id`),
  KEY `fk_assignments_subject_id_subjects` (`subject_id`),
  KEY `idx_assignments_teacher` (`staff_id`,`academic_year_id`),
  KEY `idx_assignments_due` (`school_id`,`due_date`),
  KEY `idx_assignments_status` (`school_id`,`academic_year_id`,`status`),
  KEY `ix_assignments_school_id` (`school_id`),
  KEY `ix_assignments_is_active` (`is_active`),
  KEY `idx_assignments_class` (`class_section_id`,`academic_year_id`),
  CONSTRAINT `fk_assignments_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_assignments_class_section_id_class_sections` FOREIGN KEY (`class_section_id`) REFERENCES `class_sections` (`id`),
  CONSTRAINT `fk_assignments_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_assignments_staff_id_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`),
  CONSTRAINT `fk_assignments_subject_id_subjects` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assignments`
--

LOCK TABLES `assignments` WRITE;
/*!40000 ALTER TABLE `assignments` DISABLE KEYS */;
INSERT INTO `assignments` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','test','test descroption','2026-05-27',100.00,'Active','2026-05-26','3575d3f8-f3c5-498a-b12e-a00df03db860','{}','2026-05-26 12:23:30','2026-05-26 12:23:30',1,NULL,NULL,'ca4bb6bf-ab10-4153-b8c2-734560dc7c8b',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','5ca31131-7785-451f-a040-447944567741','b1edfea4-d604-4f8c-959b-cdf713d21e84','Science Lab Report','Complete Science Lab Report and submit before due date.','2025-11-25',100.00,'Active','2025-11-18','38297bff-9aab-4474-8d86-2355f2efdbec','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','7e50dbc3-27ea-4be6-bc04-c4c29525b4f5','4daac19b-24a9-41e8-917e-1e9f2192c8aa','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','Science Project Report','Complete the assignment','2026-06-04',10.00,'active','2026-05-27','48cd67d7-0a5c-48d1-9c87-05a230f06d7b','{}','2026-05-27 09:16:33','2026-05-27 09:16:33',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','92d8d000-6478-4270-9a18-77b9d802885d','7794dcaf-e97c-41cb-83f8-c5ec057f8bd0','Essay Writing','Complete Essay Writing and submit before due date.','2025-11-22',100.00,'Active','2025-11-15','7341074a-f20f-4adc-96ee-64b30892cc56','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','Algebra Homework Ch.5','Complete Algebra Homework Ch.5 and submit before due date.','2025-11-20',100.00,'Active','2025-11-13','75e87e65-79e3-440b-bc85-054744ef4479','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','3d785786-e000-4d52-8387-d4aa0486027c','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','Math Quiz - Chapter 5','Complete the assignment','2026-06-01',10.00,'active','2026-05-27','c1691368-c6c0-4020-8830-2f3ca5f81191','{}','2026-05-27 09:16:33','2026-05-27 09:16:33',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `assignments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendance_records`
--

DROP TABLE IF EXISTS `attendance_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance_records` (
  `attendance_session_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_attendance_records_session_student` (`school_id`,`attendance_session_id`,`student_id`),
  KEY `idx_attendance_records_status` (`attendance_session_id`,`status`),
  KEY `ix_attendance_records_school_id` (`school_id`),
  KEY `ix_attendance_records_is_active` (`is_active`),
  KEY `idx_attendance_records_student` (`student_id`),
  CONSTRAINT `fk_attendance_records_attendance_session_id_attendance_sessions` FOREIGN KEY (`attendance_session_id`) REFERENCES `attendance_sessions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_attendance_records_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_attendance_records_student_id_students` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance_records`
--

LOCK TABLES `attendance_records` WRITE;
/*!40000 ALTER TABLE `attendance_records` DISABLE KEYS */;
INSERT INTO `attendance_records` VALUES ('be7d4fb4-68ce-4796-8836-c591fae76194','13118271-a690-4bd5-a38b-4cc13334f292','Present',NULL,'05776f2a-26ae-4a1e-801a-b08d047e843a','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('ad45f275-38e3-4e79-9d73-f54f69be994f','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Late',NULL,'0cb11ba2-bcc5-44d0-8b7b-0389c547b44f','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('48538b46-e76a-4870-874f-fcd91cedfd5c','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'1375596d-c05d-4c4c-9559-0a067e270341','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('d6434a17-9ccb-4c1c-aaa4-0a71cfc1a63d','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'163ed079-e7a7-4cda-bb25-413ed41fb0ad','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('4de1c310-3dc9-459b-a8dc-7e0a137d7617','4823e6f0-69e2-4a1c-a0ff-1fb9653767d5','Present',NULL,'1ada4417-02f1-4db0-820d-44326eac6f13','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('a99658bb-85d5-4c34-a324-e25a11206d96','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'1d58318c-efcd-48b2-acaa-fb1e728711f7','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('be7d4fb4-68ce-4796-8836-c591fae76194','3778f4c0-2c67-479d-9dd2-4f84f696a1dc','Present',NULL,'213692c2-b361-4981-99cc-94303835e8a6','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('eb4f7b56-55a5-4862-9caa-9dd81d3c7129','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'243202e0-fa46-4c91-88b6-7971f09e2348','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('650b827e-af26-4ac5-ab99-211c63d417e9','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'269da9f9-b131-40a1-93cd-3277c4bc5b07','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('c6dd100f-47b2-486e-bd06-53896c82ff1f','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'2de08c26-7518-44ec-86a5-d4654cce0376','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f117bd48-4fc3-4aed-b653-44f8d3b881da','4823e6f0-69e2-4a1c-a0ff-1fb9653767d5','Present',NULL,'2fb7d29b-1222-4ec3-8904-8a5795e0001c','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('be452bdc-9831-4777-ba05-a06a19d5c65a','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'2fd9a102-773c-4bf9-8518-ab1cbfa992bb','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('e87455ec-06fb-4c45-bc3a-1d79aa65e6c4','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Absent',NULL,'3d6d7335-f19c-49c3-a1e8-27a74d2d1085','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('95468487-1e53-4ee8-944f-13e5bfac624d','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'3e0d3624-7861-407a-ae00-193db76026ee','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('576b764d-17ef-4b2c-a770-d637edd47b9b','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'46454ce1-cbc1-4df1-8d75-d36be194cdba','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('4de1c310-3dc9-459b-a8dc-7e0a137d7617','394ceb26-22f3-4d34-8881-53472e29ad43','Present',NULL,'46ecc936-27c6-4d02-bdbe-ac119409fc63','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('ede264b8-af90-4332-982c-02894319c935','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'484456df-2874-4c12-99d5-383185262d3e','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('5ccb1c37-19d9-45fc-8ceb-bf6ca3dc737d','13118271-a690-4bd5-a38b-4cc13334f292','Present',NULL,'4b12a34c-fd2a-41ff-8a27-3d8815075ac2','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f117bd48-4fc3-4aed-b653-44f8d3b881da','394ceb26-22f3-4d34-8881-53472e29ad43','Present',NULL,'4dfe8547-ff8b-472d-9f7f-8672008439b8','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('4de1c310-3dc9-459b-a8dc-7e0a137d7617','d4145bca-3b08-489a-a80d-c8141b3ce925','Present',NULL,'5154f8ff-c68d-44fb-b3f5-d8bb0bebed20','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('09b73780-ad95-4133-9b6c-6bffe7abbee7','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'566d5067-86e4-4163-aff5-b779c454f806','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('4b5b1e6b-5794-4362-89c6-0611bfd75372','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Late',NULL,'56fd0bb1-fad4-4951-8a0d-13164d01ce14','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('87a3d913-d76f-495a-8b47-27ae04622090','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'5beac33c-fdbb-4652-81c6-92037aa11878','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('10a37a49-fa0f-418d-b64d-8998264c370a','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'5eda2ecb-b939-4a1b-9a61-60dfb7da7028','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('d548ba24-ca29-4ffa-a1f4-eef69164882f','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'6070ef85-3b52-4a71-8007-3722ed277b29','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f4d2e939-c11f-4ad8-b930-67a8b2fefa4c','3778f4c0-2c67-479d-9dd2-4f84f696a1dc','Absent',NULL,'63080c0e-259e-4f62-a436-6ccd808f4db0','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('de31faf0-add0-4259-ab2a-9cfc32c88a99','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Absent',NULL,'638be7dd-b2c8-4f55-8040-156ea1fec938','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('3417aa8c-20d2-4d8b-81a8-33861f023249','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'639dfbc7-8295-45dd-b6d1-3925c8bf54df','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f4d2e939-c11f-4ad8-b930-67a8b2fefa4c','d4145bca-3b08-489a-a80d-c8141b3ce925','Present',NULL,'63ab235b-e60a-4fd8-86cc-87c1ce109c77','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('5ccb1c37-19d9-45fc-8ceb-bf6ca3dc737d','4823e6f0-69e2-4a1c-a0ff-1fb9653767d5','Present',NULL,'674475a8-2b11-46df-bae7-6a58d5d12cf9','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('3ea6d492-4af3-4ab8-8fbe-684c4c102b48','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'6c193c13-3e49-4d18-820f-dd5517f6374c','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('7745d8b2-03f8-4e2b-9e36-3e116c162793','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Absent',NULL,'72fabd7f-29bf-492f-8870-7879d312ca2b','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('5ccb1c37-19d9-45fc-8ceb-bf6ca3dc737d','d4145bca-3b08-489a-a80d-c8141b3ce925','Present',NULL,'812c982a-0fa1-4e5b-bcf2-cb34f533d0b4','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f117bd48-4fc3-4aed-b653-44f8d3b881da','d4145bca-3b08-489a-a80d-c8141b3ce925','Present',NULL,'88012c34-c473-4342-8003-56a4d07802a0','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f117bd48-4fc3-4aed-b653-44f8d3b881da','13118271-a690-4bd5-a38b-4cc13334f292','Present',NULL,'8c56bbbd-47f0-43df-bf0b-17aad1d5554d','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('3c94ceb9-cd6f-4bb1-8f2c-82ef5bb52ef3','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'8d49aee7-4276-438a-9db4-f3f22895ac4c','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('ed025196-535b-414b-b7e6-1c1f413aa5e7','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Late',NULL,'991ceba1-3ea2-4f60-bf2e-366db818bc00','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('5ccb1c37-19d9-45fc-8ceb-bf6ca3dc737d','394ceb26-22f3-4d34-8881-53472e29ad43','Present',NULL,'993c3238-0664-4c3d-9718-522416e84c7b','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('be7d4fb4-68ce-4796-8836-c591fae76194','4823e6f0-69e2-4a1c-a0ff-1fb9653767d5','Present',NULL,'9e6a83fb-12d4-4f48-84f0-27de6c989e80','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('4de1c310-3dc9-459b-a8dc-7e0a137d7617','13118271-a690-4bd5-a38b-4cc13334f292','Present',NULL,'9ec641b7-6bb2-494a-9a03-ef3eab15a27f','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('3093752e-0f55-4119-aff3-fde1ec03175d','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'9f24a541-8a88-41b8-ba70-b2420765a445','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('be7d4fb4-68ce-4796-8836-c591fae76194','d4145bca-3b08-489a-a80d-c8141b3ce925','Present',NULL,'a175c156-7be1-4135-b7fc-0ca9309898bb','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('ad38f371-5c90-47c1-9e44-cb52541bd8a9','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'a9aacaf6-fac0-4f40-8fec-a3dceee8ddf1','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('448846a1-d373-4dfe-ae99-baf75f11ddc5','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'aad53103-d334-41a1-be7c-701a9af435ad','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('b2ee1787-fbdd-4b1a-8015-2c90c2ebb731','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'ab024d0d-4f04-4511-b012-2c4203889fbe','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('be7d4fb4-68ce-4796-8836-c591fae76194','394ceb26-22f3-4d34-8881-53472e29ad43','Present',NULL,'ada5f876-86d6-4562-92ee-188171dc3a63','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('244cac4b-ae30-4660-83ae-cf94a36caca8','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Absent',NULL,'afb642ea-8a83-4b82-af32-5ac06e9d7624','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f4d2e939-c11f-4ad8-b930-67a8b2fefa4c','4823e6f0-69e2-4a1c-a0ff-1fb9653767d5','Present',NULL,'b94e8f3d-a837-4a33-abd3-c6487152025e','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('3834f5a3-137b-4710-9e9e-0541216d06fa','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'c6ad6093-1b5b-4a87-be0f-9922d241b226','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('4de1c310-3dc9-459b-a8dc-7e0a137d7617','3778f4c0-2c67-479d-9dd2-4f84f696a1dc','Present',NULL,'c826fad4-3221-4062-a0e3-3a1df0be961a','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('3cc7f023-6543-4952-a19b-3e74b695ff42','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'cd05a48b-82fe-48de-bed9-aee3faa75d93','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('46937068-4da4-4a1b-84e6-6b3c3b3bf157','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'cf0afc2e-dd1a-4ac1-b179-31c38c106504','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f1e4021b-58df-4ea1-a4eb-e180757b698b','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'d3b71dd1-d00d-4156-a0c5-48f8b19c189d','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('5ccb1c37-19d9-45fc-8ceb-bf6ca3dc737d','3778f4c0-2c67-479d-9dd2-4f84f696a1dc','Absent',NULL,'d836e022-4aef-414f-8178-37af53797a49','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('cc96c9cb-7755-46c7-a979-472cc52a94b3','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'dd89452b-95e1-40fc-a785-d226613547c8','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('ddefdd91-60c1-4e19-aaf8-481255858f12','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'deb4531b-adcc-4443-8fbe-ec203e0b0312','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f117bd48-4fc3-4aed-b653-44f8d3b881da','3778f4c0-2c67-479d-9dd2-4f84f696a1dc','Present',NULL,'e1655a83-ac7a-4ead-acfe-2a098576b731','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f4d2e939-c11f-4ad8-b930-67a8b2fefa4c','13118271-a690-4bd5-a38b-4cc13334f292','Present',NULL,'eac0cbfa-ed11-4171-9c62-2834535df7d2','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('98b5c8af-e0f9-44e5-983b-aa11c6b7ca32','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Absent',NULL,'edee7a96-8a2e-493a-85df-cf6de56ef1e4','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('a4069e7c-2642-4c5b-bafa-86f845dc3624','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Absent',NULL,'ee469155-764e-41d5-bcde-bf3eaf729980','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('68e4ce45-7c56-4c67-91e8-07000060b073','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Present',NULL,'ee91c5e2-18a0-46a5-a4db-1329f385c4ed','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f4d2e939-c11f-4ad8-b930-67a8b2fefa4c','394ceb26-22f3-4d34-8881-53472e29ad43','Present',NULL,'f7d1de4e-9fd6-49e5-a883-33f9e0c9c885','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0b9773b3-b062-4667-bb8b-99849e135f18','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','Absent',NULL,'fa2574f2-d564-4d7d-b510-bf8fcb7be473','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `attendance_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendance_sessions`
--

DROP TABLE IF EXISTS `attendance_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance_sessions` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `class_section_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `date` date NOT NULL,
  `submitted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `submitted_at` datetime NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `cancelled_at` datetime DEFAULT NULL,
  `cancelled_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `total_present` int DEFAULT NULL,
  `total_absent` int DEFAULT NULL,
  `total_late` int DEFAULT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_attendance_sessions_school_class_date_year` (`school_id`,`class_section_id`,`date`,`academic_year_id`),
  KEY `fk_attendance_sessions_academic_year_id_academic_years` (`academic_year_id`),
  KEY `idx_attendance_sessions_date` (`school_id`,`date`),
  KEY `idx_attendance_sessions_class_date` (`class_section_id`,`date`),
  KEY `idx_attendance_sessions_submitted_by` (`submitted_by`,`date`),
  KEY `ix_attendance_sessions_school_id` (`school_id`),
  KEY `ix_attendance_sessions_is_active` (`is_active`),
  CONSTRAINT `fk_attendance_sessions_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_attendance_sessions_class_section_id_class_sections` FOREIGN KEY (`class_section_id`) REFERENCES `class_sections` (`id`),
  CONSTRAINT `fk_attendance_sessions_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_attendance_sessions_submitted_by_staff` FOREIGN KEY (`submitted_by`) REFERENCES `staff` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance_sessions`
--

LOCK TABLES `attendance_sessions` WRITE;
/*!40000 ALTER TABLE `attendance_sessions` DISABLE KEYS */;
INSERT INTO `attendance_sessions` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-23','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'09b73780-ad95-4133-9b6c-6bffe7abbee7','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-21','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'0b9773b3-b062-4667-bb8b-99849e135f18','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-18','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'10a37a49-fa0f-418d-b64d-8998264c370a','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-04-17','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'244cac4b-ae30-4660-83ae-cf94a36caca8','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-15','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'3093752e-0f55-4119-aff3-fde1ec03175d','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-04','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'3417aa8c-20d2-4d8b-81a8-33861f023249','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-22','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'3834f5a3-137b-4710-9e9e-0541216d06fa','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-04-14','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'3c94ceb9-cd6f-4bb1-8f2c-82ef5bb52ef3','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-11','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'3cc7f023-6543-4952-a19b-3e74b695ff42','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-04-25','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'3ea6d492-4af3-4ab8-8fbe-684c4c102b48','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-20','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'448846a1-d373-4dfe-ae99-baf75f11ddc5','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-04-15','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'46937068-4da4-4a1b-84e6-6b3c3b3bf157','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-13','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'48538b46-e76a-4870-874f-fcd91cedfd5c','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-02','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'4b5b1e6b-5794-4362-89c6-0611bfd75372','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','2025-11-14','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','2025-11-14 09:00:00','Submitted',NULL,NULL,4,1,NULL,'4de1c310-3dc9-459b-a8dc-7e0a137d7617','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-04-18','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'576b764d-17ef-4b2c-a770-d637edd47b9b','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','2025-11-13','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','2025-11-13 09:00:00','Submitted',NULL,NULL,4,1,NULL,'5ccb1c37-19d9-45fc-8ceb-bf6ca3dc737d','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-26','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'650b827e-af26-4ac5-ab99-211c63d417e9','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-05','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'68e4ce45-7c56-4c67-91e8-07000060b073','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-04-13','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'7745d8b2-03f8-4e2b-9e36-3e116c162793','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-07','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'87a3d913-d76f-495a-8b47-27ae04622090','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-04-20','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'95468487-1e53-4ee8-944f-13e5bfac624d','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-25','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'98b5c8af-e0f9-44e5-983b-aa11c6b7ca32','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-04-29','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'a4069e7c-2642-4c5b-bafa-86f845dc3624','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-04-23','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'a99658bb-85d5-4c34-a324-e25a11206d96','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-16','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'ad38f371-5c90-47c1-9e44-cb52541bd8a9','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-06','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'ad45f275-38e3-4e79-9d73-f54f69be994f','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-04-16','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'b2ee1787-fbdd-4b1a-8015-2c90c2ebb731','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-04-22','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'be452bdc-9831-4777-ba05-a06a19d5c65a','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','2025-11-11','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','2025-11-11 09:00:00','Submitted',NULL,NULL,4,1,NULL,'be7d4fb4-68ce-4796-8836-c591fae76194','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-14','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'c6dd100f-47b2-486e-bd06-53896c82ff1f','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-04-27','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'cc96c9cb-7755-46c7-a979-472cc52a94b3','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-09','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'d548ba24-ca29-4ffa-a1f4-eef69164882f','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-19','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'d6434a17-9ccb-4c1c-aaa4-0a71cfc1a63d','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-12','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'ddefdd91-60c1-4e19-aaf8-481255858f12','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-04-24','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'de31faf0-add0-4259-ab2a-9cfc32c88a99','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-04-21','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'e87455ec-06fb-4c45-bc3a-1d79aa65e6c4','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-04-30','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'eb4f7b56-55a5-4862-9caa-9dd81d3c7129','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-01','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'ed025196-535b-414b-b7e6-1c1f413aa5e7','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-04-28','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'ede264b8-af90-4332-982c-02894319c935','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','2025-11-12','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','2025-11-12 09:00:00','Submitted',NULL,NULL,4,1,NULL,'f117bd48-4fc3-4aed-b653-44f8d3b881da','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','2026-05-08','2334c80d-0b88-4096-98ff-398bf9a88855','2026-05-26 23:48:55','Submitted',NULL,NULL,28,2,1,'f1e4021b-58df-4ea1-a4eb-e180757b698b','{}','2026-05-26 23:48:55','2026-05-26 23:48:55',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','2025-11-10','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','2025-11-10 09:00:00','Submitted',NULL,NULL,4,1,NULL,'f4d2e939-c11f-4ad8-b930-67a8b2fefa4c','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `attendance_sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awards`
--

DROP TABLE IF EXISTS `awards`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `awards` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `category` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `awarded_date` date DEFAULT NULL,
  `awarded_by` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `level` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `certificate_url` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `recorded_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_awards_academic_year_id_academic_years` (`academic_year_id`),
  KEY `fk_awards_recorded_by_staff` (`recorded_by`),
  KEY `ix_awards_school_id` (`school_id`),
  KEY `idx_awards_category` (`school_id`,`academic_year_id`,`category`),
  KEY `ix_awards_is_active` (`is_active`),
  KEY `idx_awards_student` (`student_id`,`academic_year_id`),
  CONSTRAINT `fk_awards_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_awards_recorded_by_staff` FOREIGN KEY (`recorded_by`) REFERENCES `staff` (`id`),
  CONSTRAINT `fk_awards_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_awards_student_id_students` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awards`
--

LOCK TABLES `awards` WRITE;
/*!40000 ALTER TABLE `awards` DISABLE KEYS */;
INSERT INTO `awards` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4823e6f0-69e2-4a1c-a0ff-1fb9653767d5','Best in Mathematics','Academic',NULL,'2025-10-15','Principal','School',NULL,NULL,'1a220993-86bd-4488-afbc-cfa5b3f406bf','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','d4145bca-3b08-489a-a80d-c8141b3ce925','Art Competition Winner','Cultural',NULL,'2025-09-20','Art Department','Inter-School',NULL,NULL,'7a8737c5-166c-4d41-a5ad-f5897e43a28f','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `awards` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `class_assignments`
--

DROP TABLE IF EXISTS `class_assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class_assignments` (
  `staff_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `class_section_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `subject_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_class_teacher` tinyint(1) NOT NULL,
  `periods_per_week` int DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `end_date` date DEFAULT NULL,
  `end_reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_class_assignments_unique` (`school_id`,`staff_id`,`class_section_id`,`subject_id`,`academic_year_id`),
  KEY `fk_class_assignments_subject_id_subjects` (`subject_id`),
  KEY `fk_class_assignments_academic_year_id_academic_years` (`academic_year_id`),
  KEY `idx_class_assignments_class_section` (`class_section_id`,`academic_year_id`),
  KEY `idx_class_assignments_staff` (`staff_id`,`academic_year_id`),
  KEY `ix_class_assignments_school_id` (`school_id`),
  KEY `ix_class_assignments_is_active` (`is_active`),
  CONSTRAINT `fk_class_assignments_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_class_assignments_class_section_id_class_sections` FOREIGN KEY (`class_section_id`) REFERENCES `class_sections` (`id`),
  CONSTRAINT `fk_class_assignments_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_class_assignments_staff_id_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`),
  CONSTRAINT `fk_class_assignments_subject_id_subjects` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class_assignments`
--

LOCK TABLES `class_assignments` WRITE;
/*!40000 ALTER TABLE `class_assignments` DISABLE KEYS */;
INSERT INTO `class_assignments` VALUES ('7794dcaf-e97c-41cb-83f8-c5ec057f8bd0','f29d33cd-bb3b-430f-be2d-e0496256915b','92d8d000-6478-4270-9a18-77b9d802885d','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',0,NULL,'Active',NULL,NULL,'024847ca-60f5-42ee-9fcc-217203790a8c','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('b1edfea4-d604-4f8c-959b-cdf713d21e84','856f3425-69b3-44e4-a291-8f6b604441d4','5ca31131-7785-451f-a040-447944567741','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',0,NULL,'Active',NULL,NULL,'2992e193-4785-48e1-8a03-f1ea45abaffa','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('65401672-19ab-4e98-9fa7-6d58e899d261','4d085a47-3bb2-45e5-a900-e90dd767b0c7','a193e74b-557e-4898-8917-7781724a24b9','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',0,NULL,'Active',NULL,NULL,'4e357bcd-0132-4b52-9e01-26e529806242','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('d99413b6-624f-4d3d-ba74-7dbee9fac4c1','856f3425-69b3-44e4-a291-8f6b604441d4','890c0072-03e5-4611-a4e2-ab73f0034dc4','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',0,NULL,'Active',NULL,NULL,'5f1c36f4-f0ab-4b34-bb2e-868289cdaa7c','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('d99413b6-624f-4d3d-ba74-7dbee9fac4c1','8f4911ac-187b-41a2-8866-1fc178a4343d','890c0072-03e5-4611-a4e2-ab73f0034dc4','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',0,NULL,'Active',NULL,NULL,'72eabded-1d55-4327-b309-26eec937cda1','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('7794dcaf-e97c-41cb-83f8-c5ec057f8bd0','8f4911ac-187b-41a2-8866-1fc178a4343d','92d8d000-6478-4270-9a18-77b9d802885d','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',0,NULL,'Active',NULL,NULL,'78b61f27-eb17-4bcc-922f-491119860b6f','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f0bc267d-4453-40bf-9bcf-f3c888fcb48c','856f3425-69b3-44e4-a291-8f6b604441d4','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',0,NULL,'Active',NULL,NULL,'9ebda202-6ceb-41d3-9a00-baaf097ad896','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('65401672-19ab-4e98-9fa7-6d58e899d261','954300c6-bda4-498b-998f-c14d7ecdd53d','a193e74b-557e-4898-8917-7781724a24b9','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',0,NULL,'Active',NULL,NULL,'a8be1000-658f-4d62-a094-796c60d2e8d1','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('8b90d86f-8442-4425-9d1e-475c9f879aa2','4d085a47-3bb2-45e5-a900-e90dd767b0c7','4daac19b-24a9-41e8-917e-1e9f2192c8aa','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',0,NULL,'Active',NULL,NULL,'b96908fd-b01a-4e6a-af37-4df49d28d0c7','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('b1edfea4-d604-4f8c-959b-cdf713d21e84','7e50dbc3-27ea-4be6-bc04-c4c29525b4f5','5ca31131-7785-451f-a040-447944567741','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',0,NULL,'Active',NULL,NULL,'bba3e7dd-f353-4804-8e34-8d0a137b43d4','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('8b90d86f-8442-4425-9d1e-475c9f879aa2','954300c6-bda4-498b-998f-c14d7ecdd53d','4daac19b-24a9-41e8-917e-1e9f2192c8aa','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',0,NULL,'Active',NULL,NULL,'d464f3be-6208-49eb-a557-bc67704640f6','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f0bc267d-4453-40bf-9bcf-f3c888fcb48c','856f3425-69b3-44e4-a291-8f6b604441d4','92d8d000-6478-4270-9a18-77b9d802885d','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',0,NULL,'Active',NULL,NULL,'d8b59f3e-976f-4e12-9d8b-e7b46d172cd8','{}','2026-05-27 09:16:50','2026-05-27 09:16:50',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f0bc267d-4453-40bf-9bcf-f3c888fcb48c','8f4911ac-187b-41a2-8866-1fc178a4343d','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',1,NULL,'Active',NULL,NULL,'e974658b-226b-44a4-a799-22e7aec7d205','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f0bc267d-4453-40bf-9bcf-f3c888fcb48c','4d085a47-3bb2-45e5-a900-e90dd767b0c7','3d785786-e000-4d52-8387-d4aa0486027c','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',1,NULL,'Active',NULL,NULL,'f146c453-b604-4547-96f4-9500ffc4ef83','{}','2026-05-27 09:16:50','2026-05-27 09:16:50',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f0bc267d-4453-40bf-9bcf-f3c888fcb48c','7e50dbc3-27ea-4be6-bc04-c4c29525b4f5','4daac19b-24a9-41e8-917e-1e9f2192c8aa','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',0,NULL,'Active',NULL,NULL,'fd91c777-def6-45ae-985e-04096fd5c80d','{}','2026-05-27 09:16:50','2026-05-27 09:16:50',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `class_assignments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `class_sections`
--

DROP TABLE IF EXISTS `class_sections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class_sections` (
  `class_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `section_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_class_sections_school_class_section_year` (`school_id`,`class_id`,`section_id`,`academic_year_id`),
  KEY `fk_class_sections_class_id_classes` (`class_id`),
  KEY `fk_class_sections_section_id_sections` (`section_id`),
  KEY `fk_class_sections_academic_year_id_academic_years` (`academic_year_id`),
  KEY `ix_class_sections_school_id` (`school_id`),
  KEY `ix_class_sections_is_active` (`is_active`),
  CONSTRAINT `fk_class_sections_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_class_sections_class_id_classes` FOREIGN KEY (`class_id`) REFERENCES `classes` (`id`),
  CONSTRAINT `fk_class_sections_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_class_sections_section_id_sections` FOREIGN KEY (`section_id`) REFERENCES `sections` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class_sections`
--

LOCK TABLES `class_sections` WRITE;
/*!40000 ALTER TABLE `class_sections` DISABLE KEYS */;
INSERT INTO `class_sections` VALUES ('382a6692-bce1-4fc8-8e5f-c30e5faef94c','ce323069-ae19-44d7-90ae-20dc4b41fe4d','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('20557ed7-8069-4798-8f5e-a50d785c61c7','945545a5-0cec-407c-a39d-fa99806525d2','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','7e50dbc3-27ea-4be6-bc04-c4c29525b4f5','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('20557ed7-8069-4798-8f5e-a50d785c61c7','ce323069-ae19-44d7-90ae-20dc4b41fe4d','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('9f687a1f-5d17-4c16-b9d5-38ea01b72bc5','ce323069-ae19-44d7-90ae-20dc4b41fe4d','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('382a6692-bce1-4fc8-8e5f-c30e5faef94c','945545a5-0cec-407c-a39d-fa99806525d2','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','954300c6-bda4-498b-998f-c14d7ecdd53d','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('9f687a1f-5d17-4c16-b9d5-38ea01b72bc5','945545a5-0cec-407c-a39d-fa99806525d2','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','f29d33cd-bb3b-430f-be2d-e0496256915b','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `class_sections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classes`
--

DROP TABLE IF EXISTS `classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `classes` (
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `display_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sort_order` int NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `max_periods` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_classes_school_name` (`school_id`,`name`),
  KEY `ix_classes_is_active` (`is_active`),
  KEY `ix_classes_school_id` (`school_id`),
  CONSTRAINT `fk_classes_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classes`
--

LOCK TABLES `classes` WRITE;
/*!40000 ALTER TABLE `classes` DISABLE KEYS */;
INSERT INTO `classes` VALUES ('7','Class 7',7,'1147da6e-5061-4b2f-819d-d496187b3fe8','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9',NULL),('4','Class 4',4,'1cc3aca5-d683-4780-ae53-6e96c4e79821','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9',NULL),('9','Class 9',9,'20557ed7-8069-4798-8f5e-a50d785c61c7','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9',NULL),('10','Class 10',10,'382a6692-bce1-4fc8-8e5f-c30e5faef94c','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9',NULL),('5','Class 5',5,'482e7e01-7c10-4d10-bf49-0000d48b47c6','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9',NULL),('3','Class 3',3,'6f1d57aa-dc62-4777-b4d2-ddb3797cdd9e','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9',NULL),('8','Class 8',8,'9f687a1f-5d17-4c16-b9d5-38ea01b72bc5','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9',NULL),('1','Class 1',1,'ef509764-d628-4c1b-bd20-29aeb7606d84','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9',NULL),('2','Class 2',2,'f1016cdf-4518-4307-95e5-05e7fc41f02e','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9',NULL),('6','Class 6',6,'f55b7b18-39af-4520-979b-eef1ed3944f9','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9',NULL);
/*!40000 ALTER TABLE `classes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `disciplinary_records`
--

DROP TABLE IF EXISTS `disciplinary_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `disciplinary_records` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `incident_date` date NOT NULL,
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `severity` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_taken` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `reported_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `parent_notified` tinyint(1) NOT NULL,
  `parent_notified_date` date DEFAULT NULL,
  `follow_up_date` date DEFAULT NULL,
  `follow_up_notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_disciplinary_records_academic_year_id_academic_years` (`academic_year_id`),
  KEY `fk_disciplinary_records_reported_by_staff` (`reported_by`),
  KEY `ix_disciplinary_records_is_active` (`is_active`),
  KEY `idx_disciplinary_date` (`school_id`,`incident_date`),
  KEY `idx_disciplinary_status` (`school_id`,`academic_year_id`,`status`),
  KEY `ix_disciplinary_records_school_id` (`school_id`),
  KEY `idx_disciplinary_student` (`student_id`,`academic_year_id`),
  CONSTRAINT `fk_disciplinary_records_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_disciplinary_records_reported_by_staff` FOREIGN KEY (`reported_by`) REFERENCES `staff` (`id`),
  CONSTRAINT `fk_disciplinary_records_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_disciplinary_records_student_id_students` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `disciplinary_records`
--

LOCK TABLES `disciplinary_records` WRITE;
/*!40000 ALTER TABLE `disciplinary_records` DISABLE KEYS */;
INSERT INTO `disciplinary_records` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','3778f4c0-2c67-479d-9dd2-4f84f696a1dc','2025-10-05','Misconduct','Low','Talking during class','Verbal warning','f0bc267d-4453-40bf-9bcf-f3c888fcb48c',0,NULL,NULL,NULL,'Resolved','85daf83f-3cb6-4747-90de-3328f8b583f4','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `disciplinary_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `drivers`
--

DROP TABLE IF EXISTS `drivers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drivers` (
  `driver_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `license_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `license_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `license_expiry` date DEFAULT NULL,
  `experience_years` int DEFAULT NULL,
  `join_date` date DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Available',
  `emergency_contact_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `emergency_contact_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_drivers_school_driver_id` (`school_id`,`driver_id`),
  KEY `idx_drivers_status` (`school_id`,`status`),
  KEY `ix_drivers_school_id` (`school_id`),
  KEY `ix_drivers_is_active` (`is_active`),
  CONSTRAINT `fk_drivers_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drivers`
--

LOCK TABLES `drivers` WRITE;
/*!40000 ALTER TABLE `drivers` DISABLE KEYS */;
INSERT INTO `drivers` VALUES ('DRV003','Driver 3','+91-990000002',NULL,'KA0120250002','Heavy Vehicle',NULL,NULL,NULL,'Available',NULL,NULL,'0d3886d3-059e-4ec1-a0a6-92f57bb4efda','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('DRV002','Driver 2','+91-990000001',NULL,'KA0120250001','Heavy Vehicle',NULL,NULL,NULL,'Available',NULL,NULL,'3a68afc3-c0c2-4310-9efd-f075e98a327e','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('DRV006','Vamsi','7897890789',NULL,'1234','Heavy Vehicle',NULL,NULL,NULL,'Inactive',NULL,NULL,'bb12a69c-19ef-4c9e-aecd-b2b067b9e217','{}','2026-05-26 21:28:53','2026-05-26 21:42:59',0,'2026-05-26 16:13:00','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('DRV005','harsha','9898989899',NULL,'12345678','Heavy Vehicle','2026-05-13',NULL,NULL,'Active',NULL,NULL,'c7d9ef94-ac6d-4ab8-a4e6-7abd6a4ce391','{}','2026-05-24 13:36:20','2026-05-24 13:50:08',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('DRV008','Ravi','6786786789',NULL,'11212','Light Vehicle',NULL,0,NULL,'Available',NULL,NULL,'d14f0b4f-0c85-4741-bbf1-47d526f126bc','{}','2026-05-26 21:43:38','2026-05-26 21:43:38',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('DRV004','Vamsi','7893444336',NULL,'TS123456','Transport','2026-05-21',NULL,NULL,'Available',NULL,NULL,'da0a3836-4b89-470a-8f90-58c9426b78bc','{}','2026-05-24 13:30:04','2026-05-24 13:30:04',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('DRV007','driver2','1289128912',NULL,'120120','Light Vehicle',NULL,NULL,NULL,'Inactive',NULL,NULL,'de81833e-570b-4050-a0fc-fbf121415d08','{}','2026-05-26 21:31:30','2026-05-26 21:42:58',0,'2026-05-26 16:12:59','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('DRV001','Driver 1','+91-990000000',NULL,'KA0120250000','Heavy Vehicle',NULL,NULL,NULL,'Available',NULL,NULL,'e00b70b8-51d7-476d-b732-8d72ca5ef3ec','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `drivers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enum_configs`
--

DROP TABLE IF EXISTS `enum_configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enum_configs` (
  `category` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `label` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_order` int NOT NULL,
  `config` json NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_enum_configs_school_cat_val` (`school_id`,`category`,`value`),
  KEY `ix_enum_configs_is_active` (`is_active`),
  KEY `ix_enum_configs_school_id` (`school_id`),
  CONSTRAINT `fk_enum_configs_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enum_configs`
--

LOCK TABLES `enum_configs` WRITE;
/*!40000 ALTER TABLE `enum_configs` DISABLE KEYS */;
INSERT INTO `enum_configs` VALUES ('leave_type','Sick Leave','Sick Leave',4,'{}','0b249bec-1e0d-4e8d-8a3b-09438db0a334','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('leave_type','Casual Leave','Casual Leave',3,'{}','49921a31-d607-4ad7-aa57-12fd79554ad7','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('leave_type','Earned Leave','Earned Leave',5,'{}','63848d32-95f2-4852-9d71-2de4b68d586d','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('fee_type','Transport Fee','Transport Fee',2,'{}','78be0520-1e10-4952-9408-cc69eced7994','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('fee_type','Tuition Fee','Tuition Fee',0,'{}','7af26297-db8d-4668-bec3-8ac267ffe3c6','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('fee_type','Lab Fee','Lab Fee',1,'{}','95d905e7-9d42-44de-ad34-e63d934cf94e','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `enum_configs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_results`
--

DROP TABLE IF EXISTS `exam_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_results` (
  `exam_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `marks_obtained` decimal(6,2) DEFAULT NULL,
  `grade` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rank` int DEFAULT NULL,
  `attendance` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `is_pass` tinyint(1) DEFAULT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_exam_results_school_exam_student` (`school_id`,`exam_id`,`student_id`),
  KEY `idx_exam_results_student` (`student_id`),
  KEY `ix_exam_results_school_id` (`school_id`),
  KEY `idx_exam_results_grade` (`exam_id`,`grade`),
  KEY `ix_exam_results_is_active` (`is_active`),
  KEY `idx_exam_results_exam` (`exam_id`,`rank`),
  CONSTRAINT `fk_exam_results_exam_id_exams` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_exam_results_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_exam_results_student_id_students` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_results`
--

LOCK TABLES `exam_results` WRITE;
/*!40000 ALTER TABLE `exam_results` DISABLE KEYS */;
INSERT INTO `exam_results` VALUES ('0c81f59b-5047-4888-bce2-4140249c5f31','13118271-a690-4bd5-a38b-4cc13334f292',79.00,'B1',3,'Present',NULL,1,'096e2c39-1ec1-4ebe-a1f9-81c1cdf5b6da','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0c81f59b-5047-4888-bce2-4140249c5f31','d4145bca-3b08-489a-a80d-c8141b3ce925',72.00,'B1',2,'Present',NULL,1,'15e41c53-8cd1-4806-b99c-9a02a24c2b5b','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('ec775ab8-8210-4059-9baa-e84aa7831ff8','0ede033b-39d9-43c3-83d7-f8eb6e0cc230',39.00,'B+',5,'Present',NULL,1,'1c6a3d41-4667-4033-81cc-1928b7894968','{}','2026-05-27 00:15:46','2026-05-27 00:15:46',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('643d2565-56d9-4e46-b023-8b21ba7a34e2','0ede033b-39d9-43c3-83d7-f8eb6e0cc230',78.00,'B+',5,'Present',NULL,1,'61d6153e-3d6a-4b08-8af3-08c62db857c0','{}','2026-05-27 00:15:46','2026-05-27 00:15:46',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0c81f59b-5047-4888-bce2-4140249c5f31','394ceb26-22f3-4d34-8881-53472e29ad43',86.00,'A2',4,'Present',NULL,1,'ab7bf3ac-aa88-4dbe-a2e6-a78d38593ac7','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0c81f59b-5047-4888-bce2-4140249c5f31','4823e6f0-69e2-4a1c-a0ff-1fb9653767d5',65.00,'B2',1,'Present',NULL,1,'b58c68b7-70e5-4943-9316-00dd36acb00a','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0c81f59b-5047-4888-bce2-4140249c5f31','3778f4c0-2c67-479d-9dd2-4f84f696a1dc',93.00,'A2',5,'Present',NULL,1,'cc5518d0-e194-440e-b126-d251f1a027af','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `exam_results` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exams`
--

DROP TABLE IF EXISTS `exams`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exams` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `exam_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `class_section_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `subject_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `date` date DEFAULT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `total_marks` decimal(6,2) NOT NULL,
  `passing_marks` decimal(6,2) DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `examiner_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `term` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `published_at` datetime DEFAULT NULL,
  `cancelled_at` datetime DEFAULT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_exams_academic_year_id_academic_years` (`academic_year_id`),
  KEY `fk_exams_examiner_id_staff` (`examiner_id`),
  KEY `idx_exams_date` (`school_id`,`date`),
  KEY `idx_exams_status` (`school_id`,`academic_year_id`,`status`),
  KEY `idx_exams_type` (`school_id`,`academic_year_id`,`exam_type`),
  KEY `ix_exams_is_active` (`is_active`),
  KEY `ix_exams_school_id` (`school_id`),
  KEY `idx_exams_class_year` (`class_section_id`,`academic_year_id`),
  KEY `idx_exams_subject` (`subject_id`,`academic_year_id`),
  CONSTRAINT `fk_exams_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_exams_class_section_id_class_sections` FOREIGN KEY (`class_section_id`) REFERENCES `class_sections` (`id`),
  CONSTRAINT `fk_exams_examiner_id_staff` FOREIGN KEY (`examiner_id`) REFERENCES `staff` (`id`),
  CONSTRAINT `fk_exams_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_exams_subject_id_subjects` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exams`
--

LOCK TABLES `exams` WRITE;
/*!40000 ALTER TABLE `exams` DISABLE KEYS */;
INSERT INTO `exams` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Mid-Term Math','Mid-Term','8f4911ac-187b-41a2-8866-1fc178a4343d','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','2025-10-15','09:00:00','12:00:00',100.00,33.00,'Published','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','Term 1','2025-10-20 10:00:00',NULL,'0c81f59b-5047-4888-bce2-4140249c5f31','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Final Examination','Final','4d085a47-3bb2-45e5-a900-e90dd767b0c7','92d8d000-6478-4270-9a18-77b9d802885d','2026-06-11',NULL,NULL,100.00,35.00,'Scheduled','2334c80d-0b88-4096-98ff-398bf9a88855',NULL,NULL,NULL,'41838246-35f5-4c3b-8675-1dff11d70c98','{}','2026-05-27 00:15:46','2026-05-27 00:15:46',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Mid-Term Science','Mid-Term','856f3425-69b3-44e4-a291-8f6b604441d4','5ca31131-7785-451f-a040-447944567741','2025-10-15','09:00:00','12:00:00',100.00,33.00,'Published','b1edfea4-d604-4f8c-959b-cdf713d21e84','Term 1','2025-10-20 10:00:00',NULL,'4c6ea696-4c0c-498e-bc59-8ef82da3d89c','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Mid term','Unit Test','954300c6-bda4-498b-998f-c14d7ecdd53d','92d8d000-6478-4270-9a18-77b9d802885d','2026-05-08','12:00:00','03:00:00',95.00,NULL,'Draft',NULL,NULL,NULL,NULL,'60b1b9b7-1686-4dd5-90d6-69d41e172019','{}','2026-05-24 15:18:25','2026-05-24 15:33:50',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Mid-Term Examination','Mid-Term','4d085a47-3bb2-45e5-a900-e90dd767b0c7','3d785786-e000-4d52-8387-d4aa0486027c','2026-04-27',NULL,NULL,100.00,35.00,'Published','2334c80d-0b88-4096-98ff-398bf9a88855',NULL,NULL,NULL,'643d2565-56d9-4e46-b023-8b21ba7a34e2','{}','2026-05-27 00:15:46','2026-05-27 00:15:46',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Mid-Term English','Mid-Term','8f4911ac-187b-41a2-8866-1fc178a4343d','92d8d000-6478-4270-9a18-77b9d802885d','2025-10-15','09:00:00','12:00:00',100.00,33.00,'Published','7794dcaf-e97c-41cb-83f8-c5ec057f8bd0','Term 1','2025-10-20 10:00:00',NULL,'a2ee1a48-22bb-4327-aa3b-54424e85725c','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Unit Test 1','Unit Test','4d085a47-3bb2-45e5-a900-e90dd767b0c7','4daac19b-24a9-41e8-917e-1e9f2192c8aa','2026-03-28',NULL,NULL,50.00,17.00,'Published','2334c80d-0b88-4096-98ff-398bf9a88855',NULL,NULL,NULL,'ec775ab8-8210-4059-9baa-e84aa7831ff8','{}','2026-05-27 00:15:46','2026-05-27 00:15:46',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `exams` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fee_payments`
--

DROP TABLE IF EXISTS `fee_payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fee_payments` (
  `fee_record_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_date` date NOT NULL,
  `payment_method` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `reference` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `recorded_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_fee_payments_recorded_by_users` (`recorded_by`),
  KEY `ix_fee_payments_is_active` (`is_active`),
  KEY `idx_fee_payments_student` (`school_id`,`fee_record_id`),
  KEY `idx_fee_payments_date` (`school_id`,`payment_date`),
  KEY `ix_fee_payments_school_id` (`school_id`),
  KEY `idx_fee_payments_record` (`fee_record_id`),
  CONSTRAINT `fk_fee_payments_fee_record_id_fee_records` FOREIGN KEY (`fee_record_id`) REFERENCES `fee_records` (`id`),
  CONSTRAINT `fk_fee_payments_recorded_by_users` FOREIGN KEY (`recorded_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_fee_payments_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fee_payments`
--

LOCK TABLES `fee_payments` WRITE;
/*!40000 ALTER TABLE `fee_payments` DISABLE KEYS */;
INSERT INTO `fee_payments` VALUES ('79ecb344-c6d3-4a1d-ad98-c555af509d95',5000.00,'2025-11-07','Online','TXN1002',NULL,'3feb7c9a-6801-42e7-87e4-4cdf0a37a2d1','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('a2d12467-e3ec-414e-948c-426d2c74f0d4',5000.00,'2025-11-06','Online','TXN1001',NULL,'97c6865d-4f7a-4cd8-bda0-23eed1ede5a2','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('34aef52d-a34c-4d5d-96c8-76945d53cb53',5000.00,'2025-11-05','Online','TXN1000',NULL,'cd676c34-1348-4cdf-b7f4-82231fcd101b','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `fee_payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fee_penalties`
--

DROP TABLE IF EXISTS `fee_penalties`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fee_penalties` (
  `fee_record_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `penalty_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `percentage` decimal(5,2) DEFAULT NULL,
  `applied_on` datetime NOT NULL,
  `applied_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_fee_penalties_applied_by_users` (`applied_by`),
  KEY `idx_fee_penalties_record` (`fee_record_id`),
  KEY `ix_fee_penalties_is_active` (`is_active`),
  KEY `ix_fee_penalties_school_id` (`school_id`),
  KEY `idx_fee_penalties_date` (`school_id`,`applied_on`),
  CONSTRAINT `fk_fee_penalties_applied_by_users` FOREIGN KEY (`applied_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_fee_penalties_fee_record_id_fee_records` FOREIGN KEY (`fee_record_id`) REFERENCES `fee_records` (`id`),
  CONSTRAINT `fk_fee_penalties_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fee_penalties`
--

LOCK TABLES `fee_penalties` WRITE;
/*!40000 ALTER TABLE `fee_penalties` DISABLE KEYS */;
INSERT INTO `fee_penalties` VALUES ('a9fa225b-3a7c-4bf2-9b8b-4543c5624820','fixed',100.00,NULL,'2026-05-26 17:18:21','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','59eaf94f-03f1-45c9-ab56-dce34a51834e','{}','2026-05-26 22:48:20','2026-05-26 22:48:20',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('c63c4c27-55ad-4859-bb07-0f354c5ef6a6','Late Fee',100.00,NULL,'2025-11-15 10:00:00','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','84d4038f-e7ea-43c1-85cd-b3e3476bf88b','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('c63c4c27-55ad-4859-bb07-0f354c5ef6a6','fixed',100.00,NULL,'2026-05-26 17:18:21','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','8b21c683-a080-496a-b6aa-98cc6d6ec10a','{}','2026-05-26 22:48:20','2026-05-26 22:48:20',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('a9fa225b-3a7c-4bf2-9b8b-4543c5624820','Late Fee',100.00,NULL,'2025-11-15 10:00:00','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','a8688577-bd66-4da6-8afd-b2414675d29b','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('c63c4c27-55ad-4859-bb07-0f354c5ef6a6','fixed',100.00,NULL,'2026-05-26 17:18:49','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','b76e6de0-dfc4-478f-8fca-4fad88163c08','{}','2026-05-26 22:48:49','2026-05-26 22:48:49',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('a9fa225b-3a7c-4bf2-9b8b-4543c5624820','fixed',100.00,NULL,'2026-05-26 17:18:49','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','f369dd58-804f-4a01-91ce-dc2b25b7d2c3','{}','2026-05-26 22:48:49','2026-05-26 22:48:49',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `fee_penalties` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fee_records`
--

DROP TABLE IF EXISTS `fee_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fee_records` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `fee_structure_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fee_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `fee_category` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `paid` decimal(10,2) NOT NULL,
  `pending` decimal(10,2) NOT NULL,
  `total_late_fee` decimal(10,2) NOT NULL,
  `due_date` date NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_fee_records_academic_year_id_academic_years` (`academic_year_id`),
  KEY `fk_fee_records_fee_structure_id_fee_structures` (`fee_structure_id`),
  KEY `ix_fee_records_school_id` (`school_id`),
  KEY `ix_fee_records_is_active` (`is_active`),
  KEY `idx_fee_records_due_date` (`school_id`,`due_date`),
  KEY `idx_fee_records_student` (`student_id`,`academic_year_id`),
  KEY `idx_fee_records_fee_type` (`school_id`,`academic_year_id`,`fee_type`),
  KEY `idx_fee_records_status` (`school_id`,`academic_year_id`,`status`),
  CONSTRAINT `fk_fee_records_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_fee_records_fee_structure_id_fee_structures` FOREIGN KEY (`fee_structure_id`) REFERENCES `fee_structures` (`id`),
  CONSTRAINT `fk_fee_records_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_fee_records_student_id_students` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fee_records`
--

LOCK TABLES `fee_records` WRITE;
/*!40000 ALTER TABLE `fee_records` DISABLE KEYS */;
INSERT INTO `fee_records` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4823e6f0-69e2-4a1c-a0ff-1fb9653767d5','df0653d6-3df7-4b8c-87d9-61969afd65dd','Tuition Fee','academic',5000.00,5000.00,0.00,0.00,'2025-11-10','Paid',NULL,'34aef52d-a34c-4d5d-96c8-76945d53cb53','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','13118271-a690-4bd5-a38b-4cc13334f292','df0653d6-3df7-4b8c-87d9-61969afd65dd','Tuition Fee','academic',5000.00,5000.00,0.00,0.00,'2025-11-10','Paid',NULL,'79ecb344-c6d3-4a1d-ad98-c555af509d95','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','d4145bca-3b08-489a-a80d-c8141b3ce925','df0653d6-3df7-4b8c-87d9-61969afd65dd','Tuition Fee','academic',5000.00,5000.00,0.00,0.00,'2025-11-10','Paid',NULL,'a2d12467-e3ec-414e-948c-426d2c74f0d4','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','394ceb26-22f3-4d34-8881-53472e29ad43','df0653d6-3df7-4b8c-87d9-61969afd65dd','Tuition Fee','academic',5000.00,0.00,5200.00,200.00,'2025-11-10','Overdue',NULL,'a9fa225b-3a7c-4bf2-9b8b-4543c5624820','{}','2026-05-24 12:11:35','2026-05-26 22:48:49',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','3778f4c0-2c67-479d-9dd2-4f84f696a1dc','df0653d6-3df7-4b8c-87d9-61969afd65dd','Tuition Fee','academic',5000.00,0.00,5200.00,200.00,'2025-11-10','Overdue',NULL,'c63c4c27-55ad-4859-bb07-0f354c5ef6a6','{}','2026-05-24 12:11:35','2026-05-26 22:48:49',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `fee_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fee_reminders`
--

DROP TABLE IF EXISTS `fee_reminders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fee_reminders` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `target_group` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `class_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `section` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `send_via` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sent_to_count` int NOT NULL,
  `sent_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sent_at` datetime NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_fee_reminders_academic_year_id_academic_years` (`academic_year_id`),
  KEY `fk_fee_reminders_sent_by_users` (`sent_by`),
  KEY `idx_fee_reminders_year` (`school_id`,`academic_year_id`),
  KEY `ix_fee_reminders_school_id` (`school_id`),
  KEY `ix_fee_reminders_is_active` (`is_active`),
  KEY `idx_fee_reminders_sent` (`school_id`,`sent_at`),
  CONSTRAINT `fk_fee_reminders_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_fee_reminders_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_fee_reminders_sent_by_users` FOREIGN KEY (`sent_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fee_reminders`
--

LOCK TABLES `fee_reminders` WRITE;
/*!40000 ALTER TABLE `fee_reminders` DISABLE KEYS */;
INSERT INTO `fee_reminders` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Overdue',NULL,NULL,'This is a reminder that your fee payment is overdue. Please clear the dues at the earliest.','in_app',5,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','2026-05-26 17:12:25','4bc1f518-b5ea-42d1-b02b-df8bc117291b','{}','2026-05-26 22:42:24','2026-05-26 22:42:24',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Selected',NULL,NULL,'This is a reminder that your fee payment is overdue. Please clear the dues at the earliest.','in_app',5,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','2026-05-26 17:15:47','9ad0f040-a885-4332-bfdd-19cd303b64ae','{}','2026-05-26 22:45:47','2026-05-26 22:45:47',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','class','8','A','Please pay pending fees by Nov 30.','in_app',5,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','2025-11-12 09:00:00','e0cf0a98-0069-41f7-936f-ba1326cb4d3f','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `fee_reminders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fee_structures`
--

DROP TABLE IF EXISTS `fee_structures`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fee_structures` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `class_section_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fee_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `fee_category` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `frequency` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_fee_structures_year_class_type` (`school_id`,`academic_year_id`,`class_section_id`,`fee_type`),
  KEY `fk_fee_structures_academic_year_id_academic_years` (`academic_year_id`),
  KEY `ix_fee_structures_is_active` (`is_active`),
  KEY `idx_fee_structures_year` (`school_id`,`academic_year_id`),
  KEY `ix_fee_structures_school_id` (`school_id`),
  KEY `idx_fee_structures_class` (`class_section_id`,`academic_year_id`),
  CONSTRAINT `fk_fee_structures_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_fee_structures_class_section_id_class_sections` FOREIGN KEY (`class_section_id`) REFERENCES `class_sections` (`id`),
  CONSTRAINT `fk_fee_structures_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fee_structures`
--

LOCK TABLES `fee_structures` WRITE;
/*!40000 ALTER TABLE `fee_structures` DISABLE KEYS */;
INSERT INTO `fee_structures` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','Lab Fee','academic',2000.00,'Quarterly','62a6216c-4fd2-432f-9363-1d58fa0a1df6','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','Transport Fee','transport',3000.00,'Monthly','7f3cf268-1263-4094-83ac-9a76ce07b91f','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','Tuition Fee','academic',5000.00,'Monthly','df0653d6-3df7-4b8c-87d9-61969afd65dd','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `fee_structures` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grade_scales`
--

DROP TABLE IF EXISTS `grade_scales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grade_scales` (
  `grade_system_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `grade` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `min_percentage` decimal(5,2) NOT NULL,
  `max_percentage` decimal(5,2) NOT NULL,
  `grade_point` decimal(3,1) DEFAULT NULL,
  `description` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sort_order` int NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_grade_scales_system_grade` (`school_id`,`grade_system_id`,`grade`),
  KEY `idx_grade_scales_system` (`grade_system_id`,`sort_order`),
  KEY `ix_grade_scales_school_id` (`school_id`),
  KEY `ix_grade_scales_is_active` (`is_active`),
  CONSTRAINT `fk_grade_scales_grade_system_id_grade_systems` FOREIGN KEY (`grade_system_id`) REFERENCES `grade_systems` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_grade_scales_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grade_scales`
--

LOCK TABLES `grade_scales` WRITE;
/*!40000 ALTER TABLE `grade_scales` DISABLE KEYS */;
INSERT INTO `grade_scales` VALUES ('17d88271-7f52-46be-a540-af06e32f3eac','C1',51.00,60.00,6.0,NULL,4,'166f91a5-6a74-4b3b-b1d8-e0a491bbe59a','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('17d88271-7f52-46be-a540-af06e32f3eac','B2',61.00,70.00,7.0,NULL,3,'1ed374ba-7547-45ac-bf60-b4acdb2778ca','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('17d88271-7f52-46be-a540-af06e32f3eac','A2',81.00,90.00,9.0,NULL,1,'2cebcfbb-0968-41ce-8408-60a20108b73d','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('17d88271-7f52-46be-a540-af06e32f3eac','E',0.00,32.00,0.0,NULL,7,'8a0a1e24-c0f2-416b-9272-234ee82e2f06','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('17d88271-7f52-46be-a540-af06e32f3eac','B1',71.00,80.00,8.0,NULL,2,'ac05acb2-1602-4363-ad3e-efe83d7937cb','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('17d88271-7f52-46be-a540-af06e32f3eac','D',33.00,40.00,4.0,NULL,6,'ad177b37-5220-4bfc-802b-26a2d9d6e199','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('17d88271-7f52-46be-a540-af06e32f3eac','A1',91.00,100.00,10.0,NULL,0,'ccf77fca-2ea3-4483-be90-cc6b63fc53b9','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('17d88271-7f52-46be-a540-af06e32f3eac','C2',41.00,50.00,5.0,NULL,5,'cd89d490-05e9-47a3-b9d6-32696c3b6052','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `grade_scales` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grade_systems`
--

DROP TABLE IF EXISTS `grade_systems`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grade_systems` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_default` tinyint(1) NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_grade_systems_school_name` (`school_id`,`name`),
  KEY `fk_grade_systems_academic_year_id_academic_years` (`academic_year_id`),
  KEY `ix_grade_systems_school_id` (`school_id`),
  KEY `ix_grade_systems_is_active` (`is_active`),
  CONSTRAINT `fk_grade_systems_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_grade_systems_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grade_systems`
--

LOCK TABLES `grade_systems` WRITE;
/*!40000 ALTER TABLE `grade_systems` DISABLE KEYS */;
INSERT INTO `grade_systems` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','CBSE Grading',1,'17d88271-7f52-46be-a540-af06e32f3eac','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `grade_systems` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `helpers`
--

DROP TABLE IF EXISTS `helpers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `helpers` (
  `helper_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `join_date` date DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Available',
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_helpers_school_helper_id` (`school_id`,`helper_id`),
  KEY `ix_helpers_is_active` (`is_active`),
  KEY `ix_helpers_school_id` (`school_id`),
  KEY `idx_helpers_status` (`school_id`,`status`),
  CONSTRAINT `fk_helpers_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `helpers`
--

LOCK TABLES `helpers` WRITE;
/*!40000 ALTER TABLE `helpers` DISABLE KEYS */;
INSERT INTO `helpers` VALUES ('HLP005','krishna','7897897890',NULL,'Available','3a020ea8-9729-4ed5-9b16-f60d27191bdb','{}','2026-05-26 21:44:56','2026-05-26 21:44:56',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('HLP002','Helper 2','+91-991000001',NULL,'Available','84d2ce03-830f-46d8-bd96-b1d74b68d182','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('HLP004','krishna','12912912912',NULL,'Inactive','adeddb48-5b10-439b-a525-21d43acaae0a','{}','2026-05-26 21:31:52','2026-05-26 21:31:54',0,'2026-05-26 16:01:55','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('HLP001','Helper 1','+91-991000000','2026-05-29','Available','c25b7dc8-f55c-4441-bdd8-cf90674441b6','{}','2026-05-24 12:11:35','2026-05-24 13:45:01',1,NULL,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','659a72a6-284a-4b1b-b460-018096237cb9'),('HLP003','Venkat','5678567890','2026-05-30','Active','f7cc2ce7-3421-4eb1-8197-7535be2aa204','{}','2026-05-24 13:45:53','2026-05-24 13:50:08',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `helpers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `leave_applications`
--

DROP TABLE IF EXISTS `leave_applications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `leave_applications` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `staff_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `leave_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `from_date` date NOT NULL,
  `to_date` date NOT NULL,
  `days` decimal(4,1) NOT NULL,
  `is_half_day` tinyint(1) NOT NULL,
  `reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied_on` datetime NOT NULL,
  `approved_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `approved_on` datetime DEFAULT NULL,
  `rejected_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rejected_on` datetime DEFAULT NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `substitute_teacher_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cancelled_on` datetime DEFAULT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_leave_applications_academic_year_id_academic_years` (`academic_year_id`),
  KEY `fk_leave_applications_approved_by_users` (`approved_by`),
  KEY `fk_leave_applications_rejected_by_users` (`rejected_by`),
  KEY `fk_leave_applications_substitute_teacher_id_staff` (`substitute_teacher_id`),
  KEY `idx_leave_applications_status` (`school_id`,`academic_year_id`,`status`),
  KEY `ix_leave_applications_school_id` (`school_id`),
  KEY `ix_leave_applications_is_active` (`is_active`),
  KEY `idx_leave_applications_staff` (`staff_id`,`academic_year_id`),
  KEY `idx_leave_applications_dates` (`school_id`,`from_date`,`to_date`),
  CONSTRAINT `fk_leave_applications_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_leave_applications_approved_by_users` FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_leave_applications_rejected_by_users` FOREIGN KEY (`rejected_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_leave_applications_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_leave_applications_staff_id_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`),
  CONSTRAINT `fk_leave_applications_substitute_teacher_id_staff` FOREIGN KEY (`substitute_teacher_id`) REFERENCES `staff` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `leave_applications`
--

LOCK TABLES `leave_applications` WRITE;
/*!40000 ALTER TABLE `leave_applications` DISABLE KEYS */;
INSERT INTO `leave_applications` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','7794dcaf-e97c-41cb-83f8-c5ec057f8bd0','Sick Leave','2025-12-01','2025-12-02',2.0,0,'Fever','Approved','2025-11-20 10:00:00',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'0cd3bc9e-5619-4c27-9902-8cceda76b7b3','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','Casual Leave','2026-05-17','2026-05-18',2.0,0,'Family function','Approved','2026-05-27 09:16:33',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'361a4612-c7c2-4807-a88c-3c299ca5bb29','{}','2026-05-27 09:16:33','2026-05-27 09:16:33',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','b1edfea4-d604-4f8c-959b-cdf713d21e84','Casual Leave','2025-12-10','2025-12-10',1.0,0,'Personal work','Approved','2025-11-20 10:00:00','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','2026-05-24 10:27:54',NULL,NULL,NULL,NULL,NULL,'5cf5c288-4cf1-4987-b754-af4a79ccdd5e','{}','2026-05-24 12:11:35','2026-05-24 15:57:54',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','Casual Leave','2025-11-25','2025-11-26',2.0,0,'Family function','Approved','2025-11-20 10:00:00',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'6ad206e6-7284-4b21-8e86-7660cb24b894','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','65401672-19ab-4e98-9fa7-6d58e899d261','Earned Leave','2025-12-20','2025-12-25',6.0,0,'Vacation','Rejected','2025-11-20 10:00:00',NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','2026-05-24 10:32:20','Rejected by admin',NULL,NULL,'9dc1dcd6-b60c-40cd-bee8-426e43ca0bc9','{}','2026-05-24 12:11:35','2026-05-24 16:02:19',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `leave_applications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `leave_balances`
--

DROP TABLE IF EXISTS `leave_balances`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `leave_balances` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `staff_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `leave_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_allocated` int NOT NULL,
  `carried_forward` int NOT NULL,
  `used` decimal(5,1) NOT NULL,
  `pending` decimal(5,1) NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_leave_balances_staff_year_type` (`school_id`,`staff_id`,`academic_year_id`,`leave_type`),
  KEY `fk_leave_balances_academic_year_id_academic_years` (`academic_year_id`),
  KEY `ix_leave_balances_is_active` (`is_active`),
  KEY `ix_leave_balances_school_id` (`school_id`),
  KEY `idx_leave_balances_staff` (`staff_id`,`academic_year_id`),
  CONSTRAINT `fk_leave_balances_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_leave_balances_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_leave_balances_staff_id_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `leave_balances`
--

LOCK TABLES `leave_balances` WRITE;
/*!40000 ALTER TABLE `leave_balances` DISABLE KEYS */;
INSERT INTO `leave_balances` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','7794dcaf-e97c-41cb-83f8-c5ec057f8bd0','Casual Leave',12,0,2.0,0.0,'094a6ee8-dc92-471d-bf8d-0884e3170485','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','41a36af7-68e0-4843-8e42-9c09b0ceea13','Annual Leave',15,0,0.0,0.0,'0e4b6f2b-b7f3-4283-a734-9179ef6f442f','{}','2026-05-26 22:56:39','2026-05-26 22:56:39',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','Earned Leave',15,0,2.0,0.0,'1dc8a34b-1d87-46eb-a796-cff8a6445c5d','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','41a36af7-68e0-4843-8e42-9c09b0ceea13','Casual Leave',13,0,0.0,0.0,'21210304-7ad2-4bde-8bcc-b4543dc36427','{}','2026-05-26 22:56:39','2026-05-26 22:57:06',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','Casual Leave',12,0,2.0,0.0,'21514840-dee0-4aee-8143-081b7227facb','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','b1edfea4-d604-4f8c-959b-cdf713d21e84','Earned Leave',15,0,2.0,0.0,'23762af3-026d-49d2-930e-0dc594b484b9','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','65401672-19ab-4e98-9fa7-6d58e899d261','Sick Leave',10,0,2.0,0.0,'395b9770-428b-49b1-b722-2cc9c8191866','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','d99413b6-624f-4d3d-ba74-7dbee9fac4c1','Earned Leave',15,0,2.0,0.0,'41f447fb-6275-43ac-9624-9968c495d27e','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','b1edfea4-d604-4f8c-959b-cdf713d21e84','Sick Leave',10,0,2.0,0.0,'4b0500fb-f1d6-4758-9ff0-0fe01486779a','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','e4c52501-b2fc-472d-906b-f1fdef0d3dc5','Casual Leave',12,0,2.0,0.0,'6e96782b-f580-4b14-9476-37204eeaf13a','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','e4c52501-b2fc-472d-906b-f1fdef0d3dc5','Sick Leave',10,0,2.0,0.0,'6eb39d0a-d4fe-4558-9151-ce2edc307389','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','d99413b6-624f-4d3d-ba74-7dbee9fac4c1','Casual Leave',12,0,2.0,0.0,'793308ae-8402-45de-8ccf-199a096b2174','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8b90d86f-8442-4425-9d1e-475c9f879aa2','Casual Leave',12,0,2.0,0.0,'7c4d1e11-6632-49af-9176-70a0b4c9b24b','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','65401672-19ab-4e98-9fa7-6d58e899d261','Casual Leave',12,0,2.0,0.0,'7cdc82d5-f4bf-4f76-8a45-519e80b0dfd5','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','d99413b6-624f-4d3d-ba74-7dbee9fac4c1','Sick Leave',10,0,2.0,0.0,'80207102-1464-4a36-9389-014e7c834314','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','7794dcaf-e97c-41cb-83f8-c5ec057f8bd0','Earned Leave',15,0,2.0,0.0,'82718274-f16a-4b05-ac34-59be88bf046d','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','Sick Leave',10,0,2.0,0.0,'87d21f08-0a9b-4e44-adc3-81c7f43c99d4','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','41a36af7-68e0-4843-8e42-9c09b0ceea13','Sick Leave',10,0,0.0,0.0,'8b4904e9-44b8-47fc-9d14-b0a540c27779','{}','2026-05-26 22:56:39','2026-05-26 22:56:39',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8b90d86f-8442-4425-9d1e-475c9f879aa2','Earned Leave',15,0,2.0,0.0,'92af1245-a9d4-4fda-8227-95b80eb4aae1','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','e4c52501-b2fc-472d-906b-f1fdef0d3dc5','Earned Leave',15,0,2.0,0.0,'970f8bf9-4dbd-425a-8179-af6a66ea07d6','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','7794dcaf-e97c-41cb-83f8-c5ec057f8bd0','Sick Leave',10,0,2.0,0.0,'9c60af1a-d92d-4676-b4be-ac3c60228243','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','d2be05f9-8e35-4aa8-a17e-c776cf4e3afd','Sick Leave',10,0,2.0,0.0,'a152fa0a-a963-43a8-980b-05cbe9b5b282','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8b90d86f-8442-4425-9d1e-475c9f879aa2','Sick Leave',10,0,2.0,0.0,'a4845f88-0e0e-4b79-ae3a-0e765bf51902','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','65401672-19ab-4e98-9fa7-6d58e899d261','Earned Leave',15,0,2.0,-6.0,'a6f3a2bb-695e-4816-af77-4ddd9aa51e18','{}','2026-05-24 12:11:35','2026-05-24 16:02:19',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','d2be05f9-8e35-4aa8-a17e-c776cf4e3afd','Earned Leave',15,0,2.0,0.0,'c11bb8aa-17bf-4856-a44f-ea4ffc130d24','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','Annual Leave',15,0,2.0,0.0,'d42ce61b-2aff-4175-934e-1e8ea5e652f7','{}','2026-05-27 09:16:33','2026-05-27 09:16:33',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','d2be05f9-8e35-4aa8-a17e-c776cf4e3afd','Casual Leave',12,0,2.0,0.0,'dab8585c-5d1d-4350-a4af-e0b824972763','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','b1edfea4-d604-4f8c-959b-cdf713d21e84','Casual Leave',12,0,3.0,-1.0,'e16f6655-892b-44ef-86e2-2009ee43083e','{}','2026-05-24 12:11:35','2026-05-24 15:57:54',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `leave_balances` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `leave_policies`
--

DROP TABLE IF EXISTS `leave_policies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `leave_policies` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `leave_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `total_per_year` int NOT NULL,
  `carry_forward` tinyint(1) NOT NULL,
  `max_carry_forward` int DEFAULT NULL,
  `max_consecutive_days` int DEFAULT NULL,
  `requires_approval` tinyint(1) NOT NULL,
  `half_day_allowed` tinyint(1) NOT NULL,
  `medical_certificate_required_after_days` int DEFAULT NULL,
  `advance_notice_days` int DEFAULT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_leave_policies_year_type` (`school_id`,`academic_year_id`,`leave_type`),
  KEY `fk_leave_policies_academic_year_id_academic_years` (`academic_year_id`),
  KEY `ix_leave_policies_is_active` (`is_active`),
  KEY `idx_leave_policies_year` (`school_id`,`academic_year_id`),
  KEY `ix_leave_policies_school_id` (`school_id`),
  CONSTRAINT `fk_leave_policies_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_leave_policies_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `leave_policies`
--

LOCK TABLES `leave_policies` WRITE;
/*!40000 ALTER TABLE `leave_policies` DISABLE KEYS */;
INSERT INTO `leave_policies` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Casual Leave','CL',12,0,NULL,NULL,1,1,NULL,NULL,'585ed72d-084f-4aa4-9b9e-a5c656888379','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Earned Leave','EL',15,1,NULL,NULL,1,1,NULL,NULL,'705ea1e9-1459-4f59-af90-7e160fcac6ec','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Sick Leave','SL',10,0,NULL,NULL,1,1,NULL,NULL,'7ba3a8a0-31ab-4dc9-b2c5-e75f671afcc8','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `leave_policies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `library_books`
--

DROP TABLE IF EXISTS `library_books`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `library_books` (
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `author` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `isbn` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `category` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `publisher` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `total_copies` int NOT NULL,
  `available_copies` int NOT NULL,
  `shelf_location` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Available',
  `id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_library_books_school_category` (`school_id`,`category`),
  KEY `idx_library_books_school_title` (`school_id`,`title`),
  KEY `ix_library_books_is_active` (`is_active`),
  KEY `ix_library_books_school_id` (`school_id`),
  CONSTRAINT `fk_library_books_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `library_books`
--

LOCK TABLES `library_books` WRITE;
/*!40000 ALTER TABLE `library_books` DISABLE KEYS */;
INSERT INTO `library_books` VALUES ('C','Vamsi','129912','Computer Science',NULL,2,2,NULL,'Available','e71548c5-3cd0-4307-a2f5-a9f434182ebf','{}','2026-05-26 22:26:10','2026-05-26 22:34:07',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `library_books` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `library_issues`
--

DROP TABLE IF EXISTS `library_issues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `library_issues` (
  `book_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `issue_date` date NOT NULL,
  `due_date` date NOT NULL,
  `return_date` date DEFAULT NULL,
  `fine_amount` float NOT NULL DEFAULT '0',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Issued',
  `id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `borrower_id` char(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `borrower_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_library_issues_book` (`book_id`,`status`),
  KEY `idx_library_issues_student` (`student_id`,`status`),
  KEY `ix_library_issues_is_active` (`is_active`),
  KEY `ix_library_issues_school_id` (`school_id`),
  CONSTRAINT `fk_library_issues_book_id_library_books` FOREIGN KEY (`book_id`) REFERENCES `library_books` (`id`),
  CONSTRAINT `fk_library_issues_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_library_issues_student_id_students` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `library_issues`
--

LOCK TABLES `library_issues` WRITE;
/*!40000 ALTER TABLE `library_issues` DISABLE KEYS */;
INSERT INTO `library_issues` VALUES ('e71548c5-3cd0-4307-a2f5-a9f434182ebf','37e22b29-cb5d-483d-816c-49d31de35c80','2026-05-26','2026-05-28','2026-05-26',0,'Returned','51e62a25-4370-49af-8b2d-c8f78f6f5fc7','{}','2026-05-26 22:34:01','2026-05-26 22:34:07',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9','','');
/*!40000 ALTER TABLE `library_issues` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notification_recipients`
--

DROP TABLE IF EXISTS `notification_recipients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notification_recipients` (
  `notification_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `read_at` datetime DEFAULT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_notification_recipients_school_notif_user` (`school_id`,`notification_id`,`user_id`),
  KEY `idx_notification_recipients_notification` (`notification_id`),
  KEY `ix_notification_recipients_school_id` (`school_id`),
  KEY `ix_notification_recipients_is_active` (`is_active`),
  KEY `idx_notification_recipients_user` (`user_id`,`is_read`),
  CONSTRAINT `fk_notification_recipients_notification_id_notifications` FOREIGN KEY (`notification_id`) REFERENCES `notifications` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_notification_recipients_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_notification_recipients_user_id_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification_recipients`
--

LOCK TABLES `notification_recipients` WRITE;
/*!40000 ALTER TABLE `notification_recipients` DISABLE KEYS */;
INSERT INTO `notification_recipients` VALUES ('a0af2fd9-c7a5-444c-9f23-208e8e77bf75','ca4bb6bf-ab10-4153-b8c2-734560dc7c8b',0,NULL,'69c0c25b-e2d3-4dea-b711-c6d5eaf9dd23','{}','2026-05-24 14:37:38','2026-05-24 14:37:38',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `notification_recipients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `target_type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `target_class_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `target_section` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `send_via` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `scheduled_at` datetime DEFAULT NULL,
  `sent_at` datetime DEFAULT NULL,
  `archived_at` datetime DEFAULT NULL,
  `recipients_count` int NOT NULL,
  `read_count` int NOT NULL,
  `created_by_user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_notifications_created_by_user_id_users` (`created_by_user_id`),
  KEY `ix_notifications_is_active` (`is_active`),
  KEY `idx_notifications_target` (`school_id`,`target_type`),
  KEY `idx_notifications_school_status` (`school_id`,`status`,`sent_at`),
  KEY `ix_notifications_school_id` (`school_id`),
  CONSTRAINT `fk_notifications_created_by_user_id_users` FOREIGN KEY (`created_by_user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_notifications_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES ('Fee Reminder','Please clear pending fees by Nov 30.','Fee','all',NULL,NULL,'in_app','Sent',NULL,'2025-11-01 09:00:00',NULL,50,30,NULL,'0c0ffe2c-62dd-48bb-8bc3-55ce3803ccc2','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('PTM Scheduled','Parent-Teacher meeting on Dec 5th.','Meeting','all',NULL,NULL,'in_app','Sent',NULL,'2025-11-01 09:00:00',NULL,50,30,NULL,'3aedaaba-ab82-4c73-a41f-1c20d86a1bdb','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Holiday Notice','School closed on Nov 14 for Children\'s Day.','Holiday','all',NULL,NULL,'in_app','Sent',NULL,'2025-11-01 09:00:00',NULL,50,30,NULL,'5b9434b3-febd-43f6-bb99-76741585bd91','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('test','msg test',NULL,'teaching_staff',NULL,NULL,'whatsapp','Scheduled','2026-05-21 12:12:00',NULL,NULL,0,0,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','8515851b-e03a-4a05-97b1-8bcfd9ced8c3','{}','2026-05-24 14:37:04','2026-05-24 14:37:04',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('test','test',NULL,'teaching_staff','9','A','whatsapp','Sent',NULL,'2026-05-24 09:07:39',NULL,1,0,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','a0af2fd9-c7a5-444c-9f23-208e8e77bf75','{}','2026-05-24 14:37:38','2026-05-24 14:37:38',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('School Reopens','School will reopen on June 1st after summer break.','General','all',NULL,NULL,'in_app','Sent',NULL,'2025-11-01 09:00:00',NULL,50,30,NULL,'c9e32161-f73b-48bf-ada1-b2d4aacbc5ce','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parent_meetings`
--

DROP TABLE IF EXISTS `parent_meetings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parent_meetings` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `meeting_date` date NOT NULL,
  `meeting_time` time DEFAULT NULL,
  `conducted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `parent_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `attendees` json NOT NULL,
  `agenda` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `discussion_notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `action_items` json NOT NULL,
  `next_meeting_date` date DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `meeting_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `follow_up_required` tinyint(1) NOT NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_parent_meetings_academic_year_id_academic_years` (`academic_year_id`),
  KEY `fk_parent_meetings_parent_id_parents` (`parent_id`),
  KEY `idx_parent_meetings_date` (`school_id`,`meeting_date`),
  KEY `idx_parent_meetings_conductor` (`conducted_by`,`meeting_date`),
  KEY `ix_parent_meetings_school_id` (`school_id`),
  KEY `idx_parent_meetings_status` (`school_id`,`academic_year_id`,`status`),
  KEY `idx_parent_meetings_student` (`student_id`,`academic_year_id`),
  KEY `ix_parent_meetings_is_active` (`is_active`),
  CONSTRAINT `fk_parent_meetings_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_parent_meetings_conducted_by_staff` FOREIGN KEY (`conducted_by`) REFERENCES `staff` (`id`),
  CONSTRAINT `fk_parent_meetings_parent_id_parents` FOREIGN KEY (`parent_id`) REFERENCES `parents` (`id`),
  CONSTRAINT `fk_parent_meetings_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_parent_meetings_student_id_students` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parent_meetings`
--

LOCK TABLES `parent_meetings` WRITE;
/*!40000 ALTER TABLE `parent_meetings` DISABLE KEYS */;
INSERT INTO `parent_meetings` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','13118271-a690-4bd5-a38b-4cc13334f292','2025-11-07','10:00:00','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','ca246da3-0985-4874-b044-fe249a8dd2c3','[]','Academic progress discussion','Student performing well overall.','[]',NULL,'Completed','Regular PTM',0,NULL,'418460cc-0a6c-46ce-a095-ea5458a15116','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4823e6f0-69e2-4a1c-a0ff-1fb9653767d5','2025-11-05','10:00:00','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','47f0fd84-19cd-4683-890f-58f0afc1e320','[]','Academic progress discussion','Student performing well overall.','[]',NULL,'Completed','Regular PTM',0,NULL,'5525611d-4634-4931-86d3-7883e83da0cf','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','d4145bca-3b08-489a-a80d-c8141b3ce925','2025-11-06','10:00:00','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','fc93fc6b-ac92-4617-a17d-76198db7883e','[]','Academic progress discussion','Student performing well overall.','[]',NULL,'Completed','Regular PTM',0,NULL,'5928390c-2fc0-450c-8e55-701f252c5eeb','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `parent_meetings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parents`
--

DROP TABLE IF EXISTS `parents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parents` (
  `first_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `full_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `relation` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `alternate_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `occupation` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `annual_income` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address_line1` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address_line2` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `city` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `state` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pincode` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `aadhar_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_primary_contact` tinyint(1) NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parents_phone` (`school_id`,`phone`),
  KEY `ix_parents_school_id` (`school_id`),
  KEY `ix_parents_is_active` (`is_active`),
  KEY `idx_parents_email` (`school_id`,`email`),
  CONSTRAINT `fk_parents_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parents`
--

LOCK TABLES `parents` WRITE;
/*!40000 ALTER TABLE `parents` DISABLE KEYS */;
INSERT INTO `parents` VALUES ('Mr. Sharma','Sharma','Mr. Sharma','Father','parent.sharma@email.com','+91-98800005',NULL,'Engineer',NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'1a3ccc7a-4a09-42bd-8f03-2144e19d13f4','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Mr. Nair','Nair','Mr. Nair','Father','parent.nair@email.com','+91-98800006',NULL,'Engineer',NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'2c0d5879-10f3-4eb6-bda3-35a3b28f983b','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Mr. Reddy','Reddy','Mr. Reddy','Father','parent.reddy@email.com','+91-98800007',NULL,'Engineer',NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'3248eaf0-9084-44f0-b1b2-6a6de15fe349','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Mr. Chopra','Chopra','Mr. Chopra','Father','parent.chopra@email.com','+91-98800013',NULL,'Engineer',NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'44134cdd-f5f3-460b-890c-33b43afed2ad','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Mr. Mehta','Mehta','Mr. Mehta','Father','parent.mehta@email.com','+91-98800000',NULL,'Engineer',NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'47f0fd84-19cd-4683-890f-58f0afc1e320','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Mr. Singh','Singh','Mr. Singh','Father','parent.singh@email.com','+91-98800003',NULL,'Engineer',NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'4f08f177-b733-4436-b2d2-955574733911','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Mr. Verma','Verma','Mr. Verma','Father','parent.verma@email.com','+91-98800012',NULL,'Engineer',NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'59e4efea-d914-471e-be27-4bcbf1de9c5b','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Mr. Rao','Rao','Mr. Rao','Father','parent.rao@email.com','+91-98800004',NULL,'Engineer',NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'6a1963f0-5a5b-4eb2-8a9d-8a7715c172ed','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Mr. Das','Das','Mr. Das','Father','parent.das@email.com','+91-98800009',NULL,'Engineer',NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'7aca2431-96c8-46a7-bbcb-fc847341ebb6','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Mr. Iyer','Iyer','Mr. Iyer','Father','parent.iyer@email.com','+91-98800011',NULL,'Engineer',NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'7e0e8faf-d2ec-4fe3-953a-b49749445a37','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Mr. Kumar','Kumar','Mr. Kumar','Father','parent.kumar@email.com','+91-98800008',NULL,'Engineer',NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'8eeb34e0-0dc0-4857-8ddd-604cffef8740','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Mr. Joshi','Joshi','Mr. Joshi','Father','parent.joshi@email.com','+91-98800010',NULL,'Engineer',NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'936b5d94-02d4-4ee9-989a-79fcff65c79d','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Mr. Patel','Patel','Mr. Patel','Father','parent.patel@email.com','+91-98800002',NULL,'Engineer',NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'ca246da3-0985-4874-b044-fe249a8dd2c3','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Mr. Agarwal','Agarwal','Mr. Agarwal','Father','parent.agarwal@email.com','+91-98800014',NULL,'Engineer',NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'fc8c71d6-0ff2-4eaf-9339-235515fe323a','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Mr. Gupta','Gupta','Mr. Gupta','Father','parent.gupta@email.com','+91-98800001',NULL,'Engineer',NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'fc93fc6b-ac92-4617-a17d-76198db7883e','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `parents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payslips`
--

DROP TABLE IF EXISTS `payslips`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payslips` (
  `staff_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `month` int NOT NULL,
  `year` int NOT NULL,
  `basic_salary` decimal(10,2) NOT NULL,
  `total_allowances` decimal(10,2) NOT NULL,
  `total_deductions` decimal(10,2) NOT NULL,
  `net_salary` decimal(10,2) NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `paid_on` date DEFAULT NULL,
  `payment_method` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reference` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `generated_at` datetime NOT NULL,
  `generated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_payslips_month` (`school_id`,`staff_id`,`month`,`year`),
  KEY `fk_payslips_academic_year_id_academic_years` (`academic_year_id`),
  KEY `fk_payslips_generated_by_users` (`generated_by`),
  KEY `ix_payslips_school_id` (`school_id`),
  KEY `idx_payslips_period` (`school_id`,`year`,`month`),
  KEY `idx_payslips_status` (`school_id`,`year`,`month`,`status`),
  KEY `idx_payslips_staff` (`staff_id`,`year`,`month`),
  KEY `ix_payslips_is_active` (`is_active`),
  CONSTRAINT `fk_payslips_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_payslips_generated_by_users` FOREIGN KEY (`generated_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_payslips_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_payslips_staff_id_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payslips`
--

LOCK TABLES `payslips` WRITE;
/*!40000 ALTER TABLE `payslips` DISABLE KEYS */;
INSERT INTO `payslips` VALUES ('e4c52501-b2fc-472d-906b-f1fdef0d3dc5','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',10,2025,40000.00,20000.00,7000.00,53000.00,'Paid','2025-10-28','Bank Transfer',NULL,'2025-10-25 10:00:00',NULL,'0d7057e8-3eb3-4c8b-b669-4cc937bbf7ff','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('d2be05f9-8e35-4aa8-a17e-c776cf4e3afd','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',10,2025,40000.00,20000.00,7000.00,53000.00,'Paid','2025-10-28','Bank Transfer',NULL,'2025-10-25 10:00:00',NULL,'2a275440-e563-4214-b999-b99aac611219','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f0bc267d-4453-40bf-9bcf-f3c888fcb48c','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',10,2025,40000.00,20000.00,7000.00,53000.00,'Paid','2025-10-28','Bank Transfer',NULL,'2025-10-25 10:00:00',NULL,'4bbe6f6d-46b6-497d-aa14-bf15ff949a06','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('d2be05f9-8e35-4aa8-a17e-c776cf4e3afd','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',5,2026,40000.00,20000.00,7000.00,53000.00,'Generated',NULL,NULL,NULL,'2026-05-24 10:27:30','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','546f9c74-81cb-4a89-ab30-fcb631f63296','{}','2026-05-24 15:57:30','2026-05-24 15:57:30',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('7794dcaf-e97c-41cb-83f8-c5ec057f8bd0','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',5,2026,40000.00,20000.00,7000.00,53000.00,'Generated',NULL,NULL,NULL,'2026-05-24 10:27:30','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','57b3cc9b-6617-410d-a40e-1f35d08e2f5d','{}','2026-05-24 15:57:30','2026-05-24 15:57:30',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('8b90d86f-8442-4425-9d1e-475c9f879aa2','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',10,2025,40000.00,20000.00,7000.00,53000.00,'Paid','2025-10-28','Bank Transfer',NULL,'2025-10-25 10:00:00',NULL,'6c77596c-4327-4646-b073-c708bc092c32','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('e4c52501-b2fc-472d-906b-f1fdef0d3dc5','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',5,2026,40000.00,20000.00,7000.00,53000.00,'Generated',NULL,NULL,NULL,'2026-05-24 10:27:30','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','851a9369-94f7-4a54-b298-6810f5a81197','{}','2026-05-24 15:57:30','2026-05-24 15:57:30',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('d99413b6-624f-4d3d-ba74-7dbee9fac4c1','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',10,2025,40000.00,20000.00,7000.00,53000.00,'Paid','2025-10-28','Bank Transfer',NULL,'2025-10-25 10:00:00',NULL,'9a2c3e60-1bd7-4b48-a84a-d5b24e641234','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('b1edfea4-d604-4f8c-959b-cdf713d21e84','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',10,2025,40000.00,20000.00,7000.00,53000.00,'Paid','2025-10-28','Bank Transfer',NULL,'2025-10-25 10:00:00',NULL,'a08f1537-8032-4296-9203-0dad8d0fe57f','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('b1edfea4-d604-4f8c-959b-cdf713d21e84','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',5,2026,40000.00,20000.00,7000.00,53000.00,'Generated',NULL,NULL,NULL,'2026-05-24 10:27:30','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','a6666065-a6d3-43e3-8186-7b7ad568f071','{}','2026-05-24 15:57:30','2026-05-24 15:57:30',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('65401672-19ab-4e98-9fa7-6d58e899d261','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',10,2025,40000.00,20000.00,7000.00,53000.00,'Paid','2025-10-28','Bank Transfer',NULL,'2025-10-25 10:00:00',NULL,'aac9b35b-b963-4fc0-82e6-3a7bff53e79b','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('65401672-19ab-4e98-9fa7-6d58e899d261','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',5,2026,40000.00,20000.00,7000.00,53000.00,'Generated',NULL,NULL,NULL,'2026-05-24 10:27:30','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','b1fa41e5-33a8-48dd-becd-09f19a74f6d1','{}','2026-05-24 15:57:30','2026-05-24 15:57:30',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('d99413b6-624f-4d3d-ba74-7dbee9fac4c1','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',5,2026,40000.00,20000.00,7000.00,53000.00,'Generated',NULL,NULL,NULL,'2026-05-24 10:27:30','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','c3b5a08c-a6db-49f6-bcb1-31a2b677f2ed','{}','2026-05-24 15:57:30','2026-05-24 15:57:30',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f0bc267d-4453-40bf-9bcf-f3c888fcb48c','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',5,2026,40000.00,20000.00,7000.00,53000.00,'Generated',NULL,NULL,NULL,'2026-05-24 10:27:30','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','dfab17e5-4ea2-4d19-8e22-3d47a9e8a7b2','{}','2026-05-24 15:57:30','2026-05-24 15:57:30',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('8b90d86f-8442-4425-9d1e-475c9f879aa2','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',5,2026,40000.00,20000.00,7000.00,53000.00,'Generated',NULL,NULL,NULL,'2026-05-24 10:27:30','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','e06c8e50-c721-454a-a46f-66edad061c7b','{}','2026-05-24 15:57:30','2026-05-24 15:57:30',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('7794dcaf-e97c-41cb-83f8-c5ec057f8bd0','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',10,2025,40000.00,20000.00,7000.00,53000.00,'Paid','2025-10-28','Bank Transfer',NULL,'2025-10-25 10:00:00',NULL,'f49c11d6-f5d2-45f8-b06d-a82c5f3050d6','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `payslips` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `period_configs`
--

DROP TABLE IF EXISTS `period_configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `period_configs` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `duration_minutes` int DEFAULT NULL,
  `is_break` tinyint(1) NOT NULL,
  `sort_order` int NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_period_configs_unique` (`school_id`,`academic_year_id`,`start_time`),
  KEY `fk_period_configs_academic_year_id_academic_years` (`academic_year_id`),
  KEY `ix_period_configs_school_id` (`school_id`),
  KEY `ix_period_configs_is_active` (`is_active`),
  KEY `idx_period_configs_year` (`school_id`,`academic_year_id`),
  CONSTRAINT `fk_period_configs_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_period_configs_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `ck_period_configs_chk_period_configs_time` CHECK ((`end_time` > `start_time`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `period_configs`
--

LOCK TABLES `period_configs` WRITE;
/*!40000 ALTER TABLE `period_configs` DISABLE KEYS */;
INSERT INTO `period_configs` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Period 2','08:45:00','09:30:00',45,0,2,'0cc803ac-2c1a-4f20-b53e-e8e4ba63d7a7','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Period 6','12:45:00','13:30:00',45,0,8,'1a483d85-795f-4ccb-866c-76ba43174d89','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Period 4','10:30:00','11:15:00',45,0,5,'29a8975a-eb2d-4d82-9471-7404470d0152','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Break','09:30:00','09:45:00',45,1,3,'535503eb-f109-44b4-8ece-0bc6e9be982c','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Period 1','08:00:00','08:45:00',45,0,1,'5848ba1f-507c-4f61-9207-4b77558a243d','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Period 3','09:45:00','10:30:00',45,0,4,'75cd9edd-322d-44d7-976c-47966d197987','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Period 5','12:00:00','12:45:00',45,0,7,'ea31dddf-6b0f-41bb-9aee-770233b71e11','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Lunch','11:15:00','12:00:00',45,1,6,'fa84600b-64f4-4254-b8da-1a6e07e5ea89','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `period_configs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `route_assignments`
--

DROP TABLE IF EXISTS `route_assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `route_assignments` (
  `route_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `vehicle_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `driver_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `helper_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Active',
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_route_assignments_school_vehicle` (`school_id`,`vehicle_id`),
  KEY `fk_route_assignments_helper_id_helpers` (`helper_id`),
  KEY `ix_route_assignments_school_id` (`school_id`),
  KEY `idx_route_assignments_route` (`route_id`),
  KEY `idx_route_assignments_vehicle` (`vehicle_id`),
  KEY `ix_route_assignments_is_active` (`is_active`),
  KEY `idx_route_assignments_driver` (`driver_id`),
  CONSTRAINT `fk_route_assignments_driver_id_drivers` FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`id`),
  CONSTRAINT `fk_route_assignments_helper_id_helpers` FOREIGN KEY (`helper_id`) REFERENCES `helpers` (`id`),
  CONSTRAINT `fk_route_assignments_route_id_routes` FOREIGN KEY (`route_id`) REFERENCES `routes` (`id`),
  CONSTRAINT `fk_route_assignments_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_route_assignments_vehicle_id_vehicles` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `route_assignments`
--

LOCK TABLES `route_assignments` WRITE;
/*!40000 ALTER TABLE `route_assignments` DISABLE KEYS */;
INSERT INTO `route_assignments` VALUES ('aac95525-6d47-4cbb-b55a-799fa917e4cc','f622cef3-ca09-4751-953e-f85e622c652b','e00b70b8-51d7-476d-b732-8d72ca5ef3ec','c25b7dc8-f55c-4441-bdd8-cf90674441b6','Active','3ed5c8f1-61ce-47a9-92e3-d43af00bf60b','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('4a8fa349-28a2-4e52-a252-3fc5697d8fbd','56b90993-4e7e-4aae-b92f-4a198f01dc77','3a68afc3-c0c2-4310-9efd-f075e98a327e','84d2ce03-830f-46d8-bd96-b1d74b68d182','Active','4ffe0ca8-4a5d-4578-b1ba-7fe6e7b1edac','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('3bfd21e8-192c-42ab-9be9-19011a28b7c7','15272ee3-0b0f-4a77-a895-7b4a61c06928','c7d9ef94-ac6d-4ab8-a4e6-7abd6a4ce391','f7cc2ce7-3421-4eb1-8197-7535be2aa204','Active','984841c2-a08e-4e1f-8871-0938f0679261','{}','2026-05-24 13:50:08','2026-05-24 13:50:08',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('12b7ff65-6b1e-4b7a-a5c3-c7fec5a04acb','7fe5b9e5-7b9b-44ca-b4c5-da9bd9e87279','0d3886d3-059e-4ec1-a0a6-92f57bb4efda',NULL,'Active','ae11fb5c-980e-44bb-aeb0-617f0e483640','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `route_assignments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `routes`
--

DROP TABLE IF EXISTS `routes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `routes` (
  `route_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `area` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `shift` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `stops` json NOT NULL,
  `distance_km` float DEFAULT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Active',
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_routes_school_route_code` (`school_id`,`route_code`),
  KEY `ix_routes_school_id` (`school_id`),
  KEY `idx_routes_status` (`school_id`,`status`),
  KEY `ix_routes_is_active` (`is_active`),
  CONSTRAINT `fk_routes_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `routes`
--

LOCK TABLES `routes` WRITE;
/*!40000 ALTER TABLE `routes` DISABLE KEYS */;
INSERT INTO `routes` VALUES ('R03','Route 3 - Indiranagar','East','Morning','[]',18.5,NULL,NULL,'Active','12b7ff65-6b1e-4b7a-a5c3-c7fec5a04acb','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('R-005','Kondapur-Miyapur','North','Morning','[]',8,'08:00:00','09:00:00','Active','3bfd21e8-192c-42ab-9be9-19011a28b7c7','{}','2026-05-24 13:28:58','2026-05-24 13:28:58',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('R02','Route 2 - Whitefield','East','Morning','[]',15.5,NULL,NULL,'Active','4a8fa349-28a2-4e52-a252-3fc5697d8fbd','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('R-004','Gachibowli-Miyapur','North','Morning','[]',10,'07:00:00','09:00:00','Active','66036708-0063-4995-b2e9-1fe21c89382b','{}','2026-05-24 13:27:57','2026-05-24 13:27:57',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('R01','Route 1 - Koramangala','South','Morning','[]',12.5,NULL,NULL,'Active','aac95525-6d47-4cbb-b55a-799fa917e4cc','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('R-006','Wipro-Gachibowli',NULL,NULL,'[]',0,NULL,NULL,'Active','d8975ba8-e995-44ee-a67d-9c76454ec95a','{}','2026-05-26 21:45:17','2026-05-26 21:45:17',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `routes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `salary_advances`
--

DROP TABLE IF EXISTS `salary_advances`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `salary_advances` (
  `staff_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `recovery_months` int DEFAULT NULL,
  `per_month_deduction` decimal(10,2) DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied_on` datetime NOT NULL,
  `approved_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `approved_on` datetime DEFAULT NULL,
  `rejected_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `disbursed_on` datetime DEFAULT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_salary_advances_approved_by_users` (`approved_by`),
  KEY `fk_salary_advances_rejected_by_users` (`rejected_by`),
  KEY `idx_salary_advances_status` (`school_id`,`status`),
  KEY `idx_salary_advances_staff` (`staff_id`),
  KEY `ix_salary_advances_school_id` (`school_id`),
  KEY `ix_salary_advances_is_active` (`is_active`),
  CONSTRAINT `fk_salary_advances_approved_by_users` FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_salary_advances_rejected_by_users` FOREIGN KEY (`rejected_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_salary_advances_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_salary_advances_staff_id_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `salary_advances`
--

LOCK TABLES `salary_advances` WRITE;
/*!40000 ALTER TABLE `salary_advances` DISABLE KEYS */;
INSERT INTO `salary_advances` VALUES ('f0bc267d-4453-40bf-9bcf-f3c888fcb48c',20000.00,'Medical emergency',4,5000.00,'Approved','2025-10-01 10:00:00',NULL,NULL,NULL,NULL,NULL,'d465f375-5d95-4d37-8c20-6f0970a48d9c','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `salary_advances` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `salary_revisions`
--

DROP TABLE IF EXISTS `salary_revisions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `salary_revisions` (
  `staff_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `effective_date` date NOT NULL,
  `previous_basic` decimal(10,2) NOT NULL,
  `new_basic` decimal(10,2) NOT NULL,
  `revision_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `percentage` decimal(5,2) DEFAULT NULL,
  `increment_amount` decimal(10,2) DEFAULT NULL,
  `approved_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `approved_on` datetime DEFAULT NULL,
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_salary_revisions_academic_year_id_academic_years` (`academic_year_id`),
  KEY `fk_salary_revisions_approved_by_users` (`approved_by`),
  KEY `idx_salary_revisions_year` (`school_id`,`academic_year_id`),
  KEY `ix_salary_revisions_is_active` (`is_active`),
  KEY `idx_salary_revisions_date` (`school_id`,`effective_date`),
  KEY `ix_salary_revisions_school_id` (`school_id`),
  KEY `idx_salary_revisions_staff` (`staff_id`,`effective_date`),
  CONSTRAINT `fk_salary_revisions_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_salary_revisions_approved_by_users` FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_salary_revisions_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_salary_revisions_staff_id_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `salary_revisions`
--

LOCK TABLES `salary_revisions` WRITE;
/*!40000 ALTER TABLE `salary_revisions` DISABLE KEYS */;
INSERT INTO `salary_revisions` VALUES ('f0bc267d-4453-40bf-9bcf-f3c888fcb48c','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','2025-06-01',38000.00,40000.00,'Annual Increment',5.26,2000.00,NULL,NULL,NULL,'ff541a7e-de28-426f-8f26-145320ae1afd','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `salary_revisions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `salary_structures`
--

DROP TABLE IF EXISTS `salary_structures`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `salary_structures` (
  `staff_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `basic_salary` decimal(10,2) NOT NULL,
  `hra` decimal(10,2) NOT NULL,
  `da` decimal(10,2) NOT NULL,
  `transport_allowance` decimal(10,2) NOT NULL,
  `medical_allowance` decimal(10,2) NOT NULL,
  `other_allowances` json NOT NULL,
  `pf_deduction` decimal(10,2) NOT NULL,
  `professional_tax` decimal(10,2) NOT NULL,
  `tds` decimal(10,2) NOT NULL,
  `other_deductions` json NOT NULL,
  `net_salary` decimal(10,2) NOT NULL,
  `effective_from` date NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_salary_structures_active` (`school_id`,`staff_id`),
  KEY `fk_salary_structures_academic_year_id_academic_years` (`academic_year_id`),
  KEY `ix_salary_structures_is_active` (`is_active`),
  KEY `ix_salary_structures_school_id` (`school_id`),
  KEY `idx_salary_structures_staff` (`staff_id`,`academic_year_id`),
  CONSTRAINT `fk_salary_structures_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_salary_structures_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_salary_structures_staff_id_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `salary_structures`
--

LOCK TABLES `salary_structures` WRITE;
/*!40000 ALTER TABLE `salary_structures` DISABLE KEYS */;
INSERT INTO `salary_structures` VALUES ('d99413b6-624f-4d3d-ba74-7dbee9fac4c1','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',40000.00,10000.00,5000.00,3000.00,2000.00,'{}',4800.00,200.00,2000.00,'{}',53000.00,'2025-06-01','0d66a5f3-c9a3-4b1b-9529-5bd416729080','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('7794dcaf-e97c-41cb-83f8-c5ec057f8bd0','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',40000.00,10000.00,5000.00,3000.00,2000.00,'{}',4800.00,200.00,2000.00,'{}',53000.00,'2025-06-01','38e5b895-0aa2-4c64-bfe0-eb358d8e357d','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f0bc267d-4453-40bf-9bcf-f3c888fcb48c','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',40000.00,10000.00,5000.00,3000.00,2000.00,'{}',4800.00,200.00,2000.00,'{}',53000.00,'2025-06-01','57e2a7c9-394d-452a-a4d4-5770c4f1cd8f','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('e4c52501-b2fc-472d-906b-f1fdef0d3dc5','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',40000.00,10000.00,5000.00,3000.00,2000.00,'{}',4800.00,200.00,2000.00,'{}',53000.00,'2025-06-01','7bfa0a0d-3244-4faf-ad53-8e052d27dece','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('8b90d86f-8442-4425-9d1e-475c9f879aa2','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',40000.00,10000.00,5000.00,3000.00,2000.00,'{}',4800.00,200.00,2000.00,'{}',53000.00,'2025-06-01','89727a40-f3cb-4151-a0eb-2006cea04d37','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('65401672-19ab-4e98-9fa7-6d58e899d261','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',40000.00,10000.00,5000.00,3000.00,2000.00,'{}',4800.00,200.00,2000.00,'{}',53000.00,'2025-06-01','8ed079e2-982a-4d64-b927-26b0827b2799','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('d2be05f9-8e35-4aa8-a17e-c776cf4e3afd','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',40000.00,10000.00,5000.00,3000.00,2000.00,'{}',4800.00,200.00,2000.00,'{}',53000.00,'2025-06-01','be2bbadb-47e6-4bd0-9694-cddae972d8f5','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('b1edfea4-d604-4f8c-959b-cdf713d21e84','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1',40000.00,10000.00,5000.00,3000.00,2000.00,'{}',4800.00,200.00,2000.00,'{}',53000.00,'2025-06-01','dbd24d96-c900-4b4a-91a0-cfcea2b552c7','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `salary_structures` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `schools`
--

DROP TABLE IF EXISTS `schools`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schools` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `logo_url` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `address_line1` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address_line2` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `city` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `state` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `country` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pincode` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `website` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `board_affiliation` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `established_year` int DEFAULT NULL,
  `principal_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_schools_code` (`code`),
  KEY `ix_schools_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schools`
--

LOCK TABLES `schools` WRITE;
/*!40000 ALTER TABLE `schools` DISABLE KEYS */;
INSERT INTO `schools` VALUES ('659a72a6-284a-4b1b-b460-018096237cb9','Default School','SCH001',NULL,'123 School Street',NULL,'Bangalore','Karnataka','India','560001','+91-9876543210','admin@defaultschool.com',NULL,'CBSE',2000,'Dr. Principal','{}','2026-05-24 12:11:29','2026-05-24 12:11:29',1,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `schools` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sections`
--

DROP TABLE IF EXISTS `sections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sections` (
  `name` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_order` int NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_sections_school_name` (`school_id`,`name`),
  KEY `ix_sections_school_id` (`school_id`),
  KEY `ix_sections_is_active` (`is_active`),
  CONSTRAINT `fk_sections_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sections`
--

LOCK TABLES `sections` WRITE;
/*!40000 ALTER TABLE `sections` DISABLE KEYS */;
INSERT INTO `sections` VALUES ('C',3,'115be7b5-3c3f-4ba1-9ea8-ee4e018aae24','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('B',2,'945545a5-0cec-407c-a39d-fa99806525d2','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('A',1,'ce323069-ae19-44d7-90ae-20dc4b41fe4d','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `sections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `settings` (
  `category` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `key` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` json NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_settings_school_category_key` (`school_id`,`category`,`key`),
  KEY `ix_settings_is_active` (`is_active`),
  KEY `ix_settings_school_id` (`school_id`),
  CONSTRAINT `fk_settings_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `settings`
--

LOCK TABLES `settings` WRITE;
/*!40000 ALTER TABLE `settings` DISABLE KEYS */;
INSERT INTO `settings` VALUES ('attendance','minimum_percentage','{\"value\": 75}',NULL,'b3a26e90-5cc6-41ef-974e-edb85d9d93f8','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('general','academic_year_format','{\"format\": \"YYYY-YYYY\"}',NULL,'dc0c33aa-e578-4a72-bda2-0da2ce2b773a','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `staff`
--

DROP TABLE IF EXISTS `staff`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staff` (
  `employee_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `full_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `alternate_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `gender` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `photo_url` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `department` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `designation` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `employment_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `joining_date` date DEFAULT NULL,
  `left_date` date DEFAULT NULL,
  `left_reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `qualification` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `experience_years` decimal(4,1) DEFAULT NULL,
  `address_line1` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address_line2` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `city` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `state` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pincode` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `blood_group` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `emergency_contact_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `emergency_contact_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bank_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bank_account_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bank_ifsc` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pan_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `aadhar_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_teacher` tinyint(1) NOT NULL,
  `primary_subject_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `max_workload_hours` int DEFAULT NULL,
  `salary` decimal(10,2) DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_staff_school_employee_id` (`school_id`,`employee_id`),
  UNIQUE KEY `uq_staff_school_email` (`school_id`,`email`),
  KEY `idx_staff_status` (`school_id`,`status`),
  KEY `idx_staff_department` (`school_id`,`department`),
  KEY `ix_staff_school_id` (`school_id`),
  KEY `idx_staff_is_teacher` (`school_id`,`is_teacher`),
  KEY `ix_staff_is_active` (`is_active`),
  KEY `idx_staff_name` (`school_id`,`full_name`),
  KEY `fk_staff_user_id_users` (`user_id`),
  CONSTRAINT `fk_staff_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_staff_user_id_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staff`
--

LOCK TABLES `staff` WRITE;
/*!40000 ALTER TABLE `staff` DISABLE KEYS */;
INSERT INTO `staff` VALUES ('1234','Kotha','Vamsi','Kotha Vamsi','vamsi@school.com','8989898799',NULL,'Male',NULL,NULL,'Teaching','Senior Teacher','Full-Time','2026-05-27','2026-05-26',NULL,'B.Tech',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,0,NULL,'Inactive','1058e8f0-ec4e-4d1c-ae0d-c8e631566286','2334c80d-0b88-4096-98ff-398bf9a88855','{}','2026-05-26 21:50:02','2026-05-26 22:15:57',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','659a72a6-284a-4b1b-b460-018096237cb9'),('123','Vamsi','','Vamsi','vamsi@school.gmail.com','7893444336',NULL,'Male',NULL,NULL,'Teaching','Senior Maths Teacher','Full-Time','2026-05-21',NULL,NULL,'B.Tech',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,45000.00,'Active',NULL,'2aa04bce-421e-4f1d-b954-be7880714d16','{}','2026-05-24 15:54:47','2026-05-24 15:55:17',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','659a72a6-284a-4b1b-b460-018096237cb9'),('12345','Surya','Vamsi Kotha','Surya Vamsi Kotha','suryavamsikotha@gmail.com','7893444336',NULL,'Male',NULL,NULL,'Teaching','Senior Teacher','Full-Time','2026-05-05',NULL,NULL,'B.Tech',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,12,NULL,'Active','25e2d506-932b-4457-98a9-948594c6e690','41a36af7-68e0-4843-8e42-9c09b0ceea13','{}','2026-05-26 21:57:43','2026-05-26 22:03:18',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','659a72a6-284a-4b1b-b460-018096237cb9'),('EMP010','Suresh','Reddy','Suresh Reddy','suresh@admin.com','+91-98765010',NULL,NULL,NULL,NULL,'Administration','Office Staff','Full-Time','2020-06-01',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,35000.00,'Active',NULL,'4fcdf793-88fd-4b18-a25d-65f3ce2f1c7f','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('EMP004','Amit','Kumar','Amit Kumar','amit@teacher.com','+91-98765004',NULL,NULL,NULL,NULL,'Teaching','Teacher','Full-Time','2020-06-01',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,50000.00,'Active',NULL,'65401672-19ab-4e98-9fa7-6d58e899d261','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('EMP002','Robert','Brown','Robert Brown','robert@teacher.com','+91-98765002',NULL,NULL,NULL,NULL,'Teaching','Teacher','Full-Time','2020-06-01',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,50000.00,'Active',NULL,'7794dcaf-e97c-41cb-83f8-c5ec057f8bd0','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('EMP009','Meera','Patel','Meera Patel','meera@admin.com','+91-98765009',NULL,NULL,NULL,NULL,'Administration','Office Staff','Full-Time','2020-06-01',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,35000.00,'Active',NULL,'89d5c674-e945-49c7-bbae-068cbb58e58b','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('EMP006','Rahul','Verma','Rahul Verma','rahul@teacher.com','+91-98765006',NULL,NULL,NULL,NULL,'Teaching','Teacher','Full-Time','2020-06-01',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,50000.00,'Active',NULL,'8b90d86f-8442-4425-9d1e-475c9f879aa2','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('EMP003','Priya','Sharma','Priya Sharma','priya@teacher.com','+91-98765003',NULL,NULL,NULL,NULL,'Teaching','Teacher','Full-Time','2020-06-01',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,50000.00,'Active',NULL,'b1edfea4-d604-4f8c-959b-cdf713d21e84','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('EMP008','Vikram','Singh','Vikram Singh','vikram@teacher.com','+91-98765008',NULL,NULL,NULL,NULL,'Teaching','Teacher','Full-Time','2020-06-01',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,50000.00,'Active',NULL,'d2be05f9-8e35-4aa8-a17e-c776cf4e3afd','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('EMP005','Sunita','Devi','Sunita Devi','sunita@teacher.com','+91-98765005',NULL,NULL,NULL,NULL,'Teaching','Teacher','Full-Time','2020-06-01',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,50000.00,'Active',NULL,'d99413b6-624f-4d3d-ba74-7dbee9fac4c1','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('EMP007','Deepa','Nair','Deepa Nair','deepa@teacher.com','+91-98765007',NULL,NULL,NULL,NULL,'Teaching','Teacher','Full-Time','2020-06-01',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,50000.00,'Active',NULL,'e4c52501-b2fc-472d-906b-f1fdef0d3dc5','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('EMP001','Jane','Smith','Jane Smith','jane@teacher.com','+91-98765001',NULL,NULL,NULL,NULL,'Teaching','Teacher','Full-Time','2020-06-01',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,50000.00,'Active',NULL,'f0bc267d-4453-40bf-9bcf-f3c888fcb48c','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('123456','Vamsi','Kotha','Surya Vamsi Kotha','vamsi@gmail.com','8989890899',NULL,'Male',NULL,NULL,'Teaching','Senior Teacher','Contract','2026-05-28',NULL,NULL,'B.Tech',2.0,'Room No: 403, Next Gen Ultimate PG, Vinayak Nagar',NULL,'Hyderabad','Tamil Nadu','500076','B+',NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,4000.00,'Active',NULL,'fdcad9f1-1fe6-4bea-bac6-6e005f848715','{}','2026-05-26 22:18:02','2026-05-26 22:18:02',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `staff` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `staff_subjects`
--

DROP TABLE IF EXISTS `staff_subjects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staff_subjects` (
  `staff_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `subject_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_primary` tinyint(1) NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_staff_subjects_staff_subject` (`school_id`,`staff_id`,`subject_id`),
  KEY `fk_staff_subjects_subject_id_subjects` (`subject_id`),
  KEY `idx_staff_subjects_staff` (`staff_id`),
  KEY `ix_staff_subjects_school_id` (`school_id`),
  KEY `ix_staff_subjects_is_active` (`is_active`),
  CONSTRAINT `fk_staff_subjects_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_staff_subjects_staff_id_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_staff_subjects_subject_id_subjects` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staff_subjects`
--

LOCK TABLES `staff_subjects` WRITE;
/*!40000 ALTER TABLE `staff_subjects` DISABLE KEYS */;
INSERT INTO `staff_subjects` VALUES ('8b90d86f-8442-4425-9d1e-475c9f879aa2','4daac19b-24a9-41e8-917e-1e9f2192c8aa',1,'19d0b836-7561-4f97-b4aa-e5a0576cfda1','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('b1edfea4-d604-4f8c-959b-cdf713d21e84','5ca31131-7785-451f-a040-447944567741',1,'2ba3d67b-0241-400f-8ec5-477d283b39da','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('d2be05f9-8e35-4aa8-a17e-c776cf4e3afd','3d785786-e000-4d52-8387-d4aa0486027c',1,'70c4aa83-bff7-47fa-b1e6-2b4e5f4fe903','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('7794dcaf-e97c-41cb-83f8-c5ec057f8bd0','92d8d000-6478-4270-9a18-77b9d802885d',1,'8c9c432c-ade8-4416-871f-079418df0618','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('e4c52501-b2fc-472d-906b-f1fdef0d3dc5','6c54e1e1-56f6-4988-9c75-ab67ab9c2be5',1,'a1416e8f-3ce8-43b4-ba69-542a27b3ef6a','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('65401672-19ab-4e98-9fa7-6d58e899d261','a193e74b-557e-4898-8917-7781724a24b9',1,'b94fa09d-d33e-4853-8fb1-c80e9d45ce99','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('d99413b6-624f-4d3d-ba74-7dbee9fac4c1','890c0072-03e5-4611-a4e2-ab73f0034dc4',1,'be25c02e-cea9-4d9c-bf20-8568e8d9c5c4','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('f0bc267d-4453-40bf-9bcf-f3c888fcb48c','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb',1,'e11a9883-943b-445b-9a9b-ceeb9a8a41a8','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `staff_subjects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_enrollments`
--

DROP TABLE IF EXISTS `student_enrollments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_enrollments` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `class_section_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `roll_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `enrollment_date` date DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_student_enrollments_year` (`school_id`,`academic_year_id`,`student_id`),
  KEY `fk_student_enrollments_academic_year_id_academic_years` (`academic_year_id`),
  KEY `ix_student_enrollments_school_id` (`school_id`),
  KEY `idx_student_enrollments_class` (`class_section_id`,`academic_year_id`),
  KEY `idx_student_enrollments_student` (`student_id`,`academic_year_id`),
  KEY `ix_student_enrollments_is_active` (`is_active`),
  CONSTRAINT `fk_student_enrollments_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_student_enrollments_class_section_id_class_sections` FOREIGN KEY (`class_section_id`) REFERENCES `class_sections` (`id`),
  CONSTRAINT `fk_student_enrollments_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_student_enrollments_student_id_students` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_enrollments`
--

LOCK TABLES `student_enrollments` WRITE;
/*!40000 ALTER TABLE `student_enrollments` DISABLE KEYS */;
INSERT INTO `student_enrollments` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','751b589f-90f5-489f-9404-e2066a3cdd3c','856f3425-69b3-44e4-a291-8f6b604441d4','007','2025-06-01','Active','1c91f441-2f58-48fd-a249-f5e4427d0b87','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','d4145bca-3b08-489a-a80d-c8141b3ce925','8f4911ac-187b-41a2-8866-1fc178a4343d','002','2025-06-01','Active','1f844b3c-63df-484d-8e02-c00e5a10c1ce','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','0ede033b-39d9-43c3-83d7-f8eb6e0cc230','4d085a47-3bb2-45e5-a900-e90dd767b0c7','011','2025-06-01','Active','23ea5624-30f6-458e-9998-75cf0daa7007','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','bf6e92c2-a726-4a5f-950f-9140cf3e7e0f','4d085a47-3bb2-45e5-a900-e90dd767b0c7','013','2025-06-01','Active','30d4dd51-232c-4d5a-ab93-45d7426ebc68','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','2fee70ec-a7b6-45ed-9a65-35a584bd47f1','954300c6-bda4-498b-998f-c14d7ecdd53d','015','2025-06-01','Active','4002486b-b265-4351-88af-45120ebe8a69','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4823e6f0-69e2-4a1c-a0ff-1fb9653767d5','8f4911ac-187b-41a2-8866-1fc178a4343d','001','2025-06-01','Active','4430e367-e2ff-4798-885f-6e0671dda945','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','49abb42b-340e-4e49-aac5-c99e8beed487','7e50dbc3-27ea-4be6-bc04-c4c29525b4f5','010','2025-06-01','Active','47fe3c37-35b5-45cc-b2e3-c8466da91926','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','ad70329a-aaa8-4ebe-86f5-06aa25a836b7','954300c6-bda4-498b-998f-c14d7ecdd53d','014','2025-06-01','Active','66892826-acbd-49d2-904b-b8ec67d2cba3','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','68bea932-1242-4277-84e1-a2acfc7bdf9a','856f3425-69b3-44e4-a291-8f6b604441d4','006','2025-06-01','Active','6fbd5e84-79f7-4fec-881a-bf035c8f86db','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','37e22b29-cb5d-483d-816c-49d31de35c80','7e50dbc3-27ea-4be6-bc04-c4c29525b4f5','009','2025-06-01','Active','70ee7a18-8242-4999-8bfa-8cc3a39f0466','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','3778f4c0-2c67-479d-9dd2-4f84f696a1dc','f29d33cd-bb3b-430f-be2d-e0496256915b','005','2025-06-01','Active','794de709-7c98-4195-ad83-341754696d9c','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','13118271-a690-4bd5-a38b-4cc13334f292','8f4911ac-187b-41a2-8866-1fc178a4343d','003','2025-06-01','Active','8c6d4c43-4381-49c2-a232-5caeaec4ddd7','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','394ceb26-22f3-4d34-8881-53472e29ad43','f29d33cd-bb3b-430f-be2d-e0496256915b','004','2025-06-01','Active','9ef946a5-9edc-4924-904d-aed9fbe40ec2','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','169f1c23-38ce-463b-ada2-e0c0e6681177','4d085a47-3bb2-45e5-a900-e90dd767b0c7','012','2025-06-01','Active','da3fb5c9-bb23-4f1c-80c4-67780b4e4c4e','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','73c51201-b44a-4474-8ed2-180befe293e1','856f3425-69b3-44e4-a291-8f6b604441d4','008','2025-06-01','Active','e58dcac3-4e5f-4e24-9ec9-e34652aa8235','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `student_enrollments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_mentors`
--

DROP TABLE IF EXISTS `student_mentors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_mentors` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `staff_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `assigned_date` date DEFAULT NULL,
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_student_mentors_year` (`school_id`,`academic_year_id`,`student_id`),
  KEY `fk_student_mentors_academic_year_id_academic_years` (`academic_year_id`),
  KEY `fk_student_mentors_student_id_students` (`student_id`),
  KEY `idx_student_mentors_staff` (`staff_id`,`academic_year_id`),
  KEY `ix_student_mentors_is_active` (`is_active`),
  KEY `ix_student_mentors_school_id` (`school_id`),
  CONSTRAINT `fk_student_mentors_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_student_mentors_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_student_mentors_staff_id_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`),
  CONSTRAINT `fk_student_mentors_student_id_students` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_mentors`
--

LOCK TABLES `student_mentors` WRITE;
/*!40000 ALTER TABLE `student_mentors` DISABLE KEYS */;
INSERT INTO `student_mentors` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','13118271-a690-4bd5-a38b-4cc13334f292','b1edfea4-d604-4f8c-959b-cdf713d21e84','2025-06-15',NULL,'06552d20-f048-4ce1-8fd4-876d5c6eacdc','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','3778f4c0-2c67-479d-9dd2-4f84f696a1dc','d99413b6-624f-4d3d-ba74-7dbee9fac4c1','2025-06-15',NULL,'0fb92a76-12dd-4595-8764-2094161cfee5','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','394ceb26-22f3-4d34-8881-53472e29ad43','65401672-19ab-4e98-9fa7-6d58e899d261','2025-06-15',NULL,'72a17dc2-b4ad-4411-aac2-399e6f86a959','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','d4145bca-3b08-489a-a80d-c8141b3ce925','7794dcaf-e97c-41cb-83f8-c5ec057f8bd0','2025-06-15',NULL,'e73e88a9-9c07-461b-8783-1e29a3d26e80','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4823e6f0-69e2-4a1c-a0ff-1fb9653767d5','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','2025-06-15',NULL,'f092d88a-b484-4d9e-b03d-8252f8f1c0d6','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `student_mentors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_parents`
--

DROP TABLE IF EXISTS `student_parents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_parents` (
  `student_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `parent_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_student_parents` (`school_id`,`student_id`,`parent_id`),
  KEY `idx_student_parents_parent` (`parent_id`),
  KEY `ix_student_parents_is_active` (`is_active`),
  KEY `idx_student_parents_student` (`student_id`),
  KEY `ix_student_parents_school_id` (`school_id`),
  CONSTRAINT `fk_student_parents_parent_id_parents` FOREIGN KEY (`parent_id`) REFERENCES `parents` (`id`),
  CONSTRAINT `fk_student_parents_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_student_parents_student_id_students` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_parents`
--

LOCK TABLES `student_parents` WRITE;
/*!40000 ALTER TABLE `student_parents` DISABLE KEYS */;
INSERT INTO `student_parents` VALUES ('3778f4c0-2c67-479d-9dd2-4f84f696a1dc','6a1963f0-5a5b-4eb2-8a9d-8a7715c172ed','258c47eb-dc4f-4db5-842e-a29f38929f8e','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('37e22b29-cb5d-483d-816c-49d31de35c80','8eeb34e0-0dc0-4857-8ddd-604cffef8740','30ea770e-82c7-4981-b568-e1e77e962c4a','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('13118271-a690-4bd5-a38b-4cc13334f292','ca246da3-0985-4874-b044-fe249a8dd2c3','3a57134d-0e1c-4928-b253-daa84eec512c','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('73c51201-b44a-4474-8ed2-180befe293e1','3248eaf0-9084-44f0-b1b2-6a6de15fe349','3abbde9a-90dd-4013-8b31-6db0884e4dab','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('2fee70ec-a7b6-45ed-9a65-35a584bd47f1','fc8c71d6-0ff2-4eaf-9339-235515fe323a','584b4957-803f-47d3-bdc6-b160c4bd128b','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('d4145bca-3b08-489a-a80d-c8141b3ce925','fc93fc6b-ac92-4617-a17d-76198db7883e','5ab2431e-951b-4b87-8355-ddf6cfc830cc','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('68bea932-1242-4277-84e1-a2acfc7bdf9a','1a3ccc7a-4a09-42bd-8f03-2144e19d13f4','605ababa-00d4-4961-8592-a8303c2baf2c','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('169f1c23-38ce-463b-ada2-e0c0e6681177','7e0e8faf-d2ec-4fe3-953a-b49749445a37','6ecb37f1-5f38-42c8-9ea0-0e442f67eea5','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('751b589f-90f5-489f-9404-e2066a3cdd3c','2c0d5879-10f3-4eb6-bda3-35a3b28f983b','77f004fa-1635-4046-bb79-db9a1c6a6f39','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('49abb42b-340e-4e49-aac5-c99e8beed487','7aca2431-96c8-46a7-bbcb-fc847341ebb6','7ceee868-112a-4733-9c27-8865b281277a','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0ede033b-39d9-43c3-83d7-f8eb6e0cc230','936b5d94-02d4-4ee9-989a-79fcff65c79d','81485aae-2c06-4cf8-964b-abf972c2dab1','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('bf6e92c2-a726-4a5f-950f-9140cf3e7e0f','59e4efea-d914-471e-be27-4bcbf1de9c5b','8173b74c-c02e-4a27-a539-a87c1b58ea90','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('394ceb26-22f3-4d34-8881-53472e29ad43','4f08f177-b733-4436-b2d2-955574733911','e1e21f4c-514a-4260-a9c6-493867dee004','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('4823e6f0-69e2-4a1c-a0ff-1fb9653767d5','47f0fd84-19cd-4683-890f-58f0afc1e320','e755b40e-56c9-48a8-bba7-06e1673fa2b4','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('ad70329a-aaa8-4ebe-86f5-06aa25a836b7','44134cdd-f5f3-460b-890c-33b43afed2ad','f03329bf-2cf2-439c-88b0-4e2e470345e8','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `student_parents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_transport`
--

DROP TABLE IF EXISTS `student_transport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_transport` (
  `student_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `route_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `pickup_point` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `drop_point` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_student_transport_school_student_year` (`school_id`,`student_id`,`academic_year_id`),
  KEY `fk_student_transport_academic_year_id_academic_years` (`academic_year_id`),
  KEY `idx_student_transport_route` (`route_id`,`academic_year_id`),
  KEY `ix_student_transport_school_id` (`school_id`),
  KEY `idx_student_transport_student` (`student_id`),
  KEY `ix_student_transport_is_active` (`is_active`),
  CONSTRAINT `fk_student_transport_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_student_transport_route_id_routes` FOREIGN KEY (`route_id`) REFERENCES `routes` (`id`),
  CONSTRAINT `fk_student_transport_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_student_transport_student_id_students` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_transport`
--

LOCK TABLES `student_transport` WRITE;
/*!40000 ALTER TABLE `student_transport` DISABLE KEYS */;
INSERT INTO `student_transport` VALUES ('13118271-a690-4bd5-a38b-4cc13334f292','12b7ff65-6b1e-4b7a-a5c3-c7fec5a04acb','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Stop 3','Stop 3','21517030-e4d4-4aa1-88f2-5d382483f95d','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('d4145bca-3b08-489a-a80d-c8141b3ce925','4a8fa349-28a2-4e52-a252-3fc5697d8fbd','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Stop 2','Stop 2','5d8c7eba-637f-49aa-93ea-3bfb470469d1','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('3778f4c0-2c67-479d-9dd2-4f84f696a1dc','4a8fa349-28a2-4e52-a252-3fc5697d8fbd','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Stop 5','Stop 5','64657678-35c7-4ea7-83e6-677a776d0510','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('394ceb26-22f3-4d34-8881-53472e29ad43','aac95525-6d47-4cbb-b55a-799fa917e4cc','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Stop 4','Stop 4','6565b5ff-5077-4ec3-90e9-590940c6608b','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('4823e6f0-69e2-4a1c-a0ff-1fb9653767d5','aac95525-6d47-4cbb-b55a-799fa917e4cc','0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','Stop 1','Stop 1','72fa397c-2da9-4311-b2b2-5cfcb53fe52f','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `student_transport` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `admission_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `full_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `gender` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `photo_url` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `blood_group` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nationality` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `religion` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `caste` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mother_tongue` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `medical_conditions` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `allergies` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `address_line1` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address_line2` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `city` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `state` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pincode` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `admission_date` date DEFAULT NULL,
  `left_date` date DEFAULT NULL,
  `left_reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `previous_school` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `transfer_certificate_number` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `aadhar_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_students_school_admission` (`school_id`,`admission_number`),
  KEY `idx_students_name` (`school_id`,`full_name`),
  KEY `ix_students_school_id` (`school_id`),
  KEY `ix_students_is_active` (`is_active`),
  KEY `idx_students_status` (`school_id`,`status`),
  CONSTRAINT `fk_students_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES ('STU011','John','Doe','John Doe','john@student.com','+91-98700011','Male','2010-03-15',NULL,'B+',NULL,NULL,NULL,NULL,NULL,NULL,'123 Main St',NULL,'Bangalore','Karnataka','560001','2023-06-01',NULL,NULL,NULL,NULL,'Active',NULL,'0ede033b-39d9-43c3-83d7-f8eb6e0cc230','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('STU003','Rohan','Patel','Rohan Patel','rohan@student.com','+91-98700003','Male','2010-03-15',NULL,'B+',NULL,NULL,NULL,NULL,NULL,NULL,'123 Main St',NULL,'Bangalore','Karnataka','560001','2023-06-01',NULL,NULL,NULL,NULL,'Active',NULL,'13118271-a690-4bd5-a38b-4cc13334f292','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('STU012','Kavya','Iyer','Kavya Iyer','kavya@student.com','+91-98700012','Female','2010-03-15',NULL,'B+',NULL,NULL,NULL,NULL,NULL,NULL,'123 Main St',NULL,'Bangalore','Karnataka','560001','2023-06-01',NULL,NULL,NULL,NULL,'Active',NULL,'169f1c23-38ce-463b-ada2-e0c0e6681177','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('STU015','Harsh','Agarwal','Harsh Agarwal','harsh@student.com','+91-98700015','Male','2010-03-15',NULL,'B+',NULL,NULL,NULL,NULL,NULL,NULL,'123 Main St',NULL,'Bangalore','Karnataka','560001','2023-06-01',NULL,NULL,NULL,NULL,'Active',NULL,'2fee70ec-a7b6-45ed-9a65-35a584bd47f1','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('STU005','Karthik','Rao','Karthik Rao','karthik@student.com','+91-98700005','Male','2010-03-15',NULL,'B+',NULL,NULL,NULL,NULL,NULL,NULL,'123 Main St',NULL,'Bangalore','Karnataka','560001','2023-06-01',NULL,NULL,NULL,NULL,'Active',NULL,'3778f4c0-2c67-479d-9dd2-4f84f696a1dc','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('STU009','Aditya','Kumar','Aditya Kumar','aditya@student.com','+91-98700009','Male','2010-03-15',NULL,'B+',NULL,NULL,NULL,NULL,NULL,NULL,'123 Main St',NULL,'Bangalore','Karnataka','560001','2023-06-01',NULL,NULL,NULL,NULL,'Active',NULL,'37e22b29-cb5d-483d-816c-49d31de35c80','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('STU004','Ananya','Singh','Ananya Singh','ananya@student.com','+91-98700004','Female','2010-03-15',NULL,'B+',NULL,NULL,NULL,NULL,NULL,NULL,'123 Main St',NULL,'Bangalore','Karnataka','560001','2023-06-01',NULL,NULL,NULL,NULL,'Active',NULL,'394ceb26-22f3-4d34-8881-53472e29ad43','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('STU001','Arjun','Mehta','Arjun Mehta','arjun@student.com','+91-98700001','Male','2010-03-15',NULL,'B+',NULL,NULL,NULL,NULL,NULL,NULL,'123 Main St',NULL,'Bangalore','Karnataka','560001','2023-06-01',NULL,NULL,NULL,NULL,'Active',NULL,'4823e6f0-69e2-4a1c-a0ff-1fb9653767d5','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('STU010','Meghna','Das','Meghna Das','meghna@student.com','+91-98700010','Female','2010-03-15',NULL,'B+',NULL,NULL,NULL,NULL,NULL,NULL,'123 Main St',NULL,'Bangalore','Karnataka','560001','2023-06-01',NULL,NULL,NULL,NULL,'Active',NULL,'49abb42b-340e-4e49-aac5-c99e8beed487','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('STU006','Divya','Sharma','Divya Sharma','divya@student.com','+91-98700006','Female','2010-03-15',NULL,'B+',NULL,NULL,NULL,NULL,NULL,NULL,'123 Main St',NULL,'Bangalore','Karnataka','560001','2023-06-01',NULL,NULL,NULL,NULL,'Active',NULL,'68bea932-1242-4277-84e1-a2acfc7bdf9a','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('STU008','Pooja','Reddy','Pooja Reddy','pooja@student.com','+91-98700008','Female','2010-03-15',NULL,'B+',NULL,NULL,NULL,NULL,NULL,NULL,'123 Main St',NULL,'Bangalore','Karnataka','560001','2023-06-01',NULL,NULL,NULL,NULL,'Active',NULL,'73c51201-b44a-4474-8ed2-180befe293e1','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('STU007','Varun','Nair','Varun Nair','varun@student.com','+91-98700007','Male','2010-03-15',NULL,'B+',NULL,NULL,NULL,NULL,NULL,NULL,'123 Main St',NULL,'Bangalore','Karnataka','560001','2023-06-01',NULL,NULL,NULL,NULL,'Active',NULL,'751b589f-90f5-489f-9404-e2066a3cdd3c','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('STU014','Riya','Chopra','Riya Chopra','riya@student.com','+91-98700014','Female','2010-03-15',NULL,'B+',NULL,NULL,NULL,NULL,NULL,NULL,'123 Main St',NULL,'Bangalore','Karnataka','560001','2023-06-01',NULL,NULL,NULL,NULL,'Active',NULL,'ad70329a-aaa8-4ebe-86f5-06aa25a836b7','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('STU013','Nikhil','Verma','Nikhil Verma','nikhil@student.com','+91-98700013','Male','2010-03-15',NULL,'B+',NULL,NULL,NULL,NULL,NULL,NULL,'123 Main St',NULL,'Bangalore','Karnataka','560001','2023-06-01',NULL,NULL,NULL,NULL,'Active',NULL,'bf6e92c2-a726-4a5f-950f-9140cf3e7e0f','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('STU002','Sneha','Gupta','Sneha Gupta','sneha@student.com','+91-98700002','Female','2010-03-15',NULL,'B+',NULL,NULL,NULL,NULL,NULL,NULL,'123 Main St',NULL,'Bangalore','Karnataka','560001','2023-06-01',NULL,NULL,NULL,NULL,'Active',NULL,'d4145bca-3b08-489a-a80d-c8141b3ce925','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subjects`
--

DROP TABLE IF EXISTS `subjects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subjects` (
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_subjects_school_name` (`school_id`,`name`),
  UNIQUE KEY `uq_subjects_school_code` (`school_id`,`code`),
  KEY `ix_subjects_school_id` (`school_id`),
  KEY `ix_subjects_is_active` (`is_active`),
  CONSTRAINT `fk_subjects_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subjects`
--

LOCK TABLES `subjects` WRITE;
/*!40000 ALTER TABLE `subjects` DISABLE KEYS */;
INSERT INTO `subjects` VALUES ('Art','ART',NULL,'3d785786-e000-4d52-8387-d4aa0486027c','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Computer Science','COM',NULL,'4daac19b-24a9-41e8-917e-1e9f2192c8aa','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Science','SCI',NULL,'5ca31131-7785-451f-a040-447944567741','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Physical Education','PHY',NULL,'6c54e1e1-56f6-4988-9c75-ab67ab9c2be5','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Hindi','HIN',NULL,'890c0072-03e5-4611-a4e2-ab73f0034dc4','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('English','ENG',NULL,'92d8d000-6478-4270-9a18-77b9d802885d','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Social Studies','SOC',NULL,'a193e74b-557e-4898-8917-7781724a24b9','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('Mathematics','MAT',NULL,'ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `subjects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `timetable_slots`
--

DROP TABLE IF EXISTS `timetable_slots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `timetable_slots` (
  `academic_year_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `class_section_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `period_config_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `day_of_week` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `subject_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `staff_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `slot_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_timetable_slots_class` (`school_id`,`academic_year_id`,`class_section_id`,`period_config_id`,`day_of_week`),
  KEY `fk_timetable_slots_academic_year_id_academic_years` (`academic_year_id`),
  KEY `fk_timetable_slots_period_config_id_period_configs` (`period_config_id`),
  KEY `fk_timetable_slots_subject_id_subjects` (`subject_id`),
  KEY `idx_timetable_slots_class_day` (`class_section_id`,`academic_year_id`,`day_of_week`),
  KEY `idx_timetable_slots_teacher` (`staff_id`,`academic_year_id`,`day_of_week`),
  KEY `ix_timetable_slots_is_active` (`is_active`),
  KEY `ix_timetable_slots_school_id` (`school_id`),
  CONSTRAINT `fk_timetable_slots_academic_year_id_academic_years` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fk_timetable_slots_class_section_id_class_sections` FOREIGN KEY (`class_section_id`) REFERENCES `class_sections` (`id`),
  CONSTRAINT `fk_timetable_slots_period_config_id_period_configs` FOREIGN KEY (`period_config_id`) REFERENCES `period_configs` (`id`),
  CONSTRAINT `fk_timetable_slots_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_timetable_slots_staff_id_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`),
  CONSTRAINT `fk_timetable_slots_subject_id_subjects` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `timetable_slots`
--

LOCK TABLES `timetable_slots` WRITE;
/*!40000 ALTER TABLE `timetable_slots` DISABLE KEYS */;
INSERT INTO `timetable_slots` VALUES ('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','5848ba1f-507c-4f61-9207-4b77558a243d','Saturday','3d785786-e000-4d52-8387-d4aa0486027c','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','02a70f3d-502b-40ca-9317-a90f8d464c10','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','ea31dddf-6b0f-41bb-9aee-770233b71e11','Wednesday','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','07e04b19-2134-44c0-ab45-5eb46688d7d5','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','75cd9edd-322d-44d7-976c-47966d197987','Wednesday','92d8d000-6478-4270-9a18-77b9d802885d','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','08855b27-dbc7-4337-938f-66b32ce2ba00','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','29a8975a-eb2d-4d82-9471-7404470d0152','Monday','890c0072-03e5-4611-a4e2-ab73f0034dc4','d99413b6-624f-4d3d-ba74-7dbee9fac4c1','Lecture','0f084a87-80ef-40fb-83d2-32b1b763233f','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','ea31dddf-6b0f-41bb-9aee-770233b71e11','Monday','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','41a36af7-68e0-4843-8e42-9c09b0ceea13','Lecture','11310406-99fe-4d5d-8a58-2204d7283597','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','29a8975a-eb2d-4d82-9471-7404470d0152','Thursday','890c0072-03e5-4611-a4e2-ab73f0034dc4','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','140458ed-2dc5-4b5f-add9-81864e58004d','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','5848ba1f-507c-4f61-9207-4b77558a243d','Monday','3d785786-e000-4d52-8387-d4aa0486027c','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','149d423e-42dc-45ad-a159-bd9556cd7100','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','5848ba1f-507c-4f61-9207-4b77558a243d','Wednesday','3d785786-e000-4d52-8387-d4aa0486027c','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','1a79f718-487d-496d-b248-d0c05eb6a288','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','5848ba1f-507c-4f61-9207-4b77558a243d','Thursday','3d785786-e000-4d52-8387-d4aa0486027c','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','1c98e0d5-01f7-4627-b1b9-2c70f8e923fd','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','29a8975a-eb2d-4d82-9471-7404470d0152','Wednesday','890c0072-03e5-4611-a4e2-ab73f0034dc4','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','213bd38d-27d6-48f6-a5c1-987003bba42f','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','1a483d85-795f-4ccb-866c-76ba43174d89','Saturday','6c54e1e1-56f6-4988-9c75-ab67ab9c2be5','65401672-19ab-4e98-9fa7-6d58e899d261','Lecture','2595a376-71bb-4d56-a595-8d7e016a0e4d','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','29a8975a-eb2d-4d82-9471-7404470d0152','Wednesday','890c0072-03e5-4611-a4e2-ab73f0034dc4','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','26ab8ffb-e477-4942-84d5-8a55dae60c8a','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','29a8975a-eb2d-4d82-9471-7404470d0152','Monday','890c0072-03e5-4611-a4e2-ab73f0034dc4','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','2ad8261d-6818-43db-b825-5a4c7f77f7ad','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','29a8975a-eb2d-4d82-9471-7404470d0152','Monday','890c0072-03e5-4611-a4e2-ab73f0034dc4','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','2bd94b98-2465-4ac5-ab40-8e2b2a2f347f','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','1a483d85-795f-4ccb-866c-76ba43174d89','Tuesday','6c54e1e1-56f6-4988-9c75-ab67ab9c2be5','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','31131498-29a5-4811-82ff-b8baad3e2707','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','29a8975a-eb2d-4d82-9471-7404470d0152','Saturday','890c0072-03e5-4611-a4e2-ab73f0034dc4','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','3367439c-9dbe-46a4-8096-82281d6b7813','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','75cd9edd-322d-44d7-976c-47966d197987','Friday','92d8d000-6478-4270-9a18-77b9d802885d','65401672-19ab-4e98-9fa7-6d58e899d261','Lecture','343cceac-3d1d-4722-a0fd-2ef6a84185c6','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','5848ba1f-507c-4f61-9207-4b77558a243d','Friday','3d785786-e000-4d52-8387-d4aa0486027c','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','3edc606e-8cdc-427b-91bf-4b539d89f824','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','75cd9edd-322d-44d7-976c-47966d197987','Thursday','92d8d000-6478-4270-9a18-77b9d802885d','65401672-19ab-4e98-9fa7-6d58e899d261','Lecture','4708126f-c424-47ad-b512-7d86ecb14475','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','ea31dddf-6b0f-41bb-9aee-770233b71e11','Monday','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','48181ab1-eba9-4739-9408-3c698f263486','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','1a483d85-795f-4ccb-866c-76ba43174d89','Tuesday','6c54e1e1-56f6-4988-9c75-ab67ab9c2be5','65401672-19ab-4e98-9fa7-6d58e899d261','Lecture','4ae16b5d-80c9-4329-b956-fa8a6a703f00','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','5848ba1f-507c-4f61-9207-4b77558a243d','Monday','3d785786-e000-4d52-8387-d4aa0486027c','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','4bb00a19-c8ba-47c9-9396-42c72124d86b','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','5848ba1f-507c-4f61-9207-4b77558a243d','Monday','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','Lecture','4ca930af-f627-4727-b615-751d59ba4126','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','ea31dddf-6b0f-41bb-9aee-770233b71e11','Thursday','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','41a36af7-68e0-4843-8e42-9c09b0ceea13','Lecture','4dbfa11f-d458-4aa6-b145-fe8e6f691cb0','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','75cd9edd-322d-44d7-976c-47966d197987','Wednesday','92d8d000-6478-4270-9a18-77b9d802885d','65401672-19ab-4e98-9fa7-6d58e899d261','Lecture','4f088c50-9b5a-41b8-90f8-759b5717b04f','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','1a483d85-795f-4ccb-866c-76ba43174d89','Friday','6c54e1e1-56f6-4988-9c75-ab67ab9c2be5','65401672-19ab-4e98-9fa7-6d58e899d261','Lecture','4f8d62cf-a073-44a0-95a9-1d96d2976a80','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','5848ba1f-507c-4f61-9207-4b77558a243d','Tuesday','3d785786-e000-4d52-8387-d4aa0486027c','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','50343606-5388-46aa-8d15-a979faa11024','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','1a483d85-795f-4ccb-866c-76ba43174d89','Thursday','6c54e1e1-56f6-4988-9c75-ab67ab9c2be5','65401672-19ab-4e98-9fa7-6d58e899d261','Lecture','5251f74d-d651-490d-8785-60a2904cb547','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','1a483d85-795f-4ccb-866c-76ba43174d89','Monday','6c54e1e1-56f6-4988-9c75-ab67ab9c2be5','65401672-19ab-4e98-9fa7-6d58e899d261','Lecture','5ddb7bb3-a76a-4f74-a3e1-429efa5bf4f8','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','1a483d85-795f-4ccb-866c-76ba43174d89','Monday','6c54e1e1-56f6-4988-9c75-ab67ab9c2be5','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','6629ac21-ab61-4f7c-9b34-cdfd3541ba09','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','0cc803ac-2c1a-4f20-b53e-e8e4ba63d7a7','Tuesday','4daac19b-24a9-41e8-917e-1e9f2192c8aa','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','691f540b-fcc2-496c-8547-7e2db6550764','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','0cc803ac-2c1a-4f20-b53e-e8e4ba63d7a7','Monday','4daac19b-24a9-41e8-917e-1e9f2192c8aa','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','71efb884-14e3-4362-a43a-63bee42df0ec','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','29a8975a-eb2d-4d82-9471-7404470d0152','Tuesday','890c0072-03e5-4611-a4e2-ab73f0034dc4','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','73c0c522-6ace-4a72-a523-4588e020f7bf','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','75cd9edd-322d-44d7-976c-47966d197987','Friday','92d8d000-6478-4270-9a18-77b9d802885d','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','779379cd-9905-40d8-a563-210b1038a75e','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','75cd9edd-322d-44d7-976c-47966d197987','Tuesday','92d8d000-6478-4270-9a18-77b9d802885d','65401672-19ab-4e98-9fa7-6d58e899d261','Lecture','78c6fb19-29e4-4a6a-88af-0666d0f47a6e','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','5848ba1f-507c-4f61-9207-4b77558a243d','Saturday','3d785786-e000-4d52-8387-d4aa0486027c','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','7b76745e-711f-4f22-9bd6-a1a406784d3c','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','ea31dddf-6b0f-41bb-9aee-770233b71e11','Thursday','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','7b984c6e-2869-42e6-a352-cd1901378d39','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','29a8975a-eb2d-4d82-9471-7404470d0152','Friday','890c0072-03e5-4611-a4e2-ab73f0034dc4','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','7bc0c97e-b1ff-4617-afda-9459c22f6316','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','5848ba1f-507c-4f61-9207-4b77558a243d','Thursday','3d785786-e000-4d52-8387-d4aa0486027c','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','855a475f-2aad-4795-97c6-dcb8d1440ebf','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','ea31dddf-6b0f-41bb-9aee-770233b71e11','Saturday','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','91affd65-2dbd-4608-a05c-3e342ade86f6','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','75cd9edd-322d-44d7-976c-47966d197987','Saturday','92d8d000-6478-4270-9a18-77b9d802885d','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','91c3bf7a-40f2-4783-94ad-d5e348fd7a77','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','0cc803ac-2c1a-4f20-b53e-e8e4ba63d7a7','Saturday','4daac19b-24a9-41e8-917e-1e9f2192c8aa','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','94629af7-163e-4089-ad11-e20e5b3245fd','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','ea31dddf-6b0f-41bb-9aee-770233b71e11','Tuesday','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','96bee162-bd74-4b95-ab28-9b82d410fe74','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','29a8975a-eb2d-4d82-9471-7404470d0152','Saturday','890c0072-03e5-4611-a4e2-ab73f0034dc4','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','97cf1136-5ee2-4941-bf74-c44bb4aed950','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','5848ba1f-507c-4f61-9207-4b77558a243d','Tuesday','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','f0bc267d-4453-40bf-9bcf-f3c888fcb48c','Lecture','98424b75-4025-4e39-bd1a-a1340df3d7c9','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','ea31dddf-6b0f-41bb-9aee-770233b71e11','Tuesday','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','41a36af7-68e0-4843-8e42-9c09b0ceea13','Lecture','98a22097-34dd-4853-8886-ca4e47cca972','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','ea31dddf-6b0f-41bb-9aee-770233b71e11','Wednesday','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','41a36af7-68e0-4843-8e42-9c09b0ceea13','Lecture','9c0a93a6-7df4-44b0-aaf8-d9846188d0cd','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','75cd9edd-322d-44d7-976c-47966d197987','Tuesday','92d8d000-6478-4270-9a18-77b9d802885d','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','a12bc6cf-c0f5-410c-a198-1d27ecb26394','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','ea31dddf-6b0f-41bb-9aee-770233b71e11','Friday','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','a160a986-3566-46f3-9edf-e8b28e45e059','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','5848ba1f-507c-4f61-9207-4b77558a243d','Friday','3d785786-e000-4d52-8387-d4aa0486027c','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','a1c8eb78-473d-4503-91d3-ed2e2882f461','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','75cd9edd-322d-44d7-976c-47966d197987','Monday','5ca31131-7785-451f-a040-447944567741','b1edfea4-d604-4f8c-959b-cdf713d21e84','Lecture','a1fcae96-a034-42c0-9e8d-9f98f8333313','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','1a483d85-795f-4ccb-866c-76ba43174d89','Wednesday','6c54e1e1-56f6-4988-9c75-ab67ab9c2be5','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','a2a37c05-8d19-4e10-a5f6-b93fad4f8b8c','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','ea31dddf-6b0f-41bb-9aee-770233b71e11','Friday','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','41a36af7-68e0-4843-8e42-9c09b0ceea13','Lecture','a7cc99e4-04ed-4f59-9f5d-8d1795f584a7','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','75cd9edd-322d-44d7-976c-47966d197987','Thursday','92d8d000-6478-4270-9a18-77b9d802885d','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','a88bed49-1576-4ccc-9805-15ed105c19dc','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','0cc803ac-2c1a-4f20-b53e-e8e4ba63d7a7','Tuesday','92d8d000-6478-4270-9a18-77b9d802885d','7794dcaf-e97c-41cb-83f8-c5ec057f8bd0','Lecture','a91a2006-e8a6-4364-a8f7-f481e7cbe78a','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','0cc803ac-2c1a-4f20-b53e-e8e4ba63d7a7','Saturday','4daac19b-24a9-41e8-917e-1e9f2192c8aa','41a36af7-68e0-4843-8e42-9c09b0ceea13','Lecture','a9e4ce99-9fc6-4c09-b319-6fcb1c02c458','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','75cd9edd-322d-44d7-976c-47966d197987','Saturday','92d8d000-6478-4270-9a18-77b9d802885d','65401672-19ab-4e98-9fa7-6d58e899d261','Lecture','ac8de2f1-233c-4c13-a179-46aac410ec2a','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','1a483d85-795f-4ccb-866c-76ba43174d89','Saturday','6c54e1e1-56f6-4988-9c75-ab67ab9c2be5','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','ad468d3e-4898-494b-b066-4fdf6802f997','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','0cc803ac-2c1a-4f20-b53e-e8e4ba63d7a7','Thursday','4daac19b-24a9-41e8-917e-1e9f2192c8aa','41a36af7-68e0-4843-8e42-9c09b0ceea13','Lecture','adfe89c6-c901-4b43-9f0b-441d852fd255','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','1a483d85-795f-4ccb-866c-76ba43174d89','Wednesday','6c54e1e1-56f6-4988-9c75-ab67ab9c2be5','65401672-19ab-4e98-9fa7-6d58e899d261','Lecture','ae9e5ea2-8f1b-4fae-bc29-75527d21687a','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','29a8975a-eb2d-4d82-9471-7404470d0152','Tuesday','890c0072-03e5-4611-a4e2-ab73f0034dc4','d99413b6-624f-4d3d-ba74-7dbee9fac4c1','Lecture','af3516e8-0042-48ff-8c7f-bd9446d18650','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','75cd9edd-322d-44d7-976c-47966d197987','Monday','92d8d000-6478-4270-9a18-77b9d802885d','65401672-19ab-4e98-9fa7-6d58e899d261','Lecture','b2a08632-8153-434c-9d34-b836c2217616','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','ea31dddf-6b0f-41bb-9aee-770233b71e11','Monday','4daac19b-24a9-41e8-917e-1e9f2192c8aa','8b90d86f-8442-4425-9d1e-475c9f879aa2','Lecture','b6882d5b-e7bd-4dcf-b25b-6bc493d73c06','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','0cc803ac-2c1a-4f20-b53e-e8e4ba63d7a7','Tuesday','4daac19b-24a9-41e8-917e-1e9f2192c8aa','41a36af7-68e0-4843-8e42-9c09b0ceea13','Lecture','ba115820-2c87-40be-b838-936b83a749b8','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','75cd9edd-322d-44d7-976c-47966d197987','Monday','92d8d000-6478-4270-9a18-77b9d802885d','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','bb2dff91-3396-4274-8018-9e2c4b8a7fb9','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','75cd9edd-322d-44d7-976c-47966d197987','Tuesday','5ca31131-7785-451f-a040-447944567741','b1edfea4-d604-4f8c-959b-cdf713d21e84','Lecture','bb8272b3-7180-478f-aaeb-978e8fbbf79f','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','29a8975a-eb2d-4d82-9471-7404470d0152','Tuesday','890c0072-03e5-4611-a4e2-ab73f0034dc4','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','bd317693-496c-479d-a8ba-c11324e68443','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','0cc803ac-2c1a-4f20-b53e-e8e4ba63d7a7','Wednesday','4daac19b-24a9-41e8-917e-1e9f2192c8aa','41a36af7-68e0-4843-8e42-9c09b0ceea13','Lecture','ca19ea32-2d68-42b7-ab9f-873681d44c22','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','5848ba1f-507c-4f61-9207-4b77558a243d','Tuesday','3d785786-e000-4d52-8387-d4aa0486027c','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','ca643240-e555-463a-a903-2afa5fcbfee1','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','ea31dddf-6b0f-41bb-9aee-770233b71e11','Saturday','ebc3b0d1-82f9-468c-9ba1-725b94d1afeb','41a36af7-68e0-4843-8e42-9c09b0ceea13','Lecture','cde3904d-1bd7-4371-82cc-bf2566ecdda5','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','1a483d85-795f-4ccb-866c-76ba43174d89','Friday','6c54e1e1-56f6-4988-9c75-ab67ab9c2be5','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','ceebe7d1-0f6a-4021-ac86-dee9c3c8cc0e','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','0cc803ac-2c1a-4f20-b53e-e8e4ba63d7a7','Monday','92d8d000-6478-4270-9a18-77b9d802885d','7794dcaf-e97c-41cb-83f8-c5ec057f8bd0','Lecture','d550ac59-297a-455f-a2a9-0e60b1c9d5be','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','29a8975a-eb2d-4d82-9471-7404470d0152','Friday','890c0072-03e5-4611-a4e2-ab73f0034dc4','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','d8420ba1-e608-4519-b497-0b256b503a52','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','0cc803ac-2c1a-4f20-b53e-e8e4ba63d7a7','Thursday','4daac19b-24a9-41e8-917e-1e9f2192c8aa','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','db56a62f-6d75-4f8f-bddc-6c8b4451625c','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','5848ba1f-507c-4f61-9207-4b77558a243d','Wednesday','3d785786-e000-4d52-8387-d4aa0486027c','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','dc768ddc-cc2c-4cf7-bacd-c0fe25883ebe','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','8f4911ac-187b-41a2-8866-1fc178a4343d','ea31dddf-6b0f-41bb-9aee-770233b71e11','Tuesday','4daac19b-24a9-41e8-917e-1e9f2192c8aa','8b90d86f-8442-4425-9d1e-475c9f879aa2','Lecture','df495a14-61d9-4d6f-865e-577619807fd4','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','0cc803ac-2c1a-4f20-b53e-e8e4ba63d7a7','Wednesday','4daac19b-24a9-41e8-917e-1e9f2192c8aa','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','e5cc2223-5585-46f5-9479-834ec662f946','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','29a8975a-eb2d-4d82-9471-7404470d0152','Thursday','890c0072-03e5-4611-a4e2-ab73f0034dc4','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','ec582e5c-062c-4a4d-9093-1fa7491ac93f','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','0cc803ac-2c1a-4f20-b53e-e8e4ba63d7a7','Friday','4daac19b-24a9-41e8-917e-1e9f2192c8aa','41a36af7-68e0-4843-8e42-9c09b0ceea13','Lecture','f1293a3f-5ced-4776-a547-f05230ff7949','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','0cc803ac-2c1a-4f20-b53e-e8e4ba63d7a7','Friday','4daac19b-24a9-41e8-917e-1e9f2192c8aa','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','f2823b25-62b5-4f21-ab29-0d3ec5c3fe67','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','4d085a47-3bb2-45e5-a900-e90dd767b0c7','0cc803ac-2c1a-4f20-b53e-e8e4ba63d7a7','Monday','4daac19b-24a9-41e8-917e-1e9f2192c8aa','41a36af7-68e0-4843-8e42-9c09b0ceea13','Lecture','f4d463a4-009e-4e4f-b27f-55bb78681315','{}','2026-05-26 23:43:47','2026-05-26 23:43:47',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('0bdda13b-1d27-4ca3-a38c-ed15a4a8c1e1','856f3425-69b3-44e4-a291-8f6b604441d4','1a483d85-795f-4ccb-866c-76ba43174d89','Thursday','6c54e1e1-56f6-4988-9c75-ab67ab9c2be5','2334c80d-0b88-4096-98ff-398bf9a88855','Lecture','fb28ecfc-db12-4502-acfb-06d1fb01ee86','{}','2026-05-26 23:38:32','2026-05-26 23:38:32',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `timetable_slots` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `avatar_url` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `last_login_at` datetime DEFAULT NULL,
  `password_reset_token` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `password_reset_expires` datetime DEFAULT NULL,
  `is_locked` tinyint(1) NOT NULL,
  `failed_login_attempts` int NOT NULL,
  `staff_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `student_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `parent_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_users_school_email` (`school_id`,`email`),
  KEY `ix_users_school_id` (`school_id`),
  KEY `ix_users_is_active` (`is_active`),
  KEY `fk_users_student_id_students` (`student_id`),
  KEY `fk_users_parent_id_parents` (`parent_id`),
  KEY `fk_users_staff_id_staff` (`staff_id`),
  CONSTRAINT `fk_users_parent_id_parents` FOREIGN KEY (`parent_id`) REFERENCES `parents` (`id`),
  CONSTRAINT `fk_users_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `fk_users_staff_id_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`),
  CONSTRAINT `fk_users_student_id_students` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('1058e8f0-ec4e-4d1c-ae0d-c8e631566286','659a72a6-284a-4b1b-b460-018096237cb9','vamsi@school.com','$2b$12$o2jrWbfu0dJW14D91Rpp6uuo225Cmwb7/urgXlFRr6v9I5.H/o7ty','Kotha Vamsi','teacher','8989898799',NULL,NULL,NULL,NULL,0,0,NULL,NULL,NULL,'{}','2026-05-26 21:50:02','2026-05-26 21:50:02',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL),('25e2d506-932b-4457-98a9-948594c6e690','659a72a6-284a-4b1b-b460-018096237cb9','suryavamsikotha@gmail.com','$2b$12$8L/6UAOgoMtI3/TtmDCL7O1vSEuI6PUee7M76HQDcTGCsbbT8WTKC','Surya Vamsi Kotha','teacher','7893444336',NULL,NULL,NULL,NULL,0,3,NULL,NULL,NULL,'{}','2026-05-26 21:57:43','2026-05-29 17:09:39',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL),('8c5b01c2-6f73-47be-841e-b5d2c43fec91','659a72a6-284a-4b1b-b460-018096237cb9','john@student.com','$2b$12$FZ1pJGSNUlpnOqnN.Bns7O93tvhLcAykImQncYxUmxzjsO1iWofpW','John Doe','student','+91-9876543212',NULL,'2026-05-29 12:32:37',NULL,NULL,0,0,NULL,'0ede033b-39d9-43c3-83d7-f8eb6e0cc230',NULL,'{}','2026-05-24 12:11:30','2026-05-29 18:02:36',1,NULL,NULL,NULL,NULL),('99bf6ed3-bf5b-4b8e-9f02-46c192c410cc','659a72a6-284a-4b1b-b460-018096237cb9','admin@school.com','$2b$12$MLQM1pCLHrHLNIY9KeAqZubXQo/jQ2Ns403gHe1R/iZg68vpX7oQW','System Admin','admin','+91-9876543210',NULL,'2026-05-29 15:06:15',NULL,NULL,0,0,NULL,NULL,NULL,'{}','2026-05-24 12:11:30','2026-05-29 20:36:15',1,NULL,NULL,NULL,NULL),('ca4bb6bf-ab10-4153-b8c2-734560dc7c8b','659a72a6-284a-4b1b-b460-018096237cb9','jane@teacher.com','$2b$12$kzj185R03NyQmJQIGCVQ1Oc5/X0fOKaMbhGptndQj74a2CldS.4tG','Jane Smith','teacher','+91-9876543211',NULL,'2026-05-29 12:18:13',NULL,NULL,0,0,'f0bc267d-4453-40bf-9bcf-f3c888fcb48c',NULL,NULL,'{}','2026-05-24 12:11:30','2026-05-29 17:48:13',1,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vehicles`
--

DROP TABLE IF EXISTS `vehicles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vehicles` (
  `vehicle_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `plate_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `year` int DEFAULT NULL,
  `fuel_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `capacity` int NOT NULL,
  `occupied_seats` int NOT NULL DEFAULT '0',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Operational',
  `next_service_date` date DEFAULT NULL,
  `insurance_expiry` date DEFAULT NULL,
  `fitness_expiry` date DEFAULT NULL,
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `deleted_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_vehicles_school_vehicle_number` (`school_id`,`vehicle_number`),
  KEY `ix_vehicles_school_id` (`school_id`),
  KEY `ix_vehicles_is_active` (`is_active`),
  KEY `idx_vehicles_status` (`school_id`,`status`),
  CONSTRAINT `fk_vehicles_school_id_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vehicles`
--

LOCK TABLES `vehicles` WRITE;
/*!40000 ALTER TABLE `vehicles` DISABLE KEYS */;
INSERT INTO `vehicles` VALUES ('TS08B1234',NULL,'Bus','Tata starbus',2020,'Diesel',45,0,'Operational',NULL,'2029-07-19','2032-07-07','15272ee3-0b0f-4a77-a895-7b4a61c06928','{}','2026-05-24 13:03:20','2026-05-24 13:03:20',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('124',NULL,'Mini-Bus',NULL,NULL,'Petrol',10,0,'Operational',NULL,NULL,NULL,'3e61396d-0373-4624-a0e4-ed5781798707','{}','2026-05-26 21:28:16','2026-05-26 21:28:16',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('TS78K9789',NULL,'Mini-Bus','Tata',2019,'Petrol',18,0,'Operational',NULL,NULL,NULL,'5231b611-a1df-465f-915e-dfc82bb7fdf3','{}','2026-05-26 21:42:44','2026-05-26 21:42:44',1,NULL,NULL,'99bf6ed3-bf5b-4b8e-9f02-46c192c410cc',NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('KA01AB1001','KA-01-AB-1001','Bus',NULL,NULL,NULL,40,20,'Operational',NULL,NULL,NULL,'56b90993-4e7e-4aae-b92f-4a198f01dc77','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('KA01AB1002','KA-01-AB-1002','Bus',NULL,NULL,NULL,40,25,'Operational',NULL,NULL,NULL,'7fe5b9e5-7b9b-44ca-b4c5-da9bd9e87279','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9'),('KA01AB1000','KA-01-AB-1000','Bus',NULL,NULL,NULL,40,15,'Operational',NULL,NULL,NULL,'f622cef3-ca09-4751-953e-f85e622c652b','{}','2026-05-24 12:11:35','2026-05-24 12:11:35',1,NULL,NULL,NULL,NULL,'659a72a6-284a-4b1b-b460-018096237cb9');
/*!40000 ALTER TABLE `vehicles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'SchoolManagement'
--
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-29 20:47:25
