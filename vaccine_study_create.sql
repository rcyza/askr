CREATE TABLE `participant` (
	`id`	INTEGER UNIQUE,
	PRIMARY KEY(id)
);

CREATE TABLE `enrolment_checklist` (
	`record_id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`participant_id`	INTEGER references participant(id),
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

CREATE INDEX enrolment_participant_index ON enrolment_checklist(participant_id);

CREATE TABLE `road_to_health` (
    `record_id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `participant_id`	INTEGER references participant(id),
    `dob`  TEXT,
    `bweight` NUMERIC,
    `blength` INTEGER,
    `bheadc` INTEGER,
    `problems` TEXT,
    `apgar1` INTEGER,
    `apgar5` INTEGER, 
    `gest_age` INTEGER,
    `other_imm` INTEGER DEFAULT 0,
    `measles1` INTEGER DEFAULT 0,
    `m1_date` TEXT,
    `m1_batch_no` TEXT,
    `m1_weight` NUMERIC,
    `m1_height` INTEGER
);

CREATE INDEX rth_participant_index ON road_to_health(participant_id);

CREATE TABLE `sun_diary` (
	`record_id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`participant_ID`	INTEGER references participant(id),
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

CREATE INDEX sun_diary_participant_index ON sun_diary(participant_id);

CREATE TABLE `questionnaire` (
    `record_id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `participant_id`	INTEGER references participant(id),
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
    `q11weight`         DECIMAL,
    `q11height`         INTEGER,
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

CREATE INDEX questionnaire_participant_index ON questionnaire(participant_id);
