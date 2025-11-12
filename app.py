from geopy.geocoders import Nominatim
import time
import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

@st.cache_data
def load_and_process_data():
    #load the dataset(from kaggle)
    df = pd.read_csv('data/Superstore.csv', encoding='latin1')

    #perform basic data exploration

    #display the first few rows of the dataframe
    print(df.head())
    #display the summary statistics of the dataframe
    print(df.describe())
    #check for missing values in the dataframe
    print(df.isnull().sum())
    #display the data types of each column
    print(df.dtypes)
    #display the shape of the dataframe
    print(df.shape)
    #display the column names of the dataframe
    print(df.columns)
    #display the unique values in the 'Category' column
    print(df['Category'].unique())
    #display the count of unique values in the 'Category' column
    print(df['Category'].value_counts())

    #dropping the RowId and Country columns as they are not needed for analysis(redundant information)
    df = df.drop(columns=['Row ID', 'Country'])

    #converting the date columns to datetime format
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True, errors='coerce')

    #create new columns for year and month from the 'Order Date' column
    df['Order Year'] = df['Order Date'].dt.year
    df['Order Month'] = df['Order Date'].dt.month
    df['Order Day'] = df['Order Date'].dt.day
    df['Ship Delay'] = (df['Ship Date'] - df['Order Date']).dt.days

    #handle missing values but already checked and there are no missing values
    df = df.dropna(subset=['Postal Code'])  #drop rows where 'Postal Code' is missing

    #making sure everything looks good after preprocessing

    #displaying first rows of changed columns
    print(df[['Order Date', 'Ship Date']].head(10))
    print(df['Order Date'].min(), df['Order Date'].max())

    #print summary info of the dataframe
    print(df.info())
    print(df.describe)
    print(df.head())

    #checking the new 'Ship Delay' column makes sense
    print(df['Ship Delay'].describe())

    #making some business metrics

    #average order value
    order_value = df.groupby('Order ID')['Sales'].sum().mean()

    #Customer Lifetime Value (CLV)
    clv = df.groupby('Customer ID')['Profit'].sum().reset_index()

    #repeat purchase rate
    repeat_customers = df['Customer ID'].value_counts().gt(1).mean()

    #check out the values of the business metrics
    print(f"Average Order Value: ${order_value:.2f}")
    print(f"Repeat Purchase Rate: {repeat_customers:.2%}")

    #user engagement set up
    customer_orders = df.groupby('Customer ID').agg({
        'Order ID': 'nunique',
        'Sales': 'sum',
        'Profit': 'sum',
        'Order Date': ['min', 'max']
    }).reset_index()

    customer_orders.columns = ['Customer ID', 'Total Orders', 'Total Sales', 'Total Profit', 'First Order', 'Last Order']
    
    #load precomputed city coordinates(I already got coordinates for cities through api)
    coords_file = 'data/city_coordinates.csv'
    
    #fall back in case the file does not exist
    # Initialize geolocator
    geolocator = Nominatim(user_agent="superstore_dashboard")

    if not os.path.exists(coords_file):
        unique_cities = df[['City', 'State']].drop_duplicates().reset_index(drop=True)
        latitudes = []
        longitudes = []

        for idx, row in unique_cities.iterrows():
            try:
                location = geolocator.geocode(f"{row['City']}, {row['State']}")
                if location:
                    latitudes.append(location.latitude)
                    longitudes.append(location.longitude)
                else:
                    latitudes.append(None)
                    longitudes.append(None)
            except:
                latitudes.append(None)
                longitudes.append(None)
            time.sleep(1)  # prevent rate limiting

        unique_cities['Latitude'] = latitudes
        unique_cities['Longitude'] = longitudes
        unique_cities.to_csv(coords_file, index=False)
        print("City coordinates CSV created!")

    city_coords = pd.read_csv(coords_file)
    df = df.merge(city_coords, on=['City', 'State'], how='left')

    return df, customer_orders, order_value, repeat_customers, clv

#save the cleaned dataframe to a new CSV file
#df.to_csv('data/superstore_clean.csv', index=False)

#I chose to use Streamlit to create a simple dashboard to visualize some key metrics and trends in the Superstore dataset.

#load data w a spinner
with st.spinner("Loading and processing data..."):
    df, customer_orders, order_value, repeat_customers, clv = load_and_process_data()
st.success("Data loaded successfully!")

#streamlit app set up
st.set_page_config(page_title="User Engagement Dashboard", layout="wide")
st.title("Superstore User Engagement Dashboard")

#sidebar filters
st.sidebar.header("Filters")

