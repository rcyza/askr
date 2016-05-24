# -*- coding: utf-8 -*-

import os
import const
from sqlite3 import dbapi2 as sqlite3
from flask_wtf import Form
from flask import Flask, request, g, redirect, url_for, render_template, flash
from wtforms import StringField, IntegerField, DateField, TextAreaField, DecimalField, SelectField
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


class BaseForm(Form):
    @classmethod
    def append_field(cls, name, field):
        setattr(cls, name, field)
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


@app.route('/sun_diary')
def sun_diary():
    #    db = get_db()
    #    cur = db.execute('select title, text from entries order by id desc')
    #    entries = cur.fetchall()

    return render_template('sun_diary.html', times=times, headings=check_headings)


@app.route('/sun_diary/add', methods=['POST'])
def add_entry():
    #    db.execute('insert into entries (title, text) values (?, ?)',
    #               [request.form['title'], request.form['text']])
    #    db.commit()

    #    record_id, participant_ID, time, date, in_building, in_vehicle, in_sun, in_shade, wore_hat,
    #    wore_sunscreen, wore_sunglasses, wore_dress, wore_shortsleeves, wore_longsleeves, wore_shorts,
    #    wore_pants, wore_costume

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


@app.route('/road_to_health', methods=['GET', 'POST'])
def road_to_health():
    allowed = [777, 888, 999]
    yes_no = (
        (0, "0 - Yes"), (1, "1 - No"), (777, "777 - Default Value "), (888, "888 - Not Applicable "),
        (999, "999 - Missing "))

    fields = [('Participant ID', 'participant_id', 'INTEGER', ''),
              ('Date of birth', 'dob', 'DATE', '%d%b%Y'),
              ('Birth weight (kg)', 'bweight', 'NUMERIC', 3),
              ('Birth length (cm)', 'blength', 'NUMERIC', 3),
              ('Birth head circumference (cm)', 'bheadc', 'NUMERIC', 3),
              ('Problems during pregnancy/ birth/ neonatally', 'problems', 'TEXT', ''),
              ('APGAR 1 Minute (/10)', 'apgar1', 'INTEGER', allowed + range(0, 11)),
              ('APGAR 5 Minutes (/10)', 'apgar5', 'INTEGER', allowed + range(0, 11)),
              ('Gestational age', 'gest_age', 'INTEGER', ''),
              ('Received other immunisations prior', 'other_imm', 'SELECT', yes_no),
              ('Received measles 1', 'measles1', 'SELECT', yes_no),
              ('Date Measles 1 Received', 'm1_date', 'DATE', '%d%b%Y'),
              ('Batch number of measles 1', 'm1_batch_no', 'STRING', ''),
              ('Weight at Measles 1 (kg)', 'm1_weight', 'NUMERIC', 3),
              ('Height at Measles 1 (cm)', 'm1_height', 'NUMERIC', 3)]

    return generate_page(fields, "road_to_health", "road_to_health", "Road To Health")


