# Names and global data
import numpy as np
# Game names
GAMES = ['What is in an image?',
          'k-space magik', 'Brains, please!', 'Fresh Blood',
         'Proton\'s got moves','Relaxation Station','Puzzled by Projection I','Puzzled by Projection II']
INTRO = ['Learn about imaging basics!',
         'Travel around k-space and map it out!',
         'Look inside your head - with filters!',
         'A clever trick to image flow',
         'You can make the magnetization dance',
         'Measure the T1 and T2 of anything',
         'Make images with your brain',
         'Reconstruct objects with your brain']

GAMES_DICT = {}
GAMES_INFO = {}

for u in range(len(GAMES)):
    GAMES_DICT[u] = GAMES[u]
    GAMES_INFO[u] = INTRO[u]

# Game 1 instructions
GAME1_INSTRUCTIONS={
    'tabs': [f'Step {a+1}' for a in range(4)],
    'titles': ['Explore field-of-view', 'Explore matrix size','Explore zero-fill','Explore windowing'],
    'explorations':[{'Make an image': 'Press RUN to make an image with the default settings. What do you see?',
                     'Try a very big FOV': 'Set the FOV to 1000 mm and press RUN again. What do you see now?',
                     'Try a very small FOV': 'Acquire an image with FOV=100 mm. What do you see more of and what is missing now?',
                     'Experiment with FOV': 'Choose a few different FOVs and describe in your words what it means.'},
                    {'Change the matrix size':'Look at the matrix size. You may change it to different numbers to make the image more or less pixellated.',
                     'Try a small matrix size':'Put in a matrix size of 16 and press RUN. What happens?',
                     'Try a big matrix size':'Now acquire an image with matrix size = 256. What is the difference?',
                     'Experiment with matrix size': 'Try different matrix sizes and see how the image changes. How long does it take to get an image for smaller vs. larger matrix sizes? At which point is it not worth increasing it any more?',
                     'Find out what voxel size means':'How does the voxel size change when you enter different matrix sizes? Can you write an equation that relates voxel size with FOV and matrix size?'},
                    {'Change the zero-fill number':'The zero-fill is the displayed matrix size and should always be larger than the acquired matrix size. Try setting it to different numbers and acquire images.',
                     'Try the same zero-fill number as the matrix size':'Set matrix size and zero-fill to be the same at 16, 32, and 64. How does the image change?',
                     'Try a huge zero-fill number with a small matrix size':'Set matrix size to 16 and zero-fill to 64, 128, and 256. Does the zero-fill improve image resolution (that is, can you tell apart the structures better)? '},
                    {'Adjust the image display with windowing':'The windowing sliders can be moved to change the range of values that is displayed from black to wihte.',
                     'Change the minimum level':'Keeping the maximum level to the very right (100%), change the minimum level and re-run. How does the image change?',
                     'Change the maximum level':'Keeping the minimum level to the very left (0%), change the maximum level and re-run. How does the image change now?',
                     'Eliminate contrast':'Make minimum and maximum level the same and run at different values (for example, both at 0%, 50%,and 100%). Describe what exactly you see at a given level.'}],
    'tasks':{'Task 1: To see the whole picture': 'Adjust the FOV until it is just right for viewing the object with all its structures.',
             'Task 2: To see the details ': 'Adjust the matrix size until you can have a good idea of all the shapes.',
             'Task 3: Zero-fill is not magic!': 'Produce a low resolution image with a big matrix size',
             'Task 4: To see the differences': 'Adjust the windowing until there is a very large contrast between the structures.'}
}

