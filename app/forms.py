from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, IntegerField, PasswordField, DecimalField, \
                    DecimalRangeField, SelectField, RadioField, IntegerRangeField
from wtforms.validators import DataRequired, EqualTo, Email, NumberRange, InputRequired


# Accounts and Authentication
class Register_Form(FlaskForm):
    username_field = StringField("Username",validators=[DataRequired()])
    password_field = PasswordField('Password', validators=[DataRequired()])
    password2_field = PasswordField('Re-enter Password',
                                    validators=[DataRequired(), EqualTo('password_field',message='Passwords must match')])
    submit_field = SubmitField("Register!")

class Login_Form(FlaskForm):
    username_field = StringField("Username",validators=[DataRequired()],default='admin')
    password_field = PasswordField("Password",validators=[DataRequired()])
    submit_field = SubmitField("Log in")


# Calibration
class Display_Opts_Form(FlaskForm):
    autoscale_field = BooleanField("Autoscale", default=True)
    show_prev_field = BooleanField('Show previous', default=False)

class Calibration_Form(FlaskForm):
    # Hardware parameters
    f0_field = DecimalField("Frequency (MHz)", validators=[InputRequired(), NumberRange(min=0,max=50)],default=15)
    shimx_field = DecimalRangeField("Shim x", validators=[InputRequired(),NumberRange(min=-1.0,max=1.0)],default=0.0)
    shimy_field = DecimalRangeField("Shim y", validators=[InputRequired(),NumberRange(min=-1.0,max=1.0)],default=0.0)
    shimz_field = DecimalRangeField("Shim z", validators=[InputRequired(),NumberRange(min=-1.0,max=1.0)],default=0.0)
    tx_amp_field = DecimalField('Tx amplitude', validators=[InputRequired()],default=0.5)
    rx_gain_field = DecimalField('Rx gain (db)', validators=[InputRequired()],default=3)
    # FID sequence parameters
    tr_field = DecimalField('Repetition Time (ms)', validators=[DataRequired(), NumberRange(min=5,max=5000)],default=1000)
    readout_time_field = DecimalField('Readout duration (ms)',validators=[DataRequired(),NumberRange(min=10,max=100)],default=30)
    num_rep_field = IntegerField('Number of repetitions',validators=[DataRequired(),NumberRange(min=1,max=50)],default=1)
    num_avg_field = IntegerField('Number of averages', validators=[DataRequired(),NumberRange(min=1,max=100)],default=1)
    # Submit
    submit_field = SubmitField("SAVE")

class Game1Form(FlaskForm):
    #Min and Max units are in cm
    zero_fill = IntegerField(label='cubes', validators=[DataRequired(), NumberRange(min=4, max=5000)], default=128)
    FOV_scale = DecimalField(label='mm', validators=[DataRequired(), NumberRange(min=100, max=5000)],default=128)
    Matrix_scale = IntegerField(label='cubes per side', validators=[DataRequired(), NumberRange(min=4,max=1000)], default=128)
    Voxel_scale = DecimalField(label='mm', validators=[DataRequired(), NumberRange(min=.0001, max=1250)], default=1)
    submit_field = SubmitField("Run")
    submit_field_q = SubmitField("Submit Answer")
    min_scale = DecimalRangeField(label='range', validators=[DataRequired(), NumberRange(min=0.0, max=1.0),],default=0.1)
    max_scale = DecimalRangeField(label='range', validators=[DataRequired(), NumberRange(min=0.0, max=1.0)],default=0.9)
    P1_q = RadioField('question1', choices=['High Matrix Size and Low Voxel Size', 'Low Matrix Size and High Voxel Size', 'High Matrix Size and High Voxel Size', 'Low Matrix Size and Low Voxel Size'])
    P2_q = RadioField('question2', choices=['The matrix size increases', 'The matrix size decreases', 'The matrix size stays the same'])
    G_P3_q = RadioField('general questions', choices=['1', '2','3','4'])
    from_slider_value = DecimalRangeField(label='range', validators=[DataRequired(), NumberRange(min=0.0, max=100),],default=10)
    to_slider_value = DecimalRangeField(label='range', validators=[DataRequired(), NumberRange(min=0.0, max=100),],default=40)
    min_value = IntegerField(label='m', validators=[DataRequired(), NumberRange(min=0, max=100)],default=10)
    max_value = IntegerField(label='m', validators=[DataRequired(), NumberRange(min=0, max=100)],default=90)
