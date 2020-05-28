CREATE TABLE `USER_ACCOUNT` (
  `No` int(4) NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL,
  `employee_no` varchar(4) NOT NULL,
  `employment_status` varchar(10) NOT NULL,
  `department` varchar(10) NOT NULL,
  `mail_address` varchar(30) NOT NULL,
  `loginID` varchar(10) NOT NULL,
  `password` varchar(10) NOT NULL,
  PRIMARY KEY (`No`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;