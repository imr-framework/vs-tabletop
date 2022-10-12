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
    username_field = StringField("Username",validators=[DataRequired()])
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
    zero_fill = IntegerField(label='voxels per side', validators=[DataRequired(), NumberRange(min=4, max=5000)], default=128)
    FOV_scale = DecimalField(label='mm', validators=[DataRequired(), NumberRange(min=100, max=5000)],default=128)
    Matrix_scale = IntegerField(label='voxels per side', validators=[DataRequired(), NumberRange(min=4,max=1000)], default=128)
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
    min_value = IntegerField(label='min', validators=[DataRequired(), NumberRange(min=0, max=100)],default=10)
    max_value = IntegerField(label='max', validators=[DataRequired(), NumberRange(min=0, max=100)],default=90)

class Game2Form(FlaskForm):
    # Image and options
    image_name_field = SelectField('Select image', choices=[
        ('flat','Unity'), ('delta','Spike'), ('shepp-logan','Phantom'),
        ('mri-x', 'MRI (sagittal)'), ('mri-y','MRI (coronal)'), ('mri-z','MRI (axial)'),
        ('cat','Cat'), ('sin','Sine wave'), ('cos','Cosine wave'), ('circ','Circular wave'),
        ('line-x','Horizontal line'), ('line-y','Vertical line')
    ], default='flat')
    image_rotation_field = DecimalRangeField(label='Rotation (deg)', validators=[NumberRange(0,360)],default=0)
    image_phase_field = DecimalRangeField(label='Wave phase (deg)',validators=[NumberRange(0,360)],default=0)
    image_wavelength_field = DecimalRangeField(label='Wavelength',validators=[NumberRange(0.05,2)],default=1)

    kspace_name_field = SelectField('Select k-space', choices=[
        ('flat','Unity'), ('delta','Spike'),('delta2','Double spike')
    ], default='delta')
    kspace_rotation_field = DecimalRangeField(label='Rotation (deg)', validators=[NumberRange(0,360)],default=0)
    kspace_ds_separation_field = DecimalRangeField(label='Spike separation',validators=[NumberRange(0,1)],default=0.25)


    signal_name_field = SelectField('Select signal', choices=[
        ('flat','Unity'), ('delta','Spike'), ('sin','Sine wave'),('cos','Cosine wave')
    ],default='flat')
    signal_scale_field = DecimalRangeField('Vertical scale',validators=[NumberRange(-10,10)],default=1)
    signal_stretch_field = DecimalRangeField('Horizontal scale',validators=[NumberRange(0,10)],default=1)

    signal_shift_field = DecimalRangeField('Shift (%)',validators=[NumberRange(0,100)],default=0)
    signal_phase_mod_field = DecimalRangeField('Phase modulation (per point)',validators=[NumberRange(0,360)],default=0)


    spectrum_name_field = SelectField('Select spectrum', choices=[
        ('flat','Unity'), ('delta','Spike')
    ], default='delta')
    spectrum_scale_field = DecimalRangeField('Vertical scale', validators=[NumberRange(-10, 10)], default=1)
    spectrum_stretch_field = DecimalRangeField('Horizontal scale',validators=[NumberRange(0,10)],default=1)
    spectrum_shift_field = DecimalRangeField('Shift (%)', validators=[NumberRange(0, 100)], default=0)
    spectrum_phase_mod_field = DecimalRangeField('Phase modulation (per point)', validators=[NumberRange(0, 360)],
                                               default=0)


    undersample_x_field = IntegerField('Horizontal',validators=[NumberRange(1,32)],default=1)
    undersample_y_field = IntegerField('Vertical',validators=[NumberRange(1,32)],default=1)


    submit_field = SubmitField(label='Run')

class Game3Form(FlaskForm):
    options = RadioField('options', choices=['T1w', 'T2w', 'PDw'],validators=[],default='T1')
    TR = DecimalRangeField(label='TR (ms)', validators= [DataRequired(), NumberRange(min=500, max=5000)],default=2750)
    TE = DecimalRangeField(label='TE (ms)', validators= [DataRequired(), NumberRange(min=10, max=450)],default=235)
    FA = DecimalRangeField(label='FA (deg)', validators= [DataRequired(), NumberRange(min=0.0, max=360)],default=90)
    submit = SubmitField("Submit chosen parameters")
    submit_questions = SubmitField("Submit Answer")
    P1_q = RadioField('question1', choices=['T1w', 'T2w', 'PDw'], validators=[InputRequired()])
    P2_q = RadioField('question2', choices=['Contrast Decreases', 'Contrast Increases'], validators=[InputRequired()])
    P3_q = RadioField('question3', choices=['CSF', 'GM', 'WM'])
