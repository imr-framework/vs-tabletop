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
    FOV_scale = DecimalField(label='cm', validators=[DataRequired(), NumberRange(min=.1, max=1)],default=0.5)
    Matrix_scale = IntegerField(label='cubes', validators=[DataRequired(), NumberRange(min=16,max=125)], default=16)
    Voxel_scale = DecimalField(label='cm cubed', validators=[DataRequired(), NumberRange(min=.00001, max=1)], default=.01)
    submit_field = SubmitField("Run")
    min_scale = DecimalRangeField(label='', validators=[DataRequired(), NumberRange(min=0.01, max=1)],default=0)
    max_scale = DecimalRangeField(label='', validators=[DataRequired(), NumberRange(min=0.01, max=1)],default=1)

# EXAMPLE
class Game4Form(FlaskForm):
    thk_field = DecimalField('Slice thickness (mm)',places=1,validators=[DataRequired(),NumberRange(min=1.0,max=10.0)])
    flip_field = IntegerField('Flip angle (degrees)',validators=[DataRequired(),NumberRange(min=1,max=90)])
    tr_field = IntegerField('Repetition Time (ms)',validators=[DataRequired(),NumberRange(min=20,max=2000)])
    submit_field = SubmitField("Run")

# Game 5: Proton's got moves
class Game5Form(FlaskForm):
    b0_onoff_field = BooleanField("B0",default=False)
    # TODO add the following two into template
    b0_field = DecimalRangeField("B0 field strength (Tesla)", validators=[DataRequired(),
                                                                     NumberRange(min=0.001,max=0.01)],default=0.001)
    rot_frame_onoff_field = BooleanField("Rotating Frame", default=False)

    # RF
    flip_angle_field = DecimalRangeField("Flip Angle (degrees)", validators=[DataRequired(), NumberRange(min=0,max=360)],default=90)
    rf_phase_field = DecimalRangeField("Pulse direction (degrees)", validators=[DataRequired(), NumberRange(min=0,max=360)],default=0)
    # Receive
    rx_onoff_field = BooleanField("Coil",default=False)

    rx_dir_field = RadioField("Coil Direction", choices=['x','y'],validators=[DataRequired()],default='x')

    # Magnetization status
    m_theta_field = DecimalField("Theta (deg)",validators=[DataRequired(),NumberRange(min=0,max=180)],default=0)
    m_phi_field = DecimalField("Phi (deg)",validators=[DataRequired(),NumberRange(min=0,max=360)],default=0)
    m_size_field = DecimalField('|M/M0|', validators=[DataRequired(),NumberRange(min=0,max=1)],default=1)
    # No use for submit field
    submit_field = SubmitField("Tip!")

    # Whether rot frame is on or off

    # TODO include sequence parameters.
    # RF duration
    #

