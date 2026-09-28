"""Basketball strikes the man's hat brim and rebounds to the right."""

from pathlib import Path
import math

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
IMAGE_FILE = ROOT / "assets" / "garden_man.png"
OUTPUT_DIR = ROOT / "output"

SIZE = 768
SOURCE_SIZE = 1254
FPS = 60
DURATION = 5.0

# Coordinates on the original garden picture.
GROUND_Y = 1193
RADIUS = 39

START = (1120, 95)                  # Upper-right quadrant
HAT_CONTACT = (825, 180)            # Right edge of the hat
END = (1110, GROUND_Y - RADIUS)      # Lower-right quadrant

APPROACH_CONTROL = (940, 75)
REBOUND_CONTROL = (1190, 275)

HAT_CONTACT_TIME = 2.0
ARRIVAL_TIME = 4.65


def curve(start, control, end, progress):
    remaining = 1 - progress

    x = (
        remaining**2 * start[0]
        + 2 * remaining * progress * control[0]
        + progress**2 * end[0]
    )
    y = (
        remaining**2 * start[1]
        + 2 * remaining * progress * control[1]
        + progress**2 * end[1]
    )

    return x, y


def motion(t):
    """Approach the hat, rebound right, then land on the grass."""

    if t < HAT_CONTACT_TIME:
        progress = t / HAT_CONTACT_TIME
        x, y = curve(
            START,
            APPROACH_CONTROL,
            HAT_CONTACT,
            progress,
        )

    elif t < ARRIVAL_TIME:
        progress = (
            (t - HAT_CONTACT_TIME)
            / (ARRIVAL_TIME - HAT_CONTACT_TIME)
        )
        x, y = curve(
            HAT_CONTACT,
            REBOUND_CONTROL,
            END,
            progress,
        )

    else:
        x, y = END

    height_above_ground = max(
        0,
        GROUND_Y - RADIUS - y,
    )

    return x, y, height_above_ground


def basketball_sprite(radius, angle_degrees):
    """Draw an orange basketball with curved black seams."""

    supersample = 3
    padding = 4
    side = round((2 * radius + 2 * padding) * supersample)

    center = side / 2
    r = radius * supersample

    ball = Image.new("RGBA", (side, side))

    # Circular mask.
    mask = Image.new("L", (side, side))
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse(
        (center - r, center - r, center + r, center + r),
        fill=255,
    )

    # Orange color with a darker underside.
    orange = Image.new("RGBA", (side, side), (222, 69, 22, 255))
    shading = Image.new("RGBA", (side, side))
    shading_draw = ImageDraw.Draw(shading)

    shading_draw.ellipse(
        (
            center - 1.2 * r,
            center + 0.10 * r,
            center + 1.2 * r,
            center + 1.50 * r,
        ),
        fill=(104, 36, 20, 75),
    )

    orange.alpha_composite(shading)
    ball.paste(orange, (0, 0), mask)

    # Basketball seams.
    seams = Image.new("RGBA", (side, side))
    pen = ImageDraw.Draw(seams)
    line_width = max(2, round(2.8 * supersample))

    def draw_seam(start, control, end):
        points = []

        for n in range(41):
            progress = n / 40
            remaining = 1 - progress

            px = (
                remaining**2 * start[0]
                + 2 * remaining * progress * control[0]
                + progress**2 * end[0]
            )
            py = (
                remaining**2 * start[1]
                + 2 * remaining * progress * control[1]
                + progress**2 * end[1]
            )

            points.append(
                (center + px * r, center + py * r)
            )

        pen.line(
            points,
            fill=(34, 22, 17, 255),
            width=line_width,
            joint="curve",
        )

    draw_seam(
        (-1.00, -0.07),
        (-0.02, -0.67),
        (1.00, -0.12),
    )
    draw_seam(
        (-0.34, -1.00),
        (0.93, -0.18),
        (0.11, 1.00),
    )
    draw_seam(
        (-1.00, 0.52),
        (0.25, 0.88),
        (0.52, -0.25),
    )
    draw_seam(
        (-0.90, -0.55),
        (0.05, -1.05),
        (0.35, -0.88),
    )

    # Keep the seams inside the ball.
    seam_alpha = np.asarray(seams.getchannel("A"))
    mask_alpha = np.asarray(mask)

    seams.putalpha(
        Image.fromarray(
            np.minimum(seam_alpha, mask_alpha)
        )
    )

    ball.alpha_composite(seams)

    # Outer black outline.
    outline = ImageDraw.Draw(ball)
    outline.ellipse(
        (center - r, center - r, center + r, center + r),
        outline=(32, 20, 15, 255),
        width=line_width,
    )

    # Rotate the basketball during flight.
    ball = ball.rotate(
        angle_degrees,
        Image.Resampling.BICUBIC,
    )

    final_side = round(side / supersample)
    return ball.resize(
        (final_side, final_side),
        Image.Resampling.LANCZOS,
    )


def draw_ball_and_shadow(frame, x, y, height, t):
    scale = SIZE / SOURCE_SIZE

    x *= scale
    y *= scale
    ground = GROUND_Y * scale
    radius = RADIUS * scale

    # Ground shadow appears when the ball gets close to the grass.
    if height < 300:
        shadow = Image.new("RGBA", (SIZE, SIZE))
        shadow_draw = ImageDraw.Draw(shadow)

        spread = radius * (1 + height / 350)
        opacity = round(85 * (1 - height / 300))

        shadow_draw.ellipse(
            (
                x - spread,
                ground - 5 * scale,
                x + spread,
                ground + 5 * scale,
            ),
            fill=(44, 39, 30, opacity),
        )

        frame.alpha_composite(shadow)

    # Brief compression at the hat contact and landing.
    distance_to_impact = min(
        abs(t - HAT_CONTACT_TIME),
        abs(t - ARRIVAL_TIME),
    )
    squash = max(
        0,
        1 - distance_to_impact / 0.085,
    ) * 0.13

    angle = -math.degrees(t * 1.5)
    sprite = basketball_sprite(radius, angle)
    width, sprite_height = sprite.size

    if squash:
        sprite = sprite.resize(
            (
                round(width * (1 + squash)),
                round(sprite_height * (1 - squash)),
            ),
            Image.Resampling.BICUBIC,
        )
        width, sprite_height = sprite.size

    frame.alpha_composite(
        sprite,
        (
            round(x - width / 2),
            round(y + radius * squash - sprite_height / 2),
        ),
    )


def next_output():
    OUTPUT_DIR.mkdir(exist_ok=True)

    number = 1
    while (OUTPUT_DIR / f"garden_ball_{number}.mp4").exists():
        number += 1

    return OUTPUT_DIR / f"garden_ball_{number}.mp4"


def main():
    if not IMAGE_FILE.is_file():
        raise FileNotFoundError(
            f"Put the garden image here: {IMAGE_FILE}"
        )

    background = Image.open(IMAGE_FILE).convert("RGBA")
    background = background.resize(
        (SIZE, SIZE),
        Image.Resampling.LANCZOS,
    )

    destination = next_output()

    with imageio.get_writer(
        str(destination),
        fps=FPS,
        codec="libx264",
        quality=8,
        macro_block_size=1,
        pixelformat="yuv420p",
    ) as video:

        for frame_number in range(round(DURATION * FPS)):
            t = frame_number / FPS
            frame = background.copy()

            x, y, height = motion(t)
            draw_ball_and_shadow(frame, x, y, height, t)

            video.append_data(
                np.asarray(frame.convert("RGB"))
            )

    print(f"Saved: {destination}")


if __name__ == "__main__":
    main()