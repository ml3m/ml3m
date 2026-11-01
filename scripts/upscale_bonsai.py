import os
from PIL import Image
import numpy as np

COLOR_MAP = {
    # Foliage: map blue/teal to warm dark-orange, rich orange, ml3m orange, golden yellow
    (0x17, 0x3f, 0x5f): (0x7c, 0x2d, 0x12), # #7c2d12 dark burnt orange
    (0x23, 0x60, 0x8c): (0xc2, 0x41, 0x0c), # #c2410c deep orange
    (0x35, 0x85, 0xb8): (0xff, 0x91, 0x4d), # #ff914d signature ml3m orange
    (0x5c, 0xb4, 0xdd): (0xfd, 0xe0, 0x47), # #fde047 bright golden yellow
}

def process_gif(input_path, output_path):
    im = Image.open(input_path)
    all_rgba_frames = []
    durations = []
    unique_colors = set()

    for f in range(im.n_frames):
        im.seek(f)
        frame_rgba = im.convert("RGBA")
        arr = np.array(frame_rgba)
        # 2x nearest neighbor
        arr_2x = np.repeat(np.repeat(arr, 2, axis=0), 2, axis=1)

        # Recolor foliage
        for old_rgb, new_rgb in COLOR_MAP.items():
            mask = (arr_2x[:, :, 0] == old_rgb[0]) & (arr_2x[:, :, 1] == old_rgb[1]) & (arr_2x[:, :, 2] == old_rgb[2]) & (arr_2x[:, :, 3] > 0)
            arr_2x[mask, 0] = new_rgb[0]
            arr_2x[mask, 1] = new_rgb[1]
            arr_2x[mask, 2] = new_rgb[2]

        all_rgba_frames.append(arr_2x)
        durations.append(im.info.get("duration", 100))

        opaque_pixels = arr_2x[arr_2x[:, :, 3] > 0][:, :3]
        for c in np.unique(opaque_pixels, axis=0):
            unique_colors.add(tuple(c))

    # Palette with transparent slot 0
    color_to_idx = {}
    palette = [0, 0, 0]
    for idx, c in enumerate(sorted(unique_colors), start=1):
        color_to_idx[c] = idx
        palette.extend(c)

    while len(palette) < 768:
        palette.extend([0, 0, 0])

    p_frames = []
    h, w, _ = all_rgba_frames[0].shape
    for arr in all_rgba_frames:
        idx_arr = np.zeros((h, w), dtype=np.uint8)
        opaque_mask = arr[:, :, 3] > 0
        for c, idx in color_to_idx.items():
            match = (arr[:, :, 0] == c[0]) & (arr[:, :, 1] == c[1]) & (arr[:, :, 2] == c[2]) & opaque_mask
            idx_arr[match] = idx

        p_img = Image.frombytes("P", (w, h), idx_arr.tobytes())
        p_img.putpalette(palette)
        p_frames.append(p_img)

    p_frames[0].save(
        output_path,
        save_all=True,
        append_images=p_frames[1:],
        duration=durations,
        loop=0,
        transparency=0,
        disposal=2,
        optimize=False
    )
    print(f"Processed and saved {output_path}")

if __name__ == "__main__":
    growth_src = os.path.join("output", "bonsai-growth.gif")
    if os.path.exists(growth_src):
        process_gif(growth_src, os.path.join("output", "bonsai.gif"))
        process_gif(growth_src, os.path.join("output", "bonsai-growth.gif"))
