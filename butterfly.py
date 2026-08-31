from PIL import Image, ImageDraw
import imageio.v2 as imageio
import numpy as np
import math
import os

from rlottie_python import LottieAnimation

# ============================================================
#                     EXPERIMENT SETTINGS
# ============================================================
#
# MOST OF THE THINGS YOU WILL WANT TO CHANGE LATER
# ARE IN THIS SECTION.
#
# ============================================================


# ------------------------------------------------------------
# VIDEO SIZE
# ------------------------------------------------------------

WIDTH = 768
HEIGHT = 768


# ------------------------------------------------------------
# FRAME RATE
# ------------------------------------------------------------
#
# 60 FPS means:
#
# 1 second = 60 frames
# 2 seconds = 120 frames
#
# This makes the timing inside the generated video predictable.
#

FPS = 60


# ------------------------------------------------------------
# TOTAL VIDEO LENGTH
# ------------------------------------------------------------

VIDEO_DURATION = 5.0


# ------------------------------------------------------------
# IMPORTANT EEG TIMING
# ------------------------------------------------------------
#
# The butterfly appears at time = 0.
#
# At exactly this time, the butterfly will have completed
# its movement into the chimney.
#
# Example:
#
# 2.0 seconds at 60 FPS = frame 120
#

FINAL_TIME = 5.0


# ------------------------------------------------------------
# CHIMNEY ENTRY TIMING
# ------------------------------------------------------------
#
# The butterfly spends most of the time flying toward the
# chimney.
#
# During the final part, it actually enters the chimney.
#
# Example:
#
# 0.00 s -> butterfly appears
# 1.70 s -> reaches chimney
# 1.70-2.00 s -> goes inside
# 2.00 s -> completely hidden
#

ENTRY_DURATION = 0.30

FLIGHT_END_TIME = FINAL_TIME - ENTRY_DURATION


# ------------------------------------------------------------
# BUTTERFLY STARTING POSITION
# ------------------------------------------------------------

START_X = 110
START_Y = 520


# ------------------------------------------------------------
# CHIMNEY POSITION
# ------------------------------------------------------------
#
# These coordinates correspond to the house we draw below.
#

CHIMNEY_CENTER_X = 520

# Top/opening of chimney
CHIMNEY_OPENING_Y = 112

# Butterfly approaches slightly above the opening first
APPROACH_Y = 75

# Where the butterfly moves while entering
INSIDE_CHIMNEY_Y = 150


# ------------------------------------------------------------
# BUTTERFLY APPEARANCE
# ------------------------------------------------------------

# ------------------------------------------------------------
# LOTTIE BUTTERFLY
# ------------------------------------------------------------

# Size of the rendered Lottie butterfly
BUTTERFLY_SIZE = 100


# ------------------------------------------------------------
# LOTTIE PLAYBACK SPEED
# ------------------------------------------------------------
#
# 1.0 means:
# play the original Lottie at its original speed.
#
# Your Lottie:
#
# 30 FPS
# 120 frames
# 4 seconds total
#
# The wing movement in this animation is approximately 1.5 Hz.
#
# Therefore:
#
# LOTTIE_SPEED = 1.0
# ≈ original 1.5 Hz wing movement
#
# LOTTIE_SPEED = 0.5
# ≈ approximately 0.75 Hz
#
# LOTTIE_SPEED = 2.0
# ≈ approximately 3 Hz
#

LOTTIE_SPEED = 1.0


# Small movement of the ENTIRE butterfly during flight
FLUTTER_AMOUNT = 7

# Frequency of the whole-body vertical wobble
FLUTTER_FREQUENCY = 0.8

# ============================================================
#                        FOLDERS
# ============================================================

ASSETS_FOLDER = "assets"
OUTPUT_FOLDER = "output"
LOTTIE_FILE = "Butterfly Lottie Animation.json"

