import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "Banyak_pembeli",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_jumlah_kategori_produk_df(df):
    jumlah_kategori_produk = df.groupby(by="product_category_name_english").agg({
    "order_id": "count"}).sort_values(by='order_id', ascending = False).reset_index()
    jumlah_kategori_produk.columns = ["Nama_produk","Banyak_Pembeli"]
    return jumlah_kategori_produk

def create_bykota_df(df):
    bykota = df.groupby(by="customer_city").order_id.count().reset_index()
    bykota.rename(columns={"order_id": "Banyak_pembeli"}, inplace=True)
    return bykota

def create_pembayaran_df(df):
    pembayaran_metode = df.groupby(by="payment_type").agg({
    "order_id": "count",
    "payment_value": "mean",
    "price" : "sum",}).reset_index()
    pembayaran_metode.columns = ["Tipe_Pembayaran", "Banyak_Pembeli", "Rata_Rata_Pengeluaran", "Total_Harga"]
    
    return pembayaran_metode

all_df = pd.read_csv("data_gabungan.csv")

datetime_columns = ["order_purchase_timestamp"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/Raziqizzan03/Bangkit/blob/main/poto/WhatsApp%20Image%202024-03-05%20at%2020.36.32%20(1).png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
jumlah_kategori_produk = create_jumlah_kategori_produk_df(main_df)
bykota = create_bykota_df(main_df)
pembayaran_metode = create_pembayaran_df(main_df)

st.header('Dashboard Perusahaan Raziq :sunglasses:')

st.subheader('Pembelian perhari')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.Banyak_pembeli.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))

ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["Banyak_pembeli"],
    marker='o', 
    linewidth=2,
    color="orange"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader("Kategori produk Terbaik dan Terburuk")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))
 
colors = ["orange", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="Banyak_Pembeli", y="Nama_produk", data=jumlah_kategori_produk.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Kategori Produk Terbaik", loc="center", fontsize=20)
ax[0].tick_params(axis ='y', labelsize=18)
 
sns.barplot(x="Banyak_Pembeli", y="Nama_produk", data=jumlah_kategori_produk.sort_values(by="Banyak_Pembeli", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Kategori Produk Terburuk", loc="center", fontsize=20)
ax[1].tick_params(axis='y', labelsize=18)
 
plt.show()

st.pyplot(fig)


st.subheader("Pembelian Terbanyak berdasarkan kota")

fig, ax = plt.subplots(figsize=(24, 6))

colors_ = ["orange", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="Banyak_pembeli", 
    y="customer_city",
    data=bykota.sort_values(by="Banyak_pembeli", ascending=False).head(5),
    palette=colors_
)
plt.title("Banyak Pembeli berdasarkan kota", loc="center", fontsize=30)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='y', labelsize=20)
plt.show()

st.pyplot(fig)

st.subheader("Tipe Pembayaran berdasarkan beberapa kategori")
 
col1, col2, col3 = st.columns(3)

with col1:
    avg_pembeli = round(pembayaran_metode.Banyak_Pembeli.mean(), 1)
    st.metric("Rata Rata Pembeli", value=avg_pembeli)
 
with col2:
    avg_pengeluaran = round(pembayaran_metode.Rata_Rata_Pengeluaran.mean(), 1)
    st.metric("Rata Rata dari rata rata Pengeluaran", value=avg_pengeluaran)
 
with col3:
    total_harga = round(pembayaran_metode.Total_Harga.mean(), 1)
    st.metric("Rata Rata dari Total Harga", value=total_harga)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))
 
colors = ["orange", "orange", "orange", "orange"]
 
sns.barplot(y="Banyak_Pembeli", x="Tipe_Pembayaran", data=pembayaran_metode.sort_values(by="Banyak_Pembeli", ascending=False), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Pembeli", loc="center", fontsize=20)
ax[0].tick_params(axis ='x', labelsize=18)
 
sns.barplot(y="Rata_Rata_Pengeluaran", x="Tipe_Pembayaran", data=pembayaran_metode.sort_values(by="Rata_Rata_Pengeluaran", ascending=False), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Rata Rata Pengeluaran", loc="center", fontsize=20)
ax[1].tick_params(axis='x', labelsize=18)
 
sns.barplot(y="Total_Harga", x="Tipe_Pembayaran", data=pembayaran_metode.sort_values(by="Total_Harga", ascending=False), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Total Harga", loc="center", fontsize=20)
ax[2].tick_params(axis='x', labelsize=18)
 
plt.suptitle("Tipe Pembayaran Terbaik berdasarkan beberapa kategori", fontsize=20)
plt.show()

st.pyplot(fig)

st.caption('Copyright Raziq hehe')

