from PIL import Image, ImageDraw
import imageio.v2 as imageio
import numpy as np
import math
import os

from rlottie_python import LottieAnimation


# ============================================================
#                     EXPERIMENT SETTINGS
# ============================================================


# ------------------------------------------------------------
# VIDEO SIZE
# ------------------------------------------------------------

WIDTH = 768
HEIGHT = 768


# ------------------------------------------------------------
# VIDEO FRAME RATE
# ------------------------------------------------------------
#
# 60 FPS:
#
# 1 second = 60 video frames
# 5 seconds = 300 video frames
#
# Each video frame lasts approximately 16.67 ms.
#

FPS = 60


# ------------------------------------------------------------
# TOTAL VIDEO LENGTH
# ------------------------------------------------------------

VIDEO_DURATION = 5.0


# ------------------------------------------------------------
# FINAL TIME
# ------------------------------------------------------------
#
# Butterfly should be completely inside the chimney
# at this time.
#

FINAL_TIME = 5.0


# ------------------------------------------------------------
# CHIMNEY ENTRY DURATION
# ------------------------------------------------------------
#
# Last 0.30 seconds:
#
# 4.70 s -> butterfly reaches chimney
# 4.70 - 5.00 s -> butterfly enters chimney
# 5.00 s -> completely hidden
#

ENTRY_DURATION = 0.30

FLIGHT_END_TIME = (
    FINAL_TIME - ENTRY_DURATION
)


# ------------------------------------------------------------
# BUTTERFLY STARTING POSITION
# ------------------------------------------------------------

START_X = 110
START_Y = 520


# ------------------------------------------------------------
# CHIMNEY POSITION
# ------------------------------------------------------------

CHIMNEY_CENTER_X = 520

# Butterfly approaches slightly above chimney opening
APPROACH_Y = 75

# Butterfly travels downward to here while entering
INSIDE_CHIMNEY_Y = 150


# ============================================================
#                   LOTTIE BUTTERFLY
# ============================================================


# ------------------------------------------------------------
# LOTTIE FILE
# ------------------------------------------------------------
#
# Your current folder:
#
# BUTTERFLY/
#
#     butterfly.py
#     Butterfly Lottie Animation.json
#
#     assets/
#     output/
#
# Therefore we load the JSON directly from the project folder.
#

LOTTIE_FILE = "Butterfly Lottie Animation.json"


# ------------------------------------------------------------
# BUTTERFLY SIZE
# ------------------------------------------------------------
#
# Increase if butterfly appears too small.
# Decrease if it appears too large.
#

BUTTERFLY_SIZE = 100


# ------------------------------------------------------------
# LOTTIE PLAYBACK SPEED
# ------------------------------------------------------------
#
# Your JSON says:
#
# original frame rate = 30 FPS
# frames = 0 -> 120
# total original duration = 4 seconds
#
# From the wing keyframes, approximately one full wing
# movement occurs every 20 original frames.
#
# 20 / 30 = 0.667 seconds
#
# approximately:
#
# 1.5 wing cycles per second
#
#
# LOTTIE_SPEED = 1.0
# -> original animation speed
# -> approximately 1.5 Hz
#
# LOTTIE_SPEED = 0.5
# -> approximately 0.75 Hz
#
# LOTTIE_SPEED = 2.0
# -> approximately 3 Hz
#

LOTTIE_SPEED = 1.0


# ------------------------------------------------------------
# WHOLE-BUTTERFLY VERTICAL MOVEMENT
# ------------------------------------------------------------
#
# IMPORTANT:
#
# This is DIFFERENT from the Lottie wing animation.
#
# The Lottie controls the wings.
#
# This controls the gentle up/down movement of the
# entire butterfly while it flies.
#

FLUTTER_AMOUNT = 7

FLUTTER_FREQUENCY = 0.8


# ============================================================
#                         FOLDERS
# ============================================================

ASSETS_FOLDER = "assets"

OUTPUT_FOLDER = "output"


os.makedirs(
    ASSETS_FOLDER,
    exist_ok=True
)

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


# ============================================================
#                AUTOMATIC VIDEO NUMBERING
# ============================================================
#
# Creates:
#
# lottie_animation_1.mp4
# lottie_animation_2.mp4
# lottie_animation_3.mp4
#
# Previous videos are NOT overwritten.
#

