import os
import shutil

def organize_local_patches(local_dir):
    """
    將 local_dir 內的局部塊檔案，依 subject_id 建立子資料夾並搬移過去。

    檔名格式假設:
      {subject_id}_{投影}_{row}_{col}.png
    或
      {subject_id}_{投影}...  (最少要確保檔名前綴是 subject_id)

    例如:
      IXI002_Axial_Mean_0_0.png
      IXI002_Axial_Std_0_0.png
      ...
      IXI003_Axial_Mean_0_64.png
      ...
    """

    # 取得 local_dir 下所有 .png 檔案
    files = [f for f in os.listdir(local_dir) if f.endswith(".png")]

    for f in files:
        # 解析檔名，取 subject_id
        base = os.path.splitext(f)[0]  # e.g. "IXI002_Axial_Mean_0_0"
        parts = base.split("_")

        if len(parts) < 2:
            # 檔名不符合預期, e.g. "test.png"
            print(f"跳過檔名: {f}")
            continue

        # parts[0] 通常就是 subject_id (e.g. "IXI002")
        subject_id = parts[0]

        # 建立該 subject_id 的子資料夾
        subfolder = os.path.join(local_dir, subject_id)
        os.makedirs(subfolder, exist_ok=True)

        old_path = os.path.join(local_dir, f)
        new_path = os.path.join(subfolder, f)

        # 移動檔案
        shutil.move(old_path, new_path)
        print(f"移動: {old_path} => {new_path}")

    print("✅ 局部塊已依 subject_id 分類完畢！")


if __name__ == "__main__":
    local_dir = r"C:\ixi\IXI MNI\local"  # 請修改成你的實際路徑
    organize_local_patches(local_dir)
