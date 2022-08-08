# Names and global data

# Game names
GAMES = ['What is in an image?',
          'k-space magik', 'Brains please', 'Fresh Blood',
         'Proton\'s got moves','Relaxation Station','Puzzled by Projection I','Puzzled by Projection II']
GAMES_DICT = {}
for u in range(len(GAMES)):
    GAMES_DICT[u] = GAMES[u]


# Game 5 instructions
GAME5_INSTRUCTIONS={
    'tabs': ['Move 1','Move 2','Move 3','Move 4'],
    'titles': ['The Equilibrating Move','The Circulating Move','The Tipping Move','The Electrifying Move'],
    'explorations':[
                    # Move 1
                   {'Turn the main field (B0) on and off. ': 'Press the green magnet button to turn on B0.',
                    'Experiment with different B0 values.': 'Press the button again to turn off B0. Then use the slider to change the strength of B0 and turn it on again. '},
                    # Move 2
                    {'Set up environment for precession': 'First, turn off the rotating frame. Then, on the Set Initial Magnetization panel, input theta = 45, phi = 135, M/M0 = 1 and press SET. ',
                     'Let the magnetization precess':'Press "START". How would you describe this movement? ',
                     'Experiment with different B0 values': 'Change the main field values with the slider and press START again. How does the movement change with B0?',
                     'Experiment with different initial conditions': 'Set the initial magnetization to different thetas and phis, pressing SET and then START each time. How does the initial angle affect the trajectory of M?'},
                    # Move 3
                    {'Reset everything': 'Press "RESET" to turn off everything and turn on B0 again at B0 = 100 Gauss.',
                     'Prepare RF pulse':'Turn on the rotating frame and the red transmit field (megaphone icon) to enable RF pulses. The red line indicates the direction of the RF magnetic field, also called B1. It can be in any direction on the x-y plane.',
                     'Play RF pulse': 'Press "TIP" to play the default RF pulse (FA = 90 degrees, Pulse direction = 0 degree). After the movement is over, rotate the 3D display to see what happened. How would you describe what the RF pulse did to the magnetization vector? ',
                     'Experiment with different flip angles. ': 'Turn off the RF field. Use the first slider to change the flip angle. Then turn it on again and press TIP. In your words, how does the flip angle affect the movement of M?',
                     'Experiment with different pulse directions.': 'Set the initial magnetization to z and press SET. Turn off the RF field and change the flip angle to 90 degrees and the pulse directions to 0, 180, and 45 degrees in turn. Each time, reset initial M and use TIP to observe the RF in action. What role does the pulse direction play in the motion of M?'},
                    # Move 4
                    {'Set up environment for signal reception': 'Push the “RESET” button to turn off everything. Then turn on B0, set magnetization to x, and turn on the blue receive coil (ear icon). A blue coil should appear. You can re-orient it along x or y.',
                     'Let the magnetization precess in the presence of a receive coil':'Set the magnetization to x or y and press "SET". Then hit START. A green signal should appear below. What does this signal look like? Press the question mark button next to "signal(emf) to learn more." ',
                     'Experiment with field strengths': 'Change field strengths and press START each time to observe how signal changes with B0',
                     'Experiment with initial M': 'Reset M to have different theta angles and press START each time to observe how signal changes with the orientation of M'},
                    ],

    'tasks': {'Task 1: Where does M stand?': 'The orange line is the net magnetziation vector (M). What will it look like at clinical MRI field strengths (1.5T, 3T)? (1T = 10000 Gauss)',
              'Task 2: Getting out of sync': 'What do we see if our rotating frame is going faster than the spin? What if we are going slower?',
              'Task 3: Hit the target magnetization': 'Your task now is to conduct the magnetization to specified positions. Press "Randomize!" to generate a new initial M and target M. Using up to 3 RF pulses, direct the current M, shown in orange, to the target M, shown in gray. Then press "check" to check your answer.',
              'Task 4: Turning it up': 'What can we do to maximize the signal range?'}
}


GAME5_M_INFO = [
    ([90,90],[0,0,1]),
    ([90,0],[-1,0,0]),
    ([90,0],[0,1,0]),
    ([45,90],[1,0,0]),
]



# Game 7 static text

GAME7_INSTRUCTIONS = {
    'tabs': [f'Step {n}' for n in [1,2,3,4,5]],
    'titles': ['Exploring 3D models', '2D projection', '1D projection', 'Puzzle time! Part I', 'Puzzle time! Part II'],
    'explorations': [{'Explore 3D models': 'Press "Load 3D model" to visualize the default model. Rotate the model around. You may use the "transparent" button to see the internal structure too.',
                     'Look at other models': 'Use the "Select model" dropdown to choose any model and load again. Look at a few different models and get familiar with their structures. \
                     In real life, the cylinders are fit tightly in a tube and filled with water so only the cutout parts generate signal. '},
                     {'Select 2D projection axis': 'Choose an display a 3D model. Click on "show/hide lines". \
                                                    On the left, select "x", "y", or "z" to see three different ways of projecting the 3D model. \
                                                    The lines indicate the axis along which signal will accumulate.',
                      'Display 2D projected image':'Choose the z axis. Then press "2D projection" to show the projected image. How does this compare with the original model? \
                                                   Can you approximate the view by rotating the transparent 3D model?',
                      'Experiment with different models and axes':'Try "x" and "y" projections; then, try other models. Can you predict the projections just by looking at the 3D models?'},
                     {'Set up 2D projection':'Generate a 2D projection using the 3D model "Dots" in the z direction. You should see two circles on the 2D image.',
                      'Select 1D projection axis': 'Use the circular eye controller to select a projection angle of 90 degrees. Show the lines. \
                      The green lines indicate the direction along which the 2D image will be summed to make a 1D projection.',
                      'Display 1D projection':'Press "1D projection" to show the projected image. What do you see? Can you connect this to the definition of 1D projections?',
                      'Experiment with different angles': 'Use the circular eye controller to select a few different angles (0,45,135,...) and observe the 1D projections. At which angles can we tell the two circles apart? ',
                      'Experiment with different modles': 'Explore the models and generate their 1D projections. How would you predict a 1D projection, given an angle and a 2D image?'},
                     {'2D puzzle':'Now is the time for you to guess some 2D projections! Press "Randomize!" to display a special cylinder and projection angle.'},
                     {'1D puzzle': 'Guess your 1D projection. Press Randomize! to display a special cylinder, a specified 2D projection, and a 1D projection angle.'}
            ],
    'tasks': {'Task 1: Thought experiment': 'How can you figure out the internal structure without the transparency button?',
              'Task 2: 2D projection ':'If you can take one 2D projection of yourself, which axis would you choose and what would you see on the image?',
              'Task 3: 1D projection':'If we perform enough 1D projections at various angles, can we figure out what the original 2D image is? How? ',
              'Task 4: Project 2D with your brain! ':'Select the correct projection and click "submit" to check your answer. ',
              'Task 5: Project 1D with your brain!': 'Select the correct projection and click "submit" to check your answer. '}
}

GAME7_RANDOM_MODELS = [
    'g7_set1_typeA',
    'g7_set1_typeB',
    'g7_set1_typeC',
    'g7_set2_u135_d1',
    'g7_set2_u135_d2',
    'g7_set2_u135_d3'

]