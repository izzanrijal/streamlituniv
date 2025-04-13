import streamlit as st
import polars as pl
import json
from io import BytesIO
from functools import reduce

# Kolom data
columns = [
    "Perguruan Tinggi", "Program Studi", "Strata", "Kode Wilayah",
    "Nomor SK", "Tahun SK", "Peringkat", "Tanggal Kedaluwarsa", "Status"
]

# Load data JSON
with open("univ.json", "r", encoding="utf-8") as f:
    data_dict = json.load(f)
    data_rows = data_dict["data"]

# Polars DataFrame
df = pl.DataFrame(data_rows, schema=columns)

st.title("ðŸ“Š Data Akreditasi Program Studi di Indonesia")

# Sidebar filters
with st.sidebar:
    st.header("ðŸ§¹ Exclude Value (Klik X untuk sembunyikan)")

    exclude_strata = st.multiselect(
        "Sembunyikan Strata",
        options=sorted(df["Strata"].unique().to_list()),
        default=[]
    )

    exclude_wilayah = st.multiselect(
        "Sembunyikan Kode Wilayah",
        options=sorted(df["Kode Wilayah"].unique().to_list()),
        default=[]
    )

    exclude_peringkat = st.multiselect(
        "Sembunyikan Akreditasi",
        options=sorted(df["Peringkat"].unique().to_list()),
        default=[]
    )

# Apply exclude filters
filtered_df = df.filter(
    ~pl.col("Strata").is_in(exclude_strata) &
    ~pl.col("Kode Wilayah").is_in(exclude_wilayah) &
    ~pl.col("Peringkat").is_in(exclude_peringkat)
)

# Text search dengan multiple keyword
keyword_input = st.text_input("ðŸ” Cari Program Studi atau Universitas (pisahkan dengan koma)").lower()
keywords = [k.strip() for k in keyword_input.split(",") if k.strip()]

if keywords:
    conditions = [
        pl.col("Program Studi").str.to_lowercase().str.contains(k) |
        pl.col("Perguruan Tinggi").str.to_lowercase().str.contains(k)
        for k in keywords
    ]
    combined_condition = reduce(lambda a, b: a | b, conditions)
    filtered_df = filtered_df.filter(combined_condition)

# Tampilkan hasil
st.subheader("ðŸ“„ Tabel Hasil Filter")
st.dataframe(filtered_df.to_pandas(), use_container_width=True)

# Tombol Download JSON
json_data = {"data": filtered_df.rows()}
json_bytes = BytesIO(json.dumps(json_data, indent=2, ensure_ascii=False).encode("utf-8"))

st.download_button(
    label="â¬‡ï¸ Download Hasil Filter ke JSON",
    data=json_bytes,
    file_name="filtered_universitas.json",
    mime="application/json"
)
