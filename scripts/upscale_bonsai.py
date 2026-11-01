import os
from PIL import Image, ImageSequence

for name in ["bonsai.gif", "bonsai-growth.gif"]:
    p = os.path.join("output", name)
    if not os.path.exists(p):
        continue
    try:
        im = Image.open(p)
        frames = []
        durations = []
        for f in ImageSequence.Iterator(im):
            frames.append(f.convert("RGBA").resize((f.width * 2, f.height * 2), Image.Resampling.NEAREST))
            durations.append(f.info.get("duration", 100))
        palette_frames = [f.convert("P", palette=Image.Palette.ADAPTIVE) for f in frames]
        palette_frames[0].save(p, save_all=True, append_images=palette_frames[1:], duration=durations, loop=0, optimize=True)
        print(f"Upscaled {p} to 2x crisp nearest-neighbor")
    except Exception as e:
        print(f"Error upscaling {p}: {e}")
