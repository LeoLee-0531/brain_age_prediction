import os
import cv2
import numpy as np
from tqdm import tqdm

global_dir = r"C:\ixi\new gray\global"
local_dir  = r"C:\ixi\new gray\local"
os.makedirs(local_dir, exist_ok=True)

patch_size = 64
stride     = 64

files = [f for f in os.listdir(global_dir) if f.endswith(".png")]

for f in tqdm(files, desc="Generating local patches"):
    path = os.path.join(global_dir, f)
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"⚠️ 無法讀取影像: {path}")
        continue

    H, W = img.shape
    for r in range(0, H - patch_size + 1, stride):
        for c in range(0, W - patch_size + 1, stride):
            patch = img[r:r+patch_size, c:c+patch_size]

            # 計算非零像素的比例
            non_zero_count = np.count_nonzero(patch)
            total_pixels   = patch_size * patch_size
            ratio = non_zero_count / total_pixels

            if ratio < 0.01:
                # 若非零像素 < 10%，視為幾乎全黑
                continue

            base_name = os.path.splitext(f)[0]
            patch_name = f"{base_name}_{r}_{c}.png"
            patch_path = os.path.join(local_dir, patch_name)
            cv2.imwrite(patch_path, patch)

print("✅ 局部影像塊已輸出到:", local_dir)
