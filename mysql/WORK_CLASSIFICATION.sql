CREATE TABLE `WORK_CLASSIFICATION` (
  `No` int(4) NOT NULL AUTO_INCREMENT,
  `employee_no` varchar(4) NOT NULL,
  `name` varchar(20) NOT NULL,
  `date` DATE NOT NULL,
  `Going_to_work` int(5),
  `Dispatch` int(5),
  `Paid_vacation` int(5),
  `Take_the_morning_off` int(5),
  `Take_the_afternoon_off` int(5),
  `Statutory_holiday_attendance` int(5),
  `Gyeonghui_vacation` int(5),
  `NonRecoverable_late` int(5),
  `NonRecoverable_leave_early` int(5),
  `Saturday_work` int(5),
  `Short_working_hours` int(5),
  PRIMARY KEY (`No`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;