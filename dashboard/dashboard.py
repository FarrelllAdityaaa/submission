import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Helper function untuk rata-rata review score
def average_review_score_df(df):
    avg_review_score = df.groupby('product_category_name')['review_score'].mean().reset_index()
    return avg_review_score

# Helper function untuk total penjualan berdasarkan city
def sum_of_category_product_city_df(df):
    top_product_per_city = df.groupby('seller_city').product_category_name.value_counts().sort_values(ascending=False).head(10)
    top_product_per_city_df = top_product_per_city.reset_index(name='count')
    return top_product_per_city_df

# Helper function untuk total penjualan berdasarkan state
def sum_of_category_product_state_df(df):
    top_product_per_state = df.groupby('seller_state').product_category_name.value_counts().sort_values(ascending=False).head(10)
    top_product_per_state_df = top_product_per_state.reset_index(name='count')
    return top_product_per_state_df

# Helper function untuk total pendapatan seller berdasarkan city
def seller_city_revenue_df(df):
    city_revenue = df.groupby('seller_city')['price'].sum().sort_values(ascending=False).head(5)
    return city_revenue

# Helper function untuk total pendapatan seller berdasarkan state
def seller_state_revenue_df(df):
    state_revenue = df.groupby('seller_state')['price'].sum().sort_values(ascending=False).head(5)
    return state_revenue

# Helper function untuk freight value (ongkir)
def freight_value_most_df(df):
    freight_value_most = df.groupby('product_category_name')['freight_value'].sum().sort_values(ascending=False).head(5)
    return freight_value_most

def freight_value_less_df(df):
    freight_value_less = df.groupby('product_category_name')['freight_value'].sum().sort_values(ascending=True).head(5)
    return freight_value_less

# Helper function untuk RFM
def rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", 
        "order_id": "nunique", 
        "price": "sum" 
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    rfm_df['customer_id_numeric'] = pd.factorize(rfm_df['customer_id'])[0] + 1
    return rfm_df

# Load dataset 
# all_df = pd.read_csv("all_df.csv")
all_df = pd.read_csv("dashboard/all_df.csv")

# Mengatasi NaN pada order_purchase_timestamp
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'], errors='coerce')

# Drop Nilai Null yang jumlahnya sedikit
all_df = all_df.dropna(subset=['product_category_name',
                                'product_name_lenght',
                                'product_height_cm',
                                'product_width_cm',
                                'product_description_lenght',
                                'product_photos_qty',
                                'product_weight_g',
                                'customer_id',
                                'order_status',
                                'order_purchase_timestamp',
                                'order_approved_at',
                                'order_delivered_carrier_date',
                                'order_delivered_customer_date',
                                'order_estimated_delivery_date',
                                'payment_sequential',
                                'payment_type',
                                'payment_installments',
                                'payment_value',
                                'customer_unique_id',
                                'customer_zip_code_prefix',
                                'customer_city',
                                'customer_state'
                                ])

# Mengatasi permasalahan tipe data datetime karena ulah dari to_csv()
all_df['shipping_limit_date'] = pd.to_datetime(all_df['shipping_limit_date'], format='mixed')
all_df['review_creation_date'] = pd.to_datetime(all_df['review_creation_date'], format='mixed')
all_df['review_answer_timestamp'] = pd.to_datetime(all_df['review_answer_timestamp'], format='mixed')
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'], format='mixed')
all_df['order_approved_at'] = pd.to_datetime(all_df['order_approved_at'], format='mixed')
all_df['order_delivered_customer_date'] = pd.to_datetime(all_df['order_delivered_customer_date'], format='mixed')
all_df['order_delivered_carrier_date'] = pd.to_datetime(all_df['order_delivered_carrier_date'], format='mixed')
all_df['order_estimated_delivery_date'] = pd.to_datetime(all_df['order_estimated_delivery_date'], format='mixed')

# Panggil semua helper function yang ada
review_score = average_review_score_df(all_df)
sum_of_category_product_city = sum_of_category_product_city_df(all_df)
sum_of_category_product_state = sum_of_category_product_state_df(all_df)
seller_city_revenue = seller_city_revenue_df(all_df)
seller_state_revenue = seller_state_revenue_df(all_df)
freight_values_most = freight_value_most_df(all_df)
freight_values_less = freight_value_less_df(all_df)
rfm = rfm_df(all_df)

# Header
st.header(':sparkles: E-Commerce Public Information :sparkles:')

st.subheader('Best & Worst Review Product')

# Visualisasi bar chart untuk review score tertinggi
fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(8, 8))
sns.barplot(x='review_score', y='product_category_name', data=review_score.sort_values(by="review_score", ascending=False).head(5), ax=ax[0])
ax[0].set_title('Best Review Product')
ax[0].set_ylabel('Kategori Produk')
ax[0].set_xlabel('Review Score')
ax[0].tick_params(axis='y', labelsize=20)
ax[0].tick_params(axis='x', labelsize=15)

