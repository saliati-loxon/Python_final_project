import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Banking Collections Dashboard",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Banking Collections Dashboard")
st.markdown("Analysis of loan portfolio health, risk factors, and operational efficiency.")

# --- 2. Load Data ---
collections = pd.read_csv("banking_collections_dataset.csv")

# --- 3. Data cleaning and feature engineering ---
## Convert Date columns to standard Datetime format
collections['Due_Date'] = pd.to_datetime(collections['Due_Date'])
collections['Last_Payment_Date'] = pd.to_datetime(collections['Last_Payment_Date'])

## Calculate "Paid Amount"
collections['Paid_Amount'] = collections['Loan_Amount'] - collections['Outstanding_Amount']

## Calculate Recovery Rate (%)
collections['Recovery_Rate'] = (collections['Paid_Amount'] / collections['Loan_Amount']) * 100

## EMI Burden
collections['EMI_Ratio'] = collections['EMI_Amount'] / collections['Loan_Amount']
    
## Region Renaming to Ireland Provinces
collections['Region'] = collections['Region'].replace({
        "East": "Leinster",
        "West": "Munster",
        "North": "Connacht",
        "South": "Ulster"
    })
## Fill missing values
collections['Last_Payment_Date'] = collections['Last_Payment_Date'].fillna("N/A")

## create a list - color map
##Apply: color_discrete_map=color_mapping
mypalette = ["#780000","#c1121f","#fdf0d5","#003049","#669bbc"]
color_mapping = {
    "Paid": "green",
    "Partially Paid": "orange",
    "Missed": mypalette[1]}


# --- 4. Filters for streamlit ---
st.sidebar.header("Filters")
selected_regions = st.sidebar.multiselect(
    "Select Region",
    options=collections['Region'].unique(),
    default=collections['Region'].unique()
)
filtered_data = collections[collections['Region'].isin(selected_regions)]

# --- 5. Display DataFrame ---
## create a download button
st.download_button("Download Raw Data", data=collections.to_csv(), file_name="collections_csv.csv")
## dataframe in table format
st.dataframe(filtered_data)

# --- 6. Visualizations ---
st.header("Risk and Portfolio Analysis")
## 1st row
## create a layout with two side-by-side vertical sections
col1, col2 = st.columns(2)

with col1:
    st.subheader("Q1: Portfolio Overview")
    loan_counts = filtered_data['Loan_Type'].value_counts().reset_index()
    loan_counts.columns = ['Loan_Type', 'Count']
    fig1 = px.pie(loan_counts, values='Count', names='Loan_Type', hole=0.6)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Q2: Debt by Region")
    region_debt = filtered_data.groupby('Region')['Outstanding_Amount'].sum().reset_index()
    fig2 = px.bar(region_debt, x='Region', y='Outstanding_Amount', color='Outstanding_Amount')
    st.plotly_chart(fig2, use_container_width=True)

## 2nd row
col3, col4 = st.columns(2)
with col3:
    st.subheader("Q3: Payment Status Breakdown")
    status_counts = filtered_data['Payment_Status'].value_counts().reset_index()
    status_counts.columns = ['Payment_Status', 'Count']
    fig3 = px.bar(status_counts, x='Count', y='Payment_Status', orientation='h', color='Payment_Status', 
                  color_discrete_map=color_mapping)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Q9: Status by Account Type")
    # Using your sorting logic
    acct_status = filtered_data.groupby(['Account_Type', 'Payment_Status']).size().reset_index(name='Count')
    fig9 = px.bar(
        acct_status, 
        x='Account_Type', 
        y='Count', 
        color='Payment_Status', 
        barmode='group',
        category_orders={'Account_Type': ["Current", "Credit", "Savings"]}
    )
    st.plotly_chart(fig9, use_container_width=True)

## 3rd row
col5, col6 = st.columns(2)

with col5:
    st.subheader("Q4: Outstanding Debt by Risk Level")
    risk_debt = filtered_data.groupby('Risk_Level')['Outstanding_Amount'].sum().reset_index()
    
    fig4 = px.bar(
        risk_debt,
        x='Risk_Level',
        y='Outstanding_Amount',
        color='Risk_Level',
        category_orders={'Risk_Level': ['Low', 'Medium', 'High']},
        text_auto='.2s'
    )
    st.plotly_chart(fig4, use_container_width=True)

with col6:
    st.subheader("Q5: Customer Score vs. Payment Delay")
    fig5 = px.scatter(
        filtered_data,
        x='Customer_Score',
        y='Payment_Delay_Days',
        color='Risk_Level', 
        size='Outstanding_Amount', 
        opacity=0.6,
        hover_data=['Loan_Type']
    )
    st.plotly_chart(fig5, use_container_width=True)

## 4th row
col7, col8 = st.columns(2)
with col7:
    st.subheader("Q6: EMI Amount Distribution by Status")
    fig6 = px.box(
        filtered_data,
        x='Payment_Status',
        y='EMI_Amount',
        color='Payment_Status',
        points='outliers'
    )
    st.plotly_chart(fig6, use_container_width=True)

with col8:
    st.subheader("Q7: Avg Payment Delay by Loan Type")
    avg_delay = filtered_data.groupby('Loan_Type')['Payment_Delay_Days'].mean().reset_index()
    
    fig7 = px.bar(
        avg_delay,
        x='Loan_Type',
        y='Payment_Delay_Days',
        color='Payment_Delay_Days',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")
st.header("Operational Performance")

## 5th row
col9, col10 = st.columns(2)
with col9:
    st.subheader("Q8: Top 10 Collection Agents (Repaid)")
    agent_perf = filtered_data.groupby('Collection_Agent')['Paid_Amount'].sum().nlargest(15).reset_index().sort_values(by='Paid_Amount', ascending=False)
    
    fig8 = px.bar(
        agent_perf,
        x='Paid_Amount',
        y='Collection_Agent',
        orientation='h', 
        text_auto='.2s',
        color='Paid_Amount'
    )
    fig8.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig8, use_container_width=True)

with col10:
    st.subheader("Q10: Avg Past Due Days (Region vs Loan type)")
    fig10 = px.density_heatmap(
        filtered_data, 
        x='Region', 
        y='Loan_Type', 
        z='Payment_Delay_Days', 
        histfunc='avg',
        text_auto='.1f'
    )
    st.plotly_chart(fig10, use_container_width=True)