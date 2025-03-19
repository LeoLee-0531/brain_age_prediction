import os
import shutil
import pandas as pd
from sklearn.model_selection import train_test_split

# --------------------------------------------------
# 1. 設定路徑
# --------------------------------------------------
GLOBAL_DIR  = r"C:\ixi\new gray\global"  # 內含 labels.csv
LOCAL_DIR   = r"C:\ixi\new gray\local"

LABELS_PATH = os.path.join(GLOBAL_DIR, "labels.csv")

TRAIN_DIR   = r"C:\ixi\new gray\trainset"
TEST_DIR    = r"C:\ixi\new gray\testset"

# 建立輸出資料夾
os.makedirs(os.path.join(TRAIN_DIR, "global"), exist_ok=True)
os.makedirs(os.path.join(TRAIN_DIR, "local"), exist_ok=True)
os.makedirs(os.path.join(TEST_DIR,  "global"), exist_ok=True)
os.makedirs(os.path.join(TEST_DIR,  "local"), exist_ok=True)

# --------------------------------------------------
# 2. 讀取 labels.csv，先過濾掉 AGE 欄位為 NaN 的資料，再用 train_test_split 切 85:15
# --------------------------------------------------
df = pd.read_csv(LABELS_PATH)
print(f"原始資料筆數: {len(df)}")

# 過濾無年齡資料 (AGE 為 NaN)
df = df.dropna(subset=['AGE'])
df = df.reset_index(drop=True)

print(f"過濾後剩餘資料筆數: {len(df)}")

df_train, df_test = train_test_split(
    df,
    test_size=0.15,        # 15% 當測試
    random_state=42,       # 固定隨機種子 (若想每次不同可設 None)
    shuffle=True           # 打亂資料後再分
)

df_train = df_train.reset_index(drop=True)
df_test  = df_test.reset_index(drop=True)

print(f"Train set: {len(df_train)} 筆, Test set: {len(df_test)} 筆")

# 輸出 train_labels.csv / test_labels.csv
train_csv_path = os.path.join(TRAIN_DIR, "train_labels.csv")
test_csv_path  = os.path.join(TEST_DIR,  "test_labels.csv")

df_train.to_csv(train_csv_path, index=False)
df_test.to_csv(test_csv_path, index=False)

# --------------------------------------------------
# 3. 定義複製影像的函式
# --------------------------------------------------
def copy_global_images(subject_id, target_global_dir):
    """
    依 subject_id 複製全局影像檔案到目標資料夾
    預期檔名如: D0001_Axial_Mean.png, D0001_Axial_Std.png, ...
    """
    projections = [
        "Axial_Mean",
        "Axial_Std",
        "Coronal_Mean",
        "Coronal_Std",
        "Sagittal_Mean",
        "Sagittal_Std"
    ]
    for proj in projections:
        filename = f"{subject_id}_{proj}.png"
        src_path = os.path.join(GLOBAL_DIR, filename)
        dst_path = os.path.join(target_global_dir, filename)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
        else:
            print(f"[警告] 找不到檔案: {src_path}")

def copy_local_images(subject_id, target_local_dir):
    """
    依 subject_id 複製局部影像 (local patches) 到目標資料夾
    預期路徑: local/subject_id/*.png
    """
    src_folder = os.path.join(LOCAL_DIR, subject_id)
    if not os.path.exists(src_folder):
        print(f"[警告] 找不到局部影像資料夾: {src_folder}")
        return

    dst_folder = os.path.join(target_local_dir, subject_id)
    os.makedirs(dst_folder, exist_ok=True)

    for fname in os.listdir(src_folder):
        if fname.lower().endswith(".png"):
            src_path = os.path.join(src_folder, fname)
            dst_path = os.path.join(dst_folder, fname)
            shutil.copy2(src_path, dst_path)

# --------------------------------------------------
# 4. 複製影像到 trainset
# --------------------------------------------------
print("開始複製 TrainSet 影像...")
for idx, row in df_train.iterrows():
    subject_id = row["NIfTI_ID"]
    copy_global_images(subject_id, os.path.join(TRAIN_DIR, "global"))
    copy_local_images(subject_id, os.path.join(TRAIN_DIR, "local"))

# --------------------------------------------------
# 5. 複製影像到 testset
# --------------------------------------------------
print("開始複製 TestSet 影像...")
for idx, row in df_test.iterrows():
    subject_id = row["NIfTI_ID"]
    copy_global_images(subject_id, os.path.join(TEST_DIR, "global"))
    copy_local_images(subject_id, os.path.join(TEST_DIR, "local"))

print("處理完成！")