class Game3Form(FlaskForm):
    options = RadioField('options', choices=['T1', 'T2', 'PD'],validators=[InputRequired()],default='T1')
    TR = DecimalRangeField(label='TR Value(mm):', validators= [DataRequired(), NumberRange(min=500, max=5000)],default=2750)
    TE = DecimalRangeField(label='TE Value(mm):', validators= [DataRequired(), NumberRange(min=10, max=450)],default=235)
    FA = DecimalRangeField(label='FA Value(angle):', validators= [DataRequired(), NumberRange(min=0.0, max=360)],default=90)
    submit = SubmitField("Submit")
    P1_q = RadioField('question1', choices=['T1', 'T2', 'PD'], validators=[InputRequired()])
    P2_q = RadioField('question2', choices=['Contrast Increases', 'Contrast Decreases'], validators=[InputRequired()])
# EXAMPLE
class Game4Form(FlaskForm):
    thk_field = DecimalField('Slice thickness (mm)',places=1,validators=[DataRequired(),NumberRange(min=1.0,max=10.0)])
    flip_field = IntegerField('Flip angle (degrees)',validators=[DataRequired(),NumberRange(min=1,max=90)])
    tr_field = IntegerField('Repetition Time (ms)',validators=[DataRequired(),NumberRange(min=20,max=2000)])
    submit_field = SubmitField("Run")

# Game 5: Proton's got moves
class Game5Form(FlaskForm):
    b0_onoff_field = BooleanField("B0",default=False)
    b0_field = DecimalRangeField("B0 field strength (Gauss)", validators=[InputRequired(),
                                                                     NumberRange(min=0.0,max=100.0)],default=60.0)
    rot_frame_onoff_field = BooleanField("Rotating Frame", default=False)

    # RF
    tx_onoff_field = BooleanField("Coil",default=False)

    flip_angle_field = DecimalRangeField("Flip Angle", validators=[InputRequired(), NumberRange(min=0,max=360)],default=90)
    rf_phase_field = DecimalRangeField("Pulse dir.", validators=[InputRequired(),
                                                                                NumberRange(min=0.0,max=360)],default=0.0)
    # Receive
    rx_onoff_field = BooleanField("Coil",default=False)

    rx_dir_field = RadioField("Coil Direction", choices=['x','y'],validators=[InputRequired()],default='x')

    # Magnetization status
    m_theta_field = DecimalField("Theta (deg)",validators=[InputRequired(),NumberRange(min=0.0,max=180.0)],default=0.0)
    m_phi_field = DecimalField("Phi (deg)",validators=[InputRequired(),NumberRange(min=0.0,max=360.0)],default=0.0)
    m_size_field = DecimalField('|M/M0|', validators=[InputRequired(),NumberRange(min=0.0,max=1.0)],default=1.0)
    # No use for submit field
    submit_field = SubmitField("Tip!")

class Game7Form(FlaskForm):
    # For selectfields, choices are (value, label) pairs
    phantom_type_field = SelectField('Select model', choices=[
                                                                ('letterN', 'Letter N'),
                                                                ('letterY', 'Letter Y'),
                                                                ('letterC', 'Letter C'),
                                                               ],default='letterN')
    proj_2d_axis_field = RadioField("2D proj. axis", choices=['x','y','z'],default='z')
    proj_1d_angle_field = DecimalField("1D proj. angle (degrees)",validators=[NumberRange(min=0,max=360)],default=90)

    submit_field = SubmitField("Project!")


# More user interaction through questions
#class MultipleChoiceForm(FlaskForm):
    # Radio field
    # How to define labels?


