# -*- coding: utf-8 -*-

import os
import const
import sqlite3
import io
import csv
from flask_wtf import Form
from flask_wtf.file import FileField
from flask import Flask, request, g, redirect, url_for, render_template, flash
from wtforms import StringField, IntegerField, DateField, TextAreaField, DecimalField, SelectField, validators
from wtforms.validators import ValidationError

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'vaccine_study.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

app.config['DEBUG'] = True

times = ["Before 10am", "10am-2pm", "After 2pm"]
check_headings = ["Inside", "Car/Bus/etc", "Sun", "Shade", "Hat", "Sunscreen", "Sunglasses", "Dress", "Short Sleeve",
                  "Long Sleeve", "Shorts", "Pants", "Costume"]

pages = ["sun_diary",
         "road_to_health",
         "enrolment_checklist",
         "questionnaire",
         "observations",
         "telephonic_followup",
         "participant_flow_checklist",
         "blood_results",
         "weather_data"]

#  href, id, caption
navigation_bar = [("/", "", "Home"),
                  ("participant", "participant", "Participants"),
                  ("sun_diary", "sun_diary", "Sun Diary"),
                  ("road_to_health", "road_to_health", "Road to Health"),
                  ("enrolment_checklist", "enrolment_checklist", "Enrolment Checklist"),
                  ("questionnaire", "questionnaire", "Questionnaire"),
                  ("observations", "observations", "Observations"),
                  ("telephonic_followup", "telephonic_followup", "Telephonic Followup"),
                  ("participant_flow_checklist", "participant_flow_checklist", "Flow Checklist"),
                  ("blood_results", "blood_results", "Blood Results"),
                  ("weather_data", "weather_data", "Weather Data")]

participant_tables = [("participant", "participant", "Participant Information"),
                      ("sun_diary", "sun_diary", "Sun Diary"),
                      ("road_to_health", "road_to_health", "Road to Health"),
                      ("enrolment_checklist", "enrolment_checklist", "Enrolment Checklist"),
                      ("questionnaire", "questionnaire", "Questionnaire"),
                      ("telephonic_followup", "telephonic_followup", "Telephonic Followup"),
                      ("participant_flow_checklist", "participant_flow_checklist", "Flow Checklist"),
                      ("blood_results", "blood_results", "Blood Results")]


class LegalValues(object):
    def __init__(self, values=[], message=None):
        self.values = values
        self.max = max
        if not message:
            message = u'Illegal value.'
        self.message = message

    def __call__(self, form, field):
        val = field.data

        if self.values:
            if val not in self.values:
                raise ValidationError(self.message)


class UniqueValues(object):
    """ validator that checks field uniqueness """

    def __init__(self, model, field, message=None):
        self.model = model
        self.field = field
        if not message:
            message = u'this element already exists'
        self.message = message

    def __call__(self, form, field):

        db = get_db()
        check = db.cursor().execute("select count(*) from " + self.model + " where " + self.field + "=? ",
                                    [field.data]).fetchone()[0]

        if check != 0:
            raise ValidationError(self.message)


class BaseForm(Form):
    @classmethod
    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls

    @classmethod
    def remove_field(cls, name):
        delattr(cls, name)
        return cls


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