def get_next_output_filename():

    number = 1

    while True:

        filename = os.path.join(
            OUTPUT_FOLDER,
            f"lottie_animation_{number}.mp4"
        )

        if not os.path.exists(filename):

            return filename

        number += 1


# ============================================================
#                     HOUSE COLOURS
# ============================================================

BACKGROUND_COLOR = (
    248,
    245,
    237
)

OUTLINE = (
    72,
    43,
    34
)

ROOF = (
    238,
    124,
    100
)

ROOF_LIGHT = (
    249,
    148,
    120
)

ROOF_DETAIL = (
    177,
    82,
    67
)

WALL = (
    255,
    253,
    247
)

WINDOW = (
    218,
    238,
    240
)

CHIMNEY_DARK = (
    38,
    28,
    24
)


# ============================================================
#                   CREATE HOUSE SVG
# ============================================================

def create_house_svg():

    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg"
     width="{WIDTH}"
     height="{HEIGHT}"
     viewBox="0 0 {WIDTH} {HEIGHT}">

    <rect
        width="{WIDTH}"
        height="{HEIGHT}"
        fill="#f8f5ed"
    />

    <!-- HOUSE BODY -->

    <rect
        x="145"
        y="350"
        width="475"
        height="220"
        rx="8"
        fill="#fffdf7"
        stroke="#482b22"
        stroke-width="8"
    />


    <!-- MAIN ROOF -->

    <path
        d="
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
        stroke-linejoin="round"
    />


    <!-- DORMER WALL -->

    <path
        d="
        M 286 285
        L 277 208
        L 365 138
        L 454 210
        L 445 285
        Z"
        fill="#fffdf7"
        stroke="#482b22"
        stroke-width="8"
    />


    <!-- DORMER ROOF -->

    <path
        d="
        M 267 210
        L 365 116
        L 470 214"
        fill="none"
        stroke="#482b22"
        stroke-width="16"
        stroke-linecap="round"
        stroke-linejoin="round"
    />

    <path
        d="
        M 273 207
        L 365 128
        L 463 210"
        fill="none"
        stroke="#f99478"
        stroke-width="8"
        stroke-linecap="round"
        stroke-linejoin="round"
    />


    <!-- ATTIC WINDOW -->

    <circle
        cx="365"
        cy="218"
        r="25"
        fill="#daeef0"
        stroke="#482b22"
        stroke-width="7"
    />

    <line
        x1="340"
        y1="218"
        x2="390"
        y2="218"
        stroke="#482b22"
        stroke-width="6"
    />

    <line
        x1="365"
        y1="193"
        x2="365"
        y2="243"
        stroke="#482b22"
        stroke-width="6"
    />


    <!-- CHIMNEY -->

    <rect
        x="480"
        y="100"
        width="80"
        height="102"
        rx="3"
        fill="#fffdf7"
        stroke="#482b22"
        stroke-width="8"
    />

    <rect
        x="488"
        y="107"
        width="64"
        height="31"
        rx="5"
        fill="#261c18"
    />

    <rect
        x="468"
        y="86"
        width="104"
        height="31"
        rx="13"
        fill="#ee7c64"
        stroke="#482b22"
        stroke-width="8"
    />


    <!-- LEFT WINDOW -->

    <path
        d="
        M 180 492
        L 180 430
        Q 180 390 230 390
        Q 280 390 280 430
        L 280 492
        Z"
        fill="#daeef0"
        stroke="#482b22"
        stroke-width="8"
    />


    <!-- RIGHT WINDOW -->

    <path
        d="
        M 485 492
        L 485 430
        Q 485 390 535 390
        Q 585 390 585 430
        L 585 492
        Z"
        fill="#daeef0"
        stroke="#482b22"
        stroke-width="8"
    />


    <!-- DOOR -->

    <path
        d="
        M 320 570
        L 320 440
        Q 320 388 375 388
        Q 430 388 430 440
        L 430 570
        Z"
        fill="#fffdf7"
        stroke="#482b22"
        stroke-width="8"
    />


    <!-- STEPS -->

    <rect
        x="315"
        y="560"
        width="125"
        height="25"
        rx="10"
        fill="#fffdf7"
        stroke="#482b22"
        stroke-width="7"
    />

    <rect
        x="295"
        y="585"
        width="165"
        height="27"
        rx="10"
        fill="#fffdf7"
        stroke="#482b22"
        stroke-width="7"
    />

    <rect
        x="270"
        y="612"
        width="215"
        height="31"
        rx="12"
        fill="#fffdf7"
        stroke="#482b22"
        stroke-width="7"
    />