@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    allowed_ints = [777, 888, 999]

    allowed = [(777, "777 - Default Value "), (888, "888 - Not Applicable "), (999, "999 - Missing ")]

    yes_no = allowed + [(1, "1 - No"), (2, "2 - Yes")]

    yes_no_dont_know = allowed + [(1, "1 - No"), (2, "2 - Yes"), (3, "3 - Don't know")]

    fields = [('Participant ID', 'participant_id', 'INTEGER', ''),
              ('Relation to child', 'q01', 'SELECT', allowed + [(1, "1 - Mother"),
                                                                (2, "2 - Guardian"),
                                                                (3, "3 - Family Relation")]),
              ('Ethnicity', 'q02', 'SELECT', allowed + [(1, "1 - Black"),
                                                        (2, "2 - Indian/Asian"),
                                                        (3, "3 - White"),
                                                        (4, "4 - Coloured"),
                                                        (5, "5 - Other")]),
              ('Other Ethnicity', 'q02Other', 'STRING', ''),
              ('Your Age', 'q03', 'SELECT', allowed + [(1, "1 - 18-25"),
                                                       (2, "2 - 26-35"),
                                                       (3, "3 - 36-45"),
                                                       (4, "4 - 46-60"),
                                                       (5, "5 - Over 61")]),
              ('Child age years', 'q04years', 'INTEGER', ''),
              ('Child age months', 'q04months', 'INTEGER', ''),
              ('Child Sex', 'q05', 'SELECT', allowed + [(1, "1 - Male"),
                                                        (2, "2 - Female")]),
              ('Albinism', 'q06', 'SELECT', yes_no),
              ('HIV Status', 'q07', 'SELECT', allowed + [(1, "1 - Positive"),
                                                         (2, "2 - Negative")]),
              ('Child Skin', 'q08', 'SELECT', allowed + [(1, "1 - Very Fair"),
                                                         (2, "2 - White"),
                                                         (3, "3 - Light Brown"),
                                                         (4, "4 - Brown"),
                                                         (5, "5 - Dark Brown"),
                                                         (6, "6 - Very Dark Brown")]),
              ('Child gets sunburned', 'q09', 'SELECT', yes_no),
              ('Skin sensitivity', 'q10', 'SELECT', allowed + [(1, "1 - Very Sensitive"),
                                                               (2, "2 - Sensitive"),
                                                               (3, "3 - Moderately Sensitive"),
                                                               (4, "4 - Not at all")]),
              ('Child weight (kg)', 'q11weight', 'NUMERIC', 3),
              ('Child height (cm)', 'q11height', 'NUMERIC', 3),
              ('On medication', 'q12', 'SELECT', yes_no),
              ('Med 1 Name', 'q12med_1', 'STRING', ''),
              ('Med 1 Times', 'q12med_1_times', 'INTEGER', ''),
              ('Med 2 Name', 'q12med_2', 'STRING', ''),
              ('Med 2 Times', 'q12med_2_times', 'INTEGER', ''),
              ('Med 3 Name', 'q12med_3', 'STRING', ''),
              ('Med 3 Times', 'q12med_3_times', 'INTEGER', ''),
              ('Child activity level', 'q13', 'SELECT', allowed + [(1, "1 - Very Active"),
                                                                   (2, "2 - Moderately Active"),
                                                                   (3, "3 - Not very Active")]),
              ('Caregiver smokes', 'q14', 'SELECT', yes_no),
              ('Anyone in house smokes', 'q15', 'SELECT', yes_no),
              ('Breastfed at Vaccination', 'q16', 'SELECT', yes_no_dont_know),
              ('Still breastfed now', 'q17', 'SELECT', yes_no_dont_know),
              ('Mother had vaccinations', 'q18', 'SELECT', yes_no_dont_know),
              ('Mother had measles', 'q19', 'SELECT', yes_no_dont_know),
              ('Playing in sunshine', 'q20', 'SELECT', allowed + [(1, "1 - Healthy"),
                                                                  (2, "2 - Harmful"),
                                                                  (3, "3 - Don't know ")]),
              ('Travel to clinic', 'q21', 'SELECT', allowed + [(1, "1 - Bus"),
                                                               (2, "2 - Taxi"),
                                                               (3, "3 - Train"),
                                                               (4, "4 - Walk"),
                                                               (5, "5 - Private car"),
                                                               (6, "6 - Other")]),
              ('Other travel to clinic', 'q21other', 'STRING', ''),
              ('Time to travel to clinic', 'q22', 'SELECT', allowed + [(1, "1 - Less than 10 minutes"),
                                                                       (2, "2 - Between 10 and 30 minutes"),
                                                                       (3, "3 - Between 30 and 60 minutes"),
                                                                       (4, "4 - Over 60 minutes ")]),
              ('Long queue', 'q23', 'SELECT', yes_no_dont_know),
              ('Where do you wait at clinic', 'q24', 'SELECT', allowed + [(1, "1 - Shaded area"),
                                                                          (2, "2 - Unshaded area"),
                                                                          (3, "3 - Inside ")]),
              ('How long do you wait at clinic', 'q25', 'SELECT', allowed + [(1, "1 - Less than 15 minutes"),
                                                                             (2, "2 - Between 15 and 30 minutes"),
                                                                             (3, "3 - Between 30 and 60 minutes"),
                                                                             (4, "4 - Over 60 minutes ")]),
              ('Child sun protection outside clinic', 'q26', 'SELECT', yes_no + [(3, "3 - Wait inside")]),
              ('Child sun protection outside frequency', 'q27', 'SELECT', allowed + [(1, "1 - Usually"),
                                                                                     (2, "2 - Sometimes"),
                                                                                     (3, "3 - Seldom"),
                                                                                     (4, "4 - Never"),
                                                                                     (5, "5 - Wait inside")]),
              ('Hat or cap', 'q28_a', 'SELECT', yes_no),
              ('Sunscreen', 'q28_b', 'SELECT', yes_no),
              ('Long sleeve shirt', 'q28_c', 'SELECT', yes_no),
              ('Trousers', 'q28_d', 'SELECT', yes_no),
              ('Umbrella', 'q28_e', 'SELECT', yes_no),
              ('Face', 'q29_a', 'SELECT', yes_no),
              ('Arms', 'q29_b', 'SELECT', yes_no),
              ('Legs', 'q29_c', 'SELECT', yes_no),
              ('Hands', 'q29_d', 'SELECT', yes_no),
              ('Back and shoulders', 'q29_e', 'SELECT', yes_no),
              ('No sunscreen', 'q29_f', 'SELECT', yes_no),
              ('Spends time on weekdays', 'q30', 'SELECT', allowed + [(1, "1 - Mostly Inside"),
                                                                      (2, "2 - Mostly Outside")]),
              ('Spends time on weekends', 'q31', 'SELECT', allowed + [(1, "1 - Mostly Inside"),
                                                                      (2, "2 - Mostly Outside")]),
              ('Location spent outside', 'q32',  'SELECT', allowed + [(1, "1 - Shade"),
                                                                      (2, "2 - Open/sun")]),
              ('Hours spent outside', 'q33',  'SELECT', allowed + [(1, "1 - Less than 1 hour"),
                                                                   (2, "2 - 1 hour"),
                                                                   (3, "3 - 2 hours"),
                                                                   (4, "4 - 3 hours"),
                                                                   (5, "5 - More than 3 hours")]),
              ('Hat or cap', 'q34_a', 'SELECT', yes_no),
              ('Sunscreen', 'q34_b', 'SELECT', yes_no),
              ('Long sleeve shirt', 'q34_c', 'SELECT', yes_no),
              ('Trousers', 'q34_d', 'SELECT', yes_no),
              ('Umbrella', 'q34_e', 'SELECT', yes_no),
              ('Face', 'q35_a', 'SELECT', yes_no),
              ('Arms', 'q35_b', 'SELECT', yes_no),
              ('Legs', 'q35_c', 'SELECT', yes_no),
              ('Hands', 'q35_d', 'SELECT', yes_no),
              ('Back and shoulders', 'q35_e', 'SELECT', yes_no),
              ('No sunscreen', 'q35_f', 'SELECT', yes_no),
              ('Sunburn or blisters', 'q36', 'SELECT', yes_no)]

    return generate_page(fields, "questionnaire", "questionnaire", "Questionnaire")


