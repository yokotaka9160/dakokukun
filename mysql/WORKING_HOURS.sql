CREATE TABLE `WORKING_HOURS` (
  `No` int(4) NOT NULL AUTO_INCREMENT,
  `employee_no` varchar(4) NOT NULL,
  `name` varchar(20) NOT NULL,
  `date` DATE NOT NULL,
  `Total_working_hours` int(10),
  `Actual_working_hours` int(10),
  `Predetermined_time` varchar(10),
  `Scheduled_working_hours` varchar(10),
  `Overtime_hours` int(10),
  `Working_hours_outside_legal_hours` int(10),
  `Overtime_working_hours` int(10),
  `Nonstatutory_holiday_working_hours` int(10),
  `Legal_holiday_working_hours` int(10),
  `Midnight_working_hours` int(10),
  `Late_time` int(10),
  `Early_departure_time` int(10),
  PRIMARY KEY (`No`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;