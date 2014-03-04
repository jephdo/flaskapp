from flask import Flask, url_for, abort, jsonify, redirect, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, current_user, login_user, logout_user, login_required

from . import filters
from .forms import AppointmentForm, LoginForm
from .models import Base, Appointment, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sched.db'
app.config['SECRET_KEY'] = 'HUNTER2'

db = SQLAlchemy(app)
db.Model = Base

# Load custom Jinja filters from the `filters` module.
filters.init_app(app)

login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('appointment_list'))

    form = LoginForm(request.form)
    error = None

    if request.method == 'POST' and form.validate():
        email = form.username.data.lower().strip()
        password = form.password.data.lower().strip()
        user, authenticated = User.authenticate(db.session.query, email, password)
        if authenticated:
            login_user(user)
            return redirect(url_for('appointment_list'))
        else:
            error = 'Incorrent username or password'
    return render_template('user/login.html', form=form, error=error)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.errorhandler(404)
def error_not_found(error):
    return render_template('error/not_found.html'), 404

@app.route('/')
def hello():
    return 'Hello, world!'

@app.route('/appointments/')
@login_required
def appointment_list():
    """List all available appointments."""

    appts = db.session.query(Appointment) \
                      .order_by(Appointment.start.asc()) \
                      .all()

    return render_template('appointment/index.html', appts=appts)

@app.route('/appointments/<int:appointment_id>/')
@login_required
def appointment_detail(appointment_id):
    """Provide HTML page with a given appointment."""

    appt = db.session.query(Appointment).get(appointment_id)

    if appt is None:
      abort(404)
    return render_template('appointment/detail.html', appt=appt)

@app.route('/appointments/<int:appointment_id>/edit/',
           methods=['GET', 'POST'])
@login_required
def appointment_edit(appointment_id):
    """Provide HTML form to edit a given appointment."""

    appt = db.session.query(Appointment).get(appointment_id)

    if appt is None:
      abort(404)

    form = AppointmentForm(request.form, appt)

    if request.method == 'POST' and form.validate():
        form.populate_obj(appt)
        db.session.commit()
        return redirect(url_for('appointment_detail', appointment_id=appt.id))
    return render_template('appointment/edit.html', form=form)

@app.route('/appointments/create/', methods=['GET', 'POST'])
@login_required
def appointment_create():
    """Provide HTML form to create a new appointment."""

    form = AppointmentForm(request.form)
    if request.method == 'POST' and form.validate():
        appt = Appointment()
        form.populate_obj(appt)

        db.session.add(appt)
        db.session.commit()

        # on success send user back to full appointment list
        return redirect(url_for('appointment_list'))

    # either f irst load or validation error at this point
    return render_template('appointment/edit.html', form=form)

@app.route('/appointments/<int:appointment_id>/delete/',
           methods=['DELETE'])
@login_required
def appointment_delete(appointment_id):
    appt = db.session.query(Appointment).get(appointment_id)
    if appt is None:
      response = jsonify({'status': 'Not Found'})
      response.status = 404
      return response

    db.session.delete(appt)
    db.session.commit()
    return jsonify({'status': 'OK'})

if __name__ == '__main__':
    app.run(debug=True)