os.makedirs(ASSETS_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ============================================================
#                AUTOMATIC VIDEO NUMBERING
# ============================================================
#
# Running the program repeatedly creates:
#
# butterfly_video_1.mp4
# butterfly_video_2.mp4
# butterfly_video_3.mp4
#
# Old versions are never overwritten.
#

def get_next_output_filename():

    number = 1

    while True:

        filename = os.path.join(
            OUTPUT_FOLDER,
            f"butterfly_video_{number}.mp4"
        )

        if not os.path.exists(filename):
            return filename

        number += 1


# ============================================================
#                    COLOUR DEFINITIONS
# ============================================================

BACKGROUND_COLOR = (248, 245, 237)

OUTLINE = (72, 43, 34)

ROOF = (238, 124, 100)

ROOF_LIGHT = (249, 148, 120)

ROOF_DETAIL = (177, 82, 67)

WALL = (255, 253, 247)

WINDOW = (218, 238, 240)

CHIMNEY_DARK = (38, 28, 24)


# ============================================================
#                   CREATE HOUSE SVG
# ============================================================
#
# This creates a real .svg file.
#
# Later this can be useful because different parts of the
# house can be represented as separate vector elements.
#
# The MP4 itself is generated with Pillow below because that
# gives us straightforward frame-by-frame control.
#

def create_house_svg():

    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg"
     width="{WIDTH}"
     height="{HEIGHT}"
     viewBox="0 0 {WIDTH} {HEIGHT}">

    <rect width="{WIDTH}"
          height="{HEIGHT}"
          fill="#f8f5ed"/>

    <!-- HOUSE BODY -->
    <rect x="145"
          y="350"
          width="475"
          height="220"
          rx="8"
          fill="#fffdf7"
          stroke="#482b22"
          stroke-width="8"/>


    <!-- MAIN ROOF -->
    <path d="
        M 95 350
        Q 100 330 115 305
        L 185 180
        Q 198 158 225 158
        L 505 158
        Q 530 158 547 180
        L 655 315
        Q 674 340 658 350
        Z"
        fill="#ee7c64"
        stroke="#482b22"
        stroke-width="9"
        stroke-linejoin="round"/>


    <!-- DORMER WALL -->
    <path d="
        M 286 285
        L 277 208
        L 365 138
        L 454 210
        L 445 285
        Z"
        fill="#fffdf7"
        stroke="#482b22"
        stroke-width="8"/>


    <!-- DORMER ROOF -->
    <path d="
        M 267 210
        L 365 116
        L 470 214"
        fill="none"
        stroke="#482b22"
        stroke-width="16"
        stroke-linecap="round"
        stroke-linejoin="round"/>

    <path d="
        M 273 207
        L 365 128
        L 463 210"
        fill="none"
        stroke="#f99478"
        stroke-width="8"
        stroke-linecap="round"
        stroke-linejoin="round"/>


    <!-- ATTIC WINDOW -->
    <circle cx="365"
            cy="218"
            r="25"
            fill="#daeef0"
            stroke="#482b22"
            stroke-width="7"/>

    <line x1="340"
          y1="218"
          x2="390"
          y2="218"
          stroke="#482b22"
          stroke-width="6"/>

    <line x1="365"
          y1="193"
          x2="365"
          y2="243"
          stroke="#482b22"
          stroke-width="6"/>


    <!-- CHIMNEY -->
    <rect x="480"
          y="100"
          width="80"
          height="102"
          rx="3"
          fill="#fffdf7"
          stroke="#482b22"
          stroke-width="8"/>

    <rect x="488"
          y="107"
          width="64"
          height="31"
          rx="5"
          fill="#261c18"/>

    <rect x="468"
          y="86"
          width="104"
          height="31"
          rx="13"
          fill="#ee7c64"
          stroke="#482b22"
          stroke-width="8"/>


    <!-- LEFT WINDOW -->
    <path d="
        M 180 492
        L 180 430
        Q 180 390 230 390
        Q 280 390 280 430
        L 280 492
        Z"
        fill="#daeef0"
        stroke="#482b22"
        stroke-width="8"/>


    <!-- RIGHT WINDOW -->
    <path d="
        M 485 492
        L 485 430
        Q 485 390 535 390
        Q 585 390 585 430
        L 585 492
        Z"
        fill="#daeef0"
        stroke="#482b22"
        stroke-width="8"/>


    <!-- DOOR -->
    <path d="
        M 320 570
        L 320 440
        Q 320 388 375 388
        Q 430 388 430 440
        L 430 570
        Z"
        fill="#fffdf7"
        stroke="#482b22"
        stroke-width="8"/>


    <!-- STEPS -->
    <rect x="315"
          y="560"
          width="125"
          height="25"
          rx="10"
          fill="#fffdf7"
          stroke="#482b22"
          stroke-width="7"/>

    <rect x="295"
          y="585"
          width="165"
          height="27"
          rx="10"
          fill="#fffdf7"
          stroke="#482b22"
          stroke-width="7"/>

    <rect x="270"
          y="612"
          width="215"
          height="31"
          rx="12"
          fill="#fffdf7"
          stroke="#482b22"
          stroke-width="7"/>

</svg>
"""

    path = os.path.join(
        ASSETS_FOLDER,
        "house.svg"
    )

    with open(path, "w") as file:
        file.write(svg)

    print("House SVG created:", path)


# ============================================================
#                 DRAW THE HOUSE FOR VIDEO
# ============================================================

def draw_house():

    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        BACKGROUND_COLOR
    )

    draw = ImageDraw.Draw(image)


    # --------------------------------------------------------
    # HOUSE BODY
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (145, 350, 620, 570),
        radius=8,
        fill=WALL,
        outline=OUTLINE,
        width=8
    )


    # --------------------------------------------------------
    # MAIN ROOF
    # --------------------------------------------------------

    roof_points = [
        (95, 350),
        (115, 305),
        (185, 180),
        (220, 158),
        (505, 158),
        (540, 180),
        (655, 315),
        (660, 350)
    ]

    draw.polygon(
        roof_points,
        fill=ROOF
    )

    draw.line(
        roof_points + [(95, 350)],
        fill=OUTLINE,
        width=9,
        joint="curve"
    )


    # --------------------------------------------------------
    # ROOF TILE DETAILS
    # --------------------------------------------------------

    for y, start_x, end_x in [
        (225, 150, 580),
        (270, 125, 610),
        (315, 105, 640)
    ]:

        x = start_x

        while x < end_x:

            draw.arc(
                (
                    x,
                    y - 10,
                    x + 48,
                    y + 16
                ),
                start=0,
                end=180,
                fill=ROOF_DETAIL,
                width=4
            )

            x += 43


    # --------------------------------------------------------
    # CENTRAL DORMER
    # --------------------------------------------------------

    dormer = [
        (286, 285),
        (277, 208),
        (365, 138),
        (454, 210),
        (445, 285)
    ]

    draw.polygon(
        dormer,
        fill=WALL
    )

    draw.line(
        dormer + [dormer[0]],
        fill=OUTLINE,
        width=8,
        joint="curve"
    )


    # Dormer roof dark outline

    draw.line(
        [
            (267, 210),
            (365, 116),
            (470, 214)
        ],
        fill=OUTLINE,
        width=16,
        joint="curve"
    )


    # Dormer roof inner colour

    draw.line(
        [
            (274, 207),
            (365, 128),
            (463, 210)
        ],
        fill=ROOF_LIGHT,
        width=8,
        joint="curve"
    )


    # --------------------------------------------------------
    # ATTIC WINDOW
    # --------------------------------------------------------

    draw.ellipse(
        (340, 193, 390, 243),
        fill=WINDOW,
        outline=OUTLINE,
        width=7
    )

    draw.line(
        (365, 194, 365, 242),
        fill=OUTLINE,
        width=6
    )

    draw.line(
        (341, 218, 389, 218),
        fill=OUTLINE,
        width=6
    )


    # --------------------------------------------------------
    # WINDOWS
    # --------------------------------------------------------

    for x in [180, 485]:

        draw.rounded_rectangle(
            (x, 390, x + 100, 495),
            radius=40,
            fill=WINDOW,
            outline=OUTLINE,
            width=8
        )

        draw.line(
            (x + 50, 392, x + 50, 492),
            fill=OUTLINE,
            width=6
        )

        draw.line(
            (x + 3, 447, x + 97, 447),
            fill=OUTLINE,
            width=6
        )

        # Window sill

        draw.rounded_rectangle(
            (x - 12, 487, x + 112, 507),
            radius=8,
            fill=WALL,
            outline=OUTLINE,
            width=7
        )


    # --------------------------------------------------------
    # DOOR
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (320, 388, 430, 570),
        radius=48,
        fill=WALL,
        outline=OUTLINE,
        width=8
    )

    # Door knob

    draw.ellipse(
        (337, 462, 353, 478),
        fill=OUTLINE
    )


    # --------------------------------------------------------
    # STAIRS
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (315, 560, 440, 585),
        radius=10,
        fill=WALL,
        outline=OUTLINE,
        width=7
    )

    draw.rounded_rectangle(
        (295, 585, 460, 612),
        radius=10,
        fill=WALL,
        outline=OUTLINE,
        width=7
    )

    draw.rounded_rectangle(
        (270, 612, 485, 643),
        radius=12,
        fill=WALL,
        outline=OUTLINE,
        width=7
    )


    # --------------------------------------------------------
    # CHIMNEY BODY
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (480, 100, 560, 202),
        radius=3,
        fill=WALL,
        outline=OUTLINE,
        width=8
    )


    # Brick details

    draw.line(
        (480, 150, 560, 150),
        fill=OUTLINE,
        width=5
    )

    draw.line(
        (520, 150, 520, 200),
        fill=OUTLINE,
        width=5
    )

    draw.line(
        (505, 102, 505, 150),
        fill=OUTLINE,
        width=5
    )

    draw.line(
        (545, 102, 545, 150),
        fill=OUTLINE,
        width=5
    )


    # Dark chimney opening

    draw.rounded_rectangle(
        (488, 107, 552, 138),
        radius=5,
        fill=CHIMNEY_DARK
    )


    # Chimney cap

    draw.rounded_rectangle(
        (468, 86, 572, 117),
        radius=13,
        fill=ROOF,
        outline=OUTLINE,
        width=8
    )


    return image


# ============================================================
#                    SMOOTH MOVEMENT
# ============================================================
#
# Normal linear movement can look robotic.
#
# This function makes the butterfly accelerate and
# decelerate smoothly.
#

def smoothstep(t):

    t = max(0.0, min(1.0, t))

    return t * t * (3 - 2 * t)


# ============================================================
#                BUTTERFLY FLIGHT POSITION
# ============================================================

def get_flight_position(current_time):

    # Convert current flight time to 0 -> 1

    progress = current_time / FLIGHT_END_TIME

    progress = max(
        0.0,
        min(1.0, progress)
    )


    smooth = smoothstep(progress)


    # --------------------------------------------------------
    # BASIC MOVEMENT
    # --------------------------------------------------------

    x = START_X + (
        CHIMNEY_CENTER_X - START_X
    ) * smooth

    y = START_Y + (
        APPROACH_Y - START_Y
    ) * smooth


    # --------------------------------------------------------
    # CURVED FLIGHT PATH
    # --------------------------------------------------------
    #
    # The butterfly rises a little in the middle of the path.
    #

    arc = (
        -80
        * math.sin(math.pi * progress)
    )

    y += arc


    # --------------------------------------------------------
    # SMALL FLUTTER MOVEMENT
    # --------------------------------------------------------

    flutter = (
        FLUTTER_AMOUNT
        * math.sin(
            current_time
            * 2
            * math.pi
            * FLUTTER_FREQUENCY
        )
    )

    y += flutter


    return x, y


# ============================================================
#                BUTTERFLY ENTRY POSITION
# ============================================================
#
#

def get_entry_position(current_time):

    entry_time = (
        current_time - FLIGHT_END_TIME
    )

    progress = (
        entry_time / ENTRY_DURATION
    )

    progress = max(
        0.0,
        min(1.0, progress)
    )

    smooth = smoothstep(progress)


    x = CHIMNEY_CENTER_X

    y = APPROACH_Y + (
        INSIDE_CHIMNEY_Y - APPROACH_Y
    ) * smooth


    return x, y, progress


# ============================================================
#                     DRAW BUTTERFLY
# ============================================================
#
# The butterfly is drawn entirely from code.
#
# The wings continuously change shape according to time.
#

def draw_butterfly(
    image,
    x,
    y,
    current_time,
    scale=1.0
):

    transparent_layer = Image.new(
        "RGBA",
        (WIDTH, HEIGHT),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(
        transparent_layer
    )


    x = int(x)
    y = int(y)


    # --------------------------------------------------------
    # WING ANIMATION
    # --------------------------------------------------------

    phase = (
        current_time
        * WING_FREQUENCY
        * 2
        * math.pi
    )

    # Goes smoothly between approximately 0.35 and 1.0

    wing_open = (
        0.35
        + 0.65
        * abs(math.sin(phase))
    )


    size = BUTTERFLY_SIZE * scale

    wing_width = max(
        6,
        int(size * wing_open)
    )

    upper_height = max(
        8,
        int(size * 0.80)
    )

    lower_width = max(
        5,
        int(wing_width * 0.72)
    )

    lower_height = max(
        5,
        int(size * 0.55)
    )


    butterfly_outline = (
        72,
        46,
        31,
        255
    )

    upper_wing = (
        242,
        164,
        57,
        255
    )

    lower_wing = (
        238,
        113,
        62,
        255
    )

    wing_detail = (
        255,
        225,
        134,
        255
    )


    # --------------------------------------------------------
    # LEFT UPPER WING
    # --------------------------------------------------------

    draw.ellipse(
        (
            x - wing_width - 4,
            y - upper_height,
            x - 3,
            y + 4
        ),
        fill=upper_wing,
        outline=butterfly_outline,
        width=2
    )


    # --------------------------------------------------------
    # RIGHT UPPER WING
    # --------------------------------------------------------

    draw.ellipse(
        (
            x + 3,
            y - upper_height,
            x + wing_width + 4,
            y + 4
        ),
        fill=upper_wing,
        outline=butterfly_outline,
        width=2
    )


    # --------------------------------------------------------
    # LOWER LEFT WING
    # --------------------------------------------------------

    draw.ellipse(
        (
            x - lower_width,
            y - 2,
            x - 2,
            y + lower_height
        ),
        fill=lower_wing,
        outline=butterfly_outline,
        width=2
    )


    # --------------------------------------------------------
    # LOWER RIGHT WING
    # --------------------------------------------------------

    draw.ellipse(
        (
            x + 2,
            y - 2,
            x + lower_width,
            y + lower_height
        ),
        fill=lower_wing,
        outline=butterfly_outline,
        width=2
    )


    # --------------------------------------------------------
    # WING SPOTS
    # --------------------------------------------------------

    spot_radius = max(
        2,
        int(size * 0.08)
    )

    spot_y = int(
        y - upper_height * 0.45
    )


    for direction in [-1, 1]:

        spot_x = int(
            x
            + direction
            * wing_width
            * 0.55
        )

        draw.ellipse(
            (
                spot_x - spot_radius,
                spot_y - spot_radius,
                spot_x + spot_radius,
                spot_y + spot_radius
            ),
            fill=wing_detail
        )


    # --------------------------------------------------------
    # BODY
    # --------------------------------------------------------

    body_height = int(
        size * 0.85
    )

    body_width = max(
        3,
        int(size * 0.10)
    )


    draw.ellipse(
        (
            x - body_width,
            y - body_height // 2,
            x + body_width,
            y + body_height // 2
        ),
        fill=butterfly_outline
    )


    # --------------------------------------------------------
    # HEAD
    # --------------------------------------------------------

    head_radius = max(
        3,
        int(size * 0.11)
    )

    head_y = int(
        y - body_height * 0.55
    )


    draw.ellipse(
        (
            x - head_radius,
            head_y - head_radius,
            x + head_radius,
            head_y + head_radius
        ),
        fill=butterfly_outline
    )


    # --------------------------------------------------------
    # ANTENNAE
    # --------------------------------------------------------

    antenna_length = int(
        size * 0.35
    )


    draw.line(
        (
            x - 2,
            head_y,
            x - antenna_length,
            head_y - antenna_length
        ),
        fill=butterfly_outline,
        width=2
    )

    draw.line(
        (
            x + 2,
            head_y,
            x + antenna_length,
            head_y - antenna_length
        ),
        fill=butterfly_outline,
        width=2
    )


    # Put butterfly onto main frame

    image.paste(
        transparent_layer,
        (0, 0),
        transparent_layer
    )


# ============================================================
#           DRAW CHIMNEY IN FRONT OF BUTTERFLY
# ============================================================
#
# THIS IS WHAT CREATES THE "GOING INTO THE CHIMNEY" EFFECT.
#
# Drawing order:
#
# 1. House
# 2. Butterfly
# 3. Front part of chimney
#
# Therefore the chimney can visually cover the butterfly.
#

def draw_chimney_foreground(image):

    draw = ImageDraw.Draw(image)


    # Front chimney body

    draw.line(
        (480, 137, 480, 202),
        fill=OUTLINE,
        width=8
    )

    draw.line(
        (560, 137, 560, 202),
        fill=OUTLINE,
        width=8
    )


    # Front face below opening

    draw.rectangle(
        (
            484,
            138,
            556,
            198
        ),
        fill=WALL
    )


    # Restore brick details

    draw.line(
        (484, 150, 556, 150),
        fill=OUTLINE,
        width=5
    )

    draw.line(
        (520, 150, 520, 198),
        fill=OUTLINE,
        width=5
    )


    # Re-draw outside edges

    draw.line(
        (480, 137, 480, 202),
        fill=OUTLINE,
        width=8
    )

    draw.line(
        (560, 137, 560, 202),
        fill=OUTLINE,
        width=8
    )


    # Chimney cap remains in foreground

    draw.rounded_rectangle(
        (468, 86, 572, 117),
        radius=13,
        fill=ROOF,
        outline=OUTLINE,
        width=8
    )


# ============================================================
#                      CREATE VIDEO
# ============================================================

def create_video():

    output_filename = (
        get_next_output_filename()
    )


    # Number of frames in entire video

    total_frames = round(
        VIDEO_DURATION * FPS
    )


    # Useful information for EEG timing

    final_frame = round(
        FINAL_TIME * FPS
    )

    flight_end_frame = round(
        FLIGHT_END_TIME * FPS
    )


    print()
    print("================================")
    print("BUTTERFLY VIDEO")
    print("================================")

    print(
        "Resolution:",
        WIDTH,
        "x",
        HEIGHT
    )

    print(
        "Frame rate:",
        FPS,
        "FPS"
    )

    print(
        "Total video:",
        VIDEO_DURATION,
        "seconds"
    )

    print(
        "Flight reaches chimney:",
        FLIGHT_END_TIME,
        "seconds"
    )

    print(
        "Flight-end frame:",
        flight_end_frame
    )

    print(
        "Fully inside chimney:",
        FINAL_TIME,
        "seconds"
    )

    print(
        "Final frame:",
        final_frame
    )

    print("================================")
    print()


    writer = imageio.get_writer(
        output_filename,
        fps=FPS,
        codec="libx264",
        quality=8,
        macro_block_size=None
    )


    # --------------------------------------------------------
    # GENERATE EVERY VIDEO FRAME
    # --------------------------------------------------------

    for frame_number in range(
        total_frames
    ):


        # Convert frame number to seconds

        current_time = (
            frame_number / FPS
        )


        # Start every frame with the clean house

        frame = draw_house()


        # ====================================================
        # PHASE 1:
        # BUTTERFLY FLIES TOWARD CHIMNEY
        # ====================================================

        if current_time < FLIGHT_END_TIME:

            x, y = get_flight_position(
                current_time
            )

            draw_butterfly(
                frame,
                x,
                y,
                current_time,
                scale=1.0
            )


        # ====================================================
        # PHASE 2:
        # BUTTERFLY ENTERS CHIMNEY
        # ====================================================

        elif current_time < FINAL_TIME:

            x, y, entry_progress = (
                get_entry_position(
                    current_time
                )
            )


            # Butterfly becomes slightly smaller while moving
            # into the chimney opening.
            #
            # This adds a little depth without suddenly
            # changing its appearance.

            scale = (
                1.0
                - 0.30 * entry_progress
            )


            draw_butterfly(
                frame,
                x,
                y,
                current_time,
                scale=scale
            )


        # ====================================================
        # PHASE 3:
        # AFTER FINAL_TIME
        #
        # Butterfly is completely hidden.
        # ====================================================

        else:

            pass


        # ----------------------------------------------------
        # Put chimney foreground over butterfly.
        #
        # This gives us actual visual occlusion.
        # ----------------------------------------------------

        draw_chimney_foreground(
            frame
        )


        # Add frame to MP4

        writer.append_data(
            np.array(frame)
        )


    writer.close()


    print()
    print("DONE!")
    print()
    print(
        "Created:",
        output_filename
    )
    print()


# ============================================================
#                         RUN
# ============================================================

if __name__ == "__main__":

    # Save vector version of the house
    create_house_svg()

    # Create the MP4 animation
    create_video()