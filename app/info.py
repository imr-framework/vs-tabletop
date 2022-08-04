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
    'explorations':[['Turn on the main magnet on and off. ',
                    'Repeat with different main field values.',
                    ],
                    ['Turn off the rotating frame.',
                     'Set the initial magnetization to theta = 45, phi = 135, M/M0 = 1. ',
                     'Press "START". How do Mx, My, and Mz change in time? ',
                     'Change the main field value and press "START" again. ',
                     'Turn the rotating frame back on.'],

                    ['Press "RESET" to turn off everything and turn on B0 again at B0 = 100 Gauss.',
                     'Turn on the rotating frame and the red transmit button to enable RF pulses. ',
                     'Play an RF pulse ',
                     'Play RF pulses '


                    ],


                    'Expl. 4'],

    'tasks': ['The orange line is the net magnetziation vector. What will it look like at clinical MRI field strengths (1.5T, 3T)? (1T = 10000 Gauss)',
              'What do we see if our rotating frame is going faster than the spin? What if we are going slower?',
              't3',
              't4']
}
