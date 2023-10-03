#!/usr/bin/env python3
from typing import Tuple, List, Optional
from argparse import ArgumentParser
from os import get_terminal_size
from enum import Enum
from PIL import Image


ASCII = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
ASCII_SIMPLE = "@%#*+=-:. "


class Format(Enum):
    text = "text"

    def __str__(self):
        return self.value


def lerp(input_range: Tuple[int, int], out_range: Tuple[int, int], value: int):
    return out_range[0] + (value - input_range[0]) / (
        input_range[1] - input_range[0]
    ) * (out_range[1] - out_range[0])


def get_new_size(
    old_size: Optional[Tuple[int, int]] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    area: Optional[Tuple[int, int]] = None,
    prefer_area_width=True,
) -> Tuple[int, int]:
    """
    Gets new_size based on parameters
    note: old_size should be supplied unless both width and size are given
    """
    FONT_DIM = 2.25
    if width and height:
        return (width, height)
    if not old_size:
        raise Exception(
            "old_size not supplied to get_new_size when both width and height aren't given"
        )
    if width:
        return (width, int(width / old_size[0] * old_size[1] / FONT_DIM))
    if height:
        return (int(height / old_size[1] * old_size[0] * FONT_DIM), height)
    if area:
        if prefer_area_width:
            return get_new_size(old_size, width=area[0])
        return get_new_size(old_size, height=area[1])
    raise Exception("No argument given to get_new_size. Please supply width|height|area")


def img2ascii(
    img: Image.Image,
    charset: str,
    width: Optional[int],
    height: Optional[int],
    area: Optional[Tuple[int, int]],
) -> List[List[str]]:
    result = []
    size = get_new_size(img.size, width, height, area)
    sample_img = img.resize(size).convert("L")

    for i in range(size[1]):
        result.append([])
        for j in range(size[0]):
            pixel = sample_img.getpixel((j, i))
            char_idx = round(lerp((0, 255), (0, len(charset)), pixel))
            result[-1].append(charset[char_idx])
    return result


def ascii2output(ascii, format: Format):
    match format:
        case Format.text:
            return "\n".join(("".join(chars) for chars in ascii))

def run(args):
    charset = ASCII if args.detailed else ASCII_SIMPLE
    img = Image.open(args.filename)
    try:
        terminal_size = get_terminal_size()
    except:
        terminal_size = None
    ascii = img2ascii(img, charset, args.width, args.height, terminal_size)
    print(ascii2output(ascii, args.format))


if __name__ == "__main__":
    parser = ArgumentParser("asciifier")
    parser.add_argument("filename")
    parser.add_argument("-W", "--width", type=int)
    parser.add_argument("-H", "--height", type=int)
    parser.add_argument("-d", "--detailed", action="store_true")
    parser.add_argument(
        "-f", "--format", default="text", choices=list(Format), type=Format
    )

    args = parser.parse_args()
    run(args)
