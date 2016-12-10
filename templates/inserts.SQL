INSERT INTO `an_event` (`event_id`, `title`, `description`, `start_time`, `end_time`, `location_name`, `zipcode`) VALUES
(211, 'Baseball Game', 'Let\'s go to a baseball game, fam', '2016-12-11 04:00:00', '2016-12-11 08:00:00', 'Met Stadium', 11212),
(332, 'Cheese Tasting', 'n/a', '2016-12-13 05:00:00', '2016-12-16 00:00:00', 'New York', 11232);
INSERT INTO `location` (`location_name`, `zipcode`, `address`, `description`, `latitude`, `longitude`) VALUES
('Met Stadium', 11212, '1 Met Stadium', 'n/a', '44', '44'),
('New York', 11232, '101 Clark Street', 'n/a', '44', '44');
INSERT INTO `interest` (`category`, `keyword`) VALUES
('animals', 'puppies');