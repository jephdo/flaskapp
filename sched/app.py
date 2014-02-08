from flask import Flask, url_for
from flask.ext.sqlalchemy import SQLAlchemy

from .models import Base

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sched.db'

db = SQLAlchemy(app)
db.Model = Base

@app.route('/')
def hello():
    return 'Hello, world!'

@app.route('/appointments/')
def appointment_list():
    return 'Listing of all apoiintments we have.'

@app.route('/appointments/<int:appointment_id>/')
def appointment_detail(appointment_id):
    edit_url = url_for('appointment_edit', appointment_id=appointment_id)

    return edit_url
    # return 'Detail of apointment #{}.'.format(appointment_id)

@app.route('/appointments/<int:appointment_id>/edit/',
           methods=['GET', 'POST'])
def appointment_edit(appointment_id):
    return 'Form to edit appointment #{}'.format(appointment_id)

@app.route('/appointments/create/',
           methods=['GET', 'POST'])
def appointment_create():
    return 'Form to create a new appointment'

@app.route('/appointments/<int:appointment_id>/delete/',
           methods=['DELETE'])
def appointment_delete(appointment_id):
    raise NotImplementedError('DELETE')


if __name__ == '__main__':
    app.run(debug=True)