# Game 2 instructions
GAME2_INSTRUCTIONS={
    'tabs':['Step 1', 'Step 2', 'Step 3',' Step 4'],
    'titles': ['Explore 1D transforms','Explore 2D transforms','Perform k-space magiK!','Free exploration'],
    'explorations':[
        {'Get your first signal': 'Select "sine wave" in signal type and press "get signal" to load it to the left display. \
          Describe the signal in your words.',
         'Perform 1D forward transform': 'Press "forward" to perform a Fourier transform of the signal. \
                                          The right display now shows the sine wave"s spectrum. What do you see?',
         'Explore parameters':'Try changing each of the parameters, generate the signal, and get its spectrum each time. \
                                         Describe what each parameter does to the signal and to the spectrum (vertical scale, horizontal scale, shift, phase modulation).',
         'Explore signals':'Experiment with the other options in "select signal".',
         'Explore spectra':'Experiment with options in the "select spectrum" drop down on the right. \
                                      Use the "backward" button to perform an inverse Fourier transform, \
                                    which recovers the signal from its spectrum. What happens when you press Forward and then Backward or vice versa?',
         'Draw your own signal':'In the middle, go to the "Draw" tab and draw any curve you like. \
         Press "Use" and then "Get signal" or "Get spectrum" to load it onto the panel you want. '},

        {'Perform the 2D transform on images': 'Now we can look at the 2D analog of the same process. \
                                                Go to the "2D Image" tab and choose any image you like. Press "Get Image" \
                                                and then "Forward" to look at the k-space. Repeat it for a few images. \
                                                What do the k-spaces have in common?',
         'Look into the 2D sine wave':'Get the image of a 2D sine wave and generate its k-space. What do you see? \
                                       You might have to zoom in to see the details of this one. How does this compare to the 1D sine wave? ',
         'Explore image parameters':'Try changing each of the parameters below, generate a new image, and get its k-space each time. \
             Describe what each parameter does to the image and to the k-space (rotation, horizontal scale, shift, and phase modulation).',
         'Explore k-space parameters': 'Perform the Backward transform on the "Double spike" 2D k-space preset (press "Get K-space" to generate the k-space first). \
                                        Change the parameters and describe what they do (rotation, spike separation). ',
         'Free time':'Explore other images and k-space options and perform multiple backward and forward transforms. ',
         'Draw your own image': 'Go to the "Draw" tab to paint any image you like. Press "Use" and then "Get image" (or "Get k-space") to load it. \
                                 Perform transformation of your signal and spectrum. \
                                 Use the drawing board and the preset signals to explore at least one of Properties 1-5 of the Fourier transform \
                                                  (see Definitions from the top game dropdown or the lab manual) in 2D.\
                                Record your findings with sketches of the images and k-spaces for each experiment. '},
        {'Select your target': 'Load one of the MRI images and generate its k-space',
         'Perform Sampling Magik': 'Go to the "Sampling" tab in the middle. The square represents k-space and the four lines slice it up. \
                                    The lighter part will be preserved and the darker part will be erased from our k-space. \
                                    Press "APPLY" to see the slicer applied. The erased parts are set to zero and appear black.',
         'Eliminate the peripheral': 'Move the four lines closer to the middle of k-space so only a small portion of light gray remains, \
                                     and press apply. Transform the restricted k-space back to image space. How did the image change? Why? \
                                     Can you relate this to the sine wave experiments above?',
         'Eliminate the center': 'Re-load the image and generate a fresh, complete k-space; then, press "Invert" in the slicer and "Apply"\
                                  to block out the center but preserve the periphery of k-space.  \
                                  Transform backwards. What do you see now? Describe your findings.',
         'Customize your magik': 'Explore the sampling tab to section out different parts of k-space and see its effects. \
                                  Moreover, you can also use the "Erase" tab to block out more interesting shapes and see \
                                  what it does to k-space! Describe your findings.'},

        {'Magik of Image Summoning': 'On the "upload" panel, you can upload an image and generate its k-space. \
                                      Use "Erase" or "Slicer" to apply different filter effects onto your image and then transform backwards. \
                                      "Recover" reloads the complete image.',
         'Magik of Line Skipping':'Explore the effects of under-sampling factors on the "sampling" panel.',
         'Magik of Art Creation': 'Using the properties of k-space, plan out and create your own art by drawing an image, \
                                   converting it to k-space, and manipulating it with "erase" and "sampling".  \
                                   You may export the images using the camera icon on top of them.',
         'Magik of Photo Styling': 'Using a photo you have taken and your knowledge about k-space, style the photo in three different ways by changing its kspace.',
         'Magik of Poetic Understanding':'Compose a haiku or a short poem about k-space using what you learned today.'}
    ],
    'tasks':{'Task 1': 'Perform transformation of your signal and spectrum. Use the drawing board and the preset signals to explore at least one of \
          Properties 1-5 of the Fourier transform. Record your findings with sketches of the signals and spectra you used.',
             'Task 2': 'Use the sampling tab, section k-space in a way that preserves only horizontal edges on an image.',
             'Task 3': 'With the eraser tool, design a k-space "filter" that styles in the image in a particular way. ',
             'Task 4': 'Congratulations on becoming a k-space magician! Check off this task and go on.'}
}

