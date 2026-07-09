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
NARRATION_DIR = os.path.join(ROOT, "narration_audio")

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

BG_BLACK = (8, 8, 10)
BG_NAVY = (12, 16, 28)
FG_WHITE = (240, 240, 245)
ACCENT = (90, 170, 255)
YELLOW = (255, 210, 90)
GREY = (150, 155, 165)


# ---------------------------------------------------------------------------
# Íconos temáticos de fondo (flotan sutilmente en las esquinas, sin competir
# con el texto/diagramas del centro) — le dan vida a los fondos planos.
# ---------------------------------------------------------------------------

def icon_document(d, cx, cy, s, color):
    w, h = 40 * s, 52 * s
    x0, y0 = cx - w / 2, cy - h / 2
    lw = max(1, int(2 * s))
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=4 * s, outline=color, width=lw)
    for k in range(3):
        ly = y0 + 16 * s + k * 11 * s
        d.line([x0 + 8 * s, ly, x0 + w - 8 * s, ly], fill=color, width=lw)


def icon_clock(d, cx, cy, s, color):
    r = 24 * s
    lw = max(1, int(2 * s))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=lw)
    d.line([cx, cy, cx, cy - r * 0.6], fill=color, width=lw)
    d.line([cx, cy, cx + r * 0.4, cy + r * 0.2], fill=color, width=lw)


def icon_network(d, cx, cy, s, color):
    pts = [(cx - 30 * s, cy - 10 * s), (cx + 10 * s, cy - 25 * s),
           (cx + 30 * s, cy + 15 * s), (cx - 15 * s, cy + 22 * s)]
    lw = max(1, int(1.5 * s))
    for a, b in [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]:
        d.line([pts[a], pts[b]], fill=color, width=lw)
    for p in pts:
        r = 4 * s
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=color)


def icon_check(d, cx, cy, s, color):
    r = 22 * s
    lw = max(1, int(2 * s))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=lw)
    d.line([cx - 10 * s, cy, cx - 2 * s, cy + 9 * s], fill=color, width=max(1, int(2.5 * s)))
    d.line([cx - 2 * s, cy + 9 * s, cx + 12 * s, cy - 9 * s], fill=color, width=max(1, int(2.5 * s)))


THEME_ICON_FN = {
    "clock": icon_clock,
    "document": icon_document,
    "network": icon_network,
    "check": icon_check,
}

# Posiciones fijas en las 4 esquinas, lejos de la franja central donde va
# el texto/diagrama principal.
THEME_POSITIONS = [(150, 140), (1130, 140), (150, 600), (1130, 600)]


def theme_background(d, theme, i, bg, tint=ACCENT, opacity=0.16):
    if not theme:
        return
    icon_fn = THEME_ICON_FN[theme]
    color = blend(bg, tint, opacity)
    t = i / FPS
    for idx, (bx, by) in enumerate(THEME_POSITIONS):
        phase = idx * 1.3
        dy = 10 * math.sin(2 * math.pi * (t / 8) + phase)
        dx = 6 * math.sin(2 * math.pi * (t / 11) + phase * 1.6)
        icon_fn(d, bx + dx, by + dy, 1.0, color)


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


def draw_centered_lines(draw, lines, f, color, y_center, line_gap=14, x_center=None):
    if x_center is None:
        x_center = W / 2
    heights = []
    for ln in lines:
        bbox = draw.textbbox((0, 0), ln, font=f)
        heights.append(bbox[3] - bbox[1])
    total_h = sum(heights) + line_gap * (len(lines) - 1)
    y = y_center - total_h / 2
    for ln, h in zip(lines, heights):
        w = draw.textlength(ln, font=f)
        draw.text((x_center - w / 2, y), ln, font=f, fill=color)
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


def narration(name, voice_text, voice="es-419", speed=155):
    """Devuelve (ruta_wav, duracion). Usa narration_audio/<name>.mp3 (voz real,
    p.ej. ElevenLabs) si existe; si no, cae al placeholder de espeak-ng."""
    real_path = os.path.join(NARRATION_DIR, f"{name}.mp3")
    wav_out = os.path.join(AUDIO, f"{name}.wav")
    if os.path.exists(real_path):
        run(["ffmpeg", "-y", "-i", real_path,
             "-ar", str(AUDIO_RATE), "-ac", str(AUDIO_CHANNELS), wav_out])
        return wav_out, audio_duration(wav_out)
    dur = tts(voice_text, wav_out, voice=voice, speed=speed)
    return wav_out, dur


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
        theme_background(d, "clock", i, BG_BLACK)
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
                    caption_color=FG_WHITE, pad=0.6, theme=None):
    wav, dur = narration(name, voice_text)
    total = dur + pad
    n = max(1, int(total * FPS))
    f = font(FONT_BOLD, caption_size)

    def make(i, n_):
        img = new_canvas(bg)
        d = ImageDraw.Draw(img)
        theme_background(d, theme, i, bg)
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
    wav, dur = narration("title", voice_text)
    total = dur + 0.6
    n = max(1, int(total * FPS))
    f_big = font(FONT_BOLD, 90)
    f_small = font(FONT_REG, 30)

    def make(i, n_):
        img = new_canvas(BG_BLACK)
        d = ImageDraw.Draw(img)
        theme_background(d, "network", i, BG_BLACK)
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
# Diagrama de flujo simple (cajas + flechas) — Partes 1 y 2 del guion
# ---------------------------------------------------------------------------

def diagram_slide(name, boxes, voice_text, bg=BG_NAVY, theme=None):
    wav, dur = narration(name, voice_text)
    total = dur + 0.6
    n = max(1, int(total * FPS))
    f_box = font(FONT_REG, 20)

    box_w, box_h, gap = 230, 90, 50
    total_w = len(boxes) * box_w + (len(boxes) - 1) * gap
    start_x = (W - total_w) / 2
    y = H / 2 - box_h / 2

    def make(i, n_):
        img = new_canvas(bg)
        d = ImageDraw.Draw(img)
        theme_background(d, theme, i, bg)
        alpha = fade_alpha(i, n_, fade_frames=10)
        col = blend(bg, FG_WHITE, alpha)
        accent_col = blend(bg, ACCENT, alpha)
        x = start_x
        for idx, label in enumerate(boxes):
            box = [x, y, x + box_w, y + box_h]
            d.rounded_rectangle(box, radius=10, outline=accent_col, width=2,
                                 fill=(16, 20, 32))
            lines = wrap_text(d, label, f_box, box_w - 24)
            draw_centered_lines(d, lines, f_box, col, y + box_h / 2, line_gap=6,
                                x_center=x + box_w / 2)
            if idx < len(boxes) - 1:
                ay = y + box_h / 2
                d.line([x + box_w + 8, ay, x + box_w + gap - 10, ay],
                       fill=accent_col, width=3)
                d.polygon([(x + box_w + gap - 10, ay - 6),
                           (x + box_w + gap - 10, ay + 6),
                           (x + box_w + gap, ay)], fill=accent_col)
            x += box_w + gap
        return img

    scene_dir = os.path.join(FRAMES, name)
    save_frames(scene_dir, make, n)
    out = os.path.join(SCENES, f"{name}.mp4")
    encode_scene(scene_dir, out, audio_wav=wav)
    return out


# ---------------------------------------------------------------------------
# Lista de puntos acumulativa (Parte 4 del guion — "cambia esto, esto y esto")
# ---------------------------------------------------------------------------