# EXAMPLE
class Game4Form(FlaskForm):
    # Flow
    flow_onoff_field = BooleanField('Flow status',default=False)
    flow_speed_field = DecimalField('Flow speed %',validators=[NumberRange(min=0,max=100)], default=50)

    # Liquid properties
    t1_field = DecimalField('T1 (ms)', places=0, validators=[NumberRange(min=500,max=4000)],default=2000)
    t2_field = DecimalField('T2 (ms)', places=1, validators=[NumberRange(min=5,max=200)],default=200)

    # Concept simulation fields - bright blood
    bright_thk_field = DecimalField('Slice thickness (mm)', places=1, validators=[NumberRange(min=0.0,max=10.0)],default=5)
    bright_tr_field = DecimalField('Repetition Time (ms)', places=0, validators=[NumberRange(min=20,max=2000)],default=250)
    bright_fa_field = IntegerRangeField('Flip angle (deg)', validators=[NumberRange(min=0,max=90)],default=45)
    bright_te_field = DecimalField('Echo time (ms)',places=0,validators=[NumberRange(min=5,max=15)],default=5)

    # Concept simulation fields - dark blood
    dark_thk_field = DecimalField('Slice thickness (mm)', places=1, validators=[NumberRange(min=0.0,max=10.0)],default=5)
    dark_te_field = DecimalField('Echo time (ms)', places=0, validators=[NumberRange(min=5,max=100)],default=50)


    # Image simulation fields
    # Dark or bright? choice
    sequence_type_field = SelectField('Contrast type',choices=[('dark','Dark blood'),('bright','Bright blood')],default='bright')
    thk_field = DecimalField('Slice thickness (mm)',validators=[DataRequired(),NumberRange(min=1.0,max=10.0)],default=5)
    fa_field = IntegerRangeField('Flip angle (degrees)',validators=[DataRequired(),NumberRange(min=0,max=90)],default=30)
    tr_field = IntegerField('Repetition Time (ms)',validators=[DataRequired(),NumberRange(min=20,max=2000)],default=250)
    te_field = IntegerField('Echo Time (ms)',validators=[DataRequired(),NumberRange(min=5,max=100)],default=5)

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
    m_size_field = DecimalField('|M|/M0', validators=[InputRequired(),NumberRange(min=0.0,max=1.0)],default=1.0)
    # No use for submit field
    submit_field = SubmitField("Tip!")

class Game6Form(FlaskForm):
    mapping_type_field = SelectField('Map type',choices=[('T1','T1'),('T2','T2')],default='T2')



class Game7Form(FlaskForm):
    # For selectfields, choices are (value, label) pairs
    phantom_type_field = SelectField('Select model', choices=[
                                                                ('letterN', 'Letter N'),
                                                                ('letterY', 'Letter Y'),
                                                                ('letterC', 'Letter C'),
                                                                ('center_ball', 'Ball'),
                                                                ('double_cone','Double cone'),
                                                                ('double_cone_rev', 'Double cone 2'),
                                                                ('simple_cube','Cube'),
                                                                ('two_holes', 'Dots')
                                                               ],default='letterN')
    proj_2d_axis_field = RadioField("2D proj. axis", choices=['x','y','z'],default='z')
    proj_1d_angle_field = DecimalField("1D proj. angle",validators=[NumberRange(min=0,max=360)],default=90)

    submit_field = SubmitField("Project all")

class Game8Form(FlaskForm):
    proj_2d_axis_field = RadioField("2D proj. axis", choices=['x','y','z'],default='z')
    proj_1d_angle_field = DecimalField("1D proj. angle",validators=[NumberRange(min=0,max=360)],default=90)


    submit_field = SubmitField("Check answer")


# More user interaction through questions
#class MultipleChoiceForm(FlaskForm):
    # Radio field
    # How to define labels?


