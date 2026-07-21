-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3307
-- Generation Time: Jul 10, 2026 at 01:36 PM
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
  `unit_id` int(11) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `mobile` varchar(15) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admins`
--

INSERT INTO `admins` (`admin_id`, `role_id`, `unit_id`, `email`, `password`, `mobile`, `is_active`, `created_at`, `updated_at`) VALUES
(3, 5, NULL, 'hrhead.themadrassevasadan.org ', '123456', '', 1, '2026-06-18 06:01:49', '2026-06-18 06:28:12'),
(4, 7, 7, 'admin@ladyandal.org', '123456', '', 1, '2026-06-18 06:01:49', '2026-06-21 15:55:57'),
(5, 6, NULL, 'hradmin.themadrassevasadan.org ', '123456', '', 1, '2026-06-18 06:28:32', '2026-06-18 06:28:52');

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
(33, 9, 'BE', 'BE', 'Computer Science', 'Anna University Regional Campus Madurai', 'Anna University', '2020', '2024', 85.00, 8.50, '2026-06-30 14:06:33', '2026-06-30 14:06:33');

-- --------------------------------------------------------

--
-- Table structure for table `candidate_experience`
--

CREATE TABLE `candidate_experience` (
  `candidate_experience_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `company_name` varchar(255) NOT NULL,
  `designation` varchar(255) NOT NULL,
  `employment_type` varchar(100) DEFAULT NULL,
  `start_date` varchar(50) NOT NULL,
  `end_date` varchar(50) DEFAULT NULL,
  `total_experience` varchar(100) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `salary` varchar(100) DEFAULT NULL,
  `notice_period` varchar(100) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `candidate_experience`
--

INSERT INTO `candidate_experience` (`candidate_experience_id`, `user_id`, `company_name`, `designation`, `employment_type`, `start_date`, `end_date`, `total_experience`, `location`, `description`, `salary`, `notice_period`, `created_at`, `updated_at`) VALUES
(33, 9, 'infosys', 'software developer', 'Full-time', '2024-01-01', '2026-03-01', '2 Years 6 Months', NULL, 'testing', '5', 'Immediately Available', '2026-06-30 14:06:33', '2026-06-30 14:06:33');

-- --------------------------------------------------------

--
-- Table structure for table `candidate_metadata`
--

CREATE TABLE `candidate_metadata` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `about` text DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `blood_group` varchar(10) DEFAULT NULL,
  `marital_status` enum('single','married') DEFAULT NULL,
  `personal_address` text DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `pincode` varchar(20) DEFAULT NULL,
  `skills` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`skills`)),
  `languages` text DEFAULT NULL,
  `resume_doc` varchar(255) DEFAULT NULL,
  `certifications` varchar(255) DEFAULT NULL,
  `profile_status` enum('complete','incomplete') DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `candidate_metadata`
--

INSERT INTO `candidate_metadata` (`id`, `user_id`, `about`, `date_of_birth`, `blood_group`, `marital_status`, `personal_address`, `city`, `state`, `country`, `pincode`, `skills`, `languages`, `resume_doc`, `certifications`, `profile_status`, `created_at`, `updated_at`) VALUES
(1, 9, 'Detail-oriented and passionate Computer Science graduate with hands-on internship experience in full-stack web development. Proficient in JavaScript, React, and Python, with a proven ability to collaborate in Agile teams and deliver clean, scalable code', '2003-12-24', 'O+', 'married', NULL, 'Thoothukudi', 'Tamilnadu', NULL, NULL, '[\"Html\", \"Css\", \"JS\"]', 'Tamil, English', 'uploads/resumes/AMBIs project.pdf', NULL, 'complete', '2026-06-20 17:07:33', '2026-06-30 14:06:33'),
(2, 11, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'uploads/resumes/resume_11_1782144658.pdf', NULL, NULL, '2026-06-22 16:10:58', '2026-06-22 16:10:58'),
(3, 10, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'uploads/resumes/AMBIs project.pdf', NULL, NULL, '2026-06-23 17:40:29', '2026-06-23 17:40:29'),
(8, 16, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'uploads/resumes/S_Dhanabalan_Resume-original.pdf', NULL, NULL, '2026-07-06 13:41:56', '2026-07-06 13:41:56');

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
  `candidate_status` enum('screened','ineligible') DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `candidate_screening_answers`
--

INSERT INTO `candidate_screening_answers` (`id`, `candidate_id`, `job_id`, `question_id`, `answer`, `remarks`, `candidate_status`, `created_at`) VALUES
(29, 9, 36, 72, 'No', NULL, 'screened', '2026-07-01 07:10:12'),
(30, 9, 36, 73, 'Yes', NULL, 'screened', '2026-07-01 07:10:12'),
(35, 15, 37, 74, 'Yes', NULL, 'screened', '2026-07-02 05:34:41'),
(36, 15, 37, 75, 'Yes', NULL, 'screened', '2026-07-02 05:34:41'),
(37, 16, 38, 76, '3+', NULL, 'screened', '2026-07-08 11:48:50'),
(38, 16, 38, 77, 'Yes', NULL, 'screened', '2026-07-08 11:48:50'),
(39, 16, 37, 74, 'Yes', NULL, 'screened', '2026-07-08 11:52:02'),
(40, 16, 37, 75, 'Yes', NULL, 'screened', '2026-07-08 11:52:02');

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
(15, 16, 'Round 1 - Accounts team', 'move to hr round', 'NEXT_ROUND', 3, NULL, '2026-07-02 10:13:37', '2026-07-02 10:13:37'),
(16, 17, 'round 2 - hr panel', 'all cleared', 'SELECTED', 3, NULL, '2026-07-02 10:18:46', '2026-07-02 10:18:46');

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
  `applicant_job_status` enum('selected','rejected','hold','next_round') DEFAULT NULL,
  `applicant_stage` enum('prescreen-reject','screened','interview','offer','offer_accepted','onboarding') DEFAULT NULL,
  `offered_salary` decimal(15,2) DEFAULT NULL,
  `joining_date` date DEFAULT NULL,
  `probation_period` varchar(150) DEFAULT NULL,
  `issue_offer` tinyint(1) DEFAULT 0,
  `offer_issued_date` datetime DEFAULT NULL,
  `offer_expiry_date` date DEFAULT NULL,
  `offer_remarks` text DEFAULT NULL,
  `offer_accepted_on` datetime DEFAULT NULL,
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
  `masset_sync_success_on` datetime DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `job_applicants`
--