# Visualisasi bar chart untuk review score terendah
sns.barplot(x='review_score', y='product_category_name', data=review_score.sort_values(by="review_score", ascending=True).head(5), ax=ax[1])
ax[1].set_title('Worst Review Product')
ax[1].set_ylabel('Kategori Produk')
ax[1].set_xlabel('Review Score')
ax[1].tick_params(axis='y', labelsize=20)
ax[1].tick_params(axis='x', labelsize=15)
plt.subplots_adjust(hspace=0.4)

st.pyplot(fig)


st.subheader('Category Product Sold Based on City and State')

# Visualisasi bar chart untuk kategori produk yang terjual berdasarkan city dan state
fig, ax = plt.subplots(figsize=(16, 10))

sns.barplot(
    x='seller_city',
    y='count',
    hue='product_category_name',
    data=sum_of_category_product_city,
    ax=ax
)

# Mengatur judul dan label
ax.set_title('Top 10 Kategori Produk Paling Banyak Terjual Berdasarkan City', loc="center", fontsize=25)
ax.set_xlabel('Seller City', fontsize=22)
ax.set_ylabel('Count', fontsize=22)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
ax.legend(title='product_category_name', title_fontsize='20', loc='upper right', prop={'size': 18})

st.pyplot(fig)

fig, ax = plt.subplots(figsize=(16, 10))

sns.barplot(
    x='seller_state',
    y='count',
    hue='product_category_name',
    data=sum_of_category_product_state,
    ax=ax
)

# Mengatur judul dan label
ax.set_title('Top 10 Kategori Produk Paling Banyak Terjual Berdasarkan State', loc="center", fontsize=25)
ax.set_xlabel('Seller State', fontsize=22)
ax.set_ylabel('Count', fontsize=22)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.set_xticklabels(ax.get_xticklabels(), rotation=0, ha='right')
ax.legend(title='product_category_name', title_fontsize='20', loc='upper right', prop={'size': 18})

st.pyplot(fig)


st.subheader('Highest Seller Revenue Based on City and State')

# Visualisasi bar chart untuk menampilkan lokasi seller dengan pendapatan terbanyak berdasarkan city dan state
fig, ax = plt.subplots(figsize=(16, 10))
colors = ['b' if (x < seller_city_revenue.max()) else 'r' for x in seller_city_revenue]
seller_city_revenue.plot(kind='bar', color=colors, ax=ax)

ax.set_title('Top 5 Lokasi Seller dengan Pendapatan Terbanyak (Berdasarkan City)', loc="center", fontsize=25)
ax.set_xlabel('Kota', fontsize=22)
ax.set_ylabel('Total Pendapatan', fontsize=22)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

st.pyplot(fig)

fig, ax = plt.subplots(figsize=(16, 10))
colors = ['b' if (x < seller_state_revenue.max()) else 'r' for x in seller_state_revenue]
seller_state_revenue.plot(kind='bar', color=colors, ax=ax)

ax.set_title('Top 5 Lokasi Seller dengan Pendapatan Terbanyak (Berdasarkan State)', loc="center", fontsize=25)
ax.set_xlabel('Negara Bagian', fontsize=22)
ax.set_ylabel('Total Pendapatan', fontsize=22)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

st.pyplot(fig)


st.subheader('Category Product with Highest and Lowest Freight Values (Ongkir)')

col1, col2 = st.columns(2)

# freight_values['freight_value'] = freight_values['freight_value'].astype(float)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = ['b' if (x < freight_values_most.max()) else 'r' for x in freight_values_most]

    freight_values_most.plot(kind='bar', color=colors, ax=ax)

    ax.set_title('Top 5 Kategori Barang dengan Ongkir Terbanyak', loc="center", fontsize=50)
    ax.set_xlabel('Kategori Barang', fontsize=35)
    ax.set_ylabel('Freight Value (Ongkir)', fontsize=30)
    ax.tick_params(axis='y', labelsize=35)
    ax.tick_params(axis='x', labelsize=35)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = ['r' if (x == freight_values_less.min()) else 'b' for x in freight_values_less]

    freight_values_less.plot(kind='bar', color=colors, ax=ax)

    ax.set_title('Top 5 Kategori Barang dengan Ongkir Paling Sedikit', loc="center", fontsize=50)
    ax.set_xlabel('Kategori Barang', fontsize=35)
    ax.set_ylabel('Freight Value (Ongkir)', fontsize=35)
    ax.tick_params(axis='y', labelsize=35)
    ax.tick_params(axis='x', labelsize=30)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    plt.subplots_adjust(wspace=0.4)

    st.pyplot(fig)


st.subheader('Best Customer Based on RFM Parameters')

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm.monetary.mean(), "BRL", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
 
sns.barplot(y="recency", x="customer_id_numeric", data=rfm.sort_values(by="recency", ascending=True).head(5), ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="frequency", x="customer_id_numeric", data=rfm.sort_values(by="frequency", ascending=False).head(5), ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="monetary", x="customer_id_numeric", data=rfm.sort_values(by="monetary", ascending=False).head(5), ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)
