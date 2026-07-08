# Mockup de video — AgentIA YouTube EP01

Genera un video corto (~65s) que muestra el **estilo visual** propuesto para el
guion `guion_youtube_agentia_ep01.md`: intro tipo typewriter, slides narradas,
tarjeta de título y un mockup de la interfaz de AgentIA (Parte 3 del guion).

## Qué es y qué no es

- **Es** una maqueta de ritmo, tipografía, composición y estructura de escenas.
- **No** usa la voz final (usa `espeak-ng` como placeholder robótico, solo para
  tener timing real de narración).
- **No** es la interfaz real de AgentIA — es una UI simulada dibujada a mano.
- **No** incluye música ni voz profesional; eso se agrega en la producción final.

## Requisitos

```
apt-get install -y --no-install-recommends ffmpeg espeak-ng
pip3 install pillow
```

## Uso

```
python3 generate_mockup.py
```

Genera `build/mockup_ep01.mp4`. La carpeta `build/` es generada (no se versiona).

## Siguiente paso hacia producción real

1. Reemplazar la voz de `espeak-ng` por un TTS de calidad (ElevenLabs, Azure,
   OpenAI TTS, etc.) o narración grabada.
2. Reemplazar el mockup de interfaz por un screencast real de AgentIA.
3. Agregar música de fondo con licencia (baja durante la demo).
4. Ajustar resolución de salida a 1920x1080 y exportar subtítulos/capítulos.
