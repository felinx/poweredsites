/*
SQLyog Community Edition- MySQL GUI v6.05
Host - 5.1.37-1ubuntu5.4 : Database - poweredsites
*********************************************************************
Server version : 5.1.37-1ubuntu5.4
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

create database if not exists `poweredsites`;

USE `poweredsites`;

/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;

/*Table structure for table `category` */

DROP TABLE IF EXISTS `category`;

CREATE TABLE `category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name_` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `category` varchar(40) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_` (`name_`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;

/*Table structure for table `domains` */

DROP TABLE IF EXISTS `domains`;

CREATE TABLE `domains` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `domain` (`domain`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8;

/*Table structure for table `entries` */

DROP TABLE IF EXISTS `entries`;

CREATE TABLE `entries` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `title` varchar(100) NOT NULL,
  `slug` varchar(200) NOT NULL,
  `content` mediumtext NOT NULL,
  `markdown` mediumtext NOT NULL,
  `created` datetime NOT NULL,
  `updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_help` tinyint(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `FK_blog_user` (`user_id`),
  KEY `updated` (`updated`),
  CONSTRAINT `FK_blog_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=108 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

/*Table structure for table `keywords` */

DROP TABLE IF EXISTS `keywords`;

CREATE TABLE `keywords` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `keyword` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `keyword` (`keyword`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `messages` */

DROP TABLE IF EXISTS `messages`;

CREATE TABLE `messages` (
  `uuid_` varchar(32) NOT NULL,
  `from_` varchar(1024) NOT NULL,
  `user_id` int(11) NOT NULL,
  `project` varchar(20) NOT NULL,
  `body` varchar(400) NOT NULL,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`uuid_`),
  KEY `FK_messages_user` (`user_id`),
  KEY `created` (`created`),
  KEY `FK_messages_project` (`project`),
  CONSTRAINT `FK_messages_project` FOREIGN KEY (`project`) REFERENCES `project` (`subdomain`),
  CONSTRAINT `FK_messages_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `project` */

DROP TABLE IF EXISTS `project`;

CREATE TABLE `project` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subdomain` varchar(20) NOT NULL,
  `project` varchar(30) NOT NULL,
  `website` varchar(600) DEFAULT NULL,
  `keywords` varchar(100) DEFAULT NULL,
  `description` varchar(600) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `logo` varchar(600) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `uuid_` varchar(32) NOT NULL,
  `status_` tinyint(4) NOT NULL DEFAULT '0',
  `category_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `subdomain` (`subdomain`),
  UNIQUE KEY `uuid_` (`uuid_`),
  KEY `FK_project_user` (`user_id`),
  KEY `website` (`website`(255)),
  KEY `fk_project_category` (`category_id`),
  CONSTRAINT `fk_project_category` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_project_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

/*Table structure for table `project_sites` */

DROP TABLE IF EXISTS `project_sites`;

CREATE TABLE `project_sites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `site_id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_project_sites_site` (`site_id`),
  KEY `FK_project_sites_project` (`project_id`),
  CONSTRAINT `FK_project_sites_project` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`),
  CONSTRAINT `FK_project_sites_site` FOREIGN KEY (`site_id`) REFERENCES `site` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=397 DEFAULT CHARSET=utf8;

/*Table structure for table `site` */

DROP TABLE IF EXISTS `site`;

CREATE TABLE `site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sitename` varchar(100) NOT NULL,
  `website` varchar(255) NOT NULL,
  `description` varchar(600) DEFAULT NULL,
  `usecase` mediumtext,
  `usecase_md` mediumtext,
  `user_id` int(11) NOT NULL,
  `source_url` varchar(600) DEFAULT NULL,
  `logo` varchar(600) DEFAULT NULL,
  `pr` tinyint(4) NOT NULL DEFAULT '-1',
  `ar` int(11) NOT NULL DEFAULT '100000000',
  `updated_ss` datetime NOT NULL COMMENT 'snapshot updated',
  `created` datetime NOT NULL,
  `updated` datetime NOT NULL,
  `uuid_` varchar(32) NOT NULL,
  `status_` tinyint(4) NOT NULL DEFAULT '0',
  `click` int(11) NOT NULL DEFAULT '0',
  `slug` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid_`),
  UNIQUE KEY `website` (`website`),
  UNIQUE KEY `slug` (`slug`),
  KEY `FK_site_user` (`user_id`),
  KEY `updated_ss` (`updated_ss`),
  KEY `updated` (`updated`),
  CONSTRAINT `FK_site_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=88 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

/*Table structure for table `user` */

DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(40) NOT NULL,
  `openid_api` tinyint(11) NOT NULL,
  `openid_id` varchar(1024) NOT NULL,
  `openid_name` varchar(1024) NOT NULL,
  `email` varchar(120) DEFAULT NULL,
  `signup_ip` varchar(39) NOT NULL,
  `login_ip` varchar(39) NOT NULL,
  `signup_date` datetime NOT NULL,
  `login_date` datetime NOT NULL,
  `login_c` int(11) NOT NULL DEFAULT '1',
  `click_c` int(11) NOT NULL DEFAULT '0',
  `role` int(11) NOT NULL DEFAULT '0',
  `blog_name` varchar(120) DEFAULT NULL,
  `blog_url` varchar(600) DEFAULT NULL,
  `uuid_` varchar(32) NOT NULL,
  `status_` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid_`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=90 DEFAULT CHARSET=utf8;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