</svg>
"""

    path = os.path.join(
        ASSETS_FOLDER,
        "house.svg"
    )

    with open(
        path,
        "w"
    ) as file:

        file.write(svg)

    print(
        "House SVG created:",
        path
    )


# ============================================================
#                    DRAW HOUSE
# ============================================================

def draw_house():

    image = Image.new(
        "RGB",
        (
            WIDTH,
            HEIGHT
        ),
        BACKGROUND_COLOR
    )

    draw = ImageDraw.Draw(
        image
    )


    # --------------------------------------------------------
    # HOUSE BODY
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (
            145,
            350,
            620,
            570
        ),
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
        roof_points + [
            (95, 350)
        ],
        fill=OUTLINE,
        width=9,
        joint="curve"
    )


    # --------------------------------------------------------
    # ROOF TILE DETAILS
    # --------------------------------------------------------

    for (
        y,
        start_x,
        end_x
    ) in [

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
        dormer + [
            dormer[0]
        ],
        fill=OUTLINE,
        width=8,
        joint="curve"
    )


    # Dark dormer roof

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


    # Inner dormer roof

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
        (
            340,
            193,
            390,
            243
        ),
        fill=WINDOW,
        outline=OUTLINE,
        width=7
    )

    draw.line(
        (
            365,
            194,
            365,
            242
        ),
        fill=OUTLINE,
        width=6
    )

    draw.line(
        (
            341,
            218,
            389,
            218
        ),
        fill=OUTLINE,
        width=6
    )


    # --------------------------------------------------------
    # WINDOWS
    # --------------------------------------------------------

    for x in [
        180,
        485
    ]:

        draw.rounded_rectangle(
            (
                x,
                390,
                x + 100,
                495
            ),
            radius=40,
            fill=WINDOW,
            outline=OUTLINE,
            width=8
        )

        draw.line(
            (
                x + 50,
                392,
                x + 50,
                492
            ),
            fill=OUTLINE,
            width=6
        )

        draw.line(
            (
                x + 3,
                447,
                x + 97,
                447
            ),
            fill=OUTLINE,
            width=6
        )

        draw.rounded_rectangle(
            (
                x - 12,
                487,
                x + 112,
                507
            ),
            radius=8,
            fill=WALL,
            outline=OUTLINE,
            width=7
        )


    # --------------------------------------------------------
    # DOOR
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (
            320,
            388,
            430,
            570
        ),
        radius=48,
        fill=WALL,
        outline=OUTLINE,
        width=8
    )

    draw.ellipse(
        (
            337,
            462,
            353,
            478
        ),
        fill=OUTLINE
    )


    # --------------------------------------------------------
    # STAIRS
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (
            315,
            560,
            440,
            585
        ),
        radius=10,
        fill=WALL,
        outline=OUTLINE,
        width=7
    )

    draw.rounded_rectangle(
        (
            295,
            585,
            460,
            612
        ),
        radius=10,
        fill=WALL,
        outline=OUTLINE,
        width=7
    )

    draw.rounded_rectangle(
        (
            270,
            612,
            485,
            643
        ),
        radius=12,
        fill=WALL,
        outline=OUTLINE,
        width=7
    )


    # --------------------------------------------------------
    # CHIMNEY BODY
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (
            480,
            100,
            560,
            202
        ),
        radius=3,
        fill=WALL,
        outline=OUTLINE,
        width=8
    )


    # Brick details

    draw.line(
        (
            480,
            150,
            560,
            150
        ),
        fill=OUTLINE,
        width=5
    )

    draw.line(
        (
            520,
            150,
            520,
            200
        ),
        fill=OUTLINE,
        width=5
    )

    draw.line(
        (
            505,
            102,
            505,
            150
        ),
        fill=OUTLINE,
        width=5
    )

    draw.line(
        (
            545,
            102,
            545,
            150
        ),
        fill=OUTLINE,
        width=5
    )


    # Dark chimney opening

    draw.rounded_rectangle(
        (
            488,
            107,
            552,
            138
        ),
        radius=5,
        fill=CHIMNEY_DARK
    )


    # Chimney cap

    draw.rounded_rectangle(
        (
            468,
            86,
            572,
            117
        ),
        radius=13,
        fill=ROOF,
        outline=OUTLINE,
        width=8
    )


    return image


# ============================================================
#                     SMOOTH MOVEMENT
# ============================================================

def smoothstep(t):

    t = max(
        0.0,
        min(
            1.0,
            t
        )
    )

    return (
        t
        * t
        * (
            3
            - 2 * t
        )
    )


# ============================================================
#                 BUTTERFLY FLIGHT POSITION
# ============================================================

def get_flight_position(
    current_time
):

    progress = (
        current_time
        / FLIGHT_END_TIME
    )

    progress = max(
        0.0,
        min(
            1.0,
            progress
        )
    )


    smooth = smoothstep(
        progress
    )


    # --------------------------------------------------------
    # BASIC MOVEMENT
    # --------------------------------------------------------

    x = (
        START_X
        + (
            CHIMNEY_CENTER_X
            - START_X
        )
        * smooth
    )

    y = (
        START_Y
        + (
            APPROACH_Y
            - START_Y
        )
        * smooth
    )


    # --------------------------------------------------------
    # CURVED TRAJECTORY
    # --------------------------------------------------------

    arc = (
        -80
        * math.sin(
            math.pi
            * progress
        )
    )

    y += arc


    # --------------------------------------------------------
    # SMALL WHOLE-BUTTERFLY FLUTTER
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


    return (
        x,
        y
    )


# ============================================================
#                 BUTTERFLY ENTRY POSITION
# ============================================================

def get_entry_position(
    current_time
):

    entry_time = (
        current_time
        - FLIGHT_END_TIME
    )

    progress = (
        entry_time
        / ENTRY_DURATION
    )

    progress = max(
        0.0,
        min(
            1.0,
            progress
        )
    )

    smooth = smoothstep(
        progress
    )


    x = CHIMNEY_CENTER_X


    y = (
        APPROACH_Y
        + (
            INSIDE_CHIMNEY_Y
            - APPROACH_Y
        )
        * smooth
    )


    return (
        x,
        y,
        progress
    )


# ============================================================
#                  DRAW LOTTIE BUTTERFLY
# ============================================================
#
# This replaces the old Pillow butterfly completely.
#
# Python controls:
#
# - trajectory
# - X position
# - Y position
# - total timing
# - entry into chimney
# - butterfly size
#
# Lottie controls:
#
# - butterfly appearance
# - wing movement
#

def draw_lottie_butterfly(
    image,
    lottie_animation,
    x,
    y,
    current_time,
    scale=1.0
):


    # --------------------------------------------------------
    # GET LOTTIE INFORMATION
    # --------------------------------------------------------

    total_lottie_frames = (
        lottie_animation
        .lottie_animation_get_totalframe()
    )

    lottie_fps = (
        lottie_animation
        .lottie_animation_get_framerate()
    )


    # --------------------------------------------------------
    # SELECT LOTTIE FRAME
    # --------------------------------------------------------
    #
    # Example:
    #
    # current_time = 1 second
    #
    # Original Lottie = 30 FPS
    #
    # 1 * 30 = Lottie frame 30
    #
    # LOTTIE_SPEED can modify this.
    #

    lottie_frame = int(
        current_time
        * lottie_fps
        * LOTTIE_SPEED
    )


    # --------------------------------------------------------
    # LOOP THE ANIMATION
    # --------------------------------------------------------

    lottie_frame = (
        lottie_frame
        % total_lottie_frames
    )


    # --------------------------------------------------------
    # RENDER SELECTED LOTTIE FRAME
    # --------------------------------------------------------

    butterfly = (
        lottie_animation
        .render_pillow_frame(
            frame_num=lottie_frame
        )
    )


    butterfly = butterfly.convert(
        "RGBA"
    )


    # --------------------------------------------------------
    # REMOVE TRANSPARENT EMPTY SPACE
    # --------------------------------------------------------
    #
    # Lottie canvas = 500 x 500.
    #
    # The actual butterfly doesn't occupy the full canvas.
    #
    # Cropping prevents the butterfly from becoming tiny.
    #

    bbox = butterfly.getbbox()

    if bbox is not None:

        butterfly = butterfly.crop(
            bbox
        )


    # --------------------------------------------------------
    # GET CURRENT SIZE
    # --------------------------------------------------------

    original_width = (
        butterfly.width
    )

    original_height = (
        butterfly.height
    )


    # --------------------------------------------------------
    # DETERMINE NEW SIZE
    # --------------------------------------------------------

    desired_width = max(
        1,
        int(
            BUTTERFLY_SIZE
            * scale
        )
    )


    aspect_ratio = (
        original_height
        / original_width
    )


    desired_height = max(
        1,
        int(
            desired_width
            * aspect_ratio
        )
    )


    # --------------------------------------------------------
    # RESIZE
    # --------------------------------------------------------

    butterfly = butterfly.resize(
        (
            desired_width,
            desired_height
        ),
        Image.Resampling.LANCZOS
    )


    # --------------------------------------------------------
    # CENTER BUTTERFLY ON X,Y
    # --------------------------------------------------------

    paste_x = int(
        x
        - desired_width / 2
    )

    paste_y = int(
        y
        - desired_height / 2
    )


    # --------------------------------------------------------
    # PLACE LOTTIE ON VIDEO FRAME
    # --------------------------------------------------------

    image.paste(
        butterfly,
        (
            paste_x,
            paste_y
        ),
        butterfly
    )


# ============================================================
#          DRAW CHIMNEY IN FRONT OF BUTTERFLY
# ============================================================
#
# Drawing order:
#
# 1. House
# 2. Lottie butterfly
# 3. Chimney foreground
#
# Therefore the butterfly can disappear behind the chimney.
#

def draw_chimney_foreground(
    image
):

    draw = ImageDraw.Draw(
        image
    )


    # --------------------------------------------------------
    # FRONT CHIMNEY BODY
    # --------------------------------------------------------

    draw.line(
        (
            480,
            137,
            480,
            202
        ),
        fill=OUTLINE,
        width=8
    )

    draw.line(
        (
            560,
            137,
            560,
            202
        ),
        fill=OUTLINE,
        width=8
    )


    # --------------------------------------------------------
    # FRONT FACE BELOW OPENING
    # --------------------------------------------------------

    draw.rectangle(
        (
            484,
            138,
            556,
            198
        ),
        fill=WALL
    )


    # --------------------------------------------------------
    # RESTORE BRICK DETAILS
    # --------------------------------------------------------

    draw.line(
        (
            484,
            150,
            556,
            150
        ),
        fill=OUTLINE,
        width=5
    )

    draw.line(
        (
            520,
            150,
            520,
            198
        ),
        fill=OUTLINE,
        width=5
    )


    # --------------------------------------------------------
    # RESTORE OUTSIDE EDGES
    # --------------------------------------------------------

    draw.line(
        (
            480,
            137,
            480,
            202
        ),
        fill=OUTLINE,
        width=8
    )

    draw.line(
        (
            560,
            137,
            560,
            202
        ),
        fill=OUTLINE,
        width=8
    )


    # --------------------------------------------------------
    # CHIMNEY CAP
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (
            468,
            86,
            572,
            117
        ),
        radius=13,
        fill=ROOF,
        outline=OUTLINE,
        width=8
    )


# ============================================================
#                       CREATE VIDEO
# ============================================================

def create_video():


    # --------------------------------------------------------
    # CHECK LOTTIE FILE EXISTS
    # --------------------------------------------------------

    if not os.path.exists(
        LOTTIE_FILE
    ):

        raise FileNotFoundError(
            "\n\n"
            "Lottie JSON file was not found.\n"
            "\n"
            f"Expected file:\n{LOTTIE_FILE}\n"
            "\n"
            "Make sure it is beside butterfly.py."
        )


    # --------------------------------------------------------
    # LOAD LOTTIE
    # --------------------------------------------------------

    print()

    print(
        "Loading Lottie butterfly..."
    )


    lottie_animation = (
        LottieAnimation.from_file(
            LOTTIE_FILE
        )
    )


    # --------------------------------------------------------
    # READ LOTTIE INFORMATION
    # --------------------------------------------------------

    lottie_frames = (
        lottie_animation
        .lottie_animation_get_totalframe()
    )

    lottie_fps = (
        lottie_animation
        .lottie_animation_get_framerate()
    )

    lottie_duration = (
        lottie_animation
        .lottie_animation_get_duration()
    )


    # --------------------------------------------------------
    # OUTPUT FILENAME
    # --------------------------------------------------------

    output_filename = (
        get_next_output_filename()
    )


    # --------------------------------------------------------
    # VIDEO FRAME COUNTS
    # --------------------------------------------------------

    total_frames = round(
        VIDEO_DURATION
        * FPS
    )

    final_frame = round(
        FINAL_TIME
        * FPS
    )

    flight_end_frame = round(
        FLIGHT_END_TIME
        * FPS
    )


    # --------------------------------------------------------
    # SHOW SETTINGS
    # --------------------------------------------------------

    print()

    print(
        "========================================"
    )

    print(
        "LOTTIE BUTTERFLY VIDEO"
    )

    print(
        "========================================"
    )


    print(
        "Video resolution:",
        WIDTH,
        "x",
        HEIGHT
    )


    print(
        "Video frame rate:",
        FPS,
        "FPS"
    )


    print(
        "Video duration:",
        VIDEO_DURATION,
        "seconds"
    )


    print()


    print(
        "Lottie file:",
        LOTTIE_FILE
    )


    print(
        "Original Lottie FPS:",
        lottie_fps
    )


    print(
        "Original Lottie frames:",
        lottie_frames
    )


    print(
        "Original Lottie duration:",
        lottie_duration,
        "seconds"
    )


    print(
        "Lottie playback speed:",
        LOTTIE_SPEED
    )


    print(
        "Approximate wing frequency:",
        round(
            1.5
            * LOTTIE_SPEED,
            2
        ),
        "Hz"
    )


    print()


    print(
        "Whole-body flutter frequency:",
        FLUTTER_FREQUENCY,
        "Hz"
    )


    print()


    print(
        "Flight reaches chimney:",
        FLIGHT_END_TIME,
        "seconds"
    )


    print(
        "Flight-end video frame:",
        flight_end_frame
    )


    print(
        "Fully inside chimney:",
        FINAL_TIME,
        "seconds"
    )


    print(
        "Final video frame:",
        final_frame
    )


    print(
        "========================================"
    )

    print()


    # --------------------------------------------------------
    # VIDEO WRITER
    # --------------------------------------------------------

    writer = imageio.get_writer(
        output_filename,
        fps=FPS,
        codec="libx264",
        quality=8,
        macro_block_size=None
    )


    # ========================================================
    #                  GENERATE VIDEO
    # ========================================================

    for frame_number in range(
        total_frames
    ):


        # ----------------------------------------------------
        # VIDEO TIME
        # ----------------------------------------------------

        current_time = (
            frame_number
            / FPS
        )


        # ----------------------------------------------------
        # CLEAN BACKGROUND
        # ----------------------------------------------------

        frame = draw_house()


        # ====================================================
        # PHASE 1
        #
        # BUTTERFLY FLIES TOWARD CHIMNEY
        # ====================================================

        if (
            current_time
            < FLIGHT_END_TIME
        ):

            x, y = (
                get_flight_position(
                    current_time
                )
            )


            draw_lottie_butterfly(
                frame,
                lottie_animation,
                x,
                y,
                current_time,
                scale=1.0
            )


        # ====================================================
        # PHASE 2
        #
        # BUTTERFLY ENTERS CHIMNEY
        # ====================================================

        elif (
            current_time
            < FINAL_TIME
        ):

            (
                x,
                y,
                entry_progress
            ) = (
                get_entry_position(
                    current_time
                )
            )


            # Butterfly becomes slightly smaller
            # while entering chimney.

            scale = (
                1.0
                - 0.30
                * entry_progress
            )


            draw_lottie_butterfly(
                frame,
                lottie_animation,
                x,
                y,
                current_time,
                scale=scale
            )


        # ====================================================
        # PHASE 3
        #
        # BUTTERFLY COMPLETELY HIDDEN
        # ====================================================

        else:

            pass


        # ----------------------------------------------------
        # CHIMNEY FOREGROUND
        # ----------------------------------------------------

        draw_chimney_foreground(
            frame
        )


        # ----------------------------------------------------
        # ADD FRAME TO VIDEO
        # ----------------------------------------------------

        writer.append_data(
            np.array(
                frame
            )
        )


    # --------------------------------------------------------
    # FINISH VIDEO
    # --------------------------------------------------------

    writer.close()


    print()

    print(
        "DONE!"
    )

    print()

    print(
        "Created:",
        output_filename
    )

    print()


# ============================================================
#                          RUN
# ============================================================

if __name__ == "__main__":

    # Create/update SVG version of house
    create_house_svg()

    # Create Lottie butterfly video
    create_video()