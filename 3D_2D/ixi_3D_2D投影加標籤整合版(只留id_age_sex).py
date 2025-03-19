import os
import numpy as np
import nibabel as nib
import pandas as pd
import cv2
from tqdm import tqdm

########################################
# 1️⃣ 讀取 Excel 並建立 DataFrame
########################################
excel_path = r"C:\ixi\IXI MNI\Excel\IXI.csv.xlsx"
df = pd.read_excel(excel_path, engine='openpyxl')

# 確保 ID 格式 (3位數)，例如 002, 012
df["IXI_ID"] = df["IXI_ID"].astype(str).str.zfill(3)

########################################
# 2️⃣ 建立輸出資料夾
########################################
nii_folder = r"C:\ixi\csf\pve0"        # 原始 NIfTI 影像位置
output_folder = r"C:\ixi\csf\2d"  # 2D投影影像輸出位置
os.makedirs(output_folder, exist_ok=True)

# 影像尺寸
img_size = (256, 256)

# CLAHE 對比增強
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

########################################
# 3️⃣ 定義影像增強函式
########################################
def apply_gamma_correction(image, gamma=1.2):
    """Gamma 修正，提高影像對比"""
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)]).astype("uint8")
    return cv2.LUT(image, table)

def normalize_and_enhance(img):
    """標準化並應用對比度強化 (CLAHE + Gamma)"""
    # 0~255 正規化
    img = (img - np.min(img)) / (np.max(img) - np.min(img)) * 255
    img = img.astype(np.uint8)
    # CLAHE
    img = clahe.apply(img)
    # Gamma
    img = apply_gamma_correction(img, gamma=1.2)
    return img

########################################
# 4️⃣ 建立存放標註的列表
########################################
labels = []  # 用來存放 [NIfTI_ID, AGE, SEX]

########################################
# 5️⃣ 遍歷所有 .nii.gz 影像
########################################
nii_files = [f for f in os.listdir(nii_folder) if f.endswith(".nii.gz")]

for nii_file in tqdm(nii_files, desc="Processing NIfTI files"):
    # 1) 從檔名解析 ID
    #    e.g. "IXI012-Guys-1234-T1.nii.gz" → "IXI012"
    match = nii_file.split("-")[0]       # "IXI012"
    nii_id_num = match.replace("IXI", "")  # "012"
    nii_id_num = nii_id_num.zfill(3)       # 保證3位數
    nii_id_full = f"IXI{nii_id_num}"       # "IXI012"

    # 2) 在 Excel 中找對應標註
    subject = df[df["IXI_ID"] == nii_id_num]  # Excel 裡存的可能是 "012"
    if subject.empty:
        print(f"⚠️ 無法找到 {nii_id_num} 的標註資料，跳過")
        continue

    # 3) 取得年齡與性別
    age = subject["AGE"].values[0]
    # 這裡假設 Excel 欄位是 "SEX_ID (1=m, 2=f)"
    sex_id = subject["SEX_ID (1=m, 2=f)"].values[0]
    sex = "M" if sex_id == 1 else "F"

    # 4) 讀取 NIfTI 影像
    nii_path = os.path.join(nii_folder, nii_file)
    img = nib.load(nii_path).get_fdata()

    # 5) 修正影像方向 (flip)
    img = np.flip(img, axis=-1)

    # 6) 計算投影 & 影像增強
    projections = {
        "Axial_Mean": normalize_and_enhance(np.mean(img, axis=2)),
        "Axial_Std":  normalize_and_enhance(np.std(img,  axis=2, ddof=1)),
        "Coronal_Mean":   normalize_and_enhance(np.mean(img, axis=1)),
        "Coronal_Std":    normalize_and_enhance(np.std(img,  axis=1, ddof=1)),
        "Sagittal_Mean":  normalize_and_enhance(np.mean(img, axis=0)),
        "Sagittal_Std":   normalize_and_enhance(np.std(img,  axis=0, ddof=1)),
    }

    # 7) 儲存投影影像
    for proj_name, proj_img in projections.items():
        # resize
        proj_img = cv2.resize(proj_img, img_size, interpolation=cv2.INTER_CUBIC)
        # 命名 e.g. "IXI012_Axial_Mean.png"
        output_path = os.path.join(output_folder, f"{nii_id_full}_{proj_name}.png")
        cv2.imwrite(output_path, proj_img)

    # 8) 收集標註
    labels.append([nii_id_full, age, sex])

print("✅ 影像處理完成！影像已存入:", output_folder)

########################################
# 6️⃣ 輸出標註 CSV
########################################
labels_df = pd.DataFrame(labels, columns=["NIfTI_ID", "AGE", "SEX"])
labels_csv = os.path.join(output_folder, "labels.csv")
labels_df.to_csv(labels_csv, index=False, encoding="utf-8")
print("✅ labels.csv 已生成:", labels_csv)
