#!/usr/bin/env python3
"""
Mockup de estilo visual para "AgentIA - EP01" (guion YouTube).

Genera un video corto (~60-90s) que muestra el ESTILO propuesto:
- Intro tipo "typewriter" sobre fondo negro
- Slides de narración con voz en off placeholder (TTS robótico, NO es la voz final)
- Tarjeta de título/logo
- Mockup de la interfaz de AgentIA simulando la demo (Parte 3 del guion)

No usa ningún asset real de AgentIA: la interfaz es una maqueta (mockup) dibujada
con formas simples, pensada solo para validar ritmo, tipografía y composición.
"""

import os
import shutil
import subprocess
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
FPS = 24

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ROOT, "build")
FRAMES = os.path.join(BUILD, "frames")
SCENES = os.path.join(BUILD, "scenes")
AUDIO = os.path.join(BUILD, "audio")

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

BG_BLACK = (8, 8, 10)
BG_NAVY = (12, 16, 28)
FG_WHITE = (240, 240, 245)
ACCENT = (90, 170, 255)
YELLOW = (255, 210, 90)
GREY = (150, 155, 165)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, f, max_width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=f) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def new_canvas(bg=BG_BLACK):
    return Image.new("RGB", (W, H), bg)


def draw_centered_lines(draw, lines, f, color, y_center, line_gap=14):
    heights = []
    for ln in lines:
        bbox = draw.textbbox((0, 0), ln, font=f)
        heights.append(bbox[3] - bbox[1])
    total_h = sum(heights) + line_gap * (len(lines) - 1)
    y = y_center - total_h / 2
    for ln, h in zip(lines, heights):
        w = draw.textlength(ln, font=f)
        draw.text(((W - w) / 2, y), ln, font=f, fill=color)
        y += h + line_gap


def reset_dirs():
    if os.path.exists(BUILD):
        shutil.rmtree(BUILD)
    os.makedirs(FRAMES)
    os.makedirs(SCENES)
    os.makedirs(AUDIO)


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def tts(text, out_wav, voice="es-419", speed=155):
    """Voz placeholder (espeak-ng). Robótica a propósito: solo para timing/estilo."""
    run(["espeak-ng", "-v", voice, "-s", str(speed), "-p", "35", "-a", "180",
         "-w", out_wav, text])
    return audio_duration(out_wav)


def audio_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(r.stdout.strip())


def save_frames(scene_dir, frame_fn, n_frames):
    os.makedirs(scene_dir, exist_ok=True)
    for i in range(n_frames):
        img = frame_fn(i, n_frames)
        img.save(os.path.join(scene_dir, f"f_{i:05d}.png"))


AUDIO_RATE = 44100
AUDIO_CHANNELS = 2


def encode_scene(scene_dir, out_mp4, audio_wav=None, fps=FPS):
    # Every scene's audio is forced to the same sample rate/channel layout
    # (AUDIO_RATE/AUDIO_CHANNELS) so the final concat demuxer (-c copy) can
    # stitch them without a codec-parameter mismatch silencing playback.
    if audio_wav:
        run([
            "ffmpeg", "-y", "-framerate", str(fps),
            "-i", os.path.join(scene_dir, "f_%05d.png"),
            "-i", audio_wav,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-ar", str(AUDIO_RATE), "-ac", str(AUDIO_CHANNELS),
            "-c:a", "aac", "-shortest", out_mp4,
        ])
    else:
        run([
            "ffmpeg", "-y", "-framerate", str(fps),
            "-i", os.path.join(scene_dir, "f_%05d.png"),
            "-f", "lavfi", "-i", f"anullsrc=r={AUDIO_RATE}:cl=stereo",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-ar", str(AUDIO_RATE), "-ac", str(AUDIO_CHANNELS),
            "-c:a", "aac", "-shortest", out_mp4,
        ])


def fade_alpha(i, n, fade_frames=8):
    if i < fade_frames:
        return i / fade_frames
    if i > n - fade_frames:
        return max(0.0, (n - i) / fade_frames)
    return 1.0


