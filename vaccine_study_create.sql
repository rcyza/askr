CREATE TABLE `participant` (
	`record_id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`participant_ID`	INTEGER UNIQUE,
	`name`	TEXT,
	`contact_number`	TEXT,
	`contact_number_alt`	TEXT
);

CREATE TABLE `enrolment_checklist` (
    `record_id`	INTEGER PRIMARY KEY AUTOINCREMENT,
    `participant_ID`	INTEGER references participant(participant_ID),
    `to_receive_second_vax`	INTEGER DEFAULT 0,
    `received_first_vax`	INTEGER DEFAULT 0,
    `mother_can_consent`	INTEGER DEFAULT 0,
    `has_road_to_health_chart`	INTEGER DEFAULT 0,
    `available_for_study`	INTEGER DEFAULT 0,
    `meets_requirements`	INTEGER DEFAULT 0,
    `date_enrolled`	TEXT,
    `contact_number`	TEXT,
    `alt_contact_number`	TEXT
);

CREATE INDEX enrolment_participant_index ON enrolment_checklist(participant_ID);

CREATE TABLE `road_to_health` (
    `record_id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `participant_ID`	INTEGER references participant(participant_ID),
    `dob`  TEXT,
    `bweight` NUMERIC,
    `blength` NUMERIC,
    `bheadc` NUMERIC,
    `problems` TEXT,
    `apgar1` INTEGER,
    `apgar5` INTEGER, 
    `gest_age` INTEGER,
    `other_imm` INTEGER DEFAULT 0,
    `measles1` INTEGER DEFAULT 0,
    `m1_date` TEXT,
    `m1_batch_no` TEXT,
    `m1_weight` NUMERIC,
    `m1_height` NUMERIC
);

CREATE INDEX rth_participant_index ON road_to_health(participant_ID);

CREATE TABLE `sun_diary` (
    `record_id`	INTEGER PRIMARY KEY AUTOINCREMENT,
    `participant_ID`	INTEGER references participant(participant_ID),
    `time`	TEXT,
    `date`	TEXT,
    `in_building`	INTEGER DEFAULT '0',
    `in_vehicle`	INTEGER DEFAULT '0',
    `in_sun`	INTEGER DEFAULT '0',
    `in_shade`	INTEGER DEFAULT '0',
    `wore_hat`	INTEGER DEFAULT '0',
    `wore_sunscreen`	INTEGER DEFAULT '0',
    `wore_sunglasses`	INTEGER DEFAULT '0',
    `wore_dress`	INTEGER DEFAULT '0',
    `wore_shortsleeves`	INTEGER DEFAULT '0',
    `wore_longsleeves`	INTEGER DEFAULT '0',
    `wore_shorts`	INTEGER DEFAULT '0',
    `wore_pants`	INTEGER DEFAULT '0',
    `wore_costume`	INTEGER DEFAULT '0'
);

CREATE INDEX sun_diary_participant_index ON sun_diary(participant_ID);

CREATE TABLE `questionnaire` (
    `record_id`         INTEGER PRIMARY KEY AUTOINCREMENT,
    `participant_ID`	INTEGER references participant(participant_ID),
    `q01`               INTEGER,  -- 3
    `q02`               INTEGER,  -- 5
    `q02Other`          TEXT,     
    `q03`               INTEGER,  -- 5
    `q04years`          INTEGER,
    `q04months`         INTEGER,
    `q05`               INTEGER,  -- 2
    `q06`               INTEGER,  -- 2
    `q07`               INTEGER,  -- 2
    `q08`               INTEGER,  -- 6
    `q09`               INTEGER,  -- 2
    `q10`               INTEGER,  -- 4
    `q11weight`         NUMERIC,
    `q11height`         NUMERIC,
    `q12`               INTEGER,  -- 2
    `q12med_1`          TEXT,  -- 2
    `q12med_1_times`    INTEGER,  -- 2
    `q12med_2`          TEXT,  -- 2
    `q12med_2_times`    INTEGER,  -- 2
    `q12med_3`          TEXT,  -- 2
    `q12med_3_times`    INTEGER,  -- 2
    `q13`               INTEGER,  -- 3
    `q14`               INTEGER,  -- 2
    `q15`               INTEGER,  -- 2
    `q16`               INTEGER,  -- 3
    `q17`               INTEGER,  -- 3
    `q18`               INTEGER,  -- 3
    `q19`               INTEGER,  -- 3
    `q20`               INTEGER,  -- 3
    `q21`               INTEGER,  -- 6
    `q21other`          TEXT,
    `q22`               INTEGER,  -- 4
    `q23`               INTEGER,  -- 3
    `q24`               INTEGER,  -- 3
    `q25`               INTEGER,  -- 3
    `q26`               INTEGER,  -- 3
    `q27`               INTEGER,  -- 5
    `q28_a`             INTEGER DEFAULT 0,
    `q28_b`             INTEGER DEFAULT 0,
    `q28_c`             INTEGER DEFAULT 0,
    `q28_d`             INTEGER DEFAULT 0,
    `q28_e`             INTEGER DEFAULT 0,
    `q29_a`             INTEGER DEFAULT 0,
    `q29_b`             INTEGER DEFAULT 0,
    `q29_c`             INTEGER DEFAULT 0,
    `q29_d`             INTEGER DEFAULT 0,
    `q29_e`             INTEGER DEFAULT 0,
    `q29_f`             INTEGER DEFAULT 0,
    `q30`               INTEGER,  -- 3
    `q31`               INTEGER,  -- 6
    `q32`               INTEGER,  -- 4
    `q33`               INTEGER,  -- 3
    `q34_a`             INTEGER DEFAULT 0,
    `q34_b`             INTEGER DEFAULT 0,
    `q34_c`             INTEGER DEFAULT 0,
    `q34_d`             INTEGER DEFAULT 0,
    `q34_e`             INTEGER DEFAULT 0,
    `q35_a`             INTEGER DEFAULT 0,
    `q35_b`             INTEGER DEFAULT 0,
    `q35_c`             INTEGER DEFAULT 0,
    `q35_d`             INTEGER DEFAULT 0,
    `q35_e`             INTEGER DEFAULT 0,
    `q35_f`             INTEGER DEFAULT 0,
    `q36`               INTEGER  -- 2   
);

