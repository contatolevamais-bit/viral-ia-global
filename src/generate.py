#!/usr/bin/env python3
"""VIRAL IA GLOBAL v1.1: cria vídeos verticais para revisão humana.
Uso: python src/generate.py --date 2026-11-07 --count 3 --out output
Não publica automaticamente nas redes sociais.
"""
import argparse
import datetime as dt
import json
import math
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 720, 1280
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def run(command):
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(
            f"Comando falhou (código {result.returncode}): {' '.join(map(str, command))}\n"
            f"{result.stderr[-3500:]}"
        )
    return result.stdout


def audio_duration(path):
    output = run([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', str(path)
    ])
    return float(output.strip())


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, chosen_font, max_width):
    rows, current = [], ''
    for word in text.split():
        proposed = f'{current} {word}'.strip()
        if current and draw.textbbox((0, 0), proposed, font=chosen_font)[2] > max_width:
            rows.append(current)
            current = word
        else:
            current = proposed
    if current:
        rows.append(current)
    return rows


def render_scene(path, title, narration, scene, number):
    """Arte original simples com composição, não material externo sem licença."""
    rng = random.Random(number * 31 + scene * 71)
    colors = [(11, 23, 49), (15, 32, 54), (31, 22, 57),
              (14, 47, 55), (37, 25, 48)]
    picture = Image.new('RGB', (WIDTH, HEIGHT), colors[scene])
    draw = ImageDraw.Draw(picture)
    for _ in range(90):
        x, y = rng.randrange(WIDTH), rng.randrange(HEIGHT)
        radius = rng.randrange(1, 4)
        color = (70 + rng.randrange(55), 96 + rng.randrange(80),
                 145 + rng.randrange(80))
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)
    draw.ellipse((75, 145, 645, 715), outline=(63, 181, 191), width=3)
    draw.ellipse((138, 208, 582, 652), outline=(35, 103, 151), width=2)
    for idx in range(9):
        angle = idx * math.tau / 9 + scene
        x = int(360 + 250 * math.cos(angle))
        y = int(431 + 250 * math.sin(angle))
        draw.ellipse((x-6, y-6, x+6, y+6), fill=(111, 231, 213))
    draw.rounded_rectangle((48, 70, 672, 135), radius=22, fill=(18, 69, 82))
    draw.text((72, 88), 'VIRAL IA GLOBAL  •  CIÊNCIA',
              font=font(BOLD, 24), fill=(176, 249, 233))
    y = 765
    heading_font = font(BOLD, 49)
    for row in wrap(draw, title, heading_font, 605)[:4]:
        draw.text((56, y), row, font=heading_font, fill=(255, 255, 255))
        y += 62
    draw.rounded_rectangle((51, y+10, 669, y+15), radius=2,
                           fill=(64, 211, 189))
    y += 55
    body_font = font(FONT, 29)
    for row in wrap(draw, narration, body_font, 600)[:6]:
