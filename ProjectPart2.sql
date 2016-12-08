-- phpMyAdmin SQL Dump
-- version 4.5.1
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: Nov 10, 2016 at 04:50 PM
-- Server version: 10.1.10-MariaDB
-- PHP Version: 5.5.33
--
-- Database: `FindFolks`
--

-- --------------------------------------------------------

--
-- Table structure for table `member`
--

CREATE TABLE `member` (
  `username` varchar(20) NOT NULL DEFAULT '',
  `password` varchar(32) NOT NULL DEFAULT '',
  `firstname` varchar(20) NOT NULL DEFAULT '',
  `lastname` varchar(20) NOT NULL DEFAULT '',
  `email` varchar(32) NOT NULL DEFAULT '',
  `zipcode` int(5) NOT NULL,
      PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------


--
-- Table structure for table `friend`
--

CREATE TABLE `friend` (
  `friend_of` varchar(20) NOT NULL DEFAULT '',
  `friend_to` varchar(20) NOT NULL DEFAULT '',
      PRIMARY KEY (`friend_to`,`friend_of`),
  FOREIGN KEY (`friend_to`) REFERENCES `member` (`username`),
    FOREIGN KEY (`friend_of`) REFERENCES `member` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `a_group`
--

CREATE TABLE `a_group` (
  `group_id` int(20) NOT NULL AUTO_INCREMENT,
  `group_name` varchar(20) NOT NULL DEFAULT '',
  `description` text NOT NULL,
  `creator` varchar(20) NOT NULL DEFAULT '',
    PRIMARY KEY (`group_id`),
    FOREIGN KEY (`creator`) REFERENCES `member` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `interest`
--

CREATE TABLE `interest` (
  `category` varchar(20) NOT NULL DEFAULT '',
  `keyword` varchar(20) NOT NULL DEFAULT '',
     PRIMARY KEY (keyword,category) 
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `interested_in`
--

CREATE TABLE `interested_in` (
  `username` varchar(20) NOT NULL DEFAULT '',
  `category` varchar(20) NOT NULL DEFAULT '',
  `keyword` varchar(20) NOT NULL DEFAULT '',
      PRIMARY KEY (`username`,`keyword`,`category`),
  FOREIGN KEY (`username`) REFERENCES `member` (`username`),
  FOREIGN KEY (`keyword`,`category`) REFERENCES `interest` (`keyword`,`category`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `about`
--

CREATE TABLE `about` (
  `category` varchar(20) NOT NULL DEFAULT '',
  `keyword` varchar(20) NOT NULL DEFAULT '',
  `group_id` int(20) NOT NULL,
    PRIMARY KEY (`group_id`,`keyword`,`category`),
     FOREIGN KEY (`group_id`) REFERENCES `a_group` (`group_id`),
  FOREIGN KEY (`keyword`,`category`) REFERENCES `interest` (`keyword`,`category`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `belongs_to`
--

CREATE TABLE `belongs_to` (
  `group_id` int(20) NOT NULL,
  `username` varchar(20) NOT NULL DEFAULT '',
  `authorized` tinyint(1) NOT NULL,
     PRIMARY KEY (`group_id`,`username`),
  FOREIGN KEY (`group_id`) REFERENCES `a_group` (`group_id`),
  FOREIGN KEY (`username`) REFERENCES `member` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `location`
--

CREATE TABLE `location` (
  `location_name` varchar(20) NOT NULL DEFAULT '',
  `zipcode` int(5) NOT NULL,
  `address` varchar(50) NOT NULL DEFAULT '',
  `description` text NOT NULL,
  `latitude` decimal(50,0) NOT NULL,
  `longitude` decimal(50,0) NOT NULL,
     PRIMARY KEY (`location_name`,`zipcode`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------
--
-- Table structure for table `an_event`
--

CREATE TABLE `an_event` (
  `event_id` int(20) NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL DEFAULT '',
  `description` text NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `location_name` varchar(20) NOT NULL,
  `zipcode` int(5) NOT NULL,
    PRIMARY KEY (`event_id`),
    FOREIGN KEY (`location_name`,`zipcode`) REFERENCES `location` (`location_name`, `zipcode`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `organize`
--

CREATE TABLE `organize` (
  `event_id` int(20) NOT NULL,
  `group_id` int(20) NOT NULL,
      PRIMARY KEY (`event_id`,`group_id`),
  FOREIGN KEY (`event_id`) REFERENCES `an_event` (`event_id`),
  FOREIGN KEY (`group_id`) REFERENCES `a_group` (`group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `sign_up`
--

CREATE TABLE `sign_up` (
  `event_id` int(20) NOT NULL,
  `username` varchar(20) NOT NULL DEFAULT '',
  `rating` int(1) NOT NULL,
      PRIMARY KEY (`event_id`,`username`),
  FOREIGN KEY (`event_id`) REFERENCES `an_event` (`event_id`),
  FOREIGN KEY (`username`) REFERENCES `member` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

