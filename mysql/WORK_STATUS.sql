CREATE TABLE `WORK_STATUS` (
  `No` int(4) NOT NULL AUTO_INCREMENT,
  `employee_no` varchar(4) NOT NULL,
  `date` DATE NOT NULL,
  `day_of_the_week` varchar(1) NOT NULL,
  `work_start_time` DATETIME,
  `work_finish_time` DATETIME,
  `break_start_time` DATETIME,
  `break_finish_time` DATETIME,
  `interval_time` varchar(20),
  `application_and_approval` varchar(5) NOT NULL,
  PRIMARY KEY (`No`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;