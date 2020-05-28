CREATE TABLE `HOLIDAY_AND_VACATION_ACQUISITION` (
  `No` int(4) NOT NULL AUTO_INCREMENT,
  `employee_no` varchar(4) NOT NULL,
  `name` varchar(20) NOT NULL,
  `date` DATE NOT NULL,
  `Number_of_public_holidays` int(5),
  `Paid_leave_days` int(5),
  `Remaining_paid_leave_to_date` int(5),
  `Transfer_holidays` int(5),
  `Transfer_holiday_days_until_today` int(5),
  `Number_of_substitute_holidays` int(5),
  `The_number_of_days_remaining_until_today` int(5),
  `Nonstatutory_holiday_working_hours` int(5),
  `Number_of_days_off` int(5),
  PRIMARY KEY (`No`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;