CREATE INDEX questionnaire_participant_index ON questionnaire(participant_ID);

CREATE TABLE `telephonic_followup` (
    `record_id`	        INTEGER PRIMARY KEY AUTOINCREMENT,
    `participant_ID`	INTEGER references participant(participant_ID),
    `q1likedprotection`	INTEGER,
    `q1ci`	            INTEGER,
    `q1cii`	            INTEGER,
    `q1ciii`	        INTEGER,
    `q1civ`	            INTEGER,
    `q1cv`	            TEXT,
    `q2easytouse`	    INTEGER,
    `q3childlikedprotection`	INTEGER,
    `q3ci`	            INTEGER,
    `q3cii`	            INTEGER,
    `q3ciii`	        INTEGER,
    `q3civ`	            INTEGER,
    `furthercomments`	TEXT
);

CREATE INDEX telefollowup_participant_index ON telephonic_followup(participant_ID);

CREATE TABLE `blood_results` (
    `record_id`	        INTEGER PRIMARY KEY AUTOINCREMENT,
    `participant_ID`	INTEGER references participant(participant_ID),
    `measles_ELISA_factor` INTEGER,
    `measles_titre`      NUMERIC
);

CREATE INDEX blood_results_participant_index ON blood_results(participant_ID);

CREATE TABLE `participant_flow_checklist` (
    `record_id`	INTEGER PRIMARY KEY AUTOINCREMENT,
    `participant_ID` INTEGER references participant(participant_ID),
    `enroll_date` TEXT,
    `details_collected` INTEGER,
    `questionnaire` INTEGER,
    `completion_date` TEXT,
    `sun_prot_prov` INTEGER,
    `sun_diary_prov` INTEGER,
    `vaccination_date` TEXT,
    `vaccine_brand` INTEGER,
    `admin_route` INTEGER,
    `contact_3week_date` TEXT,
    `followup_4week_date` TEXT,
    `sun_diary_ret` INTEGER,
    `not_ret_reason` TEXT,
    `money_recvd` INTEGER,
    `toy_recvd` INTEGER,
    `blood_taken_date` TEXT,
    `sample_refrig` TEXT,
    `delivered_lab` TEXT,
    `followup_2month_date` TEXT,
    `blood_results_given` INTEGER
);

CREATE INDEX flow_checklist_participant_index ON participant_flow_checklist(participant_ID);

CREATE TABLE `observations` (
    `record_id`	INTEGER PRIMARY KEY AUTOINCREMENT,
    `date`	TEXT,
    `obs_time`	INTEGER,
    `weather`	INTEGER,
    `temperature`	INTEGER,
    `clinic`	TEXT,
    `parents_waiting`	INTEGER,
    `shading`	INTEGER,
    `percent_shaded`	INTEGER,
    `parents_shaded`	INTEGER,
    `percentage_parents_shaded`	INTEGER,
    `waiting_direct_sun`	INTEGER,
    `waiting_inside`	INTEGER
);

CREATE TABLE `flagged_records` (
    `flag_id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `participant_ID` INTEGER,
    `variable_name` TEXT,
    `table_name` TEXT,
    `flag_text` TEXT
);

CREATE TABLE `weather_data` (
    `record_id`	   INTEGER PRIMARY KEY AUTOINCREMENT,
    `clinic_id`	   INTEGER,
    `time`	   TEXT,
    `date`	   TEXT,
    `temp_out`       NUMERIC,
    `hi_temp`        NUMERIC,
    `low_temp`       NUMERIC,
    `out_humidity`   NUMERIC,
    `dewpoint`       NUMERIC,
    `wind_speed`     NUMERIC,
    `wind_direction` NUMERIC,
    `wind_run` 	   NUMERIC,
    `hi_speed` 	   NUMERIC,
    `hi_direction`   NUMERIC,
    `wind_chill`     NUMERIC,
    `heat_index`     NUMERIC,
    `thw_index`      NUMERIC,
    `bar`            NUMERIC,
    `Rain`           NUMERIC,
    `rain_rate`      NUMERIC,
    `heat_DD`        NUMERIC,
    `cool_DD`        NUMERIC,
    `in_temp`        NUMERIC,
    `in_humidity`    NUMERIC,
    `in_dew`         NUMERIC,
    `in_heat`        NUMERIC,
    `in_EMC`         NUMERIC,
    `in_air_density` NUMERIC,
    `wind_sample`    NUMERIC,
    `wind_TX`        NUMERIC,
    `iss_reception`  NUMERIC,
    `arc_int`        NUMERIC
);

