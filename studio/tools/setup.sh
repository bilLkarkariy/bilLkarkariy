#!/usr/bin/env bash
# Prépare un environnement neuf : dépendances, polices, voix, textures, sons.
set -euo pipefail
cd "$(dirname "$0")/.."
npm install --no-audit --no-fund
pip install -q numpy scipy pillow soundfile bpy==5.0.1 piper-tts faster-whisper
pip install -q --no-deps num2words
mkdir -p public/fonts .cache/piper public/aroll
for f in "ofl/ebgaramond/EBGaramond%5Bwght%5D.ttf:EBGaramond.ttf" \
         "ofl/ebgaramond/EBGaramond-Italic%5Bwght%5D.ttf:EBGaramond-Italic.ttf" \
         "ofl/ibmplexmono/IBMPlexMono-Light.ttf:PlexMono-Light.ttf" \
         "ofl/ibmplexmono/IBMPlexMono-Regular.ttf:PlexMono-Regular.ttf" \
         "ofl/ibmplexmono/IBMPlexMono-Medium.ttf:PlexMono-Medium.ttf" \
         "ofl/amiriquran/AmiriQuran-Regular.ttf:AmiriQuran-Regular.ttf" \
         "ofl/amiri/Amiri-Regular.ttf:Amiri-Regular.ttf"; do
  curl -sSfL -o "public/fonts/${f##*:}" "https://raw.githubusercontent.com/google/fonts/main/${f%%:*}"
done
for ext in onnx onnx.json; do
  curl -sSfL -o ".cache/piper/fr_FR-tom-medium.$ext" \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/tom/medium/fr_FR-tom-medium.$ext"
done
pip install -q torch==2.0.1 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu
pip install -q --ignore-installed packaging && pip install -q deepfilternet
mkdir -p ~/.cache/DeepFilterNet && curl -sSfL -o /tmp/dfn3.zip \
  https://raw.githubusercontent.com/Rikorose/DeepFilterNet/main/models/DeepFilterNet3.zip && unzip -o -q /tmp/dfn3.zip -d ~/.cache/DeepFilterNet
python3 tools/textures.py
python3 tools/sfx.py
echo "Ensuite : placer la photo/les rushes dans public/aroll/, puis"
echo "  python3 tools/vo.py tts script/hook.json && python3 tools/maquette.py"