def generate_page(fields, page_name, add_method, title):
    field_names = []
    flag_fields = []
    data_fields = []
    params = []

    for field in fields:
        if field[const.VARIABLE_TYPE] == 'INTEGER':
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
                DateField(field[const.DISPLAY_NAME], format=field[const.ALLOWED_VALUES]))
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

    # if request.method == 'POST':
    #     print "in POST"
    #     if rth_form.validate():

    if not rth_form.validate_on_submit():
        print "did not validate"

        print rth_form.errors

        # for field_name in field_names:
        #     if rth_form[field_name].errors:
        #         for error in rth_form[field_name].errors:
        #             print error
        return render_template('_render_template.html', title=title, add_method=add_method,
                               fields=field_names, form=rth_form)

    print "validated "
    ins = ','.join(data_fields)
    into = ','.join(params)

    values = [request.form[field_name] for field_name in data_fields]

    db = get_db()
    db.execute("insert into " + add_method + " (" + ins + ") values (" + into + ")",
               values)

    for flag_field in flag_fields:
        if not request.form[flag_field] == '':
            db.execute("insert into flagged_records (participant_id, variable_name, table_name, flag_text) values (" +
                       "?, ?, ?, ? )",
                       [request.form["participant_id"], flag_field[5:], add_method, request.form[flag_field]])

    db.commit()

    return redirect(url_for(page_name))


if __name__ == '__main__':
    app.run(host='127.0.0.1')
