INSERT INTO `an_event` (`event_id`, `title`, `description`, `start_time`, `end_time`, `location_name`, `zipcode`) VALUES
(211, 'Baseball Game', 'Let\'s go to a baseball game, fam', '2016-12-11 04:00:00', '2016-12-11 08:00:00', 'Met Stadium', 11212),
(332, 'Cheese Tasting', 'n/a', '2016-12-13 05:00:00', '2016-12-16 00:00:00', 'New York', 11232);
INSERT INTO `location` (`location_name`, `zipcode`, `address`, `description`, `latitude`, `longitude`) VALUES
('Met Stadium', 11212, '1 Met Stadium', 'n/a', '44', '44'),
('New York', 11232, '101 Clark Street', 'n/a', '44', '44');
INSERT INTO `interest` (`category`, `keyword`) VALUES
('animals', 'puppies');
INSERT INTO `member` (`username`, `password`, `firstname`, `lastname`, `email`, `zipcode`) VALUES
('bitch', 'bitch', 'bitch', 'bitch', 'bitch@bitch.com', 90786),
('bitch2.0', 'idgi', 'oldfashioned', 'chunk', 'ugly@nyu.edu', 90210),
('shayaansaiyed', '96a4cc498f0b9535bb7f44ffb65f9d2b', 'shayaan', 'saiyed', 'shayaan@saiyed.com', 11232),
('Taylor', '56c052be7cc218dbc1a4092a9db64c50', 'Taylor', 'Taylor', 'taylor@IllSue.com', 11111);
INSERT INTO `an_event` (`event_id`, `title`, `description`, `start_time`, `end_time`, `location_name`, `zipcode`) VALUES
(412, 'Taylor Swift Concert', 'the tickets were free', '2016-12-11 10:00:00', '2016-12-22 09:00:00', 'Met Stadium', 11212);
INSERT INTO `sign_up` (`event_id`, `username`, `rating`) VALUES
(211, 'shayaansaiyed', 2),
(332, 'shayaansaiyed', 5),
(412, 'shayaansaiyed', 6);


