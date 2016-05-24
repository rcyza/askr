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
        (0, "0 - Yes"), (1, "1 - No"), (777, "777 - Not Entered "), (888, "888 - Not Applicable "),
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
    allowed = [777, 888, 999]

    fields = [('Participant ID', 'participant_id', 'INTEGER', ''),
              ('q01', '', 'INTEGER', allowed + range(0, 3 + 1)),
              ('q02', '', 'INTEGER', allowed + range(0, 5 + 1)),
              ('q02Other', '', 'STRING', ''),
              ('q03', '', 'INTEGER', allowed + range(0, 5 + 1)),
              ('q04years', '', 'INTEGER', ''),
              ('q04months', '', 'INTEGER', ''),
              ('q05', '', 'INTEGER', allowed + range(0, 2 + 1)),
              ('q06', '', 'INTEGER', allowed + range(0, 2 + 1)),
              ('q07', '', 'INTEGER', allowed + range(0, 2 + 1)),
              ('q08', '', 'INTEGER', allowed + range(0, 6 + 1)),
              ('q09', '', 'INTEGER', allowed + range(0, 2 + 1)),
              ('q10', '', 'INTEGER', allowed + range(0, 4 + 1)),
              ('q11weight', '', 'NUMERIC', 3),
              ('q11height', '', 'INTEGER', ''),
              ('q12', '', 'INTEGER', allowed + range(0, 2 + 1)),
              ('q12med_1', '', 'STRING', ''),
              ('q12med_1_times', '', 'INTEGER', allowed + range(0, 2 + 1)),
              ('q12med_2', '', 'STRING', ''),
              ('q12med_2_times', '', 'INTEGER', allowed + range(0, 2 + 1)),
              ('q12med_3', '', 'STRING', ''),
              ('q12med_3_times', '', 'INTEGER', allowed + range(0, 2 + 1)),
              ('q13', '', 'INTEGER', allowed + range(0, 3 + 1)),
              ('q14', '', 'INTEGER', allowed + range(0, 2 + 1)),
              ('q15', '', 'INTEGER', allowed + range(0, 2 + 1)),
              ('q16', '', 'INTEGER', allowed + range(0, 3 + 1)),
              ('q17', '', 'INTEGER', allowed + range(0, 3 + 1)),
              ('q18', '', 'INTEGER', allowed + range(0, 3 + 1)),
              ('q19', '', 'INTEGER', allowed + range(0, 3 + 1)),
              ('q20', '', 'INTEGER', allowed + range(0, 3 + 1)),
              ('q21', '', 'INTEGER', allowed + range(0, 6 + 1)),
              ('q21other', '', 'STRING', ''),
              ('q22', '', 'INTEGER', allowed + range(0, 4 + 1)),
              ('q23', '', 'INTEGER', allowed + range(0, 3 + 1)),
              ('q24', '', 'INTEGER', allowed + range(0, 3 + 1)),
              ('q25', '', 'INTEGER', allowed + range(0, 3 + 1)),
              ('q26', '', 'INTEGER', allowed + range(0, 3 + 1)),
              ('q27', '', 'INTEGER', allowed + range(0, 5 + 1)),
              ('q28_a', '', 'INTEGER', allowed + [0, 1]),
              ('q28_b', '', 'INTEGER', allowed + [0, 1]),
              ('q28_c', '', 'INTEGER', allowed + [0, 1]),
              ('q28_d', '', 'INTEGER', allowed + [0, 1]),
              ('q28_e', '', 'INTEGER', allowed + [0, 1]),
              ('q29_a', '', 'INTEGER', allowed + [0, 1]),
              ('q29_b', '', 'INTEGER', allowed + [0, 1]),
              ('q29_c', '', 'INTEGER', allowed + [0, 1]),
              ('q29_d', '', 'INTEGER', allowed + [0, 1]),
              ('q29_e', '', 'INTEGER', allowed + [0, 1]),
              ('q29_f', '', 'INTEGER', allowed + [0, 1]),
              ('q30', '', 'INTEGER', allowed + range(0, 3 + 1)),
              ('q31', '', 'INTEGER', allowed + range(0, 6 + 1)),
              ('q32', '', 'INTEGER', allowed + range(0, 4 + 1)),
              ('q33', '', 'INTEGER', allowed + range(0, 3 + 1)),
              ('q34_a', '', 'INTEGER', allowed + [0, 1]),
              ('q34_b', '', 'INTEGER', allowed + [0, 1]),
              ('q34_c', '', 'INTEGER', allowed + [0, 1]),
              ('q34_d', '', 'INTEGER', allowed + [0, 1]),
              ('q34_e', '', 'INTEGER', allowed + [0, 1]),
              ('q35_a', '', 'INTEGER', allowed + [0, 1]),
              ('q35_b', '', 'INTEGER', allowed + [0, 1]),
              ('q35_c', '', 'INTEGER', allowed + [0, 1]),
              ('q35_d', '', 'INTEGER', allowed + [0, 1]),
              ('q35_e', '', 'INTEGER', allowed + [0, 1]),
              ('q35_f', '', 'INTEGER', allowed + [0, 1]),
              ('q36', '', 'INTEGER', allowed + range(0, 2 + 1))]

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
