-- MySQL dump 10.13  Distrib 8.4.11, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: copet
-- ------------------------------------------------------
-- Server version	8.4.11

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
-- Current Database: `copet`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `copet` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `copet`;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',3,'add_permission'),(6,'Can change permission',3,'change_permission'),(7,'Can delete permission',3,'delete_permission'),(8,'Can view permission',3,'view_permission'),(9,'Can add group',2,'add_group'),(10,'Can change group',2,'change_group'),(11,'Can delete group',2,'delete_group'),(12,'Can view group',2,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add client',6,'add_client'),(22,'Can change client',6,'change_client'),(23,'Can delete client',6,'delete_client'),(24,'Can view client',6,'view_client'),(25,'Can add user',13,'add_user'),(26,'Can change user',13,'change_user'),(27,'Can delete user',13,'delete_user'),(28,'Can view user',13,'view_user'),(29,'Can add invoice',7,'add_invoice'),(30,'Can change invoice',7,'change_invoice'),(31,'Can delete invoice',7,'delete_invoice'),(32,'Can view invoice',7,'view_invoice'),(33,'Can add payment',9,'add_payment'),(34,'Can change payment',9,'change_payment'),(35,'Can delete payment',9,'delete_payment'),(36,'Can view payment',9,'view_payment'),(37,'Can add project',10,'add_project'),(38,'Can change project',10,'change_project'),(39,'Can delete project',10,'delete_project'),(40,'Can view project',10,'view_project'),(41,'Can add time entry',11,'add_timeentry'),(42,'Can change time entry',11,'change_timeentry'),(43,'Can delete time entry',11,'delete_timeentry'),(44,'Can view time entry',11,'view_timeentry'),(45,'Can add invoice line',8,'add_invoiceline'),(46,'Can change invoice line',8,'change_invoiceline'),(47,'Can delete invoice line',8,'delete_invoiceline'),(48,'Can view invoice line',8,'view_invoiceline'),(49,'Can add time entry event',12,'add_timeentryevent'),(50,'Can change time entry event',12,'change_timeentryevent'),(51,'Can delete time entry event',12,'delete_timeentryevent'),(52,'Can view time entry event',12,'view_timeentryevent'),(53,'Can add technician certificate',14,'add_techniciancertificate'),(54,'Can change technician certificate',14,'change_techniciancertificate'),(55,'Can delete technician certificate',14,'delete_techniciancertificate'),(56,'Can view technician certificate',14,'view_techniciancertificate'),(57,'Can add technician sequence',15,'add_techniciansequence'),(58,'Can change technician sequence',15,'change_techniciansequence'),(59,'Can delete technician sequence',15,'delete_techniciansequence'),(60,'Can view technician sequence',15,'view_techniciansequence'),(61,'Can add public holiday',16,'add_publicholiday'),(62,'Can change public holiday',16,'change_publicholiday'),(63,'Can delete public holiday',16,'delete_publicholiday'),(64,'Can view public holiday',16,'view_publicholiday');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_eliteapp_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_eliteapp_user_id` FOREIGN KEY (`user_id`) REFERENCES `eliteapp_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(2,'auth','group'),(3,'auth','permission'),(4,'contenttypes','contenttype'),(6,'eliteapp','client'),(7,'eliteapp','invoice'),(8,'eliteapp','invoiceline'),(9,'eliteapp','payment'),(10,'eliteapp','project'),(16,'eliteapp','publicholiday'),(14,'eliteapp','techniciancertificate'),(15,'eliteapp','techniciansequence'),(11,'eliteapp','timeentry'),(12,'eliteapp','timeentryevent'),(13,'eliteapp','user'),(5,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-10-10 20:34:28.889486'),(2,'contenttypes','0002_remove_content_type_name','2026-10-10 20:34:28.980204'),(3,'auth','0001_initial','2026-10-10 20:34:29.234442'),(4,'auth','0002_alter_permission_name_max_length','2026-10-10 20:34:29.411529'),(5,'auth','0003_alter_user_email_max_length','2026-10-10 20:34:29.416803'),(6,'auth','0004_alter_user_username_opts','2026-10-10 20:34:29.422238'),(7,'auth','0005_alter_user_last_login_null','2026-10-10 20:34:29.427383'),(8,'auth','0006_require_contenttypes_0002','2026-10-10 20:34:29.430285'),(9,'auth','0007_alter_validators_add_error_messages','2026-10-10 20:34:29.436461'),(10,'auth','0008_alter_user_username_max_length','2026-10-10 20:34:29.442881'),(11,'auth','0009_alter_user_last_name_max_length','2026-10-10 20:34:29.448438'),(12,'auth','0010_alter_group_name_max_length','2026-10-10 20:34:29.462088'),(13,'auth','0011_update_proxy_permissions','2026-10-10 20:34:29.468392'),(14,'auth','0012_alter_user_first_name_max_length','2026-10-10 20:34:29.474475'),(15,'eliteapp','0001_initial','2026-10-10 20:34:31.199422'),(16,'admin','0001_initial','2026-10-10 20:34:31.369623'),(17,'admin','0002_logentry_remove_auto_add','2026-10-10 20:34:31.382393'),(18,'admin','0003_logentry_add_action_flag_choices','2026-10-10 20:34:31.401576'),(19,'sessions','0001_initial','2026-10-10 20:34:31.459836'),(20,'eliteapp','0002_technician_profile','2026-10-16 20:17:03.506544'),(21,'eliteapp','0003_technician_certificates','2026-10-16 20:25:22.245587'),(22,'eliteapp','0004_user_photo','2026-10-16 21:11:37.565899'),(23,'eliteapp','0005_technician_sequence','2026-10-16 21:33:23.182572'),(24,'eliteapp','0006_user_assignment_date','2026-10-17 15:35:49.697852'),(25,'eliteapp','0007_client_registration_fields','2026-10-17 17:04:57.643230'),(26,'eliteapp','0008_client_logo','2026-10-17 17:15:42.050759'),(27,'eliteapp','0009_client_start_work_date','2026-10-17 19:50:50.956273'),(28,'eliteapp','0010_project_manager_name','2026-10-17 20:46:49.749761'),(29,'eliteapp','0011_project_technician_rates_public_holiday','2026-10-17 20:46:50.130024'),(30,'eliteapp','0012_project_holiday_billing_rate','2026-10-17 20:46:50.322157'),(31,'eliteapp','0013_project_access_user','2026-10-17 23:53:48.556233');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('3e6h8nwu0mdbitfiwk3a5hbpbhb496jz','.eJxVjDEOgzAMAP_iuYpIAnHC2L1vQHZsGtoKJAJT1b9XSAztene6Nwy0b2XYq67DJNCDhcsvY8pPnQ8hD5rvi8nLvK0TmyMxp63mtoi-rmf7NyhUC_RA3nNnE2pqIlPI6FxGtBjTqNxma71vJHnWgCHGjhON0qobUZSFmwCfL9WGOBM:1xHpbT:FBqG5pOa6XuRG8TrwSCMC6DxjYq5TKdWdcdoN8hE_gA','2026-10-30 21:36:39.340328'),('ezjxflnxgcgswso7j6wgsi3ecuzygfit','.eJxVjEEOwiAQAP-yZ0NgoVB69O4bmoXdStXQpLQn499Nkx70OjOZN4y0b2Xcm6zjzDCAg8svS5SfUg_BD6r3ReWlbuuc1JGo0zZ1W1he17P9GxRqBQZA8egtYcQJdbKGde59bzIFr1OQzJ7JRmc9Run0JFOnAzvngkHJLhr4fAHOgjc-:1xIDvx:mojzHCkdci4a88gRoZnmxDLtn3TKfxmj0YSh7pyI15M','2026-10-31 23:35:25.632229'),('v4shbolo9fwh8e3yo68ddmmr9v9ij23y','.eJxVjDEOgzAMAP_iuYpIAnHC2L1vQHZsGtoKJAJT1b9XSAztene6Nwy0b2XYq67DJNCDhcsvY8pPnQ8hD5rvi8nLvK0TmyMxp63mtoi-rmf7NyhUC_RA3nNnE2pqIlPI6FxGtBjTqNxma71vJHnWgCHGjhON0qobUZSFmwCfL9WGOBM:1xIBc9:W2ihLKBE95_Z5TwsNURT58yNmf4K2ph9I-sPNvmm4Sk','2026-10-31 21:06:49.201183'),('x9ya59ozkto8bd7aily7pja3euutvtjt','.eJxVjDEOgzAMAP_iuYpoYhPC2J03ICexC20VJAJT1b9XSAztene6N4y8b9O4V1nHOUMPCJdfFjk9pRwiP7jcF5OWsq1zNEdiTlvNsGR53c72bzBxnaAH7xp12DqlxCjeoija7FDbpA158TbZ6NrOarZEpDFQR9FzkHBFzQyfL9r4N-k:1xIBdI:Qzdnxm-7MyGeE4_An-nIiQvGgsjw8K9nW5Y9bRO7b1s','2026-10-31 21:08:00.708706'),('yiu2ythp2cj8zj8vypr7vlogfe3ihexq','.eJxVjDEOgzAMAP_iuYpIAnHC2L1vQHZsGtoKJAJT1b9XSAztene6Nwy0b2XYq67DJNCDhcsvY8pPnQ8hD5rvi8nLvK0TmyMxp63mtoi-rmf7NyhUC_RA3nNnE2pqIlPI6FxGtBjTqNxma71vJHnWgCHGjhON0qobUZSFmwCfL9WGOBM:1xFdrJ:n595PFnWPSXO4e7OeU5Ft7cJXJ_NZR5_FQMXZEbDbtE','2026-10-24 20:39:57.662615');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eliteapp_client`
--

DROP TABLE IF EXISTS `eliteapp_client`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eliteapp_client` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(160) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contact_name` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `billing_address` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `rc` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nif` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `article_number` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nis` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `logo` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_work_date` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eliteapp_client`
--

LOCK TABLES `eliteapp_client` WRITE;
/*!40000 ALTER TABLE `eliteapp_client` DISABLE KEYS */;
INSERT INTO `eliteapp_client` VALUES (1,'GENERAL ELECTRIC','DIRECTOR','h.informatiq69898ue7@gmail.com','023709292','12 freres Ouglise El Mouradia',1,'59595562/16-00','65952626','2655488','5958565626265','client-logos/General_Electric_logo.svg.png','2022-11-17');
/*!40000 ALTER TABLE `eliteapp_client` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eliteapp_invoice`
--

DROP TABLE IF EXISTS `eliteapp_invoice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eliteapp_invoice` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `client_name` varchar(160) COLLATE utf8mb4_unicode_ci NOT NULL,
  `billing_address` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_name` varchar(160) COLLATE utf8mb4_unicode_ci NOT NULL,
  `purchase_order` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `currency` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tax_percent` decimal(5,2) NOT NULL,
  `subtotal` decimal(14,2) NOT NULL,
  `tax_amount` decimal(14,2) NOT NULL,
  `total` decimal(14,2) NOT NULL,
  `issued_at` datetime(6) NOT NULL,
  `due_date` date NOT NULL,
  `created_by_id` bigint NOT NULL,
  `project_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `eliteapp_invoice_project_id_38cb12b6_fk_eliteapp_project_id` (`project_id`),
  KEY `eliteapp_invoice_created_by_id_9f652a4a_fk_eliteapp_user_id` (`created_by_id`),
  CONSTRAINT `eliteapp_invoice_created_by_id_9f652a4a_fk_eliteapp_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `eliteapp_user` (`id`),
  CONSTRAINT `eliteapp_invoice_project_id_38cb12b6_fk_eliteapp_project_id` FOREIGN KEY (`project_id`) REFERENCES `eliteapp_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eliteapp_invoice`
--

LOCK TABLES `eliteapp_invoice` WRITE;
/*!40000 ALTER TABLE `eliteapp_invoice` DISABLE KEYS */;
/*!40000 ALTER TABLE `eliteapp_invoice` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eliteapp_invoiceline`
--

DROP TABLE IF EXISTS `eliteapp_invoiceline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eliteapp_invoiceline` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `technician_name` varchar(160) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `work_date` date NOT NULL,
  `hours` decimal(7,2) NOT NULL,
  `rate` decimal(10,2) NOT NULL,
  `amount` decimal(14,2) NOT NULL,
  `invoice_id` bigint NOT NULL,
  `time_entry_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `time_entry_id` (`time_entry_id`),
  KEY `eliteapp_invoiceline_invoice_id_f648face_fk_eliteapp_invoice_id` (`invoice_id`),
  CONSTRAINT `eliteapp_invoiceline_invoice_id_f648face_fk_eliteapp_invoice_id` FOREIGN KEY (`invoice_id`) REFERENCES `eliteapp_invoice` (`id`),
  CONSTRAINT `eliteapp_invoiceline_time_entry_id_62e83bd8_fk_eliteapp_` FOREIGN KEY (`time_entry_id`) REFERENCES `eliteapp_timeentry` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eliteapp_invoiceline`
--

LOCK TABLES `eliteapp_invoiceline` WRITE;
/*!40000 ALTER TABLE `eliteapp_invoiceline` DISABLE KEYS */;
/*!40000 ALTER TABLE `eliteapp_invoiceline` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eliteapp_payment`
--

DROP TABLE IF EXISTS `eliteapp_payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eliteapp_payment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `amount` decimal(14,2) NOT NULL,
  `date` date NOT NULL,
  `method` varchar(12) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reference` varchar(160) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` bigint NOT NULL,
  `invoice_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `eliteapp_payment_created_by_id_776a8b4c_fk_eliteapp_user_id` (`created_by_id`),
  KEY `eliteapp_payment_invoice_id_be85a647_fk_eliteapp_invoice_id` (`invoice_id`),
  CONSTRAINT `eliteapp_payment_created_by_id_776a8b4c_fk_eliteapp_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `eliteapp_user` (`id`),
  CONSTRAINT `eliteapp_payment_invoice_id_be85a647_fk_eliteapp_invoice_id` FOREIGN KEY (`invoice_id`) REFERENCES `eliteapp_invoice` (`id`),
  CONSTRAINT `positive_payment` CHECK ((`amount` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eliteapp_payment`
--

LOCK TABLES `eliteapp_payment` WRITE;
/*!40000 ALTER TABLE `eliteapp_payment` DISABLE KEYS */;
/*!40000 ALTER TABLE `eliteapp_payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eliteapp_project`
--

DROP TABLE IF EXISTS `eliteapp_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eliteapp_project` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(160) COLLATE utf8mb4_unicode_ci NOT NULL,
  `site` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `hourly_rate` decimal(10,2) NOT NULL,
  `budget` decimal(14,2) NOT NULL,
  `purchase_order` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(12) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `client_id` bigint NOT NULL,
  `project_manager_id` bigint DEFAULT NULL,
  `manager_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `technician_hourly_rate` decimal(10,2) NOT NULL,
  `holiday_day_rate` decimal(10,2) NOT NULL,
  `holiday_billing_day_rate` decimal(10,2) NOT NULL,
  `access_user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `access_user_id` (`access_user_id`),
  KEY `eliteapp_project_client_id_bce0e02b_fk_eliteapp_client_id` (`client_id`),
  KEY `eliteapp_project_project_manager_id_91f54ffb_fk_eliteapp_user_id` (`project_manager_id`),
  CONSTRAINT `eliteapp_project_access_user_id_1c10a7d7_fk_eliteapp_user_id` FOREIGN KEY (`access_user_id`) REFERENCES `eliteapp_user` (`id`),
  CONSTRAINT `eliteapp_project_client_id_bce0e02b_fk_eliteapp_client_id` FOREIGN KEY (`client_id`) REFERENCES `eliteapp_client` (`id`),
  CONSTRAINT `eliteapp_project_project_manager_id_91f54ffb_fk_eliteapp_user_id` FOREIGN KEY (`project_manager_id`) REFERENCES `eliteapp_user` (`id`),
  CONSTRAINT `positive_project_budget` CHECK ((`budget` >= 0)),
  CONSTRAINT `positive_project_holiday_billing_rate` CHECK ((`holiday_billing_day_rate` >= 0)),
  CONSTRAINT `positive_project_holiday_rate` CHECK ((`holiday_day_rate` >= 0)),
  CONSTRAINT `positive_project_rate` CHECK ((`hourly_rate` >= 0)),
  CONSTRAINT `positive_technician_project_rate` CHECK ((`technician_hourly_rate` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eliteapp_project`
--

LOCK TABLES `eliteapp_project` WRITE;
/*!40000 ALTER TABLE `eliteapp_project` DISABLE KEYS */;
INSERT INTO `eliteapp_project` VALUES (1,'SKIKDA','SKikDA SITE','dspfdsohkjldvbdkfbgdshjkfdsfsdf',1200.00,0.00,'02/2026','ACTIVE','2026-10-17 20:46:58.401803',1,NULL,'hamid',1000.00,1300.00,1500.00,NULL);
/*!40000 ALTER TABLE `eliteapp_project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eliteapp_project_technicians`
--

DROP TABLE IF EXISTS `eliteapp_project_technicians`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eliteapp_project_technicians` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `project_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `eliteapp_project_technicians_project_id_user_id_8fb140ce_uniq` (`project_id`,`user_id`),
  KEY `eliteapp_project_tec_user_id_717b96fa_fk_eliteapp_` (`user_id`),
  CONSTRAINT `eliteapp_project_tec_project_id_34a79d86_fk_eliteapp_` FOREIGN KEY (`project_id`) REFERENCES `eliteapp_project` (`id`),
  CONSTRAINT `eliteapp_project_tec_user_id_717b96fa_fk_eliteapp_` FOREIGN KEY (`user_id`) REFERENCES `eliteapp_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eliteapp_project_technicians`
--

LOCK TABLES `eliteapp_project_technicians` WRITE;
/*!40000 ALTER TABLE `eliteapp_project_technicians` DISABLE KEYS */;
INSERT INTO `eliteapp_project_technicians` VALUES (1,1,3),(2,1,4);
/*!40000 ALTER TABLE `eliteapp_project_technicians` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eliteapp_publicholiday`
--

DROP TABLE IF EXISTS `eliteapp_publicholiday`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eliteapp_publicholiday` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `date` date NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `date` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eliteapp_publicholiday`
--

LOCK TABLES `eliteapp_publicholiday` WRITE;
/*!40000 ALTER TABLE `eliteapp_publicholiday` DISABLE KEYS */;
/*!40000 ALTER TABLE `eliteapp_publicholiday` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eliteapp_techniciancertificate`
--

DROP TABLE IF EXISTS `eliteapp_techniciancertificate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eliteapp_techniciancertificate` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `eliteapp_technicianc_user_id_d5b8ad43_fk_eliteapp_` (`user_id`),
  CONSTRAINT `eliteapp_technicianc_user_id_d5b8ad43_fk_eliteapp_` FOREIGN KEY (`user_id`) REFERENCES `eliteapp_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eliteapp_techniciancertificate`
--

LOCK TABLES `eliteapp_techniciancertificate` WRITE;
/*!40000 ALTER TABLE `eliteapp_techniciancertificate` DISABLE KEYS */;
INSERT INTO `eliteapp_techniciancertificate` VALUES (1,'technician-certificates/5d9d62a05e4747538472d31ff7a1911b.pdf','company-profile.pdf','2026-10-16 20:42:56.655617',3),(2,'technician-certificates/86d02b813d6d466080ae2b5ef6292e82.pdf','Brand Identity Manual.pdf','2026-10-16 21:27:33.665542',4);
/*!40000 ALTER TABLE `eliteapp_techniciancertificate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eliteapp_techniciansequence`
--

DROP TABLE IF EXISTS `eliteapp_techniciansequence`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eliteapp_techniciansequence` (
  `year` smallint unsigned NOT NULL,
  `last_number` int unsigned NOT NULL,
  PRIMARY KEY (`year`),
  CONSTRAINT `eliteapp_techniciansequence_chk_1` CHECK ((`year` >= 0)),
  CONSTRAINT `eliteapp_techniciansequence_chk_2` CHECK ((`last_number` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eliteapp_techniciansequence`
--

LOCK TABLES `eliteapp_techniciansequence` WRITE;
/*!40000 ALTER TABLE `eliteapp_techniciansequence` DISABLE KEYS */;
INSERT INTO `eliteapp_techniciansequence` VALUES (2026,3);
/*!40000 ALTER TABLE `eliteapp_techniciansequence` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eliteapp_timeentry`
--

DROP TABLE IF EXISTS `eliteapp_timeentry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eliteapp_timeentry` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `start` datetime(6) NOT NULL,
  `end` datetime(6) NOT NULL,
  `break_minutes` int unsigned NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(12) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reviewed_at` datetime(6) DEFAULT NULL,
  `rejection_reason` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `project_id` bigint NOT NULL,
  `reviewed_by_id` bigint DEFAULT NULL,
  `technician_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `eliteapp_ti_technic_428b6b_idx` (`technician_id`,`start`,`end`),
  KEY `eliteapp_timeentry_project_id_a8b00846_fk_eliteapp_project_id` (`project_id`),
  KEY `eliteapp_timeentry_reviewed_by_id_b656cab7_fk_eliteapp_user_id` (`reviewed_by_id`),
  CONSTRAINT `eliteapp_timeentry_project_id_a8b00846_fk_eliteapp_project_id` FOREIGN KEY (`project_id`) REFERENCES `eliteapp_project` (`id`),
  CONSTRAINT `eliteapp_timeentry_reviewed_by_id_b656cab7_fk_eliteapp_user_id` FOREIGN KEY (`reviewed_by_id`) REFERENCES `eliteapp_user` (`id`),
  CONSTRAINT `eliteapp_timeentry_technician_id_88f8e570_fk_eliteapp_user_id` FOREIGN KEY (`technician_id`) REFERENCES `eliteapp_user` (`id`),
  CONSTRAINT `eliteapp_timeentry_chk_1` CHECK ((`break_minutes` >= 0)),
  CONSTRAINT `time_end_after_start` CHECK ((`end` > `start`))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eliteapp_timeentry`
--

LOCK TABLES `eliteapp_timeentry` WRITE;
/*!40000 ALTER TABLE `eliteapp_timeentry` DISABLE KEYS */;
INSERT INTO `eliteapp_timeentry` VALUES (1,'2026-10-17 07:00:00.000000','2026-10-17 17:00:00.000000',0,'h','SUBMITTED',NULL,'','2026-10-17 21:20:02.729385',1,NULL,4),(2,'2026-10-16 07:00:00.000000','2026-10-16 16:00:00.000000',0,'1','SUBMITTED',NULL,'','2026-10-17 23:27:31.109398',1,NULL,4);
/*!40000 ALTER TABLE `eliteapp_timeentry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eliteapp_timeentryevent`
--

DROP TABLE IF EXISTS `eliteapp_timeentryevent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eliteapp_timeentryevent` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `status` varchar(12) COLLATE utf8mb4_unicode_ci NOT NULL,
  `comment` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `actor_id` bigint NOT NULL,
  `entry_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `eliteapp_timeentryevent_actor_id_ec92be2b_fk_eliteapp_user_id` (`actor_id`),
  KEY `eliteapp_timeentryev_entry_id_56fb0702_fk_eliteapp_` (`entry_id`),
  CONSTRAINT `eliteapp_timeentryev_entry_id_56fb0702_fk_eliteapp_` FOREIGN KEY (`entry_id`) REFERENCES `eliteapp_timeentry` (`id`),
  CONSTRAINT `eliteapp_timeentryevent_actor_id_ec92be2b_fk_eliteapp_user_id` FOREIGN KEY (`actor_id`) REFERENCES `eliteapp_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eliteapp_timeentryevent`
--

LOCK TABLES `eliteapp_timeentryevent` WRITE;
/*!40000 ALTER TABLE `eliteapp_timeentryevent` DISABLE KEYS */;
INSERT INTO `eliteapp_timeentryevent` VALUES (1,'DRAFT','','2026-10-17 21:20:02.730315',4,1),(2,'SUBMITTED','','2026-10-17 22:30:52.422585',4,1),(3,'DRAFT','','2026-10-17 23:27:31.110659',4,2),(4,'SUBMITTED','','2026-10-17 23:27:38.223336',4,2);
/*!40000 ALTER TABLE `eliteapp_timeentryevent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eliteapp_user`
--

DROP TABLE IF EXISTS `eliteapp_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eliteapp_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `specialty` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `employee_number` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `hourly_cost` decimal(10,2) NOT NULL,
  `client_id` bigint DEFAULT NULL,
  `address` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `birth_date` date DEFAULT NULL,
  `certificates` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `cv` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `experience` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `photo` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `assignment_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  KEY `eliteapp_user_client_id_93a9c03d_fk_eliteapp_client_id` (`client_id`),
  CONSTRAINT `eliteapp_user_client_id_93a9c03d_fk_eliteapp_client_id` FOREIGN KEY (`client_id`) REFERENCES `eliteapp_client` (`id`),
  CONSTRAINT `client_required_for_project_manager` CHECK ((((`client_id` is not null) and (`role` = _utf8mb4'PROJECT_MANAGER')) or ((`role` <> _utf8mb4'PROJECT_MANAGER') and (`client_id` is null)))),
  CONSTRAINT `positive_hourly_cost` CHECK ((`hourly_cost` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eliteapp_user`
--

LOCK TABLES `eliteapp_user` WRITE;
/*!40000 ALTER TABLE `eliteapp_user` DISABLE KEYS */;
INSERT INTO `eliteapp_user` VALUES (1,'pbkdf2_sha256$1500000$QoXy9ARW4Ta2I6xqwzdMDy$txxMCBqY8nyD0tYxmzXsNMUadmbMpzSuLcw6K0+sRy0=','2026-10-17 21:06:49.193974',1,'copt','','','copt@gmail.com',1,1,'2026-10-10 20:39:47.505236','ADMIN','','','',0.00,NULL,'',NULL,'','','','',NULL),(3,'pbkdf2_sha256$1500000$bxDRcANJKEIhneZ0LMDrgc$pRvoaCBhSMoHAPRztT5+uFuQQXD5AG7H2f7mubylTA4=',NULL,0,'yes','AROUCHE','MOHAMED','baitul.technology@gmail.com',0,1,'2026-10-16 20:40:58.450666','TECHNICIAN','0783773656','MECHANICAL TECH','CP-2026-00001',0.00,NULL,'FDSFDSF','2003-06-21','','','','technician-photos/images.jpg','2026-10-01'),(4,'pbkdf2_sha256$1500000$qkwwyALnqTZDk5bMtiRZT4$LvP+qtKIsPRuskgeXqYLB0ej5ohJU1McwAO/+LZEufE=','2026-10-17 23:35:25.628492',0,'hani','HANNI','REDAOUIA','baitul.technology@gmail.com',0,1,'2026-10-16 21:27:30.773092','TECHNICIAN','0783773657','ELECTRICAL','CP-2026-00002',0.00,NULL,'RUE ABELHAMID KHOUDJA SECTION 38 GROUPE 10 RDC N°14','1996-10-07','','technician-cvs/AHMED_REZAG_CV_1.pdf','<!--copetrolite-experience:v1-->Research Professional – Territorial Studies &amp; GIS          from 2022<br>CRDIG / CRAD – Université Laval | Québec, Canada<br><br> Tasks :<br><br>  • Conduct territorial and spatial diagnostics of urban, social, and environmental dynamics<br><br>  • Analyze and structure qualitative, quantitative, and GIS data to identify territorial needs and<br><br>   challenges.<br><br>  • Produce thematic maps, spatial analyses, and territorial indicators for strategic planning.<br><br>  • Facilitate workshops with institutions, communities, and stakeholders on sustainability and<br><br>   ecological transition.<br><br>  • Deliver GIS, territorial analysis, and sustainability training to students and professionals.<br><br>  • Support and facilitate scientiﬁc, academic, and professional committees and working groups.<br><br>  • Supervise student projects and promote **knowledge transfer between research and<br><br>   practice.<br><br> Urban Planner   2021<br> City of Repentigny – Sustainable Development &amp; Urban<br> Planning | Québec, Canada<br><br>  Tasks :<br><br>   • Contributed to planning and zoning document development and revisions**.<br><br>   • Reviewed projects for planning and zoning compliance.<br><br>   • Processed permits, certiﬁcates, and variance applications.<br><br>   • Prepared technical assessments and planning recommendations.<br><br>   • Addressed environmental and urban sustainability issues, including stormwater and heat<br><br>     islands.<br><br>   • Coordinated with municipal departments, institutions, and planning consultants.<br><br>   • Monitored planning regulations and emerging urban development practices.<br>Urban Planning Inspector                                                                   2020<br>Village of Senneville – Urban Planning &amp; Permitting Department | Québec, Canada<br><br> Tasks :<br><br>  • Reviewed permit and certiﬁcate applications through to administrative decisions.<br><br>  • Veriﬁed project compliance with planning and building regulations.<br><br>  • Conducted site inspections and followed up on non-compliance issues.<br><br>  • Advised residents and municipal departments with a solution-oriented approach.<br><br>  • Prepared inspection reports and managed enforcement cases.<br><br>  • Coordinated with municipal departments and professionals to ensure project compliance.<br><br>Environmental &amp; Urban Planning Intern                                                        2019<br>Village of Senneville – Urban Planning &amp; Permitting Department | Québec, Canada<br><br> Tasks :<br><br>  • Supported site inspections and project compliance monitoring.<br><br>  • Assisted with planning case analysis and local data collection.<br><br>  • Produced thematic maps, GIS data, and planning documents.<br><br>  • Supported ﬁeld visits, administrative follow-up, and citizen services.<br><br>  • Identiﬁed environmental issues and natural hazards in development projects.<br><br>  • Assessed natural area protection and stormwater management measures.<br><br>  • Collected and analyzed environmental data to support territorial planning.<br><br>Architect                                                                                     2011 - 2017Roles / Title at site<br>Société Civile des Études Diverses (S.C.É.D) | Algeria<br><br> Tasks :<br><br>  • Supported site inspections and project compliance monitoring.<br><br>  • Assisted with planning case analysis and local data collection.<br><br>  • Produced thematic maps, GIS data, and planning documents.<br><br>  • Supported ﬁeld visits, administrative follow-up, and citizen services.<br><br>  • Identiﬁed environmental issues and natural hazards in development projects.<br><br>  • Assessed natural area protection and stormwater management measures.<br><br>  • Collected and analyzed environmental data to support territorial planning.<br><br>Architect                                                                                    2007- 2011<br>COSIDER | Algeria                                                                                                                                                                                            Roles / Title at site<br><br> Tasks :<br><br>  • Designed architectural projects across ESQ, APS, APD, PRO, and DCE phases.<br><br>  • Produced architectural drawings and technical documents using AutoCAD, Revit, and BIM.<br><br>  • Coordinated design ofﬁces, contractors, and multidisciplinary technical teams.<br><br>  • Managed technical coordination between architecture, structural, and building systems disciplines.<br><br>  • Ensured compliance with public building standards, accessibility, ﬁre safety, and environmental regulations.<br><br>  • Monitored construction works and veriﬁed compliance with approved plans.<br><br>  • Proposed technical solutions and supported the resolution of outstanding construction issues.','technician-photos/40adb147-d371-43a3-ac62-409f0f930961.png','2026-10-14');
/*!40000 ALTER TABLE `eliteapp_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eliteapp_user_groups`
--

DROP TABLE IF EXISTS `eliteapp_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eliteapp_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `eliteapp_user_groups_user_id_group_id_8b0768b5_uniq` (`user_id`,`group_id`),
  KEY `eliteapp_user_groups_group_id_52790000_fk_auth_group_id` (`group_id`),
  CONSTRAINT `eliteapp_user_groups_group_id_52790000_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `eliteapp_user_groups_user_id_65139719_fk_eliteapp_user_id` FOREIGN KEY (`user_id`) REFERENCES `eliteapp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eliteapp_user_groups`
--

LOCK TABLES `eliteapp_user_groups` WRITE;
/*!40000 ALTER TABLE `eliteapp_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `eliteapp_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eliteapp_user_user_permissions`
--

DROP TABLE IF EXISTS `eliteapp_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eliteapp_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `eliteapp_user_user_permi_user_id_permission_id_9389e9cc_uniq` (`user_id`,`permission_id`),
  KEY `eliteapp_user_user_p_permission_id_228207a9_fk_auth_perm` (`permission_id`),
  CONSTRAINT `eliteapp_user_user_p_permission_id_228207a9_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `eliteapp_user_user_p_user_id_14b5bdde_fk_eliteapp_` FOREIGN KEY (`user_id`) REFERENCES `eliteapp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eliteapp_user_user_permissions`
--

LOCK TABLES `eliteapp_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `eliteapp_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `eliteapp_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'copet'
--

--
-- Dumping routines for database 'copet'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-26 15:12:35