@app.before_first_request
def check_db():
    """tries to find a sqlite db"""
    if not os.path.isfile(app.config['DATABASE']):
        init_db()


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('vaccine_study_create.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def askr_main():
    db = get_db()

    id_list = {}

    for href, table_name, title in participant_tables:
        id_list[table_name] = db.cursor().execute("select participant_ID from " + table_name).fetchall()
        print table_name, id_list[table_name]

    response_data = {}

    table_map = {"sun_diary": 0,
                 "road_to_health": 1,
                 "enrolment_checklist": 2,
                 "questionnaire": 3,
                 "telephonic_followup": 4,
                 "participant_flow_checklist": 5,
                 "blood_results": 6,
                 "participant": 7}

    columns = ["Sun Diary",
               "Road to Health",
               "Enrolment Checklist",
               "Questionnaire",
               "Telephonic Followup",
               "Flow Checklist",
               "Blood Results",
               "Participant Information"]

    for key, value in id_list.iteritems():
        for participant_id in id_list[key]:
            if participant_id[0] not in response_data:
                response_data[participant_id[0]] = [0, 0, 0, 0, 0, 0, 0, 0]

            cur_resp = response_data[participant_id[0]]
            cur_resp[table_map[key]] = 1
            response_data[participant_id[0]] = cur_resp

    return render_template('display.html', title=navigation_bar[0][2], navigation_bar=navigation_bar,
                           page_name=navigation_bar[0][1], response_data=response_data, cols=columns)


@app.route('/' + pages[0])
def sun_diary():
    #    db = get_db()
    #    cur = db.execute('select title, text from entries order by id desc')
    #    entries = cur.fetchall()

    return render_template('sun_diary.html', times=times, headings=check_headings, title="Sun Diary",
                           navigation_bar=navigation_bar, page_name="sun_diary")


@app.route('/sun_diary/add', methods=['POST'])
def add_entry():
    #    db.execute('insert into entries (title, text) values (?, ?)',
    #               [request.form['title'], request.form['text']])
    #    db.commit()

    #    record_id, participant_ID, time, date, in_building, in_vehicle, in_sun, in_shade, wore_hat,
    #    wore_sunscreen, wore_sunglasses, wore_dress, wore_shortsleeves, wore_longsleeves, wore_shorts,
    #    wore_pants, wore_costume

    # raise ValueError("add entry")

    db = get_db()
    for day in range(1, 8):
        for time in times:
            selected_items = request.form.getlist(str(day) + time)
            s = [request.form['participant_id'], time, request.form['day' + str(day)]]
            for heading in check_headings:
                if heading in selected_items:
                    s.append(1)
                else:
                    s.append(0)
            print s
            db.execute("insert into sun_diary (participant_ID, time, date, in_building, in_vehicle, in_sun, in_shade, "
                       "wore_hat, wore_sunscreen, wore_sunglasses, wore_dress, wore_shortsleeves, wore_longsleeves, "
                       "wore_shorts, wore_pants, wore_costume) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       s)
    db.commit()

    flash('New entry was successfully posted')
    return redirect(url_for('sun_diary'))


@app.route('/' + navigation_bar[1][0], methods=['GET', 'POST'])
def participant():
    fields = [('Participant ID', 'participant_id', 'INTEGER', 'UNIQUE'),
              ('Name', 'name', 'STRING', ''),
              ('Contact Number', 'contact_number', 'STRING', ''),
              ('Alternative Contact Number', 'contact_number_alt', 'STRING', '')]

    return generate_page(fields, "participant", "participant", "Participant")


@app.route('/' + pages[1], methods=['GET', 'POST'])
def road_to_health():
    allowed = [777, 888, 999]
    yes_no = (
        (0, "0 - Yes"), (1, "1 - No"), (777, "777 - Default Value "), (888, "888 - Not Applicable "),
        (999, "999 - Missing "))

    fields = [('Participant ID', 'participant_id', 'INTEGER', 'UNIQUE'),
              ('Date of birth', 'dob', 'DATE', '%d%b%Y'),
              ('Birth weight (kg)', 'bweight', 'NUMERIC', 3),
              ('Birth length (cm)', 'blength', 'NUMERIC', 3),
              ('Birth head circumference (cm)', 'bheadc', 'NUMERIC', 3),
              ('Problems during pregnancy/ birth/ neonatally', 'problems', 'TEXT', ''),
              ('APGAR 1 Minute (/10)', 'apgar1', 'INTEGER', range(0, 11) + allowed),
              ('APGAR 5 Minutes (/10)', 'apgar5', 'INTEGER', range(0, 11) + allowed),
              ('Gestational age', 'gest_age', 'INTEGER', ''),
              ('Received other immunisations prior', 'other_imm', 'SELECT', yes_no),
              ('Received measles 1', 'measles1', 'SELECT', yes_no),
              ('Date Measles 1 Received', 'm1_date', 'DATE', '%d%b%Y'),
              ('Batch number of measles 1', 'm1_batch_no', 'STRING', ''),
              ('Weight at Measles 1 (kg)', 'm1_weight', 'NUMERIC', 3),
              ('Height at Measles 1 (cm)', 'm1_height', 'NUMERIC', 3)]

    return generate_page(fields, "road_to_health", "road_to_health", "Road To Health")


@app.route('/' + pages[2], methods=['GET', 'POST'])
def enrolment_checklist():
    std_yes_no = (
        (0, "0 - Yes"), (1, "1 - No"), (777, "777 - Default Value "), (888, "888 - Not Applicable "),
        (999, "999 - Missing "))

    fields = [('Participant ID', 'participant_ID', 'INTEGER', 'UNIQUE'),
              # 1. Child is here to receive second measles vaccine?
              ('Here for second measles vaccine', 'to_receive_second_vax', 'SELECT', std_yes_no),
              # 2. Child received first measles vaccine?
              ('Child received first vaccine', 'received_first_vax', 'SELECT', std_yes_no),
              # 3. Mother is able to sign consent (>/= 18years old)?
              ('Mother can consent', 'mother_can_consent', 'SELECT', std_yes_no),
              # 4. Mother has child’s road to health chart?
              ('Has road to health chart', 'has_road_to_health_chart', 'SELECT', std_yes_no),
              # 5. Mother confirms they will be available for duration of study?
              ('Mother available for duration of study', 'available_for_study', 'SELECT', std_yes_no),
              # 6. Does this person meet ALL the above requirements (i.e. answers is YES to all 5 questions)?
              ('Meets all requirements', 'meets_requirements', 'SELECT', std_yes_no),
              ('Date enrolled', 'date_enrolled', 'DATE', '%d%b%Y'),
              ('Contact number', 'contact_number', 'STRING', ''),
              ('Alternate contact number', 'alt_contact_number', 'STRING', '')]

    return generate_page(fields, "enrolment_checklist", "enrolment_checklist", "Enrolment Checklist")


@app.route('/' + pages[3], methods=['GET', 'POST'])
def questionnaire():
    allowed = [(777, "777 - Default Value "), (888, "888 - Not Applicable "), (999, "999 - Missing ")]

    yes_no = [(1, "1 - No"), (2, "2 - Yes")] + allowed

    std_yes_no = [(0, "0 - Yes"), (1, "1 - No")] + allowed

    yes_no_dont_know = [(1, "1 - No"), (2, "2 - Yes"), (3, "3 - Don't know")] + allowed

    fields = [('Participant ID', 'participant_ID', 'INTEGER', 'UNIQUE'),
              ('1. Relation to child', 'q01', 'SELECT', [(1, "1 - Mother"),
                                                         (2, "2 - Guardian"),
                                                         (3, "3 - Family Relation")] + allowed),
              ('2. Ethnicity', 'q02', 'SELECT', [(1, "1 - Black"),
                                                 (2, "2 - Indian/Asian"),
                                                 (3, "3 - White"),
                                                 (4, "4 - Coloured"),
                                                 (5, "5 - Other")] + allowed),
              ('Other Ethnicity', 'q02Other', 'STRING', ''),
              ('3. Your Age', 'q03', 'SELECT', [(1, "1 - 18-25"),
                                                (2, "2 - 26-35"),
                                                (3, "3 - 36-45"),
                                                (4, "4 - 46-60"),
                                                (5, "5 - Over 61")] + allowed),
              ('4. Child age years', 'q04years', 'INTEGER', ''),
              ('4. Child age months', 'q04months', 'INTEGER', ''),
              ('5. Child Sex', 'q05', 'SELECT', [(1, "1 - Male"),
                                                 (2, "2 - Female")] + allowed),
              ('6. Albinism', 'q06', 'SELECT', yes_no),
              ('7. HIV Status', 'q07', 'SELECT', [(1, "1 - Positive"),
                                                  (2, "2 - Negative")] + allowed),
              ('8. Child Skin', 'q08', 'SELECT', [(1, "1 - Very Fair"),
                                                  (2, "2 - White"),
                                                  (3, "3 - Light Brown"),
                                                  (4, "4 - Brown"),
                                                  (5, "5 - Dark Brown"),
                                                  (6, "6 - Very Dark Brown")] + allowed),
              ('9. Child gets sunburned', 'q09', 'SELECT', yes_no),
              ('10. Skin sensitivity', 'q10', 'SELECT', [(1, "1 - Very Sensitive"),
                                                         (2, "2 - Sensitive"),
                                                         (3, "3 - Moderately Sensitive"),
                                                         (4, "4 - Not at all")] + allowed),
              ('11. Child weight (kg)', 'q11weight', 'NUMERIC', 3),
              ('11. Child height (cm)', 'q11height', 'NUMERIC', 3),
              ('12. On medication', 'q12', 'SELECT', yes_no),
              ('12. Med 1 Name', 'q12med_1', 'STRING', ''),
              ('12. Med 1 Times', 'q12med_1_times', 'INTEGER', ''),
              ('12. Med 2 Name', 'q12med_2', 'STRING', ''),
              ('12. Med 2 Times', 'q12med_2_times', 'INTEGER', ''),
              ('12. Med 3 Name', 'q12med_3', 'STRING', ''),
              ('12. Med 3 Times', 'q12med_3_times', 'INTEGER', ''),
              ('13. Child activity level', 'q13', 'SELECT', allowed + [(1, "1 - Very Active"),
                                                                       (2, "2 - Moderately Active"),
                                                                       (3, "3 - Not very Active")]),
              ('14. Caregiver smokes', 'q14', 'SELECT', yes_no),
              ('15. Anyone in house smokes', 'q15', 'SELECT', yes_no),
              ('16. Breastfed at Vaccination', 'q16', 'SELECT', yes_no_dont_know),
              ('17. Still breastfed now', 'q17', 'SELECT', yes_no_dont_know),
              ('18. Mother had vaccinations', 'q18', 'SELECT', yes_no_dont_know),
              ('19. Mother had measles', 'q19', 'SELECT', yes_no_dont_know),
              ('20. Playing in sunshine', 'q20', 'SELECT', [(1, "1 - Healthy"),
                                                            (2, "2 - Harmful"),
                                                            (3, "3 - Don't know ")] + allowed),
              ('21. Travel to clinic', 'q21', 'SELECT', [(1, "1 - Bus"),
                                                         (2, "2 - Taxi"),
                                                         (3, "3 - Train"),
                                                         (4, "4 - Walk"),
                                                         (5, "5 - Private car"),
                                                         (6, "6 - Other")] + allowed),
              ('21. Other travel to clinic', 'q21other', 'STRING', ''),
              ('22. Time to travel to clinic', 'q22', 'SELECT', [(1, "1 - Less than 10 minutes"),
                                                                 (2, "2 - Between 10 and 30 minutes"),
                                                                 (3, "3 - Between 30 and 60 minutes"),
                                                                 (4, "4 - Over 60 minutes ")] + allowed),
              ('23. Long queue', 'q23', 'SELECT', yes_no_dont_know),
              ('24. Where do you wait at clinic', 'q24', 'SELECT', [(1, "1 - Shaded area"),
                                                                    (2, "2 - Unshaded area"),
                                                                    (3, "3 - Inside ")] + allowed),
              ('25. How long do you wait at clinic', 'q25', 'SELECT', [(1, "1 - Less than 15 minutes"),
                                                                       (2, "2 - Between 15 and 30 minutes"),
                                                                       (3, "3 - Between 30 and 60 minutes"),
                                                                       (4, "4 - Over 60 minutes ")] + allowed),
              ('26. Child sun protection outside clinic', 'q26', 'SELECT', yes_no + [(3, "3 - Wait inside")]),
              ('27. Child sun protection outside frequency', 'q27', 'SELECT', [(1, "1 - Usually"),
                                                                               (2, "2 - Sometimes"),
                                                                               (3, "3 - Seldom"),
                                                                               (4, "4 - Never"),
                                                                               (5, "5 - Wait inside")] + allowed),
              ('28a. Hat or cap', 'q28_a', 'SELECT', std_yes_no),
              ('28b. Sunscreen', 'q28_b', 'SELECT', std_yes_no),
              ('28c. Long sleeve shirt', 'q28_c', 'SELECT', std_yes_no),
              ('28d. Trousers', 'q28_d', 'SELECT', std_yes_no),
              ('28e. Umbrella', 'q28_e', 'SELECT', std_yes_no),
              ('29a. Face', 'q29_a', 'SELECT', std_yes_no),
              ('29b. Arms', 'q29_b', 'SELECT', std_yes_no),
              ('29c. Legs', 'q29_c', 'SELECT', std_yes_no),
              ('29d. Hands', 'q29_d', 'SELECT', std_yes_no),
              ('29e. Back and shoulders', 'q29_e', 'SELECT', std_yes_no),
              ('29f. No sunscreen', 'q29_f', 'SELECT', std_yes_no),
              ('30. Spends time on weekdays', 'q30', 'SELECT', [(1, "1 - Mostly Inside"),
                                                                (2, "2 - Mostly Outside")] + allowed),
              ('31. Spends time on weekends', 'q31', 'SELECT', [(1, "1 - Mostly Inside"),
                                                                (2, "2 - Mostly Outside")] + allowed),
              ('32. Location spent outside', 'q32', 'SELECT', [(1, "1 - Shade"),
                                                               (2, "2 - Open/sun")] + allowed),
              ('33. Hours spent outside', 'q33', 'SELECT', [(1, "1 - Less than 1 hour"),
                                                            (2, "2 - 1 hour"),
                                                            (3, "3 - 2 hours"),
                                                            (4, "4 - 3 hours"),
                                                            (5, "5 - More than 3 hours")] + allowed),
              ('34a. Hat or cap', 'q34_a', 'SELECT', std_yes_no),
              ('34b. Sunscreen', 'q34_b', 'SELECT', std_yes_no),
              ('34c. Long sleeve shirt', 'q34_c', 'SELECT', std_yes_no),
              ('34d. Trousers', 'q34_d', 'SELECT', std_yes_no),
              ('34e. Umbrella', 'q34_e', 'SELECT', std_yes_no),
              ('35a. Face', 'q35_a', 'SELECT', std_yes_no),
              ('35b. Arms', 'q35_b', 'SELECT', std_yes_no),
              ('35c. Legs', 'q35_c', 'SELECT', std_yes_no),
              ('35d. Hands', 'q35_d', 'SELECT', std_yes_no),
              ('35e. Back and shoulders', 'q35_e', 'SELECT', std_yes_no),
              ('35f. No sunscreen', 'q35_f', 'SELECT', std_yes_no),
              ('36. Sunburn or blisters', 'q36', 'SELECT', yes_no)]

    return generate_page(fields, "questionnaire", "questionnaire", "Questionnaire")


@app.route('/' + pages[4], methods=['GET', 'POST'])
def observations():
    allowed = [(777, "777 - Default Value "), (888, "888 - Not Applicable "), (999, "999 - Missing ")]
    yes_no = [(1, "1 - No"), (2, "2 - Yes")] + allowed

    fields = [('Date', 'date', 'DATE', '%d%b%Y'),
              ('Observation time', 'obs_time', 'SELECT', [(1, "1 - Before 10h00 "),
                                                          (2, "2 - 10h00 - 14h00"),
                                                          (3, "3 - After 14h00")] + allowed),
              ('Describe weather today', 'weather', 'SELECT', [(1, '1 - Sunny'),
                                                               (2, '2 - Some cloud cover'),
                                                               (3, '3 - Completely overcast'),
                                                               (4, '4 - Raining')] + allowed),
              ('What is the temperature today?', 'temperature', 'SELECT', [(1, "1 - Cold"),
                                                                           (2, "2 - Mild"),
                                                                           (3, "3 - Hot")] + allowed),
              ('Clinic name', 'clinic', 'STRING', ''),
              ('People waiting outside', 'parents_waiting', 'SELECT', yes_no),
              ('Shade awning or trees outside', 'shading', 'SELECT', yes_no),
              ('Percentage all people in shade (%)', 'percent_shaded', 'INTEGER', ''),
              ('People standing in shade', 'parents_shaded', 'SELECT', yes_no),
              ('Percentage parents and children in shade (%)', 'percentage_parents_shaded', 'INTEGER', ''),
              ('Parents and children waiting in direct sun', 'waiting_direct_sun', 'SELECT', yes_no),
              ('Parents and children waiting inside clinic', 'waiting_inside', 'SELECT', yes_no)]

    return generate_page(fields, "observations", "observations", "Observations")


@app.route('/' + pages[5], methods=['GET', 'POST'])
def telephonic_followup():
    allowed = [(777, "777 - Default Value "), (888, "888 - Not Applicable "), (999, "999 - Missing ")]
    yes_no = [(1, "1 - Yes"), (2, "2 - No")] + allowed

    fields = [('Participant ID', 'participant_ID', 'INTEGER', 'UNIQUE'),
              ('1. Liked using sun protection', 'q1likedprotection', 'SELECT', yes_no),
              ('1ci. Didn\'t like: feeling of sunscreen', 'q1ci', 'SELECT', yes_no),
              ('1cii. Didn\'t like: sunscreen would hurt', 'q1cii', 'SELECT', yes_no),
              ('1ciii. Didn\'t like: friends or family sentiment', 'q1ciii', 'SELECT', yes_no),
              ('1civ. Didn\'t like: the umbrella', 'q1civ', 'SELECT', yes_no),
              ('1cv. Didn\'t like: other reasons', 'q1cv', 'TEXT', ''),
              ('2. Easy to use sun protection?', 'q2easytouse', 'SELECT', yes_no),
              ('3. Child liked sun protection?', 'q3childlikedprotection', 'SELECT', yes_no),
              ('3ci. Child didn\'t like: want to wear', 'q3ci', 'SELECT', yes_no),
              ('3cii. Child didn\'t like: hat', 'q3cii', 'SELECT', yes_no),
              ('3ciii. Child didn\'t like: sunscreen', 'q3ciii', 'SELECT', yes_no),
              ('3civ. Child didn\'t like: long sleeve top', 'q3civ', 'SELECT', yes_no),
              ('Further comments', 'furthercomments', 'TEXT', '')]

    return generate_page(fields, "telephonic_followup", "telephonic_followup", "Telephonic Followup")


@app.route('/' + pages[6], methods=['GET', 'POST'])
def participant_flow_checklist():
    allowed = [(777, "777 - Default Value "), (888, "888 - Not Applicable "), (999, "999 - Missing ")]
    yes_no = [(1, "1 - Yes"), (2, "2 - No")] + allowed

    fields = [('Participant ID', 'participant_ID', 'INTEGER', 'UNIQUE'),
              ('Enrollment date', 'enroll_date', 'DATE', '%d%b%Y'),
              ('Contact details collected', 'details_collected', 'SELECT', yes_no),
              ('Questionnaire', 'questionnaire', 'SELECT', yes_no),
              ('Completion date', 'completion_date', 'DATE', '%d%b%Y'),
              ('Sun protection equipment provided', 'sun_prot_prov', 'SELECT', yes_no),
              ('Sun diary provided', 'sun_diary_prov', 'SELECT', yes_no),
              ('Vaccination date', 'vaccination_date', 'DATE', '%d%b%Y'),
              ('Measles vaccine brand', 'vaccine_brand', 'SELECT', [(1, "1 - Sanofi"),
                                                                    (2, "2 - MeasBio")] + allowed),
              ('Administration route', 'admin_route', 'SELECT', [(1, "1 - Subcutaneous"),
                                                                 (2, "2 - Intramuscular")] + allowed),
              ('3 week contact date', 'contact_3week_date', 'DATE', '%d%b%Y'),
              ('4 week follow up date', 'followup_4week_date', 'DATE', '%d%b%Y'),
              ('Sun diary returned', 'sun_diary_ret', 'SELECT', yes_no),
              ('reason not returned', 'not_ret_reason', 'STRING', yes_no),
              ('Received travel money', 'money_recvd', 'SELECT', yes_no),
              ('Received toy', 'toy_recvd', 'SELECT', yes_no),
              ('Blood sample taken date', 'blood_taken_date', 'DATE', '%d%b%Y'),
              ('Sample refrigerated (how quickly)', 'sample_refrig', 'STRING', yes_no),
              ('Delivered to lab date', 'delivered_lab', 'DATE', '%d%b%Y'),
              ('2 month follow up Completed date', 'followup_2month_date', 'DATE', '%d%b%Y'),
              ('Blood results given', 'blood_results_given', 'SELECT', yes_no)]

    return generate_page(fields, "participant_flow_checklist", "participant_flow_checklist", "Flow Checklist")


@app.route('/' + pages[7], methods=['GET', 'POST'])
def blood_results():
    allowed = [(777, "777 - Default Value "), (888, "888 - Not Applicable "), (999, "999 - Missing ")]

    fields = [('Participant ID', 'participant_ID', 'INTEGER', 'UNIQUE'),
              ('ELISA Factor', 'measles_ELISA_factor', 'SELECT', [(1, "1 - Positive"),
                                                                  (2, "2 - Negative")] + allowed),
              ('Titre (mIU/ml)', 'measles_titre', 'NUMERIC', 3)]

    return generate_page(fields, "blood_results", "blood_results", "Blood Results")


@app.route('/' + pages[8], methods=['GET'])
def weather_data():

    fields = [('Data upload', 'data_upload', 'DATAFILE', 'TABDEL'),
              ('Clinic', 'clinic_id', 'SELECT', [(1, "1 - Intervention"),
                                                 (2, "2 - Control")])]

    return generate_page(fields, "weather_data", "weather_data", "Weather Data")


@app.route('/' + pages[8], methods=['POST'])
def upload_data():

    f = request.files['data_upload']
    clinic_id = request.form['clinic_id']

    if not f:
        return "No file"

    stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.reader(stream, delimiter='\t')

    next(csv_input, None)
    next(csv_input, None)

    db = get_db()

    for row in csv_input:
        row.insert(0, clinic_id)

        print row
        db.execute("insert into weather_data (clinic_id, time, date, temp_out, hi_temp, low_temp, out_humidity, "
                   "dewpoint, wind_speed, wind_direction, wind_run, hi_speed, hi_direction, wind_chill, heat_index, "
                   "thw_index, bar, Rain, rain_rate, heat_DD, cool_DD, in_temp, in_humidity, in_dew, in_heat, in_EMC, "
                   "in_air_density, wind_sample, wind_TX, iss_reception, arc_int) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,"
                   " ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   row)

    db.commit()

    flash('Weather data was successfully uploaded')

    return redirect(url_for('weather_data'))


def generate_page(fields, page_name, add_method, title):
    field_names = []
    flag_fields = []
    data_fields = []
    params = []

    print "generating page", page_name

    for field in fields:
        if field[const.VARIABLE_TYPE] == 'INTEGER':
            if field[const.ALLOWED_VALUES] == 'UNIQUE':
                BaseForm.append_field(
                    field[const.DISPLAY_NAME] if field[const.VARIABLE_NAME] == '' else field[const.VARIABLE_NAME],
                    IntegerField(field[const.DISPLAY_NAME], [UniqueValues(add_method, field[const.VARIABLE_NAME])]))
            else:
                BaseForm.append_field(
                    field[const.DISPLAY_NAME] if field[const.VARIABLE_NAME] == '' else field[const.VARIABLE_NAME],
                    IntegerField(field[const.DISPLAY_NAME], [LegalValues(field[const.ALLOWED_VALUES])]))
        elif field[const.VARIABLE_TYPE] == 'SELECT':
            BaseForm.append_field(
                field[const.DISPLAY_NAME] if field[const.VARIABLE_NAME] == '' else field[const.VARIABLE_NAME],
                SelectField(field[const.DISPLAY_NAME], choices=field[const.ALLOWED_VALUES], default=777, coerce=int))
        elif field[const.VARIABLE_TYPE] == 'DATE':
            BaseForm.append_field(
                field[const.DISPLAY_NAME] if field[const.VARIABLE_NAME] == '' else field[const.VARIABLE_NAME],
                DateField(field[const.DISPLAY_NAME], format=field[const.ALLOWED_VALUES],
                          validators=(validators.Optional(),)))
        elif field[const.VARIABLE_TYPE] == 'TEXT':
            BaseForm.append_field(
                field[const.DISPLAY_NAME] if field[const.VARIABLE_NAME] == '' else field[const.VARIABLE_NAME],
                TextAreaField(field[const.DISPLAY_NAME]))
        elif field[const.VARIABLE_TYPE] == 'STRING':
            BaseForm.append_field(
                field[const.DISPLAY_NAME] if field[const.VARIABLE_NAME] == '' else field[const.VARIABLE_NAME],
                StringField(field[const.DISPLAY_NAME]))
        elif field[const.VARIABLE_TYPE] == 'NUMERIC':
            BaseForm.append_field(
                field[const.DISPLAY_NAME] if field[const.VARIABLE_NAME] == '' else field[const.VARIABLE_NAME],
                DecimalField(field[const.DISPLAY_NAME], places=field[const.ALLOWED_VALUES]))
        elif field[const.VARIABLE_TYPE] == 'DATAFILE':
            BaseForm.append_field(
                field[const.DISPLAY_NAME] if field[const.VARIABLE_NAME] == '' else field[const.VARIABLE_NAME],
                FileField())

        flag_name = "flag_" + field[const.VARIABLE_NAME]

        BaseForm.append_field(
            flag_name, StringField(flag_name)
        )

        field_names.append(
            (field[const.DISPLAY_NAME] if field[const.VARIABLE_NAME] == '' else field[const.VARIABLE_NAME],
             flag_name))

        data_fields.append(
            field[const.DISPLAY_NAME] if field[const.VARIABLE_NAME] == '' else field[const.VARIABLE_NAME])
        flag_fields.append(flag_name)
        params.append('?')

    rth_form = BaseForm(request.form)

    for field in rth_form.data:
        if field not in field_names:
            BaseForm.remove_field(field)

    # if request.method == 'POST':
    #     print "in POST"
    #     if rth_form.validate():

    if not rth_form.validate_on_submit():
        print "did not validate"

        print rth_form.errors
        print rth_form.data

      #  raise ValueError("Build us a shrubbery")

        # for field_name in field_names:
        #     if rth_form[field_name].errors:
        #         for error in rth_form[field_name].errors:
        #             print error
        return render_template('_render_template.html', title=title, page_name=page_name, add_method=add_method,
                               fields=field_names, form=rth_form, navigation_bar=navigation_bar)

    print "validated "
    ins = ','.join(data_fields)
    into = ','.join(params)

    values = [request.form[field_name] for field_name in data_fields]

    db = get_db()
    db.execute("insert into " + add_method + " (" + ins + ") values (" + into + ")",
               values)

    for flag_field in flag_fields:
        if not request.form[flag_field] == '':
            db.execute("insert into flagged_records (participant_ID, variable_name, table_name, flag_text) values (" +
                       "?, ?, ?, ? )",
                       [request.form["participant_ID"], flag_field[5:], add_method, request.form[flag_field]])

    db.commit()

    return redirect(url_for(page_name))


if __name__ == '__main__':
    print "Starting up askr. "
    app.run(host='0.0.0.0')  # , debug=True, use_debugger=False, use_reloader=False)
