<h1 align="center">Virtual Scanner Tabletop Web Games</h3>
<p float="left">
<img title="PyPulseq Badge" src="https://img.shields.io/badge/made%20using-pypulseq-brightgreen" height="15"><img title="Virtual Scanner Badge" src="https://img.shields.io/badge/made%20using-virtual--scanner-blue" height="15">
</p>
<br>

This is the development branch for the games software as part of the [DELTA DIY project](https://github.com/delta-diy-mri/delta-diy-mri.github.io).
The goal is to use this in a master's level MRI course and obtain feedback.

Virtual Scanner Tabletop is an extension to [Virtual Scanner](https://github.com/imr-framework/virtual-scanner/) comprising of educational games about MRI that can be run by simulation or connected to a real educational MRI scanner. Target audience include high school, college, and post-grad students as well as members of the MR and scientific community at large.   


## Quickstart

### Method 1:
Play online  here on Heroku [vs-tabletop games](https://vs-tabletop-713f97371131.herokuapp.com/). You can register your name/password but lasts only a session. Free things sometimes have these challenges :)

### Method 2: `pip install`
1. On the command line, make a new virtual environment using the command: `python -m venv myenv` For more info on creating virtual environments,
see [here](https://docs.python.org/3/library/venv.html]). Activate the virtual environment using the command `source venv/bin/activate` on the terminal from the folder where you installed the virtual environment
2. Install the games using the command: 'pip install vs-tabletop-lite'
3. cd into the main folder called "vstabletop" (`venv\Lib\site-packages\vstabletop`) and run `app.py`. Click into the link in the program output (examplee: http://127.0.0.1:5000/). Log in as `admin` using password `123456`.
   
#### Troubleshooting 
(version 1.0.0b5) - You might encounter problems with installing Kiwisolver which requires Visual C++. If you have trouble getting the Visual C++, you can ignore the kiwisolver and perform the following steps:
1. Install vs-tabletop without dependencies: `pip install vs-tabletop==1.0.0b4 --no-deps`
2. After it's installed, find `requirements.txt` in the `vstabletop` folder and remove the `kiwisolver==1.0.1` line
3. Install the rest of the requirements: `pip install -r requirements.txt`
4. Run `app.py` the same way as described above. The games should be able to run normally.

### Method 3: Cloning 
1. Clone the repository.
2. Make a virtual environment as described in Method 1, activate it, and install everything specified in `requirements.txt`
3. `cd` into the app directory and run `questions.py` to set up the database.
4. Run the app in one of two ways:
   (a) Run `app.py` using Pycharm or other IDE, or on the command line with `python app.py`
   (b) On the command line, set the FLASK_APP variable (`set FLASK_APP=app` on Windows, or `export FLASK_APP=app` on non-Windows). Then run the app with: `flask run`
5. Click into the link in the program output (example: http://127.0.0.1:5000/) or copy & paste it into the browser. Log in as admin using password `123456`.

### Method 4: Virtual Machine
1. Please visit the wiki page [here](https://github.com/imr-framework/vs-tabletop/wiki/Virtual-Machine-with-Vagrant) if you are interested in using a virtual machine to play these games

Please also use this method (recommended) if you want to contribute to the repository.

If on windows, make sure to check you are not running on OneDrive but only from a local folder.


## Tabletop Games
The eight tabletop games are grouped into 4 pairs, each containing a "beginner" game and an "advanced" game. 
Games 1, 3, 5, 7 are beginner games and the games 2, 4, 6, 8 are advanced games. 

| # | Game          | Conceptsr |
| --- | ------------- | ------------- |
| 1 | What's in an image?      | FOV, resolution, windowing  |
| 2 | K-space magiK            | projection imaging, k-space  |
| 3 | Brains, please!          | contrast, T1/T2/PD, TR/TE/FA | 
| 4 | Fresh blood              | flow imaging |
| 5 | Proton's got moves       | M9, precession, RF pulses, signal detection | 
| 6 | Relaxation station       | T1 and T2 relaxation, FID | 
| 7 | Puzzled by projection I  | 1D and 2D projection (forward) |
| 8 | Puzzled by projection II | 1D and 2D projection (inverse)|

## 7. 👥 Contributing and Community guidelines
`vs-tabletop` adheres to a code of conduct adapted from the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct.
Contributing guidelines can be found [here](https://github.com/imr-framework/vs-tabletop/blob/main/CONTRIBUTING.md).

# References:
1. Please cite our article: Tong, G., Ananth, R., Vaughan Jr, J.T. and Geethanath, S., 2024. Expanding access to magnetic resonance education through open-source web tutorials. NMR in Biomedicine, pp.e5109-e5109.
2. Brain images from the Coursera Neurohacking in R (https://www.kaggle.com/datasets/ilknuricke/neurohackinginrimages) were used in Game 2.

## Feedback:
If you have played the games, please provide your feedback [here](https://docs.google.com/forms/d/e/1FAIpQLSf_nnL1OdemcEtcI9C57LcKRiQtvmovZ4TxX30x6MR1IuSZNw/viewform).
Your time is sincerely appreciated and will help us make this tool better.

## Screenshots for quick reference
Screenshots are in-development previews of the games. They will be updated at the first release. 

### Login page
![login](https://user-images.githubusercontent.com/31249056/186200814-f0abacb0-a4ad-490d-9b64-76e72f4bb6a9.png)

### Game navigation
![index](https://user-images.githubusercontent.com/31249056/186200755-38525e6b-4196-49d0-a23d-320a164ff2b4.png)

### Module 1 (beginner): What's in an image?
![game1](https://user-images.githubusercontent.com/31249056/186200870-c4d1a934-bf80-4f34-95e4-698a1fe6dee5.png)

### Module 2 (beginner): Brains, please!
![game3](https://user-images.githubusercontent.com/31249056/186200887-3504892c-3367-4fe4-a222-fc35fb869f8e.png)

### Module 3 (beginner): Proton's got moves
![game5](https://user-images.githubusercontent.com/31249056/186201062-cae3af09-749e-4e0a-a254-b803f7e22772.png)

### Module 4 (beginner): Puzzled by Projection I 
![game7](https://user-images.githubusercontent.com/31249056/186201082-00fc2dad-a9b1-4911-8862-99fbd73cccdc.png)

