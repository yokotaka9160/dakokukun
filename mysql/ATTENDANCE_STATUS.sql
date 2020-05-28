CREATE TABLE `ATTENDANCE_STATUS` (
  `No` int(4) NOT NULL AUTO_INCREMENT,
  `employee_no` varchar(4) NOT NULL,
  `name` varchar(20) NOT NULL,
  `date` DATE NOT NULL,
  `Number_of_working_days` int(5),
  `Number_of_days_to_work` int(5),
  `Number_of_days_to_work_on_nonstatutory_holidays` int(5),
  `Statutory_holiday_attendance_days` int(5),
  `Days_of_absence` int(5),
  `Late_days` int(5),
  `Number_of_early_departures` int(5),
  PRIMARY KEY (`No`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;