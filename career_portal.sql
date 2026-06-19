-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 17, 2026 at 08:00 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `career_portal`
--

-- --------------------------------------------------------

--
-- Table structure for table `admins`
--

CREATE TABLE `admins` (
  `admin_id` int(11) NOT NULL,
  `role_id` int(11) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `school_name` text DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admins`
--

INSERT INTO `admins` (`admin_id`, `role_id`, `email`, `password`, `school_name`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 2, 'aravind124@gmail.com', 'aravind@123', NULL, 1, '2026-06-02 15:25:49', '2026-06-02 15:25:49'),
(2, 3, 'dhanabalan12@gmail.com', 'bala@123', 'Sir Mutha', 1, '2026-06-16 14:14:24', '2026-06-17 00:31:02');

-- --------------------------------------------------------

--
-- Table structure for table `candidate_education_details`
--

CREATE TABLE `candidate_education_details` (
  `candidate_education_details_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `education_level` varchar(150) DEFAULT NULL,
  `degree_name` varchar(255) DEFAULT NULL,
  `specialization` varchar(255) DEFAULT NULL,
  `institution_name` varchar(255) DEFAULT NULL,
  `university_name` varchar(255) DEFAULT NULL,
  `start_year` year(4) DEFAULT NULL,
  `end_year` year(4) DEFAULT NULL,
  `percentage` decimal(5,2) DEFAULT NULL,
  `cgpa` decimal(4,2) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `candidate_education_details`
--

INSERT INTO `candidate_education_details` (`candidate_education_details_id`, `user_id`, `education_level`, `degree_name`, `specialization`, `institution_name`, `university_name`, `start_year`, `end_year`, `percentage`, `cgpa`, `created_at`, `updated_at`) VALUES
(2, 3, 'B.E. Computer Science', 'B.E. Computer Science', NULL, NULL, 'Anna University', '2013', '2017', NULL, 8.75, '2026-06-16 21:09:39', '2026-06-16 21:09:39');

-- --------------------------------------------------------

--
-- Table structure for table `candidate_experience`
--

CREATE TABLE `candidate_experience` (
  `candidate_experience_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `company_name` varchar(255) NOT NULL,
  `job_title` varchar(255) NOT NULL,
  `employment_type` varchar(100) DEFAULT NULL,
  `start_date` date NOT NULL,
  `end_date` date DEFAULT NULL,
  `total_experience` varchar(100) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `candidate_experience`
--

INSERT INTO `candidate_experience` (`candidate_experience_id`, `user_id`, `company_name`, `job_title`, `employment_type`, `start_date`, `end_date`, `total_experience`, `location`, `description`, `created_at`, `updated_at`) VALUES
(2, 3, 'TCS', 'Software Engineer', 'Full-time', '2018-06-01', '2021-08-01', NULL, NULL, '', '2026-06-16 21:09:39', '2026-06-16 21:09:39');

-- --------------------------------------------------------

--
-- Table structure for table `candidate_metadata`
--

CREATE TABLE `candidate_metadata` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `marital_status` varchar(50) DEFAULT NULL,
  `personal_address` text DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `pincode` varchar(20) DEFAULT NULL,
  `candidate_category` enum('fresher','experienced') DEFAULT NULL,
  `skills` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`skills`)),
  `resume_doc` varchar(255) DEFAULT NULL,
  `profile_status` enum('complete','incomplete') DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `about` text DEFAULT NULL,
  `designation` varchar(255) DEFAULT NULL,
  `company` varchar(255) DEFAULT NULL,
  `experience` varchar(100) DEFAULT NULL,
  `salary` varchar(100) DEFAULT NULL,
  `expected_salary` varchar(100) DEFAULT NULL,
  `notice_period` varchar(100) DEFAULT NULL,
  `work_mode` varchar(100) DEFAULT NULL,
  `employment_type` varchar(100) DEFAULT NULL,
  `preferred_role` varchar(255) DEFAULT NULL,
  `languages` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `candidate_metadata`
--

INSERT INTO `candidate_metadata` (`id`, `user_id`, `date_of_birth`, `marital_status`, `personal_address`, `city`, `state`, `country`, `pincode`, `candidate_category`, `skills`, `resume_doc`, `profile_status`, `created_at`, `updated_at`, `about`, `designation`, `company`, `experience`, `salary`, `expected_salary`, `notice_period`, `work_mode`, `employment_type`, `preferred_role`, `languages`) VALUES
(1, 3, '1995-05-12', NULL, NULL, 'Chennai', 'Tamil Nadu', NULL, NULL, NULL, '[\"management\", \"good communication\", \"MySQL\"]', NULL, NULL, '2026-06-16 21:09:39', '2026-06-16 21:12:05', 'Updated about section for testing', 'Teacher', 'Laksmi metriculation', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `candidate_screening_answers`
--

CREATE TABLE `candidate_screening_answers` (
  `id` int(11) NOT NULL,
  `candidate_id` int(11) NOT NULL,
  `job_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `answer` text DEFAULT NULL,
  `remarks` text DEFAULT NULL,
  `candidate_status` enum('applied','screened','ineligible') DEFAULT 'applied',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `candidate_screening_answers`
--

INSERT INTO `candidate_screening_answers` (`id`, `candidate_id`, `job_id`, `question_id`, `answer`, `remarks`, `candidate_status`, `created_at`) VALUES
(3, 3, 12, 17, '3', NULL, NULL, '2026-06-16 19:51:51'),
(4, 3, 12, 18, 'Yes', NULL, NULL, '2026-06-16 19:51:51'),
(5, 4, 12, 17, '2', NULL, NULL, '2026-06-17 02:22:58'),
(6, 4, 12, 18, 'No', NULL, NULL, '2026-06-17 02:22:58'),
(7, 3, 16, 25, 'Yes', NULL, NULL, '2026-06-17 02:58:08'),
(8, 3, 16, 26, 'Yes', NULL, NULL, '2026-06-17 02:58:08'),
(9, 4, 18, 29, '2+ years', NULL, NULL, '2026-06-17 04:46:16');

-- --------------------------------------------------------

--
-- Table structure for table `interview_remarks`
--

CREATE TABLE `interview_remarks` (
  `interview_remarks_id` int(11) NOT NULL,
  `job_interview_id` int(11) NOT NULL,
  `round` varchar(50) DEFAULT NULL,
  `remarks` text DEFAULT NULL,
  `applicant_status` varchar(100) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `updated_by` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `interview_remarks`
--

INSERT INTO `interview_remarks` (`interview_remarks_id`, `job_interview_id`, `round`, `remarks`, `applicant_status`, `created_by`, `updated_by`, `created_at`, `updated_at`) VALUES
(1, 2, 'Round 2 - Technical Interview', 'testing', 'SELECTED', 1, NULL, '2026-06-17 00:18:14', '2026-06-17 00:18:14'),
(2, 3, 'Round 1 - Technical Interview', 'Selected', 'SELECTED', 1, NULL, '2026-06-17 03:01:12', '2026-06-17 03:01:12');

-- --------------------------------------------------------

--
-- Table structure for table `job_applicants`
--

CREATE TABLE `job_applicants` (
  `job_applicant_id` int(11) NOT NULL,
  `mss_app_no` varchar(50) NOT NULL,
  `job_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `resume_doc` varchar(255) DEFAULT NULL,
  `cover_letter` text DEFAULT NULL,
  `skills_match` decimal(5,2) DEFAULT NULL,
  `expected_salary` decimal(15,2) DEFAULT NULL,
  `applicant_job_status` enum('selected','rejected','hold','next_round') DEFAULT NULL,
  `offered_salary` decimal(15,2) DEFAULT NULL,
  `issue_offer` tinyint(1) DEFAULT 0,
  `offer_issued_date` datetime DEFAULT NULL,
  `offer_expiry_date` date DEFAULT NULL,
  `offer_remarks` text DEFAULT NULL,
  `offer_template` text DEFAULT NULL,
  `offer_letter_doc` text DEFAULT NULL,
  `issued_by` int(11) DEFAULT NULL,
  `offer_acceptance_status` enum('pending','accepted','expired') DEFAULT 'pending',
  `sync_masset` tinyint(1) DEFAULT 0,
  `masset_synced_at` text DEFAULT NULL,
  `masset_synced_by` int(11) DEFAULT NULL,
  `masset_employee_id` text DEFAULT NULL,
  `masset_status` varchar(50) DEFAULT NULL,
  `issue_appointment_order` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `joining_date` date DEFAULT NULL,
  `probation_period` varchar(150) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `job_applicants`
--

INSERT INTO `job_applicants` (`job_applicant_id`, `mss_app_no`, `job_id`, `user_id`, `resume_doc`, `cover_letter`, `skills_match`, `expected_salary`, `applicant_job_status`, `offered_salary`, `issue_offer`, `offer_issued_date`, `offer_expiry_date`, `offer_remarks`, `offer_template`, `offer_letter_doc`, `issued_by`, `offer_acceptance_status`, `sync_masset`, `masset_synced_at`, `masset_synced_by`, `masset_employee_id`, `masset_status`, `issue_appointment_order`, `created_at`, `updated_at`, `joining_date`, `probation_period`) VALUES
(2, '', 12, 3, 'PE_TM_Binding (1).pdf', '', NULL, 0.00, 'selected', 2.00, 1, '2026-06-17 00:00:00', '2026-06-25', 'testing', 'teaching', 'Dear <span class=\"ph\">Ramesh Kannan</span>,<br><br>\nCongratulations! We are delighted to extend this offer for the role of <span class=\"ph\">Maths</span> at <span class=\"ph\">Sir Mutha</span>.<br><br>\nAs a member of our academic faculty under <span class=\"p', 2, 'accepted', 1, '2026-06-17 01:13:01.955942', 1, 'EMP0002', '', 0, '2026-06-16 19:51:51', '2026-06-17 01:13:01', '2026-06-20', '3 Months'),
(9, '', 16, 3, 'TTBS MIddleware http Interface Ver 1.2 5.pdf', '', NULL, 0.00, 'selected', 4.00, 1, '2026-06-17 00:00:00', '2026-06-20', 'offer issue', 'teaching', 'Dear <span class=\"ph\">Ramesh Kannan</span>,<br><br>\nCongratulations! We are delighted to extend this offer for the role of <span class=\"ph\">chemistry</span> at <span class=\"ph\">Sir Mutha</span>.<br><br>\nAs a member of our academic faculty under <span class=\"ph\">Science & Math</span>, your responsibilities will include curriculum delivery, student assessment, and participation in school events as per the academic calendar.<br><br>\nCompensation: <span class=\"ph\">4</span> LPA | Joining: <span class=\"ph\">25 Jun 2026</span> | Probation: <span class=\"ph\">3 Months</span><br><br>\nKindly confirm your acceptance by <span class=\"ph\">20 Jun 2026</span>.<br><br>\nRegards,<br><strong>School Admin — TMSS</strong><br><br><em style=\"color:var(--text3);font-size:12px;\">Additional terms: offer issue</em>', 2, 'accepted', 1, '2026-06-17 05:51:23.161017', 1, 'EMP-0009', NULL, 0, '2026-06-17 02:58:08', '2026-06-17 05:51:23', '2026-06-25', '3 Months'),
(10, '', 18, 4, 'MOA - MVG.pdf', '', NULL, 0.00, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, 0, '2026-06-17 04:46:16', '2026-06-17 04:46:16', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `job_interview_schedule`
--

CREATE TABLE `job_interview_schedule` (
  `Job_interview_id` int(11) NOT NULL,
  `job_id` int(11) NOT NULL,
  `job_applicant_id` int(11) NOT NULL,
  `interview_round` varchar(100) DEFAULT NULL,
  `interview_mode` enum('offline','online') DEFAULT NULL,
  `scheduled_date` date DEFAULT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `rescheduled_date` date DEFAULT NULL,
  `rescheduled_start_time` time DEFAULT NULL,
  `rescheduled_end_time` time DEFAULT NULL,
  `meeting_link` varchar(255) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `address` text NOT NULL,
  `interviewer_name` varchar(255) DEFAULT NULL,
  `status` enum('scheduled','rescheduled','completed','cancelled') DEFAULT 'scheduled',
  `reschedule_reason` text DEFAULT NULL,
  `cancelled_reason` text DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `rescheduled_by` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `job_interview_schedule`
--

INSERT INTO `job_interview_schedule` (`Job_interview_id`, `job_id`, `job_applicant_id`, `interview_round`, `interview_mode`, `scheduled_date`, `start_time`, `end_time`, `rescheduled_date`, `rescheduled_start_time`, `rescheduled_end_time`, `meeting_link`, `location`, `address`, `interviewer_name`, `status`, `reschedule_reason`, `cancelled_reason`, `created_by`, `rescheduled_by`, `created_at`, `updated_at`) VALUES
(2, 12, 2, 'Round 2 - Technical Interview', 'offline', '2026-06-16', '10:00:00', NULL, NULL, NULL, NULL, NULL, 'admin block', 'admin block', 'lady andal', 'completed', NULL, NULL, 1, NULL, '2026-06-16 21:45:05', '2026-06-17 00:18:14'),
(3, 16, 9, 'Round 1 - Technical Interview', 'offline', '2026-06-17', '10:00:00', NULL, NULL, NULL, NULL, NULL, 'mss', 'mss', 'Sir Mutha', 'completed', NULL, NULL, 1, NULL, '2026-06-17 03:00:48', '2026-06-17 03:01:12');

-- --------------------------------------------------------

--
-- Table structure for table `job_posts`
--

CREATE TABLE `job_posts` (
  `job_id` int(11) NOT NULL,
  `job_unique_id` varchar(50) NOT NULL,
  `job_posted_by` int(11) NOT NULL,
  `job_title` varchar(255) DEFAULT NULL,
  `job_type` varchar(100) DEFAULT NULL,
  `job_description` text DEFAULT NULL,
  `school_name` varchar(255) DEFAULT NULL,
  `department` varchar(255) DEFAULT NULL,
  `vacancy_count` int(11) DEFAULT NULL,
  `min_exp` varchar(100) DEFAULT NULL,
  `max_exp` varchar(100) DEFAULT NULL,
  `skills_required` text DEFAULT NULL,
  `education_qualification` text DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `closing_date` date DEFAULT NULL,
  `additional_requirements` text DEFAULT NULL,
  `job_status` enum('publish','draft','closed') DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `job_posts`
--

INSERT INTO `job_posts` (`job_id`, `job_unique_id`, `job_posted_by`, `job_title`, `job_type`, `job_description`, `school_name`, `department`, `vacancy_count`, `min_exp`, `max_exp`, `skills_required`, `education_qualification`, `start_date`, `closing_date`, `additional_requirements`, `job_status`, `created_at`, `updated_at`) VALUES
(11, 'JOBO5395', 1, 'chemistry', 'Part-time', 'testing', 'Sir Mutha', 'Science & Math', 5, '1', '2', 'Lesson Planning, Curriculum Development, Student Assessment', 'Diploma in Mechanical Engineering, Diploma in Electrical Engineering, Diploma in Education (D.Ed)', '2026-06-16', '2026-06-17', 'testing', 'publish', '2026-06-16 16:11:03', '2026-06-16 20:59:32'),
(12, 'JOB9UCOT', 1, 'Maths', 'Full-time', 'testing', 'Sir Mutha', 'Science & Math', 4, '2', '4', 'Curriculum Development, Student Assessment', 'B.Sc, B.Com', '2026-06-18', '2026-06-17', '', 'publish', '2026-06-16 17:30:23', '2026-06-17 00:41:56'),
(16, 'JOBWNK2F', 1, 'chemistry', 'Part-time', 'testing', 'Sir Mutha', 'Science & Math', 5, '1', '2', 'Lesson Planning, Curriculum Development, Student Assessment', 'Diploma in Mechanical Engineering, Diploma in Electrical Engineering, Diploma in Education (D.Ed)', '2026-06-17', '2026-06-17', 'testing', 'publish', '2026-06-16 20:38:07', '2026-06-17 00:42:02'),
(17, 'JOB3GGAZ', 1, 'PT Teacher', 'Full-time', 'pt teacher', 'Shanthi Sadan', 'Physical Education', 1, '2', '3', 'Curriculum Development', 'MCA', '2026-06-19', '2026-07-11', '', 'publish', '2026-06-17 04:12:42', '2026-06-17 04:12:42'),
(18, 'JOBWJWUX', 1, 'Musical Teacher', 'Full-time', 'testing', 'Sir Mutha School (CBSE)', 'Arts & Music', 3, '1', '2', 'Classroom Management, Lesson Planning, Parent Communication', 'UG - Other', '2026-06-17', '2026-07-17', '', 'publish', '2026-06-17 04:44:58', '2026-06-17 04:44:58');

-- --------------------------------------------------------

--
-- Table structure for table `job_pre_screening_questions`
--

CREATE TABLE `job_pre_screening_questions` (
  `question_id` int(11) NOT NULL,
  `job_id` int(11) NOT NULL,
  `question_text` text DEFAULT NULL,
  `question_type` enum('mcq','boolean') NOT NULL,
  `options` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`options`)),
  `expected_answer` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `job_pre_screening_questions`
--

INSERT INTO `job_pre_screening_questions` (`question_id`, `job_id`, `question_text`, `question_type`, `options`, `expected_answer`, `created_at`, `updated_at`) VALUES
(15, 11, 'How many years of experience do you have teaching Mathematics at secondary level?', 'boolean', '[\"Yes\", \"No\"]', 'Yes', '2026-06-16 16:11:03', '2026-06-16 16:11:03'),
(16, 11, 'Are you CTET/TET certified?', 'boolean', '[\"Yes\", \"No\"]', 'No', '2026-06-16 16:11:03', '2026-06-16 16:11:03'),
(17, 12, 'How many years of experience do you have teaching Mathematics at secondary level?', 'mcq', '[\"2\", \"3\"]', '2', '2026-06-16 17:30:23', '2026-06-16 17:30:23'),
(18, 12, 'Are you CTET/TET certified?', 'boolean', '[\"Yes\", \"No\"]', 'Yes', '2026-06-16 17:30:23', '2026-06-16 17:30:23'),
(25, 16, 'How many years of experience do you have teaching Mathematics at secondary level?', 'boolean', '[\"Yes\", \"No\"]', 'Yes', '2026-06-16 20:38:07', '2026-06-16 20:38:07'),
(26, 16, 'Are you CTET/TET certified?', 'boolean', '[\"Yes\", \"No\"]', 'No', '2026-06-16 20:38:07', '2026-06-16 20:38:07'),
(27, 17, 'How many years of experience do you have teaching Mathematics at secondary level?', 'mcq', '[\"1+\", \"2+\", \"3+\"]', '3+', '2026-06-17 04:12:42', '2026-06-17 04:12:42'),
(28, 17, 'Are you CTET/TET certified?', 'boolean', '[\"Yes\", \"No\"]', 'Yes', '2026-06-17 04:12:42', '2026-06-17 04:12:42'),
(29, 18, 'How many years of experience do you have in Music?', 'mcq', '[\"1 year\", \"2 years\", \"2+ years\"]', '2+ years', '2026-06-17 04:44:58', '2026-06-17 04:44:58');

-- --------------------------------------------------------

--
-- Table structure for table `notification_logs`
--

CREATE TABLE `notification_logs` (
  `notification_id` int(11) NOT NULL,
  `sender_user_id` int(11) DEFAULT NULL,
  `recipient_user_id` int(11) DEFAULT NULL,
  `sender_type` varchar(20) DEFAULT NULL,
  `recipient_type` varchar(20) DEFAULT NULL,
  `recipient_mobile` varchar(20) DEFAULT NULL,
  `recipient_email` varchar(255) DEFAULT NULL,
  `user_role` varchar(50) DEFAULT NULL,
  `notification_type` varchar(100) DEFAULT NULL,
  `channel` varchar(50) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `read_at` datetime DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `gender` varchar(20) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `mobile` varchar(20) DEFAULT NULL,
  `oauth_provider` varchar(50) DEFAULT NULL,
  `oauth_uid` varchar(255) DEFAULT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  `user_status` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `role_id`, `first_name`, `last_name`, `gender`, `email`, `password`, `mobile`, `oauth_provider`, `oauth_uid`, `image_path`, `user_status`, `created_at`, `updated_at`) VALUES
(3, 4, 'Ramesh', 'Kannan', 'male', 'ramesramesh0724@gmail.com', '$2b$12$.BGggakz8zqE6Z9tfeUoH.esXKjqZI2OMv3qcMszyvz.h5rDNqyoO', '9876543210', NULL, NULL, NULL, 1, '2026-06-16 15:09:12', '2026-06-16 21:09:39'),
(4, 4, 'tarun', 'S', '', 'tarun@gmail.com', '$2b$12$uz8xduQ7OAGCv72f5JTW7uXNDzt16ZvdnzWcPffK.Stsn0E.cI6FG', '8610420713', NULL, NULL, NULL, 1, '2026-06-17 01:54:42', '2026-06-17 01:54:42');

-- --------------------------------------------------------

--
-- Table structure for table `user_login_logs`
--

CREATE TABLE `user_login_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `user_type` varchar(50) DEFAULT NULL,
  `login_time` datetime DEFAULT NULL,
  `logout_time` datetime DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `status` enum('success','failed') DEFAULT NULL,
  `session_id` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_login_logs`
--

INSERT INTO `user_login_logs` (`id`, `user_id`, `user_type`, `login_time`, `logout_time`, `ip_address`, `user_agent`, `status`, `session_id`, `created_at`) VALUES
(4, 1, 'hr_admin', '2026-06-16 14:47:26', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzgxNjUwMDQ2fQ.pfg2BKyGnf3tMbmgurLPa40m8Pm9qsCP-yW-Fm39unE', '2026-06-16 14:47:26'),
(5, 1, 'hr_admin', '2026-06-16 14:56:52', '2026-06-16 14:56:56', '192.168.0.12', NULL, 'success', NULL, '2026-06-16 14:56:52'),
(6, 2, 'candidate', '2026-06-16 15:08:09', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwicm9sZSI6ImNhbmRpZGF0ZSIsImV4cCI6MTc4MTY1MTI4OX0.15G2pQB4b_x_cR2D2c-BtAQkLfqOvS67Amitda6ywNQ', '2026-06-16 15:08:09'),
(7, 3, 'candidate', '2026-06-16 15:09:12', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6ImNhbmRpZGF0ZSIsImV4cCI6MTc4MTY1MTM1Mn0.dpeCNj3hBNyl5VXrZ-oNva145g2eA8LuyPofvAKfORQ', '2026-06-16 15:09:12'),
(8, 1, 'hr_admin', '2026-06-16 16:10:23', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzgxNjU1MDIzfQ.P426Lq-S0Rym_SuAddI-1XEazl0wYlDqJcd8wu-KJTU', '2026-06-16 16:10:23'),
(9, 1, 'hr_admin', '2026-06-16 16:17:21', '2026-06-16 16:47:26', '192.168.0.12', NULL, 'success', NULL, '2026-06-16 16:17:21'),
(10, 1, 'hr_admin', '2026-06-16 17:18:21', '2026-06-16 17:18:33', '192.168.0.12', NULL, 'success', NULL, '2026-06-16 17:18:21'),
(11, 1, 'hr_admin', '2026-06-16 17:26:47', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzgxNjU5NjA3fQ.jtYWV_wx0Nnh89874QpF-UB1WHQExuaNvaAZmJWrKi4', '2026-06-16 17:26:47'),
(12, 3, 'candidate', '2026-06-16 19:23:15', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6ImNhbmRpZGF0ZSIsImV4cCI6MTc4MTY2NjU5NX0.zVPybaW3SGlewPM2MlBYlZUy6yq8XLGiNUBewGFhSn8', '2026-06-16 19:23:15'),
(13, 1, 'hr_admin', '2026-06-16 20:08:51', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzgxNjY5MzMxfQ.azXqduKQC_kbPtHm5i-Jtb6uPgiNDwZHC-x1wCcm31Y', '2026-06-16 20:08:51'),
(14, 1, 'hr_admin', '2026-06-16 20:15:02', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzgxNjY5NzAyfQ.seRRksBanipWtl_Nva2cAzjFGxfHvvx_gzUrAgbV8iA', '2026-06-16 20:15:02'),
(15, 1, 'hr_admin', '2026-06-16 20:15:59', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzgxNjY5NzU5fQ.IwIPZ0s-aOEUo5RXfk8q2Hfxf3-b5YxPmD_OiNqmYA4', '2026-06-16 20:15:59'),
(16, 2, 'school_admin', '2026-06-16 20:16:05', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwicm9sZSI6InNjaG9vbF9hZG1pbiIsImV4cCI6MTc4MTY2OTc2NX0.XxvMQj-x74mWpsLKaH-y3LLC4SUw503UFFISYtaiCy0', '2026-06-16 20:16:05'),
(17, 1, 'hr_admin', '2026-06-16 20:19:25', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzgxNjY5OTY1fQ.kzcIuhaFEKlTiMYgP4m_8MQ9R_iTAOkUoWNF_TM8VB8', '2026-06-16 20:19:25'),
(18, 1, 'hr_admin', '2026-06-16 20:19:38', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzgxNjY5OTc4fQ.URbiaMuj1GM2PsrZbFtyPCjEp51_71T-rdR4Hg7Kcvo', '2026-06-16 20:19:38'),
(19, 1, 'hr_admin', '2026-06-16 20:26:41', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzgxNjcwNDAxfQ.EW5vxjEp_21JSh0SDURa0fGQxMTk_k-F8BbS3pEhTyg', '2026-06-16 20:26:41'),
(20, 1, 'hr_admin', '2026-06-16 20:32:12', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzgxNjcwNzMyfQ.8knQ9OdsIuk5bV9tFS9K8qVMV4mTG6oK3uesMHNJd4E', '2026-06-16 20:32:12'),
(21, 1, 'hr_admin', '2026-06-16 20:35:49', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzgxNjcwOTQ5fQ.c_ah3MEmVHsR5Xw37uELZ4aJjzXXhCwQvnjbohHfiII', '2026-06-16 20:35:49'),
(22, 3, 'candidate', '2026-06-16 20:59:17', '2026-06-16 21:15:57', '192.168.0.12', NULL, 'success', NULL, '2026-06-16 20:59:17'),
(23, 1, 'hr_admin', '2026-06-16 21:16:24', '2026-06-16 22:26:05', '192.168.0.12', NULL, 'success', NULL, '2026-06-16 21:16:24'),
(24, 1, 'hr_admin', '2026-06-16 22:28:46', '2026-06-16 22:45:01', '192.168.0.12', NULL, 'success', NULL, '2026-06-16 22:28:46'),
(25, 1, 'hr_admin', '2026-06-16 22:45:16', '2026-06-16 22:56:31', '192.168.0.12', NULL, 'success', NULL, '2026-06-16 22:45:16'),
(26, 1, 'hr_admin', '2026-06-16 22:56:49', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzgxNjc5NDA5fQ.Pp48T4ELJljVbOfR9oOOyejzRPjzAmW17K1XmTO_v4w', '2026-06-16 22:56:49'),
(27, 1, 'hr_admin', '2026-06-16 23:05:16', '2026-06-16 23:49:06', '192.168.0.12', NULL, 'success', NULL, '2026-06-16 23:05:16'),
(28, 2, 'school_admin', '2026-06-16 23:49:31', '2026-06-17 00:05:28', '192.168.0.12', NULL, 'success', NULL, '2026-06-16 23:49:31'),
(29, 1, 'hr_admin', '2026-06-17 00:06:01', '2026-06-17 00:20:43', '192.168.0.12', NULL, 'success', NULL, '2026-06-17 00:06:01'),
(30, 2, 'school_admin', '2026-06-17 00:21:43', '2026-06-17 00:38:56', '192.168.0.12', NULL, 'success', NULL, '2026-06-17 00:21:43'),
(31, 3, 'candidate', '2026-06-17 00:39:11', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6ImNhbmRpZGF0ZSIsImV4cCI6MTc4MTY4NTU1MX0.I3qQy7tyti-UBB-DJfy-zJ1bBiG56RxMXeeWVrNBlj0', '2026-06-17 00:39:11'),
(32, 1, 'hr_admin', '2026-06-17 00:47:28', '2026-06-17 00:53:00', '192.168.0.12', NULL, 'success', NULL, '2026-06-17 00:47:28'),
(33, 2, 'school_admin', '2026-06-17 00:53:30', '2026-06-17 01:05:43', '192.168.0.12', NULL, 'success', NULL, '2026-06-17 00:53:30'),
(34, 1, 'hr_admin', '2026-06-17 01:06:13', NULL, '192.168.0.12', NULL, 'failed', NULL, '2026-06-17 01:06:13'),
(35, 1, 'hr_admin', '2026-06-17 01:06:23', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzgxNjg3MTgzfQ.SGBq6Qq_-brWpF62HBLSI24Tpf3NWtJRmi3CjKWcZIQ', '2026-06-17 01:06:23'),
(36, 1, 'hr_admin', '2026-06-17 01:46:04', '2026-06-17 01:46:14', '192.168.0.12', NULL, 'success', NULL, '2026-06-17 01:46:04'),
(37, 4, 'candidate', '2026-06-17 01:54:42', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0Iiwicm9sZSI6ImNhbmRpZGF0ZSIsImV4cCI6MTc4MTY5MDA4Mn0.yxB7ftt-wVIFqvXgkUiBCK0KjKgQhGxeCndN2cdFpTY', '2026-06-17 01:54:42'),
(38, 1, 'hr_admin', '2026-06-17 02:01:29', '2026-06-17 02:06:39', '192.168.0.12', NULL, 'success', NULL, '2026-06-17 02:01:29'),
(39, 2, 'school_admin', '2026-06-17 02:07:08', '2026-06-17 02:10:16', '192.168.0.12', NULL, 'success', NULL, '2026-06-17 02:07:08'),
(40, 1, 'hr_admin', '2026-06-17 02:10:39', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzgxNjkxMDM5fQ.SrsJ9w-ZxjX030RZjFt61QpnVGDzOFmZuEuw0tm8658', '2026-06-17 02:10:39'),
(41, 4, 'candidate', '2026-06-17 02:15:42', NULL, '192.168.0.12', NULL, 'failed', NULL, '2026-06-17 02:15:42'),
(42, 4, 'candidate', '2026-06-17 02:15:53', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0Iiwicm9sZSI6ImNhbmRpZGF0ZSIsImV4cCI6MTc4MTY5MTM1M30.we8iUk6V82Ts3m7Zh-gjp46adyZrlkw1a5VcPnRAZ5k', '2026-06-17 02:15:53'),
(43, 1, 'hr_admin', '2026-06-17 02:25:35', '2026-06-17 02:47:49', '192.168.0.12', NULL, 'success', NULL, '2026-06-17 02:25:35'),
(44, 3, 'candidate', '2026-06-17 02:54:00', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6ImNhbmRpZGF0ZSIsImV4cCI6MTc4MTY5MzY0MH0.ZI01Dt7YJPx_dJEIQLO4yGREikS66OwJq0HwgH-alcw', '2026-06-17 02:54:00'),
(45, 1, 'hr_admin', '2026-06-17 02:59:34', '2026-06-17 03:01:40', '192.168.0.12', NULL, 'success', NULL, '2026-06-17 02:59:34'),
(46, 2, 'school_admin', '2026-06-17 03:02:00', '2026-06-17 03:03:03', '192.168.0.12', NULL, 'success', NULL, '2026-06-17 03:02:00'),
(47, 3, 'candidate', '2026-06-17 03:03:17', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6ImNhbmRpZGF0ZSIsImV4cCI6MTc4MTY5NDE5N30.Scgy-8DR2yGwq6tgR83EMS7VDdY3lwUv6BznbH_XzBE', '2026-06-17 03:03:17'),
(48, 1, 'hr_admin', '2026-06-17 03:05:28', '2026-06-17 03:56:51', '192.168.0.12', NULL, 'success', NULL, '2026-06-17 03:05:28'),
(49, 3, 'candidate', '2026-06-17 03:57:22', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6ImNhbmRpZGF0ZSIsImV4cCI6MTc4MTY5NzQ0Mn0.SRXxUSuEmLxs0FSEyc3GguRdDrMYp9WKq9n1TtI3O4E', '2026-06-17 03:57:22'),
(50, 3, 'candidate', '2026-06-17 03:59:13', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6ImNhbmRpZGF0ZSIsImV4cCI6MTc4MTY5NzU1M30.Lp7rnUTAZWhqc1TaVYf9Fwz4Nzyg55O7Q-1JZaO33mQ', '2026-06-17 03:59:13'),
(51, 1, 'hr_admin', '2026-06-17 04:09:58', '2026-06-17 04:12:54', '192.168.0.12', NULL, 'success', NULL, '2026-06-17 04:09:58'),
(52, 1, 'hr_admin', '2026-06-17 04:16:50', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzgxNjk4NjEwfQ.wgNkjNpxek591iB83aomBqOQu5u0W45SkOr2FGxCmTc', '2026-06-17 04:16:50'),
(53, 1, 'hr_admin', '2026-06-17 04:39:16', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzgxNjk5OTU2fQ.DW5qGh1mbqKgSYRNKk51pS4nMYuGPef8TuW6hO6EU6Q', '2026-06-17 04:39:16'),
(54, 4, 'candidate', '2026-06-17 04:45:20', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0Iiwicm9sZSI6ImNhbmRpZGF0ZSIsImV4cCI6MTc4MTcwMDMyMH0.rNdyLBPyrDQn43ssZ5_KUlQaTfSoK8syCGbgG3qzSIU', '2026-06-17 04:45:20'),
(55, 1, 'hr_admin', '2026-06-17 04:48:25', NULL, '192.168.0.12', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzgxNzAwNTA1fQ.rQvVeVGOAT2IACijvSZeHZvss-A23ro4YgnAFy4B51o', '2026-06-17 04:48:25');

-- --------------------------------------------------------

--
-- Table structure for table `user_roles`
--

CREATE TABLE `user_roles` (
  `role_id` int(11) NOT NULL,
  `role_name` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_roles`
--

INSERT INTO `user_roles` (`role_id`, `role_name`) VALUES
(1, 'hr_head'),
(2, 'hr_admin'),
(3, 'school_admin'),
(4, 'candidate');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admins`
--
ALTER TABLE `admins`
  ADD PRIMARY KEY (`admin_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `fk_role_id` (`role_id`);

--
-- Indexes for table `candidate_education_details`
--
ALTER TABLE `candidate_education_details`
  ADD PRIMARY KEY (`candidate_education_details_id`),
  ADD KEY `fk_user_educational_id` (`user_id`);

--
-- Indexes for table `candidate_experience`
--
ALTER TABLE `candidate_experience`
  ADD PRIMARY KEY (`candidate_experience_id`),
  ADD KEY `ix_candidate_experience_user_id` (`user_id`);

--
-- Indexes for table `candidate_metadata`
--
ALTER TABLE `candidate_metadata`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_candidate_metadata_id` (`user_id`);

--
-- Indexes for table `candidate_screening_answers`
--
ALTER TABLE `candidate_screening_answers`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_candidate_id` (`candidate_id`),
  ADD KEY `fk_job_list_id` (`job_id`),
  ADD KEY `fk_question_id` (`question_id`);

--
-- Indexes for table `interview_remarks`
--
ALTER TABLE `interview_remarks`
  ADD PRIMARY KEY (`interview_remarks_id`),
  ADD KEY `fk_job_interview_schedule` (`job_interview_id`);

--
-- Indexes for table `job_applicants`
--
ALTER TABLE `job_applicants`
  ADD PRIMARY KEY (`job_applicant_id`),
  ADD KEY `fk_job_post_id` (`job_id`),
  ADD KEY `fk_job_apply_id` (`user_id`),
  ADD KEY `fk_offer_issued_id` (`issued_by`);

--
-- Indexes for table `job_interview_schedule`
--
ALTER TABLE `job_interview_schedule`
  ADD PRIMARY KEY (`Job_interview_id`),
  ADD KEY `fk_job_created_id` (`job_id`),
  ADD KEY `fk_job_applicant_id` (`job_applicant_id`),
  ADD KEY `fk_job_createdby_id` (`created_by`),
  ADD KEY `fk_job_rescheduled_by_id` (`rescheduled_by`);

--
-- Indexes for table `job_posts`
--
ALTER TABLE `job_posts`
  ADD PRIMARY KEY (`job_id`),
  ADD KEY `fk_job_posted_id` (`job_posted_by`);

--
-- Indexes for table `job_pre_screening_questions`
--
ALTER TABLE `job_pre_screening_questions`
  ADD PRIMARY KEY (`question_id`),
  ADD KEY `fk_job_id` (`job_id`);

--
-- Indexes for table `notification_logs`
--
ALTER TABLE `notification_logs`
  ADD PRIMARY KEY (`notification_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `fk_user_role` (`role_id`);

--
-- Indexes for table `user_login_logs`
--
ALTER TABLE `user_login_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_user_login_id` (`user_id`);

--
-- Indexes for table `user_roles`
--
ALTER TABLE `user_roles`
  ADD PRIMARY KEY (`role_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admins`
--
ALTER TABLE `admins`
  MODIFY `admin_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `candidate_education_details`
--
ALTER TABLE `candidate_education_details`
  MODIFY `candidate_education_details_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `candidate_experience`
--
ALTER TABLE `candidate_experience`
  MODIFY `candidate_experience_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `candidate_metadata`
--
ALTER TABLE `candidate_metadata`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `candidate_screening_answers`
--
ALTER TABLE `candidate_screening_answers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `interview_remarks`
--
ALTER TABLE `interview_remarks`
  MODIFY `interview_remarks_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `job_applicants`
--
ALTER TABLE `job_applicants`
  MODIFY `job_applicant_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `job_interview_schedule`
--
ALTER TABLE `job_interview_schedule`
  MODIFY `Job_interview_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `job_posts`
--
ALTER TABLE `job_posts`
  MODIFY `job_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `job_pre_screening_questions`
--
ALTER TABLE `job_pre_screening_questions`
  MODIFY `question_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- AUTO_INCREMENT for table `notification_logs`
--
ALTER TABLE `notification_logs`
  MODIFY `notification_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `user_login_logs`
--
ALTER TABLE `user_login_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=56;

--
-- AUTO_INCREMENT for table `user_roles`
--
ALTER TABLE `user_roles`
  MODIFY `role_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `admins`
--
ALTER TABLE `admins`
  ADD CONSTRAINT `fk_role_id` FOREIGN KEY (`role_id`) REFERENCES `user_roles` (`role_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `candidate_education_details`
--
ALTER TABLE `candidate_education_details`
  ADD CONSTRAINT `fk_user_educational_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `candidate_experience`
--
ALTER TABLE `candidate_experience`
  ADD CONSTRAINT `candidate_experience_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `candidate_metadata`
--
ALTER TABLE `candidate_metadata`
  ADD CONSTRAINT `fk_candidate_metadata_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `candidate_screening_answers`
--
ALTER TABLE `candidate_screening_answers`
  ADD CONSTRAINT `fk_candidate_id` FOREIGN KEY (`candidate_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_job_list_id` FOREIGN KEY (`job_id`) REFERENCES `job_posts` (`job_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_question_id` FOREIGN KEY (`question_id`) REFERENCES `job_pre_screening_questions` (`question_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `interview_remarks`
--
ALTER TABLE `interview_remarks`
  ADD CONSTRAINT `fk_job_interview_schedule` FOREIGN KEY (`job_interview_id`) REFERENCES `job_interview_schedule` (`Job_interview_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `job_applicants`
--
ALTER TABLE `job_applicants`
  ADD CONSTRAINT `fk_job_apply_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_offer_issued_id` FOREIGN KEY (`issued_by`) REFERENCES `admins` (`admin_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `job_interview_schedule`
--
ALTER TABLE `job_interview_schedule`
  ADD CONSTRAINT `fk_job_applicant_id` FOREIGN KEY (`job_applicant_id`) REFERENCES `job_applicants` (`job_applicant_id`),
  ADD CONSTRAINT `fk_job_created_id` FOREIGN KEY (`job_id`) REFERENCES `job_posts` (`job_id`),
  ADD CONSTRAINT `fk_job_createdby_id` FOREIGN KEY (`created_by`) REFERENCES `admins` (`admin_id`),
  ADD CONSTRAINT `fk_job_rescheduled_by_id` FOREIGN KEY (`rescheduled_by`) REFERENCES `admins` (`admin_id`);

--
-- Constraints for table `job_posts`
--
ALTER TABLE `job_posts`
  ADD CONSTRAINT `fk_job_posted_id` FOREIGN KEY (`job_posted_by`) REFERENCES `admins` (`admin_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `job_pre_screening_questions`
--
ALTER TABLE `job_pre_screening_questions`
  ADD CONSTRAINT `fk_job_id` FOREIGN KEY (`job_id`) REFERENCES `job_posts` (`job_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `fk_user_role` FOREIGN KEY (`role_id`) REFERENCES `user_roles` (`role_id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
