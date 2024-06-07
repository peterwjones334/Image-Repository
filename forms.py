from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, SelectField
from wtforms.validators import DataRequired, ValidationError

def validate_image(form, field):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'tiff'}
    if '.' not in field.data.filename or field.data.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        raise ValidationError('Invalid file extension. Allowed extensions are png, jpg, jpeg, gif, tiff.')

class UploadForm(FlaskForm):
    image = FileField('Image', validators=[DataRequired(), validate_image])
    part_number = StringField('Part Number', validators=[DataRequired()])
    version = StringField('Version', validators=[DataRequired()])
    owner = SelectField('Owner', choices=[('Consumer', '0'), ('Provider', '1'), ('Other', '2')], validators=[DataRequired()])
    category = SelectField('Category', choices=[('Generic', '0'), ('Specific', '1'), ('Specialized', '2')], validators=[DataRequired()])
    marking = SelectField('Marking', choices=[('Not Marked', '0'), ('Proprietary', '1'), ('Confidential', '2'), ('Secret', '3')], validators=[DataRequired()])
    submit = SubmitField('Upload')