#category filter
category_filter = st.sidebar.multiselect(
    "Select Category:",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

#region filter
region_filter = st.sidebar.multiselect(
    "Select Region:",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

#date range filter
date_filter = st.sidebar.date_input(
    "Select Date Range:",
    value=(df['Order Date'].min(), df['Order Date'].max()),
    min_value=df['Order Date'].min(),
    max_value=df['Order Date'].max()
)

#apply filters to the dataframe
filtered_df = df[
    (df["Category"].isin(category_filter)) &
    (df["Region"].isin(region_filter)) &
    (df['Order Date'] >= pd.to_datetime(date_filter[0])) &
    (df['Order Date'] <= pd.to_datetime(date_filter[1]))
]

#KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Average Order Value", f"${order_value:.2f}")
col2.metric("Repeat Purchase Rate", f"{repeat_customers:.2%}")
col3.metric("Total Customers", f"{df['Customer ID'].nunique()}")
col4.metric("Total Sales", f"${filtered_df['Sales'].sum():,.2f}")

total_orders = filtered_df['Order ID'].nunique()
avg_ship_delay = filtered_df['Ship Delay'].mean()
st.markdown(f"**Total Orders:** {total_orders:,} | **Average Ship Delay (days):** {avg_ship_delay:.2f}")

#sales over time
sales_over_time = filtered_df.groupby('Order Date')['Sales'].sum().reset_index()
fig_sales_time = px.line(sales_over_time, x='Order Date', y='Sales', title='Sales Over Time')
st.plotly_chart(fig_sales_time, use_container_width=True)

#interactive map of customer locations
st.subheader("Sales by Location (Interactive Map)")
sales_by_city = filtered_df.groupby(['City', 'State', 'Latitude', 'Longitude'])['Sales'].sum().reset_index()

fig_map = px.scatter_mapbox(
    sales_by_city,
    lat="Latitude",
    lon="Longitude",
    size="Sales",
    color="Sales",
    hover_name="City",
    hover_data={"State": True, "Sales": ":,.2f", "Latitude": False, "Longitude": False},
    color_continuous_scale=px.colors.cyclical.IceFire,
    size_max=25,
    zoom=3,
    mapbox_style="carto-positron"
)
st.plotly_chart(fig_map, use_container_width=True)
#profit by category
profit_by_category = filtered_df.groupby('Category')['Profit'].sum().reset_index()
fig_profit = px.bar(profit_by_category, x='Category', y='Profit', title="Profit by Category", color='Category')
st.plotly_chart(fig_profit, use_container_width=True)

#top products
st.subheader("Top 10 Products by Sales")
top_products = filtered_df.groupby('Product Name')['Sales'].sum().nlargest(10).reset_index()
fig_top_products = px.bar(top_products, x='Product Name', y='Sales', 
                          color='Sales', title="Top 10 Products by Sales",
                          hover_data=['Sales'])
st.plotly_chart(fig_top_products, use_container_width=True)

#top 10 customers
top_customers = filtered_df.groupby('Customer Name')['Sales'].sum().nlargest(10).reset_index()
fig_top_customers = px.bar(top_customers, x='Customer Name', y='Sales',
                           title="Top 10 Customers by Sales", color='Sales')
st.plotly_chart(fig_top_customers, use_container_width=True)

#ship delay distribution
st.subheader("Shipping Delay Distribution")
fig_ship_delay = px.histogram(filtered_df, x='Ship Delay', nbins=20, title="Ship Delay (days) Distribution")
st.plotly_chart(fig_ship_delay, use_container_width=True)

#orders by region
orders_by_region = filtered_df.groupby('Region')['Order ID'].nunique().reset_index()
fig_orders_region = px.pie(orders_by_region, names='Region', values='Order ID', title="Orders by Region")
st.plotly_chart(fig_orders_region, use_container_width=True)

#customer lifetime value distribution
st.subheader("Customer Lifetime Value (Profit)")
clv_filtered = clv[clv['Customer ID'].isin(filtered_df['Customer ID'].unique())]
fig_clv = px.histogram(clv_filtered, x='Profit', nbins=20, title="Customer Lifetime Value Distribution")
st.plotly_chart(fig_clv, use_container_width=True)

#Cohort Analysis
st.subheader("Cohort Analysis")

# Create cohort month from first order
df['Cohort Month'] = df.groupby('Customer ID')['Order Date'].transform('min').dt.to_period('M')

# Order month as period
df['Order Month Period'] = df['Order Date'].dt.to_period('M')

# Cohort Index: number of months since first purchase
df['Cohort Index'] = (df['Order Month Period'] - df['Cohort Month']).apply(lambda x: x.n)

# Cohort size by initial month
cohort_data = df.groupby(['Cohort Month', 'Cohort Index'])['Customer ID'].nunique().reset_index()
cohort_counts = cohort_data.pivot(index='Cohort Month', columns='Cohort Index', values='Customer ID')

# Retention rate
cohort_sizes = cohort_counts.iloc[:,0]
retention = cohort_counts.divide(cohort_sizes, axis=0)

# Convert index (Cohort Month) to string to avoid JSON serialization issues
retention.index = retention.index.astype(str)

# Plot heatmap
fig_cohort = px.imshow(
    retention,
    labels=dict(x="Months Since First Purchase", y="Cohort Month", color="Retention Rate"),
    x=retention.columns,
    y=retention.index,
    text_auto=True,
    aspect="auto",
    color_continuous_scale='Blues'
)
st.plotly_chart(fig_cohort, use_container_width=True)