INSERT INTO `job_applicants` (`job_applicant_id`, `mss_app_no`, `job_id`, `user_id`, `resume_doc`, `cover_letter`, `skills_match`, `applicant_job_status`, `applicant_stage`, `offered_salary`, `joining_date`, `probation_period`, `issue_offer`, `offer_issued_date`, `offer_expiry_date`, `offer_remarks`, `offer_accepted_on`, `offer_template`, `offer_letter_doc`, `issued_by`, `offer_acceptance_status`, `sync_masset`, `masset_synced_at`, `masset_synced_by`, `masset_employee_id`, `masset_status`, `issue_appointment_order`, `masset_sync_success_on`, `created_at`, `updated_at`) VALUES
(21, 'MSS-APP-21', 36, 9, 'uploads/resumes/AMBIs project.pdf', '', NULL, 'selected', 'interview', 8.00, '2026-07-10', '3 Months', 1, '2026-07-02 00:00:00', '2026-07-07', NULL, '2026-07-02 00:00:00', 'standard', 'Dear <span class=\"ph\">Ramesh Kannan</span>,<br><br>\nWe are pleased to offer you the position of <span class=\"ph\">PT Teacher</span> at <span class=\"ph\">Shanthi Sadan</span>, under the <span class=\"ph\">Teaching</span> department.<br><br>\nThis is a full-time position with a gross annual compensation of <span class=\"ph\">8</span> LPA. Your expected date of joining is <span class=\"ph\">10 Jul 2026</span>. You will be subject to a probationary period of <span class=\"ph\">3 Months</span>.<br><br>\nPlease confirm your acceptance by <span class=\"ph\">7 Jul 2026</span>. If you have any questions, feel free to reach out to our HR team.<br><br>\nWe look forward to welcoming you to the team.<br><br>\nWarm regards,<br><strong>School Admin - admin@school.org</strong>', 4, 'accepted', 0, NULL, NULL, NULL, NULL, 0, NULL, '2026-07-01 07:10:12', '2026-07-02 15:19:55'),
(24, 'MSS-APP-24', 37, 15, 'uploads/resumes/anand_data.pdf', '', NULL, NULL, 'screened', NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, 0, NULL, '2026-07-02 05:34:41', '2026-07-02 05:34:41'),
(25, 'MSS-APP-25', 38, 16, 'uploads/resumes/S_Dhanabalan_Resume-original.pdf', '', NULL, NULL, 'screened', NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, 0, NULL, '2026-07-08 11:48:50', '2026-07-08 11:48:50'),
(26, 'MSS-APP-26', 37, 16, 'uploads/resumes/S_Dhanabalan_Resume-original.pdf', '', NULL, NULL, 'interview', NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'pending', 0, NULL, NULL, NULL, NULL, 0, NULL, '2026-07-08 11:52:02', '2026-07-08 12:18:07');

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
(16, 36, 21, 'Round 1 - Accounts team', 'online', '2026-07-13', '10:00:00', '11:00:00', NULL, NULL, NULL, 'https://meet.google.com/abc-defg-hij', NULL, '', 'admin@ladyandal.org', 'completed', NULL, NULL, 3, NULL, '2026-07-02 10:07:28', '2026-07-02 10:13:37'),
(17, 36, 21, 'round 2 - hr panel', 'online', '2026-07-23', '10:00:00', '11:00:00', NULL, NULL, NULL, 'https://meet.google.com/abc-defg-hij', NULL, '', 'admin@ladyandal.org', 'completed', NULL, NULL, 3, NULL, '2026-07-02 10:18:18', '2026-07-02 10:18:46'),
(18, 37, 26, 'Round 1 - Technical Interview', 'online', '2026-07-10', '11:00:00', '12:00:00', NULL, NULL, NULL, 'https://google.meet/sgsa-sasd-bgtb', NULL, '', 'admin@ladyandal.org', 'scheduled', NULL, NULL, 3, NULL, '2026-07-08 12:18:07', '2026-07-08 12:18:07');

-- --------------------------------------------------------

--
-- Table structure for table `job_posts`
--

