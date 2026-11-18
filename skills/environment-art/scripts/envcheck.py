"""Measure and compare patches of a target picture and a game capture. Needs opencv-python and numpy.

  python -I envcheck.py measure "<label>=<image>:<x0>,<y0>,<x1>,<y1>" ...
  python -I envcheck.py pair <target.png> <capture.png> <out.png>
  python -I envcheck.py grid <image.png> <out.png> [--cols 6] [--rows 4]

`measure` prints one line a patch, so the same quantities can be read off the target and the game:

  lightness   mean lightness, 0 to 100
  spread      5th to 95th percentile of lightness after a small blur: how far the patch runs from
              dark to light once thin lines are smoothed out
  line        share of pixels clearly darker than their neighbourhood: how much of it is joint or crack
  saturation  95th percentile of chroma: the strongest colour in it
  evenness    variation of edge density over a 4 by 4 grid, as a share of its mean. Low means detail
              is spread evenly (a pattern, or scatter); high means clumps with rests between

The numbers are evidence for a person or a critic to read. A patch that contains a cast shadow, a
figure or lettering measures those too: choose patches of bare surface. No threshold lives here;
compare the game with the target, and with a build already known to be wrong.

`pair` sets the two pictures side by side at one height. `grid` lays a lettered grid (A1 to F4 by
default) over a copy, so a note can say where it means. Never score the gridded copy: marks on a
picture change how it is judged.
"""
import sys

import cv2
import numpy as np


def patch(spec):
    label, rest = spec.split('=', 1)
    path, box = rest.rsplit(':', 1)
    x0, y0, x1, y1 = map(int, box.split(','))
    image = cv2.imread(path)
    if image is None:
        sys.exit(f'cannot read {path}')
    return label, image[y0:y1, x0:x1]


def measure(specs):
    print(f'{"patch":28s} {"lightness":>9s} {"spread":>7s} {"line":>6s} {"saturation":>10s} {"evenness":>8s}')
    for spec in specs:
        label, bgr = patch(spec)
        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
        light = lab[:, :, 0] * 100 / 255
        chroma = np.hypot(lab[:, :, 1] - 128, lab[:, :, 2] - 128)
        smooth = cv2.GaussianBlur(light, (0, 0), 3)
        around = cv2.GaussianBlur(light, (0, 0), 14)
        edges = cv2.Canny(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY), 60, 140) > 0
        cells = [c.mean() for row in np.array_split(edges, 4, axis=0) for c in np.array_split(row, 4, axis=1)]
        evenness = np.std(cells) / (np.mean(cells) + 1e-6)
        print(f'{label:28s} {light.mean():9.1f} {np.percentile(smooth, 95) - np.percentile(smooth, 5):7.1f} '
              f'{(light < around - 5).mean() * 100:5.1f}% {np.percentile(chroma, 95):10.1f} {evenness:8.2f}')


def pair(target, capture, out):
    a, b = cv2.imread(target), cv2.imread(capture)
    if a is None or b is None:
        sys.exit('cannot read one of the pictures')
    height = min(a.shape[0], b.shape[0], 900)
    fit = lambda im: cv2.resize(im, (round(im.shape[1] * height / im.shape[0]), height), interpolation=cv2.INTER_AREA)
    cv2.imwrite(out, np.hstack([fit(a), np.full((height, 12, 3), 20, np.uint8), fit(b)]))
    print(f'wrote {out}: target on the left, capture on the right')


def grid(path, out, cols=6, rows=4):
    image = cv2.imread(path)
    if image is None:
        sys.exit(f'cannot read {path}')
    h, w = image.shape[:2]
    for c in range(cols):
        for r in range(rows):
            x, y = round(c * w / cols), round(r * h / rows)
            cv2.rectangle(image, (x, y), (round((c + 1) * w / cols), round((r + 1) * h / rows)), (255, 255, 255), 1)
            cv2.putText(image, f'{chr(65 + c)}{r + 1}', (x + 6, y + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)
            cv2.putText(image, f'{chr(65 + c)}{r + 1}', (x + 6, y + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.imwrite(out, image)
    print(f'wrote {out}: cells A1 to {chr(64 + cols)}{rows}, for locating notes only')


if __name__ == '__main__':
    args = sys.argv[1:]
    option = lambda name, default: int(args[args.index(name) + 1]) if name in args else default
    if len(args) >= 2 and args[0] == 'measure':
        measure(args[1:])
    elif len(args) == 4 and args[0] == 'pair':
        pair(*args[1:])
    elif len(args) >= 3 and args[0] == 'grid':
        grid(args[1], args[2], option('--cols', 6), option('--rows', 4))
    else:
        sys.exit(__doc__)
