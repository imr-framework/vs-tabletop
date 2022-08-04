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
                    ['Turn on the main magnet on and off. ',
                    'Repeat with different main field values.'],
                    # Move 2
                    ['Turn off the rotating frame.',
                     'Set the initial magnetization to theta = 45, phi = 135, M/M0 = 1. ',
                     'Press "START". How do Mx, My, and Mz change in time? ',
                     'Change the main field value and press "START" again. ',
                     'Turn the rotating frame back on.'],
                    # Move 3
                    ['Press "RESET" to turn off everything and turn on B0 again at B0 = 100 Gauss.',
                     'Turn on the rotating frame and the red transmit button to enable RF pulses. ',
                     'Press "TIP" to play the default RF pulse (FA = 90, pulse along x).',
                     'Experiment with different flip angles and pulse directions. '],
                    # Move 4
                    ['Push the “RESET” button to turn off everything. Then turn on B0.',
                    'Press on the ear button to turn on the receive coil.',
                    'Set the magnetization to x or y and press "SET". Then hit “RUN”.',
                     'Change field strengths and re-run to observe how signal changes.',
                    'Reset M to have different theta angles and re-run to observe how signal changes.'],

                    ],

    'tasks': ['The orange line is the net magnetziation vector (M). What will it look like at clinical MRI field strengths (1.5T, 3T)? (1T = 10000 Gauss)',
              'What do we see if our rotating frame is going faster than the spin? What if we are going slower?',
              'Press "Randomize!" to generate a new initial M and target M. Using up to 3 RF pulses, direct M to the target value displayed in gray. Then press "check" to check your answer.',
              'List all the things we can do to maximize the signal range. ']
}


GAME5_M_INFO = [
    ([90,90],[0,0,1]),
    ([90,0],[-1,0,0]),
    ([90,0],[0,1,0]),
    ([45,90],[1,0,0]),
]