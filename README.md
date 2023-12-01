<h1 align="center">Virtual Scanner Tabletop Web Games</h3>
<p float="left">
<img title="PyPulseq Badge" src="https://img.shields.io/badge/made%20using-pypulseq-brightgreen" height="15"><img title="Virtual Scanner Badge" src="https://img.shields.io/badge/made%20using-virtual--scanner-blue" height="15">
</p>
<br>

Virtual Scanner Tabletop is an extension to [Virtual Scanner](https://github.com/imr-framework/virtual-scanner/) comprising of educational games about MRI that can be run by simulation or connected to a real educational MRI scanner. Target audience include high school, college, and post-grad students as well as members of the MR and scientific community at large.   

## Quickstart
### Method 1: `pip install`
1. On the command line, make a new virtual environment in your terminal using the command: '''python -m venv myenv''' For more info on creating virtual environments,
see here [https://docs.python.org/3/library/venv.html]. 
2. Pip install the games using the command: '''pip install vs-tabletop'''
3. cd into the main folder called "vstabletop" (`venv\Lib\site-packages\vstabletop`) and run '''app.py'''. Click into the link in the program output (examplee: http://127.0.0.1:5000/). Log in as admin using password `123456`. 
#### Troubleshooting 
(version 1.0.0b5) - You might encounter problems with installing Kiwisolver which requires Visual C++. If you have trouble getting the Visual C++, you can ignore the kiwisolver and perform the following steps:
1. Install vs-tabletop without dependencies: `pip install vs-tabletop==1.0.0b4 --no-deps`
2. After it's installed, find `requirements.txt` in the `vstabletop` folder and remove the `kiwisolver==1.0.1` line
3. Install the rest of the requirements: `pip install -r requirements.txt`
4. Run `app.py` the same way as described above. The games should be able to run normally.

### Method 2: Cloning 
1. Clone the repository.
2. Make a virtual environment, activate it, and install everything specified in `requirements.txt`
3. `cd` into the app directory and run `questions.py` to set up the database.
4. Run the app in one of two ways:
   (a) Run app.py using Pycharm or other IDE, or on the command line with `python app.py`
   (b) On the command line, set the FLASK_APP variable (`set FLASK_APP=app` on Windows, or `export FLASK_APP=app` on non-Windows). Then run the app with: `flask run`
5. Click into the link in the program output (example: http://127.0.0.1:5000/) or copy & paste it into the browser. Log in as admin using password `123456`.

Please provide feedback here after you've tried all the beginner games:smile:: https://forms.gle/HMby4NHcmrTLi5Ai7

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

## Screenshots 
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

# References
Brain images from the Coursera Neurohacking in R (https://www.kaggle.com/datasets/ilknuricke/neurohackinginrimages) were used in Game 2.