def blend(base_color, fg_color, alpha):
    return tuple(int(base_color[k] + (fg_color[k] - base_color[k]) * alpha) for k in range(3))


# ---------------------------------------------------------------------------
# SCENE 1 — Hook: typewriter sobre negro
# ---------------------------------------------------------------------------

def scene_hook():
    text = 'Una consulta. Un ejecutivo. 40 minutos.'
    f = font(FONT_BOLD, 54)
    type_seconds = 2.6
    hold_seconds = 2.0
    total_seconds = type_seconds + hold_seconds
    n = int(total_seconds * FPS)
    type_frames = int(type_seconds * FPS)

    def make(i, n_):
        img = new_canvas(BG_BLACK)
        d = ImageDraw.Draw(img)
        chars = len(text) if i >= type_frames else int(len(text) * (i / type_frames))
        shown = text[:chars]
        d.text((0, 0), "", font=f)  # no-op, keeps font referenced
        w = d.textlength(shown, font=f)
        d.text(((W - w) / 2, H / 2 - 30), shown, font=f, fill=FG_WHITE)
        # cursor
        if chars < len(text) and (i // 3) % 2 == 0:
            d.text(((W - w) / 2 + w + 4, H / 2 - 30), "|", font=f, fill=ACCENT)
        return img

    scene_dir = os.path.join(FRAMES, "s1")
    save_frames(scene_dir, make, n)
    out = os.path.join(SCENES, "s1.mp4")
    encode_scene(scene_dir, out, audio_wav=None)
    return out


# ---------------------------------------------------------------------------
# Slides narradas genéricas (fondo + texto centrado + fade + voz)
# ---------------------------------------------------------------------------

def narrated_slide(name, caption, voice_text, bg=BG_NAVY, caption_size=40,
                    caption_color=FG_WHITE, pad=0.6):
    wav = os.path.join(AUDIO, f"{name}.wav")
    dur = tts(voice_text, wav)
    total = dur + pad
    n = max(1, int(total * FPS))
    f = font(FONT_BOLD, caption_size)

    def make(i, n_):
        img = new_canvas(bg)
        d = ImageDraw.Draw(img)
        lines = wrap_text(d, caption, f, W - 220)
        alpha = fade_alpha(i, n_, fade_frames=10)
        col = blend(bg, caption_color, alpha)
        draw_centered_lines(d, lines, f, col, H / 2)
        return img

    scene_dir = os.path.join(FRAMES, name)
    save_frames(scene_dir, make, n)
    out = os.path.join(SCENES, f"{name}.mp4")
    encode_scene(scene_dir, out, audio_wav=wav)
    return out


# ---------------------------------------------------------------------------
# Title card
# ---------------------------------------------------------------------------

def scene_title():
    voice_text = ("Se llama AgentIA. Y en este video vas a ver exactamente cómo funciona.")
    wav = os.path.join(AUDIO, "title.wav")
    dur = tts(voice_text, wav)
    total = dur + 0.6
    n = max(1, int(total * FPS))
    f_big = font(FONT_BOLD, 90)
    f_small = font(FONT_REG, 30)

    def make(i, n_):
        img = new_canvas(BG_BLACK)
        d = ImageDraw.Draw(img)
        alpha = fade_alpha(i, n_, fade_frames=10)
        col = blend(BG_BLACK, FG_WHITE, alpha)
        col_accent = blend(BG_BLACK, ACCENT, alpha)
        title = "AgentIA"
        w = d.textlength(title, font=f_big)
        d.text(((W - w) / 2, H / 2 - 80), title, font=f_big, fill=col_accent)
        sub = "Normativa aduanera al instante"
        w2 = d.textlength(sub, font=f_small)
        d.text(((W - w2) / 2, H / 2 + 40), sub, font=f_small, fill=col)
        return img

    scene_dir = os.path.join(FRAMES, "title")
    save_frames(scene_dir, make, n)
    out = os.path.join(SCENES, "title.mp4")
    encode_scene(scene_dir, out, audio_wav=wav)
    return out


# ---------------------------------------------------------------------------
# SCENE — Mockup de interfaz de AgentIA (Parte 3 del guion)
# ---------------------------------------------------------------------------

QUERY_TEXT = ("¿Un componente electrónico importado desde China puede acceder a "
              "preferencia arancelaria bajo el acuerdo ChAFTA?")

RESPONSE_LINES = [
    "Sí. El componente puede acceder a preferencia arancelaria bajo ChAFTA",
    "si cumple la norma de origen aplicable a su partida.",
    "",
    "Documento requerido: Certificado de Origen ChAFTA.",
    "Plazo de presentación: al momento de la tramitación de la DIN.",
]

SOURCE_TAG = "Fuente: Acuerdo ChAFTA — Art. 4.3, Régimen de Origen"


def draw_app_chrome(d):
    # barra superior de la "app"
    d.rectangle([0, 0, W, 70], fill=(18, 22, 34))
    f = font(FONT_BOLD, 26)
    d.text((30, 20), "AgentIA", font=f, fill=ACCENT)
    f2 = font(FONT_REG, 18)
    d.text((30, 46), "Consultas de normativa aduanera", font=f2, fill=GREY)
    # panel central
    d.rounded_rectangle([60, 100, W - 60, H - 40], radius=16, fill=(20, 24, 38))


def scene_demo_query():
    """Se 'escribe' la consulta en el input."""
    voice_text = ("Vamos a simular el escenario del inicio. Un cliente quiere "
                  "importar un componente electrónico desde China y pregunta si "
                  "califica para preferencia arancelaria bajo el ChAFTA.")
    wav = os.path.join(AUDIO, "demo_query.wav")
    dur = tts(voice_text, wav)
    total = max(dur + 0.6, 4.0)
    n = int(total * FPS)
    f_input = font(FONT_REG, 24)
    type_frames = int(n * 0.7)

    def make(i, n_):
        img = new_canvas(BG_NAVY)
        d = ImageDraw.Draw(img)
        draw_app_chrome(d)
        # input box
        box = [100, H - 160, W - 100, H - 90]
        d.rounded_rectangle(box, radius=12, outline=ACCENT, width=2, fill=(14, 17, 28))
        chars = len(QUERY_TEXT) if i >= type_frames else int(len(QUERY_TEXT) * (i / type_frames))
        shown = QUERY_TEXT[:chars] or "Escribe tu consulta..."
        color = FG_WHITE if chars else GREY
        lines = wrap_text(d, shown, f_input, box[2] - box[0] - 40)
        y = box[1] + 14
        for ln in lines[:2]:
            d.text((box[0] + 20, y), ln, font=f_input, fill=color)
            y += 30
        return img

    scene_dir = os.path.join(FRAMES, "demo_query")
    save_frames(scene_dir, make, n)
    out = os.path.join(SCENES, "demo_query.mp4")
    encode_scene(scene_dir, out, audio_wav=wav)
    return out


def scene_demo_loading():
    voice_text = "Observa el tiempo de respuesta."
    wav = os.path.join(AUDIO, "demo_loading.wav")
    dur = tts(voice_text, wav)
    total = max(dur + 1.2, 2.0)
    n = int(total * FPS)
    f_label = font(FONT_REG, 24)

    def make(i, n_):
        img = new_canvas(BG_NAVY)
        d = ImageDraw.Draw(img)
        draw_app_chrome(d)
        box = [100, H - 160, W - 100, H - 90]
        d.rounded_rectangle(box, radius=12, outline=ACCENT, width=2, fill=(14, 17, 28))
        d.text((box[0] + 20, box[1] + 14), QUERY_TEXT[:60] + "...",
                font=font(FONT_REG, 20), fill=GREY)
        dots = "." * (1 + (i // 6) % 3)
        d.text((100, 220), f"Buscando en la normativa{dots}", font=f_label, fill=ACCENT)
        return img

    scene_dir = os.path.join(FRAMES, "demo_loading")
    save_frames(scene_dir, make, n)
    out = os.path.join(SCENES, "demo_loading.mp4")
    encode_scene(scene_dir, out, audio_wav=wav)
    return out


def scene_demo_response():
    voice_text = ("La respuesta incluye la condición de origen aplicable, el "
                  "documento requerido y el plazo de presentación. Y nota esto: "
                  "cita la fuente exacta. No es una opinión del sistema.")
    wav = os.path.join(AUDIO, "demo_response.wav")
    dur = tts(voice_text, wav)
    total = dur + 1.0
    n = int(total * FPS)
    f_resp = font(FONT_REG, 24)
    f_tag = font(FONT_BOLD, 20)
    reveal_frames = int(n * 0.35)
    highlight_start = int(n * 0.55)

    def make(i, n_):
        img = new_canvas(BG_NAVY)
        d = ImageDraw.Draw(img)
        draw_app_chrome(d)
        alpha = fade_alpha(i, reveal_frames, fade_frames=8) if i < reveal_frames else 1.0
        col = blend(BG_NAVY, FG_WHITE, min(alpha, 1.0))

        card = [100, 110, W - 100, H - 90]
        d.rounded_rectangle(card, radius=12, fill=(16, 20, 32))
        y = card[1] + 24
        for ln in RESPONSE_LINES:
            d.text((card[0] + 24, y), ln, font=f_resp, fill=col)
            y += 32

        if i >= highlight_start:
            hi_alpha = fade_alpha(i - highlight_start, n_ - highlight_start, fade_frames=6)
            box_col = blend(BG_NAVY, YELLOW, min(hi_alpha, 1.0))
            tag_box = [card[0] + 20, y + 10, card[2] - 20, y + 50]
            d.rounded_rectangle(tag_box, radius=8, outline=box_col, width=3)
            d.text((tag_box[0] + 14, tag_box[1] + 8), SOURCE_TAG, font=f_tag, fill=box_col)
        return img

    scene_dir = os.path.join(FRAMES, "demo_response")
    save_frames(scene_dir, make, n)
    out = os.path.join(SCENES, "demo_response.mp4")
    encode_scene(scene_dir, out, audio_wav=wav)
    return out


# ---------------------------------------------------------------------------
# Closing note (deja claro que es un mockup)
# ---------------------------------------------------------------------------

def scene_closing():
    voice_text = "Fin del mockup de estilo. El guion completo tiene quince minutos."
    return narrated_slide(
        "closing",
        "MOCKUP DE ESTILO — Guion completo v1.0 · AgentIA EP01 · Toxiro Digital",
        voice_text,
        bg=BG_BLACK,
        caption_size=32,
        caption_color=GREY,
    )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    reset_dirs()

    scenes = []
    scenes.append(scene_hook())
    scenes.append(narrated_slide(
        "s2_intro",
        "Imagina esto.",
        "Imagina esto. Un cliente llama a tu agencia a las once de la mañana. "
        "Tu ejecutivo más experimentado no recuerda el detalle, y cuarenta minutos "
        "después, tiene una respuesta parcial. El cliente ya llamó a otra agencia.",
    ))
    scenes.append(narrated_slide(
        "s3_question",
        "¿Cuántas veces pasa esto en tu agencia cada semana?",
        "Eso no es un problema de tu equipo. Es un problema de información. "
        "Y tiene solución.",
    ))
    scenes.append(scene_title())
    scenes.append(scene_demo_query())
    scenes.append(scene_demo_loading())
    scenes.append(scene_demo_response())
    scenes.append(scene_closing())

    list_path = os.path.join(BUILD, "concat_list.txt")
    with open(list_path, "w") as fh:
        for s in scenes:
            fh.write(f"file '{s}'\n")

    final_out = os.path.join(BUILD, "mockup_ep01.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
         "-c", "copy", final_out])
    print(f"OK -> {final_out}")


if __name__ == "__main__":
    main()
