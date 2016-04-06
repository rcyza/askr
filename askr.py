# -*- coding: utf-8 -*-

import os
from sqlite3 import dbapi2 as sqlite3
from flask_wtf import Form
from flask import Flask, request, g, redirect, url_for, render_template, flash
from wtforms import StringField, IntegerField, DateField, TextAreaField
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


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
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

    fields = [('Participant ID', 'participant_id', 'INTEGER', ''),
              ('Date of birth', 'dob', 'DATE', '%d/%m/%Y'),
              ('Birth weight (g)', 'bweight', 'INTEGER', ''),
              ('Birth length (cm)', 'blength', 'INTEGER', ''),
              ('Birth head circumference (cm)', 'bheadc', 'INTEGER', ''),
              ('Problems during pregnancy/ birth/ neonatally', 'problems', 'TEXT', ''),
              ('APGAR 1 Minute', 'apgar1', 'INTEGER', allowed + range(0, 11)),
              ('APGAR 5 Minutes', 'apgar5', 'INTEGER', allowed + range(0, 11)),
              ('Gestational age', 'gest_age', 'INTEGER', ''),
              ('Received other immunisations prior', 'other_imm', 'INTEGER', allowed + [0, 1]),
              ('Received measles 1', 'measles1', 'INTEGER', allowed + [0, 1]),
              ('Date Measles 1 Received', 'm1_date', 'DATE', '%d/%m/%Y'),
              ('Batch number of measles 1', 'm1_batch_no', 'STRING', ''),
              ('Weight at Measles 1 (cm)', 'm1_weight', 'INTEGER', ''),
              ('Height at Measles 1 (cm)', 'm1_height', 'INTEGER', '')]

    field_names = []

    for field in fields:
        if field[2] == 'INTEGER':
            BaseForm.append_field(field[1], IntegerField(field[0], [LegalValues(field[3])]))
        elif field[2] == 'DATE':
            BaseForm.append_field(field[1], DateField(field[0], format=field[3]))
        elif field[2] == 'TEXT':
            BaseForm.append_field(field[1], TextAreaField(field[0]))
        elif field[2] == 'STRING':
            BaseForm.append_field(field[1], StringField(field[0]))

        field_names.append(field[1])

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
        return render_template('_render_template.html', title='Road to Health', add_method='road_to_health',
                               fields=field_names, form=rth_form)

    print "validated "
    ins = ','.join(field_names)

    values = [request.form[field_name] for field_name in field_names]

    print values

    db = get_db()
    db.execute("insert into road_to_health (" + ins + ") values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
               values)
    db.commit()

    for field_name in field_names:
        print request.form[field_name]

    return redirect(url_for('road_to_health'))

if __name__ == '__main__':
    app.run(host='127.0.0.1')