def bullets_scene(name, title, points, active_index, voice_text, bg=BG_NAVY, theme=None):
    wav, dur = narration(name, voice_text)
    total = dur + 0.5
    n = max(1, int(total * FPS))
    f_title = font(FONT_BOLD, 32)
    f_point = font(FONT_REG, 28)

    def make(i, n_):
        img = new_canvas(bg)
        d = ImageDraw.Draw(img)
        theme_background(d, theme, i, bg)
        tw = d.textlength(title, font=f_title)
        d.text(((W - tw) / 2, 80), title, font=f_title, fill=GREY)

        alpha = fade_alpha(i, n_, fade_frames=10)
        y = 230
        for idx, p in enumerate(points):
            if idx > active_index:
                continue
            col = FG_WHITE if idx < active_index else blend(bg, ACCENT, alpha)
            d.text((170, y), f"•  {p}", font=f_point, fill=col)
            y += 64
        return img

    scene_dir = os.path.join(FRAMES, name)
    save_frames(scene_dir, make, n)
    out = os.path.join(SCENES, f"{name}.mp4")
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
    wav, dur = narration("demo_query", voice_text)
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
    wav, dur = narration("demo_loading", voice_text)
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
    wav, dur = narration("demo_response", voice_text)
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
        theme="clock",
    ))
    scenes.append(narrated_slide(
        "s3_question",
        "¿Cuántas veces pasa esto en tu agencia cada semana?",
        "Eso no es un problema de tu equipo. Es un problema de información. "
        "Y tiene solución.",
        theme="network",
    ))
    scenes.append(scene_title())

    # --- Parte 1: el problema real ---
    scenes.append(diagram_slide(
        "p1_problem",
        ["Cliente", "Ejecutivo", "Búsqueda\nmanual", "Respuesta\n(40 min)"],
        "El conocimiento de normativa aduanera está atrapado en las personas. "
        "Está en la cabeza del ejecutivo con experiencia, en un PDF perdido en "
        "una carpeta compartida, en un correo de hace dos años.",
        theme="document",
    ))
    scenes.append(narrated_slide(
        "p1_risk",
        "Rotación de personal + normativa en constante cambio =\nriesgo operacional permanente",
        "Y cuando ese ejecutivo no está, el conocimiento desaparece con él. "
        "El resultado: respuestas lentas, inconsistentes, y en el peor caso, "
        "incorrectas.",
        caption_size=34,
        theme="document",
    ))
    scenes.append(narrated_slide(
        "p1_pause",
        "¿Y si el conocimiento no dependiera de quién está disponible?",
        "Esa es la pregunta que dio origen a AgentIA.",
        theme="network",
    ))

    # --- Parte 2: qué es AgentIA y cómo funciona ---
    scenes.append(diagram_slide(
        "p2_rag",
        ["Consulta", "AgentIA", "Base de\nconocimiento", "Respuesta\n+ fuente"],
        "AgentIA está construido sobre una base de conocimiento específica: "
        "reglamentos, circulares y acuerdos comerciales vigentes. Cuando alguien "
        "consulta, el sistema busca en los documentos reales y construye una "
        "respuesta citando la fuente.",
        theme="network",
    ))
    scenes.append(narrated_slide(
        "p2_tagline",
        "No alucina. Busca. Cita. Responde.",
        "No alucina. Busca. Cita. Responde. Veámoslo en acción.",
        caption_size=48,
        theme="network",
    ))

    scenes.append(scene_demo_query())
    scenes.append(scene_demo_loading())
    scenes.append(scene_demo_response())

    # --- Parte 4: qué significa esto para una agencia ---
    scenes.append(narrated_slide(
        "p4_title",
        "Lo que cambia cuando el conocimiento está disponible siempre",
        "Hablemos de lo concreto. ¿Qué cambia en la operación de una agencia "
        "cuando tiene esto disponible?",
        caption_size=36,
        theme="check",
    ))
    p4_points = [
        "Velocidad de respuesta al cliente",
        "Consistencia entre ejecutivos",
        "Actualización automática de la normativa",
        "Liberación del ejecutivo experto",
    ]
    p4_lines = [
        "Primero: la velocidad de respuesta al cliente.",
        "Segundo: la consistencia. La respuesta es la misma sin importar quién atienda.",
        "Tercero: la actualización automática, cuando Aduanas emite una nueva circular.",
        "Cuarto: la liberación del ejecutivo experto para lo que realmente requiere su criterio.",
    ]
    for idx, line in enumerate(p4_lines):
        scenes.append(bullets_scene(
            f"p4_point{idx + 1}", "Lo que cambia:", p4_points, idx, line,
            theme="check",
        ))
    scenes.append(narrated_slide(
        "p4_final",
        "La agencia que responde mejor y más rápido\nno necesita competir en precio.",
        "La agencia que responde mejor y más rápido no necesita competir en precio.",
        theme="check",
        caption_size=34,
    ))

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
