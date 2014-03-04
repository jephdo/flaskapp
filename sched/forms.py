from wtforms import Form, BooleanField, DateTimeField, TextAreaField, TextField, PasswordField
from wtforms.validators import Length, required


class AppointmentForm(Form):
    title = TextField('Title', [Length(max=255)])
    start = DateTimeField('Start', [required()])
    end = DateTimeField('End')
    allday = BooleanField('All Day')
    location = TextField('Location', [Length(max=255)])
    description = TextAreaField('Description')

class LoginForm(Form):
    """Render HTML input for user login form.

    Authentication (i.e. password verification) happens in the view function.
    """
    username = TextField('Username', [required()])
    password = PasswordField('Password', [required()])


if __name__ == '__main__':
    from werkzeug.datastructures import ImmutableMultiDict as multidict

    data = multidict([('title', 'Hello, form!')])
    form = AppointmentForm()
    print('Here is validation...')
    print('Does it validate: {}'.format(form.validate()))
    print('There is an error attached to the field')
    print('form.start.errors: {}'.format(form.start.errors))
    print(form.title.label)
    print(form.title)

