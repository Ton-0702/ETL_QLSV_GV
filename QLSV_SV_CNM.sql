CREATE TABLE `teacher` (
  `teacher_id` nvarchar(6) PRIMARY KEY,
  `name` nvarchar(35),
  `level` nvarchar(15),
  `birthday` DATE,
  `nationality` nvarchar(45),
  `degree` nvarchar(45),
  `graduation_country` nvarchar(45),
  `graduation_year` year
);

CREATE TABLE `subject` (
  `subject_id` varchar(6) PRIMARY KEY,
  `name_subject` nvarchar(80),
  `total_credit` int,
  `program_semester` varchar(3)
);

CREATE TABLE `student` (
  `student_id` varchar(6) PRIMARY KEY,
  `student_name` nvarchar(45),
  `birthday_stu` DATE,
  `sex` varchar(4),
  `academic_year` year,
  `class_name` varchar(10)
);

CREATE TABLE `course_detail` (
  `teacher_id` nvarchar(6),
  `subject_id` varchar(6),
  `type` varchar(15),
  PRIMARY KEY (`teacher_id`, `subject_id`)
);

CREATE TABLE `point` (
  `subject_id` varchar(6),
  `student_id` varchar(6),
  `Score_tk1` float,
  `Score_tk2` float,
  `Score_tk3` float,
  `Score_th1` float,
  `Score_th2` float,
  `Score_th3` float,
  `Score_gk` float,
  `Score_ck` float,
  PRIMARY KEY (`subject_id`, `student_id`)
);

ALTER TABLE `course_detail` ADD FOREIGN KEY (`teacher_id`) REFERENCES `teacher` (`teacher_id`);

ALTER TABLE `course_detail` ADD FOREIGN KEY (`subject_id`) REFERENCES `subject` (`subject_id`);

ALTER TABLE `point` ADD FOREIGN KEY (`subject_id`) REFERENCES `subject` (`subject_id`);

ALTER TABLE `point` ADD FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`);