GAME3_INSTRUCTIONS={
    'tabs':[f'Step {a+1}' for a in range(3)],
    'titles':['Explore MRI contrasts','Explore MRI parameters',''],
    'explorations':[{},{}],
    'tasks':{'Task 1':'',
             'Task 2':''}
}

# Game 4 info
GAME4_INFO = {
    'T1_BLOOD': 2000e-3, # T1 = 2000 ms
    'T2_BLOOD': 200e-3, # T2 = 200 ms
    'T2s_BLOOD': 200e-3 / 6  # Roughly the same ratio as CSF in the Brainweb model
}

GAME4_INSTRUCTIONS={
    'tabs':[f'Step {a+1}' for a in range(3)],
    'titles':[],
    'explorations':[{},{}],
    'tasks':{'Task 1':'',
             'Task 2':''}
}
# Game 5 instructions
GAME5_INSTRUCTIONS={
    'tabs': ['Move 1','Move 2','Move 3','Move 4'],
    'titles': ['The Equilibrating Move','The Circulating Move','The Tipping Move','The Electrifying Move'],
    'explorations':[
                    # Move 1
                   {'Turn the main field (B0) on and off. ': 'Press the green magnet button to turn on B0.',
                    'Experiment with different B0 values.': 'Press the button again to turn off B0. Then use the slider to change the strength of B0 and turn it on again. '},
                    # Move 2
                    {'Set up environment for precession': 'First, turn off the rotating frame. Then, on the Set Initial Magnetization panel, input theta = 45 degrees, phi = 135 degrees, M/M0 = 1 and press SET. ',
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

FOV = 0.24
R = FOV/2
s2 = np.sqrt(2)
GAME6_INFO = {
    'phantom_n': 32, 'phantom_fov': FOV,
    't1_array_centers': [(R/(2*s2),R/(2*s2)),(-R/(2*s2),R/(2*s2)),(-R/(2*s2),-R/(2*s2)),(R/(2*s2),-R/(2*s2))],
    't2_array_centers': [(0,R/2),(-R/2,0),(0,-R/2),(R/2,0)]
}


GAME6_INSTRUCTIONS={
    'tabs':[f'Step {a+1}' for a in range(3)],
    'titles':[],
    'explorations':[{},{}],
    'tasks':{'Task 1':'',
             'Task 2':''}
}

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

GAME8_RANDOM_MODELS = [
    'g7_set1_typeA',
    'g7_set1_typeB',
    'g7_set1_typeC',
    'g7_set2_u135_d1',
    'g7_set2_u135_d2',
    'g7_set2_u135_d3',
    'center_ball',
    'double_cone',
    'double_cone_rev',
    'letterC',
    'letterN',
    'letterY',
    'simple_cube',
    'two_holes'
]


GAME8_INSTRUCTIONS={
    'tabs':[f'Step {a+1}' for a in range(3)],
    'titles':[],
    'explorations':[{},{}],
    'tasks':{'Task 1':'',
             'Task 2':''}
}
# Verbose definitions for each game (in html)
# Game 1
GAME1_BACKGROUND = {
    "Pixels / voxels": " It is a metric defining each unit in a picture/scan. A pixel defines space in a scan with two dimensions, \
    while the voxel defines a space in three dimensions. MR images are made up of voxels as they always have a third dimension or thickness. \
    The pixel is two-dimensional and exists on the x-y plane while the voxel is three-dimensional and exists on the x, y, and z space. \
    The pixel only has a length and a width while the voxel has a depth as well.",
    "Resolution": "Resolution refers to how sharp an image is and is related to the size of the individual pixel or voxel. \
    The smaller the pixel or voxel the greater the resolution. Voxels segment continuous space into discrete units. \
    The signal in each voxel is an average of all the sub-signals within it. The smaller you make the voxels, \
    the more closely spaced details you see because they tend to be assigned to different voxels. \
    You cannot see the details when using very large voxels because the spatial details are averaged out \
    and any locational information at smaller scales than the voxel is lost. Higher resolution images show more details.",
    "Voxel size": "This is the physical length of one side of a voxel, which is cuboidal. A voxel can have different x, y, and z side lengths." ,
    "Matrix size (N)": "Matrix size is an integer equal to the number of voxels in each dimension. \
    For example, an MR image can have a matrix size of 512 x 256, meaning that one side is divided into 512 parts and the other \
    is divided into 256 parts. The image would have a total of 512 x 256 = 131072 voxels. \
    Small and a lot of voxels mean the information is going to be better localized leading to more of the details being pronounced \
    (remember that the more information gets averaged in each pixel, the less pronounced it will be). \
    This is like having a high-megapixel camera. ",
    "Field-of-View (FOV)" : "When you take photos, the viewing window only shows a limited portion of all space. \
                            As you zoom in on a camera, only a small part of the image is seen while the rest is discarded. \
                            FOV refers to how much physical distance is covered between the left and right (or top and bottom) \
                            sides of the rectangular image and is usually given in millimeters in MRI. \
                            When matrix size is kept the same but FOV is increased, \
                            each pixel covers a larger distance and this lowers the image resolution.",
    "Relationship between imaging parameters": "Since Voxel Size, Matrix Size, and Field-of-View are dependent on each other, \
                                                they cannot all be freely set. This is similar to a simple y=mx+z function. \
                                                You can set two of the three variables freely and solve for the other but you cannot \
                                                set the value for all three variables and have the equation be true everytime. \
                                                Similarly, we can change two of either FOV, Voxel size, or Matrix Size and solve for \
                                                the other variable. The equation relating all three variables is: Field-of-View = Matrix Size x Voxel Size.",
    "Windowing": "Windowing affects the image contrast by filtering out certain signal intensities. When you window an MRI image, \
                  you are selecting which signal intensities you want to view and which you want to ignore. \
                  The window is defined by two values: the min intensity and the max intensity. \
                  When an image is windowed, all values <= min level are set to zero while all values >= max level are set to 1. \
                  The values in between min level and max level are rescaled so they range from 0 to 1. The width of the window is defined as:\
	              window width = max level - min level.  The level of the window is defined as the midpoint of this range:\
				 level = 0.5 x (max level + min level). The wider your window, the more intensity values are present and \
				  the more contrast you can cover,  but smaller contrasts are less apparent. \
				  The opposite is true for when the window gets narrower as fewer intensity values will be selected \
				  and tiny intensity differences will appear more dramatic.",
    "Voxel size vs. true resolution": "Voxel size is often representative of resolution, but not always. \
                                       One definition of true spatial resolution is how close together (say, in millimeters) \
                                       two dots can get before they can no longer be told apart. \
                                       In fact, with a technique called zero-filling, we can generate images of very large matrix sizes \
                                       from images of smaller matrix sizes. In this process, the voxel size is reduced, \
                                       but true resolution is not improved because the new image contains no more information \
                                       than the old, pixelated image. The information we missed out on when acquiring fewer pixels \
                                       from the beginning are NOT recovered by the zero-filling. \
                                       It merely “smoothes out the pixels” but does not improve true resolution at all."
}

GAME2_BACKGROUND = {
    "Basics":"An image can be seen in more than one way. Just like a piano sonata can be represented either \
             as a WAV file (a time domain signal) or discrete notes on a sheet music, an image can be in the form \
            for human eyes as a grayscale map or as its spatial frequency domain, or k-space. \
            Any 2D image (MR image, photo, drawing) can be converted to a k-space, and any 1D signal can be converted \
            to a spectrum. The conversion process is essentially the same. ",
    "Signal":"A signal is a function representing some processes we are eager to investigate. \
              It can be discrete or continuous, categorical or interval, and in 1D or 2D or 3D or more dimensions. \
              Examples: ECGs, brain waves, average June temperature of the past 10 years in your city… \
              In this game, 'signal' is used specifically for a 1-dimensional continuous wave/curve in time",
    "Sampling":"This refers to the process of gathering data at selected locations in k-space or in time. \
                In discrete sampling, we get an approximate idea of a continuous signal by looking at it \
                at a limited number of times. We want to sample just enough to get a fair representation of our signal.",
    "Spectrum":"This is a curve that shows you how much of each frequency is in a signal. \
                Each pair of peaks on the spectrum corresponds to a sinusoidal wave on the signal. \
                Higher peaks means the component has larger amplitude, and peaks closer to the center means \
                the component has lower frequency.",
    "Fourier Transform (FT)":"FT a mathematical operation that converts a signal to its spectrum. \
                              This process is one-to-one: we can apply the inverse Fourier transform to \
                            the spectrum and get back the same signal. The amount of information is preserved \
                            before and after the transformation. Mathematically, the FT can be performed as \
                            an integral in time or space with complex exponentials thrown in. ",
    "Properties of FT": "\
          <ol>\
          <li>The FT of the sum of two (or more) signals is equal to the sum of the FTs of those two (or more) signals.</li> \
          <li>The FT of the product of two signals is equal to their FTs convolved together, and vice versa. </li>\
          <li>If you multiply a signal by a constant C, the FT of it is also multiplied by C.</li>\
          <li>If a signal gets wider, its FT gets narrower, and vice versa. </li> \
          <li>If you move the signal horizontally, its FT gets a linearly varying complex phase. If you move the FT, the signal gets the same. </li>\
        </ol>",
    "Image space": "Explored in Game 1, image spaces are grayscale maps stored as matrices. \
                    Each entry of the matrix represents a point in space and its magnitude tells \
                    you how bright the image is at that spot.",
    "K-space":"What you get if you perform a Fourier transform on the image space. Because the image space is 2D, \
             we have to integrate in two directions. Similar properties apply to the 2D FT and 1D FT.",
    "Spatial frequency:": "If a sine wave is represented by a pair of peaks on the spectrum, what is represented by a \
                           pair of peaks in k-space? This is where spatial frequency comes in. \
                          If there were two peaks symmetric by the origin in k-space and the line connecting the peaks is horizontal,\
                           there would be vertical stripes in image space. \
                           The brightness is not either black or white, but varies along the same horizontal line in the form \
                           of a sinusoidal function. Importantly, the points in k-space and image-space do NOT map one-to-one.\
                          Changing one point in k-space will change ALL POINTS in the image space, and vice versa. \
                          This is because each point in k-space corresponds to a spatial wave that occupies the entire image. \
                          Because of this, many image artifacts in MR are not straightforward, but require some amount of \
                          “k-space intuition” to understand. ",
    "K-space and MRI acquisition": "While the camera and the human eye both speak the language of image space \
                                   (as projected onto the image sensor in the camera and the retina in the human eye),\
                                   MRI speaks in k-space - it is the natural place where we get our data. \
                                   This is because of the following:  \
         <ol> \
          <li>The protons in hydrogen atoms are tiny magnets that, when placed in a magnetic field, rotates around that field\'s direction.</li> \
          <li>The stronger this field is, the faster they rotate. </li>\
          <li>The position of a rotating thing can be represented as a complex exponential whose argument changes with time. </li>\
          <li>When we apply an imaging gradient field (one of the three key magnetic fields that the MRI scanner uses), the complex exponentials get their frequencies modulated in such a way that the signal is the Fourier transform of the image. The signal in general is a spatial integral of all the tiny rotating magnets, so this process physically performs a Fourier transform (with the protons themselves being the complex exponential terms)! </li> \
          <li>If we apply the gradients correctly, each point in time gets mapped to a different point in k-space, and we know this mapping.</li> \
          <li>By sampling the signal at different times, we can fill up k-space. </li> \
          <li>Lastly, we perform an inverse 2D FT to convert the k-space back to the image. This step is called image reconstruction.</li>\
        </ol>"
}

GAME3_BACKGROUND = {
    "Basics": "Like any other part of the body, the brain has many types of tissues with different physical properties. \
    When using the MR scanner, we often rely on them to tell apart brain regions and look for areas where these properties \
    change because of diseases. To highlight specific tissues, we can use a T1-weighted, T2-weighted, or PD-weighted scan.",
    "Brain tissue types":"There are 3 major types of brain tissues: \
          <ul>\
          <li>Cerebrospinal fluid (CSF)</li> \
          <li>White Matter (WM)</li>\
          <li> Gray Matter(GM)</li> \
        </ul>\
    <b>CSF</b> is the liquid content of brain ventricles. It flows in and around the brain to absorb impact from injuries to the skull \
    and provide nutrients. <b> White matter </b> effects learning, distribution of action potentials, and communication between different regions of \
    the brain. It is called white matter because its neuronal axons are covered in a protective fatty sheath which gives it a white color. \
    <b>Gray matter</b> mainly receives incoming information and regulates outgoing information.",
    "RF pulse":"An RF pulse is a short-lived magnetic field that tips the protons off their main magnetic field axis so that they are at an angle to it. \
                 How much they get tipped depends on the strength and duration of the pulse.",
    "Flip Angle (FA)": "FA is the net rotation angle of the magnetization when an RF pulse is applied. \
                        FA = 0 signifies no change, while FA = 180 degrees signifies a rotation of half a circle \
                        so the magnetization is pointing straight down.  At low flip angles, the MR signal \
                        is roughly proportional to the flip angle. This no longer holds at higher flip angles, \
                        and the signal dependence on flip angle gets more complicated and depends on the next two MR parameters.",
    "Echo Time (TE)": "TE is the time difference between the time when the RF pulse arrives at the target \
                       to the time when the signal bounces back and hits a peak, forming what’s called an echo. ",
    "Repetition Time (TR)": "TR is the time difference between one set of RF pulses \
                             (a 90 degree pulse and an 180 degree pulse in the example below) \
                             and the next. It is called “repetition” because we excite the spins in exactly \
                             the same way between the two intervals. We need to repeat the excitation because \
                             we only have time to get partial information within each TR. \
                             Combining signals from multiple TRs gives us a complete image. ",
    "Tissue properties": "MRI measures three main tissue parameters: \
                        <ul>\
                            <li>Longitudinal relaxation time (T1) </li>\
                            <li>Transverse relaxation time (T2) </li>\
                            <li>Proton Density (PD) </li>\
                        </ul>\
                         T1 and T2 have units of seconds or milliseconds and decide how fast signals relax back \
                         into their equilibrium value. PD refers to the relative density of protons, \
                         so it measures how much signal we can get from the same volume of tissue. \
                         All other things being equal, the higher PD a tissue has, the brighter it looks on the image.\
                         The table below shows typical T1, T2, and PD values for the three brain tissue types at a main field strength of 1.5 Tesla.\
                            <table class='table'><tr><th scope='col'></th><th scope='col'><b>GM</b></th><th scope='col'><b>WM</b></th><th scope='col'><b>CSF</b></th></tr> \
                              <tr><th scope='row'><b>T1 (ms)</b></th><td>1130</td><td>750</td><td>1940</td></tr>\
                              <tr><th scope='row'><b>T2 (ms)</b></th><td>119</td><td>87</td><td>230</td></tr>\
                              <tr><th scope='row'><b>PD (relative)</b></th><td>1.04</td><td>0.95</td><td>1.02</td></tr>\
                            </table>",
    "Contrast types": "You can think of contrasts as filters for MR images. Three basic contrast types exist: \
                        <ul>\
                            <li>T1-weighted (T1w)</li>\
                            <li>T2-weighted (T2w)</li>\
                            <li>PD-weighted (PDw)</li>\
                        </ul>\
                      In general, T1w highlights tissues with short T1, \
                      T2w highlights tissues with long T2, \
                      and PDw highlights tissues with high PD. \
                      The table below shows how to get T1w, T2w, or PDw contrasts by setting sequence parameters: \
                    <table class='table'><tr><th scope='col'><b>Contrast</b></th><th scope='col'><b>TE</b></th><th scope='col'><b>TR</b></th></tr> \
                    <tr><th scope='row'><b>T1w</b></th><td>Short</td><td>Medium</td></tr>\
                    <tr><th scope='row'><b>T2w</b> </th><td>Medium</td><td>Long</td></tr>\
                    <tr><th scope='row'><b>PDw</b></th><td>Short</td><td>Long</td></tr>\
                  </table>"
}


GAME5_BACKGROUND = {
    "Spin": "Protons, neutrons, and electrons all have intrinsic angular momentum, also called spin. \
               These subatomic particles are always rotating around their own center axes by nature. ",
    "Magnetic Moment": "A vector that measures how much of a magnetic dipole a thing is \
                        and the direction of this dipole. A loop of wire carrying a current has a magnetic moment, \
                        and so does a fridge magnet. Protons are magnets too, and each of them has a fixed magnetic moment μ.",
    "Net Magnetization (<b>M</b>)":"Because the protons and their magnetic moments are small, \
                                    it is preferable to think about the sum of their behavior \
                                     rather than trying to model each individual proton. \
                                     Net Magnetization is the average vector of all the proton magnetic moments within a volume in space.\
                                   When there is no outside magnetic field, the spins are all pointing at random directions and M is zero. \
                                   When you turn on such a field and keep it on, however, \
                                   net magnetization develops and ends up larger for higher magnetic field strengths \
                                   because of energy level effects.",
    "Main magnetic field (B0)": "A strong magnetic field (clinically, about 30000 to 70000 times Earth’s field) essential to MR. \
                                 It is made highly uniform and points along the z axis. \
                                 When you go into the MR scanner, you are under its influence and a net magnetization vector develops in you!",
    "Precession": "The motion of the protons as they spin around the axis of the main magnetic field in a cone like manner. \
                   This happens partly because the protons have angular momentum, and partly because the main magnetic field \
                   is pulling on the proton’s magnetic moment. ",
    "Rotating frame of reference" : "Since the magnetic moment is rotating so fast, its movement can quickly become very complicated \
                                     when we start turning on additional magnetic fields. The way to simplify this motion is to pretend \
                                      that we are also going around the precession axis at exactly the same speed, \
                                      in an ultra-fast merry-go-round kind of way. Once we are on this bandwagon, the spin’s magnetic moment \
                                       seems to stay still. It is just like how two people standing on two trains side by side moving \
                                        at the same speed seem stationary to each other.",
    "Radiofrequency (RF) pulses" : "RF pulses is a second and more short-lived magnetic field that we use to talk to spins.\
                                    The RF field is perpendicular to the main field and has to rotate as fast as the spin’s \
                                    precession to catch up with it. Once it catches up, it flips the spins as if turning a wrench, \
                                    knocking them out of the comfortable z equilibrium and towards the xy plane. \
                                    Then, after we have rotated the desired amount, the pulse is turned off. \
                                   The axis of rotation is along the RF field vector itself and the angle is proportional \
                                   to both the strength and the duration of the pulse. \
                                   The figure below shows how M is turned by 90 degrees in (b) and then spreads out \
                                   because individual spins have slightly different frequencies in real life.",
    "Nutation" : "It is just another word for RF rotation of the net magnetization vector to distinguish it from precession. ",
    "Electromotive force (emf)" : "This is the electrical voltage created when the magnetic flux across a looped wire changes. \
                                  This happens only when this wire, also called a coil, is placed correctly so that magnetic fields \
                                  generated by the net magnetization M pass through it. When M is in precession, \
                                  a sinusoidal voltage can be measured across the coil.",
    "Free induction decay (FID)" : "This is the more realistic emf signal that occurs right after the 90 degree RF pulse. \
                                    Due to interactions between spins causing them to have slightly different frequencies over time, \
                                    the signal goes down to zero exponentially at predictable rates described by the T2 tissue parameter."
}

GAME7_BACKGROUND = {
    "3D coordinates": "Any point in 3D space can be located with a 3D vector (x,y,z), \
     which denotes its position relative to a known origin point. \
     A 3D model is defined by surfaces, which are defined by triangles, \
     which are in turn defined by its three vertices, each of which has coordinates (xi,yi,zi). ",
    "2D projections": "Imagine a brick suspended in air in a room with a top light that emits parallel rays. \
                      The brick casts a rectangular, uniform shadow. Now, if we drill holes in the brick, \
                      they are going to pass light and change the shape of the shadow. \
                      If we start playing with different geometrical shapes, \
                      all of them will have shadows of different shapes and sizes. \
                      If we change the brick into a translucent block of glass, \
                      the shadow will be lighter, as more light comes through. <br>\
                      Real world objects such as your brain are made of different materials at different spots. \
                      Therefore, when light passes through them, the amount that reaches the other side varies \
                      and creates a weirdly shaded shadow. \
                      In this case, we are talking about quite high-energy light: X-rays!<br> \
                      In fact, this is almost exactly how plain X-rays work. \
                      We see more X-rays coming out the other side when there is less material \
                      for it to pass through. The amount of light can be measured on a light-sensitive sheet. \
                      Then the total amount of material the light had to pass through can be calculated for each point on the shadow.\
                      Brighter parts mean there was more material, and darker parts mean there was less.<br> \
                      More mathematically, a 2D projection of a 3D function along an axis can be calculated \
                      by summing up the function f(x,y,z) across all values on that axis. \
                      For example, a projection along the z axis can be calculated by creating a function g(x,y), where: \
                          g(x0,y0) = (sum of f(x0,y0,z) for all z between negative infinity and positive infinity)  \
                      If you have taken calculus, you know this can be done with an integral for continuous functions.\
                      In the game, you will be able to perform 2D projections along the x, y, and z axes.",
                      "1D projection": "This procedure turn 2D images into 1D curves just like 2D projections \
                                        turn 3D volumes into 2D images. We can choose any angle from 0 degrees to 180 degrees \
                                        to make the projection.",
                      "Projection imaging": "This works by making projections of the same subject and combining them\
                                             to make images that show its internal structure. Examples include:\
                                            <ul> \
                                                <li><b>Plain radiograph or X-ray</b>: uses X-rays to obtain a single 2D projection on X-ray-sensitive film or digital screen and views it directly as the image. In a chest X-ray, there is no front to back information and things overlap with each other. </li>\
                                                <li><b>Computed Tomography (CT)</b>: uses a rotating thin blade of X-ray to obtain many 2D-to-1D projections around a certain slice of your body (for example, around your waist or feet). These projections are combined, or reconstructed, to a single slice that shows clear internal structure and no overlap. </li>\
                                                <li><b>Projection reconstruction in MRI</b>: certain types of MRI data can be reconstructed using CT-like methods. Why this is the case involves spatially varying magnetic fields and how hydrogen in your body responds to them as well as mathematical relationships between projections and spatial frequencies. </li>\
                                            </ul>"
}