CREATE TABLE `job_posts` (
  `job_id` int(11) NOT NULL,
  `uuid` char(36) DEFAULT NULL,
  `job_posted_by` int(11) NOT NULL,
  `job_title` varchar(255) DEFAULT NULL,
  `job_type` varchar(100) DEFAULT NULL,
  `job_description` text DEFAULT NULL,
  `school_name` varchar(255) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `programme` varchar(100) DEFAULT NULL,
  `department` varchar(255) DEFAULT NULL,
  `vacancy_count` int(11) DEFAULT NULL,
  `min_exp` varchar(100) DEFAULT NULL,
  `max_exp` varchar(100) DEFAULT NULL,
  `skills_required` text DEFAULT NULL,
  `education_qualification` text DEFAULT NULL,
  `closing_date` date DEFAULT NULL,
  `additional_requirements` text DEFAULT NULL,
  `job_status` enum('publish','draft','closed') DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `views` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `job_posts`
--

INSERT INTO `job_posts` (`job_id`, `uuid`, `job_posted_by`, `job_title`, `job_type`, `job_description`, `school_name`, `location`, `programme`, `department`, `vacancy_count`, `min_exp`, `max_exp`, `skills_required`, `education_qualification`, `closing_date`, `additional_requirements`, `job_status`, `created_at`, `updated_at`, `views`) VALUES
(36, '6e51281e-5eba-485d-8b9e-1f5ceef204d0', 3, 'PT Teacher', 'Full-time', 'testing', 'Shanthi Sadan', 'Chetpet', NULL, 'Teaching', 3, '3', '4', 'Lesson Planning, Student Assessment', 'B.Ed, BFA (Fine Arts)', '2026-07-31', '', 'publish', '2026-07-01 05:37:35', '2026-07-06 07:01:02', 2),
(37, '96514684-c057-4276-a89a-51423b0c313f', 3, 'Musical Teacher', 'Part-time', 'test', 'Sir Mutha Venkatasubba Rao Concert Hall', 'Chetpet', NULL, 'Music', 4, '3', '5', 'Curriculum Development', 'M.E / M.Tech', '2026-07-16', '', 'publish', '2026-07-01 08:55:53', '2026-07-02 05:34:18', 4),
(38, '6c061bfa-dcb1-4af0-b1df-293b266f1f7d', 3, 'testing', 'Full-time', 'testing', 'Sir Mutha School, Chetpet', 'Tambaram', 'Pre-Primary', 'Teaching', 2, '2', '3', 'work balance', 'BE ECE', '2026-07-18', '', 'publish', '2026-07-02 07:49:06', '2026-07-06 10:36:58', 2);

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
(72, 36, 'How many years of experience do you have teaching Mathematics at secondary level?', 'boolean', '[\"Yes\", \"No\"]', 'No', '2026-07-01 05:37:35', '2026-07-01 05:37:35'),
(73, 36, 'Are you CTET/TET certified?', 'boolean', '[\"Yes\", \"No\"]', 'Yes', '2026-07-01 05:37:35', '2026-07-01 05:37:35'),
(74, 37, 'How many years of experience do you have teaching Mathematics at secondary level?', 'boolean', '[\"Yes\", \"No\"]', 'Yes', '2026-07-01 08:55:54', '2026-07-01 08:55:54'),
(75, 37, 'Are you CTET/TET certified?', 'boolean', '[\"Yes\", \"No\"]', 'Yes', '2026-07-01 08:55:54', '2026-07-01 08:55:54'),
(76, 38, 'How many years of experience do you have teaching Mathematics at secondary level?', 'mcq', '[\"2+\", \"3+\"]', '3+', '2026-07-02 07:49:06', '2026-07-02 07:49:06'),
(77, 38, 'Are you CTET/TET certified?', 'boolean', '[\"Yes\", \"No\"]', 'Yes', '2026-07-02 07:49:06', '2026-07-02 07:49:06');

-- --------------------------------------------------------

--
-- Table structure for table `job_view_logs`
--

CREATE TABLE `job_view_logs` (
  `id` int(11) NOT NULL,
  `job_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `viewed_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `job_view_logs`
--

INSERT INTO `job_view_logs` (`id`, `job_id`, `user_id`, `viewed_at`) VALUES
(9, 37, 9, '2026-07-02 04:30:54'),
(10, 36, 9, '2026-07-02 04:39:20'),
(13, 37, 15, '2026-07-02 05:34:18'),
(14, 38, 9, '2026-07-02 15:27:02'),
(15, 36, 16, '2026-07-06 07:01:02'),
(16, 38, 16, '2026-07-06 10:36:58');

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

--
-- Dumping data for table `notification_logs`
--

INSERT INTO `notification_logs` (`notification_id`, `sender_user_id`, `recipient_user_id`, `sender_type`, `recipient_type`, `recipient_mobile`, `recipient_email`, `user_role`, `notification_type`, `channel`, `title`, `message`, `status`, `is_read`, `read_at`, `created_at`, `updated_at`) VALUES
(1, 12, 3, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Ramesh Kannan for \'Musical Teacher\' at The Madras Seva Sadan Higher Secondary School, Chetpet.', 'sent', 1, '2026-07-01 06:01:25', '2026-06-30 15:57:07', '2026-07-01 06:01:25'),
(2, 12, 5, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Ramesh Kannan for \'Musical Teacher\' at The Madras Seva Sadan Higher Secondary School, Chetpet.', 'sent', 1, '2026-07-01 06:54:41', '2026-06-30 15:57:08', '2026-07-01 06:54:41'),
(3, 12, 3, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Ramesh Kannan for \'Chemistry Teacher\' at Prem Vihar.', 'sent', 1, '2026-07-01 06:01:25', '2026-06-30 16:28:46', '2026-07-01 06:01:25'),
(4, 12, 5, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Ramesh Kannan for \'Chemistry Teacher\' at Prem Vihar.', 'sent', 1, '2026-07-01 06:54:41', '2026-06-30 16:28:46', '2026-07-01 06:54:41'),
(5, 9, 3, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Ramesh Kannan for \'PT Teacher\' at Shanthi Sadan.', 'sent', 1, '2026-07-02 05:39:08', '2026-07-01 07:10:12', '2026-07-02 05:39:08'),
(6, 9, 5, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Ramesh Kannan for \'PT Teacher\' at Shanthi Sadan.', 'sent', 0, NULL, '2026-07-01 07:10:12', '2026-07-01 01:40:12'),
(7, 13, 3, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Ramesh Kannan for \'Musical Teacher\' at Sir Mutha Venkatasubba Rao Concert Hall.', 'sent', 1, '2026-07-02 05:39:08', '2026-07-02 05:21:02', '2026-07-02 05:39:08'),
(8, 13, 5, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Ramesh Kannan for \'Musical Teacher\' at Sir Mutha Venkatasubba Rao Concert Hall.', 'sent', 0, NULL, '2026-07-02 05:21:02', '2026-07-01 23:51:02'),
(9, 14, 3, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Ramesh Kannan for \'Musical Teacher\' at Sir Mutha Venkatasubba Rao Concert Hall.', 'sent', 1, '2026-07-02 05:39:08', '2026-07-02 05:29:28', '2026-07-02 05:39:08'),
(10, 14, 5, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Ramesh Kannan for \'Musical Teacher\' at Sir Mutha Venkatasubba Rao Concert Hall.', 'sent', 0, NULL, '2026-07-02 05:29:28', '2026-07-01 23:59:28'),
(11, 15, 3, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Ramesh Kannan for \'Musical Teacher\' at Sir Mutha Venkatasubba Rao Concert Hall.', 'sent', 1, '2026-07-02 05:39:08', '2026-07-02 05:34:41', '2026-07-02 05:39:08'),
(12, 15, 5, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Ramesh Kannan for \'Musical Teacher\' at Sir Mutha Venkatasubba Rao Concert Hall.', 'sent', 0, NULL, '2026-07-02 05:34:41', '2026-07-02 00:04:41'),
(13, 3, 9, 'hr', 'candidate', NULL, NULL, NULL, 'interview_scheduled', 'in_app', 'Interview Scheduled', 'An interview for \'PT Teacher\' has been scheduled on Jul 13, 2026 at 10:00 AM (Mode: online).', 'sent', 1, '2026-07-02 15:19:45', '2026-07-02 10:07:28', '2026-07-02 15:19:45'),
(14, 3, 3, 'hr', 'schoolAdmin', NULL, NULL, NULL, 'interview_scheduled', 'in_app', 'Interview Scheduled', 'Interview round \'Round 1 - Accounts team\' has been scheduled for candidate Ramesh Kannan on Jul 13, 2026 at 10:00 AM.', 'sent', 0, NULL, '2026-07-02 10:07:28', '2026-07-02 04:37:28'),
(15, 3, 3, 'hr', 'hr', NULL, NULL, NULL, 'interview_scheduled', 'in_app', 'Interview Scheduled', 'Interview round \'Round 1 - Accounts team\' scheduled for Ramesh Kannan for \'PT Teacher\' on Jul 13, 2026 at 10:00 AM.', 'sent', 1, '2026-07-02 10:12:48', '2026-07-02 10:07:28', '2026-07-02 10:12:48'),
(16, 3, 5, 'hr', 'hr', NULL, NULL, NULL, 'interview_scheduled', 'in_app', 'Interview Scheduled', 'Interview round \'Round 1 - Accounts team\' scheduled for Ramesh Kannan for \'PT Teacher\' on Jul 13, 2026 at 10:00 AM.', 'sent', 0, NULL, '2026-07-02 10:07:28', '2026-07-02 04:37:28'),
(17, 3, 9, 'hr', 'candidate', NULL, NULL, NULL, 'status_update', 'in_app', 'Application Status Update', 'Your application status for \'PT Teacher\' has been updated to next_round.', 'sent', 1, '2026-07-02 15:19:45', '2026-07-02 10:13:37', '2026-07-02 15:19:45'),
(18, 3, 3, 'hr', 'schoolAdmin', NULL, NULL, NULL, 'status_update', 'in_app', 'Application Status Update', 'Application status for candidate Ramesh Kannan has been updated to next_round.', 'sent', 0, NULL, '2026-07-02 10:13:37', '2026-07-02 04:43:37'),
(19, 3, 3, 'hr', 'hr', NULL, NULL, NULL, 'status_update', 'in_app', 'Application Status Update', 'Application status for candidate Ramesh Kannan has been updated to next_round for \'PT Teacher\'.', 'sent', 1, '2026-07-02 10:32:08', '2026-07-02 10:13:37', '2026-07-02 10:32:08'),
(20, 3, 5, 'hr', 'hr', NULL, NULL, NULL, 'status_update', 'in_app', 'Application Status Update', 'Application status for candidate Ramesh Kannan has been updated to next_round for \'PT Teacher\'.', 'sent', 0, NULL, '2026-07-02 10:13:37', '2026-07-02 04:43:37'),
(21, 3, 9, 'hr', 'candidate', NULL, NULL, NULL, 'interview_scheduled', 'in_app', 'Interview Scheduled', 'An interview for \'PT Teacher\' has been scheduled on Jul 23, 2026 at 10:00 AM (Mode: online).', 'sent', 1, '2026-07-02 15:19:45', '2026-07-02 10:18:18', '2026-07-02 15:19:45'),
(22, 3, 3, 'hr', 'schoolAdmin', NULL, NULL, NULL, 'interview_scheduled', 'in_app', 'Interview Scheduled', 'Interview round \'round 2 - hr panel\' has been scheduled for candidate Ramesh Kannan on Jul 23, 2026 at 10:00 AM.', 'sent', 0, NULL, '2026-07-02 10:18:18', '2026-07-02 04:48:18'),
(23, 3, 9, 'hr', 'candidate', NULL, NULL, NULL, 'status_update', 'in_app', 'Application Status Update', 'Your application status for \'PT Teacher\' has been updated to selected.', 'sent', 1, '2026-07-02 15:19:45', '2026-07-02 10:18:46', '2026-07-02 15:19:45'),
(24, 3, 3, 'hr', 'schoolAdmin', NULL, NULL, NULL, 'offer_request', 'in_app', 'Offer Letter Request', 'Candidate Ramesh Kannan has been selected for \'PT Teacher\'. Please generate and issue an offer letter.', 'sent', 0, NULL, '2026-07-02 10:18:46', '2026-07-02 04:48:46'),
(25, 3, 3, 'hr', 'hr', NULL, NULL, NULL, 'status_update', 'in_app', 'Application Status Update', 'Application status for candidate Ramesh Kannan has been updated to selected for \'PT Teacher\'.', 'sent', 1, '2026-07-02 10:32:08', '2026-07-02 10:18:46', '2026-07-02 10:32:08'),
(26, 3, 5, 'hr', 'hr', NULL, NULL, NULL, 'status_update', 'in_app', 'Application Status Update', 'Application status for candidate Ramesh Kannan has been updated to selected for \'PT Teacher\'.', 'sent', 0, NULL, '2026-07-02 10:18:46', '2026-07-02 04:48:46'),
(27, 4, 9, 'schoolAdmin', 'candidate', NULL, NULL, NULL, 'offer_issued', 'in_app', 'Job Offer Issued', 'You have been issued a job offer for the position of \'PT Teacher\' at Shanthi Sadan. Please review it on your dashboard.', 'sent', 1, '2026-07-02 15:19:45', '2026-07-02 15:01:30', '2026-07-02 15:19:45'),
(28, 4, 3, 'schoolAdmin', 'hr', NULL, NULL, NULL, 'offer_issued', 'in_app', 'Job Offer Issued', 'A job offer has been issued to candidate Ramesh Kannan for \'PT Teacher\' at Shanthi Sadan.', 'sent', 1, '2026-07-02 15:19:05', '2026-07-02 15:01:30', '2026-07-02 15:19:05'),
(29, 4, 5, 'schoolAdmin', 'hr', NULL, NULL, NULL, 'offer_issued', 'in_app', 'Job Offer Issued', 'A job offer has been issued to candidate Ramesh Kannan for \'PT Teacher\' at Shanthi Sadan.', 'sent', 0, NULL, '2026-07-02 15:01:30', '2026-07-02 09:31:30'),
(30, 4, 9, 'schoolAdmin', 'candidate', NULL, NULL, NULL, 'offer_issued', 'in_app', 'Job Offer Issued', 'You have been issued a job offer for the position of \'PT Teacher\' at Shanthi Sadan. Please review it on your dashboard.', 'sent', 1, '2026-07-02 15:19:45', '2026-07-02 15:18:19', '2026-07-02 15:19:45'),
(31, 4, 3, 'schoolAdmin', 'hr', NULL, NULL, NULL, 'offer_issued', 'in_app', 'Job Offer Issued', 'A job offer has been issued to candidate Ramesh Kannan for \'PT Teacher\' at Shanthi Sadan by admin@ladyandal.org (Unit: Lady Andal School IB).', 'sent', 1, '2026-07-02 15:19:05', '2026-07-02 15:18:19', '2026-07-02 15:19:05'),
(32, 4, 5, 'schoolAdmin', 'hr', NULL, NULL, NULL, 'offer_issued', 'in_app', 'Job Offer Issued', 'A job offer has been issued to candidate Ramesh Kannan for \'PT Teacher\' at Shanthi Sadan by admin@ladyandal.org (Unit: Lady Andal School IB).', 'sent', 0, NULL, '2026-07-02 15:18:19', '2026-07-02 09:48:19'),
(33, 9, 3, 'candidate', 'hr', NULL, NULL, NULL, 'offer_accepted', 'in_app', 'Offer Accepted', 'Candidate Ramesh Kannan has accepted the offer for \'PT Teacher\' at Shanthi Sadan.', 'sent', 1, '2026-07-08 12:18:37', '2026-07-02 15:19:55', '2026-07-08 12:18:37'),
(34, 9, 5, 'candidate', 'hr', NULL, NULL, NULL, 'offer_accepted', 'in_app', 'Offer Accepted', 'Candidate Ramesh Kannan has accepted the offer for \'PT Teacher\' at Shanthi Sadan.', 'sent', 0, NULL, '2026-07-02 15:19:55', '2026-07-02 09:49:55'),
(35, 16, 3, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Dhana Balan for \'testing\' at Sir Mutha School, Chetpet.', 'sent', 1, '2026-07-08 12:18:37', '2026-07-08 11:48:50', '2026-07-08 12:18:37'),
(36, 16, 5, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Dhana Balan for \'testing\' at Sir Mutha School, Chetpet.', 'sent', 0, NULL, '2026-07-08 11:48:50', '2026-07-08 06:18:50'),
(37, 16, 3, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Dhana Balan for \'Musical Teacher\' at Sir Mutha Venkatasubba Rao Concert Hall.', 'sent', 1, '2026-07-08 12:18:37', '2026-07-08 11:52:02', '2026-07-08 12:18:37'),
(38, 16, 5, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Dhana Balan for \'Musical Teacher\' at Sir Mutha Venkatasubba Rao Concert Hall.', 'sent', 0, NULL, '2026-07-08 11:52:02', '2026-07-08 06:22:02'),
(39, 17, 3, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Dhana balan for \'PT Teacher\' at Shanthi Sadan.', 'sent', 1, '2026-07-08 12:18:28', '2026-07-08 11:56:47', '2026-07-08 12:18:28'),
(40, 17, 5, 'candidate', 'hr', NULL, NULL, NULL, 'new_application', 'in_app', 'New Job Application', 'New application received from Dhana balan for \'PT Teacher\' at Shanthi Sadan.', 'sent', 0, NULL, '2026-07-08 11:56:47', '2026-07-08 06:26:47'),
(41, 3, 16, 'hr', 'candidate', NULL, NULL, NULL, 'interview_scheduled', 'in_app', 'Interview Scheduled', 'An interview for \'Musical Teacher\' has been scheduled on 10 July, 2026 at 11:00 AM (Mode: online).', 'sent', 1, '2026-07-08 12:29:12', '2026-07-08 12:18:07', '2026-07-08 12:29:12'),
(42, 3, 4, 'hr', 'schoolAdmin', NULL, NULL, NULL, 'interview_scheduled', 'in_app', 'Interview Scheduled', 'Interview round \'Round 1 - Technical Interview\' has been scheduled for candidate Dhana Balan on 10 July, 2026 at 11:00 AM.', 'sent', 0, NULL, '2026-07-08 12:18:09', '2026-07-08 06:48:09');

-- --------------------------------------------------------

--
-- Table structure for table `otp_logs`
--

CREATE TABLE `otp_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `otp` int(11) NOT NULL,
  `is_verified` int(11) NOT NULL,
  `purpose` varchar(100) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `otp_logs`
--

INSERT INTO `otp_logs` (`id`, `user_id`, `otp`, `is_verified`, `purpose`, `created_at`) VALUES
(1, 9, 594577, -1, 'password update', '2026-06-30 19:24:29'),
(2, 9, 985821, -1, 'password update', '2026-06-30 19:28:22'),
(3, 9, 269220, -1, 'password update', '2026-06-30 19:29:36'),
(4, 9, 413313, -1, 'password update', '2026-06-30 19:31:12'),
(5, 9, 170534, -1, 'password update', '2026-06-30 19:32:10'),
(6, 9, 498580, -1, 'password update', '2026-06-30 19:35:27'),
(7, 9, 184647, -1, 'password update', '2026-06-30 19:38:54'),
(8, 9, 997912, 1, 'password update', '2026-06-30 19:42:22'),
(9, 9, 478024, 1, 'password update', '2026-07-02 04:53:11'),
(10, 18, 9143, 1, 'mobile update', '2026-07-08 13:18:23');

-- --------------------------------------------------------

--
-- Table structure for table `pre_screening_questions`
--

CREATE TABLE `pre_screening_questions` (
  `id` int(11) NOT NULL,
  `questions` text DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `updated_by` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pre_screening_questions`
--

INSERT INTO `pre_screening_questions` (`id`, `questions`, `created_by`, `updated_by`, `created_at`, `updated_at`) VALUES
(1, 'Have you taught in a CBSE school before?', 5, NULL, '2026-07-02 07:07:31', '2026-07-02 07:07:31'),
(2, 'What is your approach to differentiated learning?', 5, NULL, '2026-07-02 07:07:31', '2026-07-02 07:08:48'),
(3, 'Are you comfortable with online teaching platforms?', 5, NULL, '2026-07-02 07:08:07', '2026-07-02 07:08:07'),
(4, 'Do you have experience with the IB curriculum?', 5, NULL, '2026-07-02 07:08:07', '2026-07-02 07:08:07'),
(5, 'What is your average student pass percentage in board exams?', 5, NULL, '2026-07-02 07:08:40', '2026-07-02 07:08:40'),
(7, 'How Many Years do you have experience in IT Admin?', 3, 3, '2026-07-02 02:18:40', '2026-07-02 02:18:40');

-- --------------------------------------------------------

--
-- Table structure for table `units`
--

CREATE TABLE `units` (
  `id` int(11) NOT NULL,
  `unit_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `units`
--

INSERT INTO `units` (`id`, `unit_name`) VALUES
(1, 'The Madras Seva Sadan - Head Office'),
(5, 'School of Sound and Music'),
(7, 'Lady Andal School IB'),
(8, 'Sir Mutha School, Chetpet'),
(10, 'Prem Vihar'),
(11, 'Shanthi Sadan'),
(12, 'The Madras Seva Sadan Higher Secondary School, Chetpet'),
(13, 'The Madras Seva Sadan Higher Secondary School, Tambaram'),
(14, 'The Madras Seva Sadan Primary School, Tambaram'),
(15, 'Lady Andal Open School - NIOS'),
(16, 'Lady Andal Open School - OS'),
(22, 'Sir & Lady M. Venkatasubba Rao School, Tambaram'),
(24, 'Sir Mutha Venkatasubba Rao Concert Hall'),
(26, 'Lady Andal House of Children, Chetpet');

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
  `image_path` varchar(255) DEFAULT NULL,
  `user_status` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `role_id`, `first_name`, `last_name`, `gender`, `email`, `password`, `mobile`, `oauth_provider`, `image_path`, `user_status`, `created_at`, `updated_at`) VALUES
(9, 8, 'Ramesh', 'Kannan', 'Male', 'ramesramesh0724@gmail.com', '$2b$12$dXaSJMCy/clvvoY92Tqtyeb1VkboFeOBH84xiUiDgXMv7gDawaNYW', '9500755440', NULL, 'uploads/profile_images/profile_9_1782111069.jpg', 1, '2026-06-19 13:14:13', '2026-07-02 04:53:58'),
(10, 8, 'Tharun', 'bala', '', 'tharun123@gmail.com', '$2b$12$TqmBdZe1IWfaXm3TuDTmMu8S8x/yH5G3xSupT7JyDfYpShXRYxxs6', '9503037845', NULL, NULL, 1, '2026-06-22 05:26:02', '2026-06-22 05:26:02'),
(11, 8, 'Aravind', 'ezakiel', '', 'anil12@gmail.com', '$2b$12$nn94VgqenZ8NZ24kNlMHSOLjeGL/FIASyanURfcshkX/UUIIZkoge', '9478389057', NULL, NULL, 1, '2026-06-22 16:10:10', '2026-06-23 17:38:46'),
(15, 8, 'Ramesh', 'Kannan', '', 'rameshkannan8178@gmail.com', '$2b$12$OezGkZdW7Nw6XVvIssZ1OOxv/5LmSuNXPaYBN3hJ9Xpiz9spuj892', '6374848585', 'Google', NULL, 1, '2026-07-02 05:34:11', '2026-07-02 05:34:41'),
(16, 8, 'Dhana', 'Balan', '', 's.dhanabalan02@gmail.com', '$2b$12$TMyXt90w6303oUIPJO5ndOfoT/XbuDKfPZUI2EwoZfJICtCBW3oCO', '8610420713', 'Google', 'uploads/profile_images/profile_16_1783512912.jpg', 1, '2026-07-03 05:54:59', '2026-07-08 12:15:12'),
(18, 8, 'Tarun', 'S', '', 'tarun@gmail.com', '$2b$12$O22S4vwvBTdpHOI5gYY7ieFottaDAH62nS1lpvdqp9a/Fy1CdSVkS', '9345548743', NULL, NULL, 1, '2026-07-08 13:03:12', '2026-07-08 13:18:37');

-- --------------------------------------------------------

--
-- Table structure for table `user_login_logs`
--

CREATE TABLE `user_login_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `user_type` varchar(50) DEFAULT NULL,
  `login_time` datetime DEFAULT NULL,
  `login_type` varchar(50) DEFAULT NULL,
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

INSERT INTO `user_login_logs` (`id`, `user_id`, `user_type`, `login_time`, `login_type`, `logout_time`, `ip_address`, `user_agent`, `status`, `session_id`, `created_at`) VALUES
(1, 9, 'candidate', '2026-07-01 07:09:08', 'password', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwicm9sZSI6ImNhbmRpZGF0ZSIsImV4cCI6MTc4MjkxODU0OH0.-tGrWzVlbC7gfHB6CGmg43Xf_HyzFtKGdEDUZiOx27g', '2026-07-01 07:09:08'),
(2, 3, 'hr_head', '2026-07-01 07:11:34', 'password', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6ImhyX2hlYWQiLCJleHAiOjE3ODI5MTg2OTR9.a3lLcct7evXft_S2Z81-xdaElHNfPrFdG_U2tf8zasU', '2026-07-01 07:11:34'),
(3, 9, 'candidate', '2026-07-01 07:26:57', 'password', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwicm9sZSI6ImNhbmRpZGF0ZSIsImV4cCI6MTc4MjkxOTYxN30.yv6erw55BYckBf7GA6aqVa1RXWwkn7X0k-SrYljcY9g', '2026-07-01 07:26:57'),
(4, 3, 'hr_head', '2026-07-01 07:28:10', 'password', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6ImhyX2hlYWQiLCJleHAiOjE3ODI5MTk2OTB9.VxSK7MWSGp-HN5DjiwD6hNteh6-EdCmYcQb7TsoYCoU', '2026-07-01 07:28:10'),
(5, 3, 'hr_head', '2026-07-01 08:47:32', 'password', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6ImhyX2hlYWQiLCJleHAiOjE3ODI5MjQ0NTJ9.NBAkvX1zWwXffRoRwu_TWKWD9qfeKhI1ebSgNCcrqO0', '2026-07-01 08:47:32'),
(6, 3, 'hr_head', '2026-07-01 08:51:18', 'password', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6ImhyX2hlYWQiLCJleHAiOjE3ODI5MjQ2Nzh9.p724jb3ZWzRTkyUMC8Gg4fP4xca1BKX9HXs8bCJMXy0', '2026-07-01 08:51:18'),
(7, 3, 'hr_head', '2026-07-01 08:52:17', 'password', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6ImhyX2hlYWQiLCJleHAiOjE3ODI5MjQ3Mzd9.-fKh_c0nlwpGSki_m88isqTFqhsbVInJBjnBidXQOLg', '2026-07-01 08:52:17'),
(8, 3, 'hr_head', '2026-07-01 08:55:36', 'password', '2026-07-01 08:56:09', '127.0.0.1', NULL, 'success', NULL, '2026-07-01 08:55:36'),
(9, 3, 'hr_head', '2026-07-02 04:30:10', 'password', '2026-07-02 04:30:23', '127.0.0.1', NULL, 'success', NULL, '2026-07-02 04:30:10'),
(10, 9, 'candidate', '2026-07-02 04:30:42', 'password', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwicm9sZSI6ImNhbmRpZGF0ZSIsImV4cCI6MTc4Mjk5NTQ0Mn0.al5WerlrkSEL6o8I9XqPrYhLmll_K4mOFWzseIQ2i5Q', '2026-07-02 04:30:42'),
(11, 9, 'candidate', '2026-07-02 04:41:24', 'password', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwicm9sZSI6ImNhbmRpZGF0ZSIsImV4cCI6MTc4Mjk5NjA4NH0.X2rrGLannM6pkYOm-7AEEdviz-05e6pPMp4Ng-XIUSs', '2026-07-02 04:41:24'),
(12, 9, 'candidate', '2026-07-02 05:19:29', 'password', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwicm9sZSI6ImNhbmRpZGF0ZSIsImV4cCI6MTc4Mjk5ODM2OX0.whGE4UeJG7BwROZB53h-xWMS81PUfZfXcOroLHggcow', '2026-07-02 05:19:29'),
(13, 13, 'candidate', '2026-07-02 05:20:23', 'google', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMyIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODI5OTg0MjN9.46rM6x6h2SB9qFDGSQEbS3_81ppMjqpQW0BMGqq-r7Y', '2026-07-02 05:20:23'),
(14, 14, 'candidate', '2026-07-02 05:28:55', 'google', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNCIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODI5OTg5MzV9.EBfp527fETfTFBnKTaVrPDOfDsMbik-N6EAsyZRwiMk', '2026-07-02 05:28:55'),
(15, 15, 'candidate', '2026-07-02 05:34:11', 'google', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNSIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODI5OTkyNTF9.6vIcwjEEBQnhrwv7cUd3-fc8ZPwniyROaC6csi-4Jps', '2026-07-02 05:34:11'),
(16, 3, 'hr_head', '2026-07-02 05:38:54', 'password', '2026-07-02 11:00:49', '127.0.0.1', NULL, 'success', NULL, '2026-07-02 05:38:54'),
(17, 4, 'school_admin', '2026-07-02 11:01:11', 'password', '2026-07-02 11:02:41', '127.0.0.1', NULL, 'success', NULL, '2026-07-02 11:01:11'),
(18, 3, 'hr_head', '2026-07-02 11:02:59', 'password', '2026-07-02 12:24:24', '127.0.0.1', NULL, 'success', NULL, '2026-07-02 11:02:59'),
(19, 4, 'school_admin', '2026-07-02 12:24:44', 'password', '2026-07-02 13:25:18', '127.0.0.1', NULL, 'success', NULL, '2026-07-02 12:24:44'),
(20, 3, 'hr_head', '2026-07-02 13:25:30', 'password', '2026-07-02 13:43:56', '127.0.0.1', NULL, 'success', NULL, '2026-07-02 13:25:30'),
(21, 4, 'school_admin', '2026-07-02 13:44:13', 'password', '2026-07-02 14:26:40', '127.0.0.1', NULL, 'success', NULL, '2026-07-02 13:44:13'),
(22, 3, 'hr_head', '2026-07-02 14:27:42', 'password', '2026-07-02 15:12:49', '127.0.0.1', NULL, 'success', NULL, '2026-07-02 14:27:42'),
(23, 4, 'school_admin', '2026-07-02 14:27:57', 'password', '2026-07-02 15:17:48', '127.0.0.1', NULL, 'success', NULL, '2026-07-02 14:27:57'),
(24, 4, 'school_admin', '2026-07-02 15:17:59', 'password', '2026-07-02 15:18:41', '127.0.0.1', NULL, 'success', NULL, '2026-07-02 15:17:59'),
(25, 3, 'hr_head', '2026-07-02 15:18:53', 'password', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6ImhyX2hlYWQiLCJleHAiOjE3ODMwMzQzMzN9.EKqgPK6jNe23ftu_dwa8RmFVA6ILJX78_ImHwpgAQ7E', '2026-07-02 15:18:53'),
(26, 9, 'candidate', '2026-07-02 15:19:32', 'password', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Iiwicm9sZSI6ImNhbmRpZGF0ZSIsImV4cCI6MTc4MzAzNDM3Mn0.F42tJLKoW0ewgPRlQ5UhHk6MlR6CL9IXQOkmhQsFnoE', '2026-07-02 15:19:32'),
(27, 16, 'candidate', '2026-07-03 05:54:59', 'google', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNiIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODMwODY4OTl9.8BIBgbTwOLeF7OXnT0VEcPt55ysSyXPmRg6qwyIT6Fo', '2026-07-03 05:54:59'),
(28, 16, 'candidate', '2026-07-06 06:59:13', 'google', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNiIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODMzNDk5NTN9.hUGnB7tT51spO8z_sIlqY1tr1chxeUo6N3cYoYeBH2I', '2026-07-06 06:59:13'),
(29, 16, 'candidate', '2026-07-06 10:35:23', 'google', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNiIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODMzNjI5MjN9.rD3OvXNAS7X05-sJlZlpCUYZGcVULL7Nrwx9sgPnaUQ', '2026-07-06 10:35:23'),
(30, 16, 'candidate', '2026-07-06 12:30:59', 'google', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNiIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODMzNjk4NTl9.Njo9Eg6MHxx75_AR5Gt-lZww9ALReYYhtIgTnOpY7s0', '2026-07-06 12:30:59'),
(31, 16, 'candidate', '2026-07-06 12:39:18', 'google', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNiIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODMzNzAzNTh9.ca4tw5AvNtk5ighVQP4kYRQp3t9LzxcMy9WGxdlyzy8', '2026-07-06 12:39:18'),
(32, 16, 'candidate', '2026-07-06 13:28:06', 'google', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNiIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODMzNzMyODZ9.GEF2QGTpInTcCvuQp2KpI4G2c3MLBZu3lrG6x7OVFAY', '2026-07-06 13:28:06'),
(33, 16, 'candidate', '2026-07-07 07:29:56', 'google', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNiIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODM0MzgxOTZ9.054GxF0VQU9QP1iaeg5huhWLqpm7EmKHohyZFcnUVak', '2026-07-07 07:29:56'),
(34, 3, 'hr_head', '2026-07-08 06:33:58', 'password', '2026-07-08 06:35:41', '127.0.0.1', NULL, 'success', NULL, '2026-07-08 06:33:58'),
(35, 3, 'hr_head', '2026-07-08 06:36:48', 'password', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6ImhyX2hlYWQiLCJleHAiOjE3ODM1MjE0MDh9.EYt57-Do5Oe_ap5yBEiCuqS9jM7_Fn60COb-IfCrKeg', '2026-07-08 06:36:48'),
(36, 3, 'hr_head', '2026-07-08 06:48:55', 'password', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6ImhyX2hlYWQiLCJleHAiOjE3ODM1MjIxMzV9.IM0RjHDHITUPbPrSopnILKK7CnPIVoXG1i_bA2leAfA', '2026-07-08 06:48:55'),
(37, 3, 'hr_head', '2026-07-08 06:49:45', 'password', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6ImhyX2hlYWQiLCJleHAiOjE3ODM1MjIxODV9.In5yVQueyszneFWxEfnfkYJ5PCkdfYRBoOR1tdMeBww', '2026-07-08 06:49:45'),
(38, 3, 'hr_head', '2026-07-08 06:50:56', 'password', '2026-07-08 07:35:28', '127.0.0.1', NULL, 'success', NULL, '2026-07-08 06:50:56'),
(39, 4, 'school_admin', '2026-07-08 07:35:40', 'password', '2026-07-08 07:44:52', '127.0.0.1', NULL, 'success', NULL, '2026-07-08 07:35:40'),
(40, 3, 'hr_head', '2026-07-08 07:44:59', 'password', '2026-07-08 09:25:09', '127.0.0.1', NULL, 'success', NULL, '2026-07-08 07:44:59'),
(41, 4, 'school_admin', '2026-07-08 09:25:17', 'password', '2026-07-08 09:32:39', '127.0.0.1', NULL, 'success', NULL, '2026-07-08 09:25:17'),
(42, 3, 'hr_head', '2026-07-08 09:32:47', 'password', '2026-07-08 11:12:34', '127.0.0.1', NULL, 'success', NULL, '2026-07-08 09:32:47'),
(43, 16, 'candidate', '2026-07-08 11:13:46', 'google', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNiIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODM1MzgwMjZ9.Cg5bi0dLdDhQi7TPvAo0IQZskdWTFoem3QFI1_4EEcg', '2026-07-08 11:13:46'),
(44, 17, 'candidate', '2026-07-08 11:55:03', 'google', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNyIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODM1NDA1MDN9.iEvhGrQx_KG6IY5-_cTbDd_7FO0p39tljBiXgnbc56o', '2026-07-08 11:55:03'),
(45, 17, 'candidate', '2026-07-08 12:10:50', 'google', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNyIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODM1NDE0NTB9.iboXhY9mFgZbV9S0khVeaPJ8N0INwH-3ugWdRDmdIuI', '2026-07-08 12:10:50'),
(46, 16, 'candidate', '2026-07-08 12:11:27', 'google', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNiIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODM1NDE0ODd9.km3UplrzRPXMgOunWS-EPUAlCvlUH1nmL4F6npAARcg', '2026-07-08 12:11:27'),
(47, 3, 'hr_head', '2026-07-08 12:16:10', 'password', '2026-07-08 12:27:56', '127.0.0.1', NULL, 'success', NULL, '2026-07-08 12:16:10'),
(48, 16, 'candidate', '2026-07-08 12:28:22', 'google', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNiIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODM1NDI1MDJ9.ySL5kcUk8e7_7tbgtttH8AQxYAeVVtuM_zE6RCBBxWs', '2026-07-08 12:28:22'),
(49, 16, 'candidate', '2026-07-08 12:49:07', 'google', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNiIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODM1NDM3NDd9.1e0AGZhEfsPsywusCq-LWoaC3CggPLMTYmO6apEjmwE', '2026-07-08 12:49:07'),
(50, 18, 'candidate', '2026-07-08 13:03:12', NULL, NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxOCIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODM1NDQ1OTJ9.ghntRo1bgGej2l4KQXoTn65-skttBwPvwW_xCkvcKSg', '2026-07-08 13:03:12'),
(51, 18, 'candidate', '2026-07-08 13:03:50', 'password', NULL, '127.0.0.1', NULL, 'success', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxOCIsInJvbGUiOiJjYW5kaWRhdGUiLCJleHAiOjE3ODM1NDQ2MzB9.zr3OK1pRsC7NWwMwqsdnb52MzXedWEeRIZnlPnRy5ws', '2026-07-08 13:03:50');

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
(5, 'hr_head'),
(6, 'hr_team'),
(7, 'school_admin'),
(8, 'candidate');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admins`
--
ALTER TABLE `admins`
  ADD PRIMARY KEY (`admin_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `fk_role_id` (`role_id`),
  ADD KEY `fk_unit_id` (`unit_id`);

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
-- Indexes for table `job_view_logs`
--
ALTER TABLE `job_view_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_job_view_logs_job_id` (`job_id`),
  ADD KEY `ix_job_view_logs_user_id` (`user_id`);

--
-- Indexes for table `notification_logs`
--
ALTER TABLE `notification_logs`
  ADD PRIMARY KEY (`notification_id`);

--
-- Indexes for table `otp_logs`
--
ALTER TABLE `otp_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `pre_screening_questions`
--
ALTER TABLE `pre_screening_questions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `created_by` (`created_by`),
  ADD KEY `updated_by` (`updated_by`);

--
-- Indexes for table `units`
--
ALTER TABLE `units`
  ADD PRIMARY KEY (`id`);

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
  MODIFY `admin_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `candidate_education_details`
--
ALTER TABLE `candidate_education_details`
  MODIFY `candidate_education_details_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;

--
-- AUTO_INCREMENT for table `candidate_experience`
--
ALTER TABLE `candidate_experience`
  MODIFY `candidate_experience_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

--
-- AUTO_INCREMENT for table `candidate_metadata`
--
ALTER TABLE `candidate_metadata`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `candidate_screening_answers`
--
ALTER TABLE `candidate_screening_answers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=43;

--
-- AUTO_INCREMENT for table `interview_remarks`
--
ALTER TABLE `interview_remarks`
  MODIFY `interview_remarks_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `job_applicants`
--
ALTER TABLE `job_applicants`
  MODIFY `job_applicant_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `job_interview_schedule`
--
ALTER TABLE `job_interview_schedule`
  MODIFY `Job_interview_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `job_posts`
--
ALTER TABLE `job_posts`
  MODIFY `job_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

--
-- AUTO_INCREMENT for table `job_pre_screening_questions`
--
ALTER TABLE `job_pre_screening_questions`
  MODIFY `question_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=78;

--
-- AUTO_INCREMENT for table `job_view_logs`
--
ALTER TABLE `job_view_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `notification_logs`
--
ALTER TABLE `notification_logs`
  MODIFY `notification_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=43;

--
-- AUTO_INCREMENT for table `otp_logs`
--
ALTER TABLE `otp_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `pre_screening_questions`
--
ALTER TABLE `pre_screening_questions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `units`
--
ALTER TABLE `units`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `user_login_logs`
--
ALTER TABLE `user_login_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=52;

--
-- AUTO_INCREMENT for table `user_roles`
--
ALTER TABLE `user_roles`
  MODIFY `role_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `admins`
--
ALTER TABLE `admins`
  ADD CONSTRAINT `fk_role_id` FOREIGN KEY (`role_id`) REFERENCES `user_roles` (`role_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_unit_id` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

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
-- Constraints for table `job_view_logs`
--
ALTER TABLE `job_view_logs`
  ADD CONSTRAINT `job_view_logs_ibfk_1` FOREIGN KEY (`job_id`) REFERENCES `job_posts` (`job_id`),
  ADD CONSTRAINT `job_view_logs_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `otp_logs`
--
ALTER TABLE `otp_logs`
  ADD CONSTRAINT `otp_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `pre_screening_questions`
--
ALTER TABLE `pre_screening_questions`
  ADD CONSTRAINT `pre_screening_questions_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `admins` (`admin_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `pre_screening_questions_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `admins` (`admin_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `fk_user_role` FOREIGN KEY (`role_id`) REFERENCES `user_roles` (`role_id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
