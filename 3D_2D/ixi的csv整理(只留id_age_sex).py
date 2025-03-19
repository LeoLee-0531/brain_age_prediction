import pandas as pd

excel_path = r"C:\ixi\IXI MNI\Excel\IXI.csv.xlsx"

# 1. 讀取 Excel 檔案
df = pd.read_excel(excel_path)

# 2. 篩選需要的欄位
df_filtered = df[["IXI_ID", "AGE", "SEX_ID (1=m, 2=f)"]]

# 3. 重新命名欄位
df_filtered.rename(columns={"SEX_ID (1=m, 2=f)": "SEX"}, inplace=True)

# 4. (可選) 將 1,2 → M,F 映射
# 如果你要把 1,2 變成字串 'M','F'，可打開以下程式：
# df_filtered["SEX"] = df_filtered["SEX"].map({1: "M", 2: "F"})

# 若你想保留數字 1,2 不做轉換，可以直接略過上面那行

# 檢查結果
print(df_filtered.head())

# 5. 儲存為 CSV，供後續 DataLoader 使用
output_csv_path = r"C:\ixi\IXI MNI\output_png1\labels.csv"
df_filtered.to_csv(output_csv_path, index=False)

print(f"✅ labels.csv 已儲存至: {output_csv_path}")
