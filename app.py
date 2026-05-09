import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =========================
# Page Config
# =========================
st.set_page_config(page_title="Housing Price Dashboard", layout="wide")

# =========================
# Load & Clean Data
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("final_dataset.csv")

    df.columns = df.columns.str.strip()

    df = df.rename(columns={
        "State_Name": "state",
        "median_home_value": "price",
        "median_income": "income",
        "pm25_state_mean": "pm25",
        "climate_event_count_5yr": "risk",
        "Crime_Rate": "crime",
        "Avg_Home_Insurance_2022": "insurance"
    })

    numeric_cols = ["price", "income", "pm25", "risk", "crime", "insurance"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    return df

df = load_data()

us_state_to_abbrev = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
    "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    "District of Columbia": "DC"
}

# =========================
# Sidebar
# =========================
# Navigation
st.sidebar.subheader("Navigation")
selected_page = st.sidebar.radio(
    "Select a page",
    [
        "🌍 Overview",
        "🏠 House Price",
        "💵 Income",
        "🛡️ Insurance",
        "🌪️ Climate",
        "🚨 Crime",
        "💨 PM2.5"
    ],
    label_visibility="collapsed"
)

# Filters
st.sidebar.subheader("Filters")
selected_states = st.sidebar.multiselect(
    "Select states to compare:",
    options=sorted(df["state"].unique()),
    default=[],
    placeholder="🔍 Choose states..."
)

if len(selected_states) == 0:
    st.sidebar.info("🌍 Currently showing: All States")
    plot_df = df
else:
    st.sidebar.success(f" Filter Active: Comparing {len(selected_states)} states")
    plot_df = df[df["state"].isin(selected_states)]

st.sidebar.divider()


st.title("U.S. Housing Environment Analyze Dashboard")
st.caption("Analyze housing prices with income, air quality, climate risk, crime rate, and insurance cost.")
st.divider()

if selected_page == "🌍 Overview":
    # =========================
    # U.S. Housing Price Distribution
    # =========================
    st.subheader("🗺️ U.S. Housing Price Distribution")
    st.markdown("##### *From coast to coast, how extreme is the geographic divide in U.S. housing prices?*")
    map_df = plot_df.copy()
    map_df["state_code"] = map_df["state"].map(us_state_to_abbrev)

    fig_map = px.choropleth(
        map_df,
        locations="state_code",
        locationmode="USA-states",
        color="price",
        hover_name="state",
        scope="usa",
        color_continuous_scale="Reds",
        labels={'price': 'House Price ($)'},
        range_color=[50000, 800000]
    )

    fig_map.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>House Price: $%{z:,.0f}<extra></extra>"
    )

    fig_map.add_trace(go.Scattergeo(
        locations=map_df["state_code"], 
        locationmode="USA-states",      
        text=map_df["state_code"],      
        mode="text",                    
        textfont=dict(color="black", size=20), 
        hoverinfo="skip",                
    ))

    fig_map.update_layout(
        height=1000,
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        geo=dict(
            bgcolor='rgba(0,0,0,0)'
        ),
        coloraxis_colorbar=dict(
            title_font=dict(size=22),
            tickfont=dict(size=20),
            thickness=30
        ), 
        hoverlabel=dict(
            font=dict(
                size=24,
                color="black"
            ),
            align="left"
        )
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # =========================
    # Income vs. Insurance Cost
    # =========================
    st.subheader("📈 Income vs. Insurance Cost")
    st.markdown("##### *Does earning a higher income inevitably mean paying more for risk, and how large is the real gap between income and insurance costs across different states?*")

    sort_option = st.radio(
        "Sort by:",
        [ "State Name (A-Z)","High to Low (Income)", "High to Low (Insurance)" ],
        horizontal=True
    )

    if sort_option == "High to Low (Income)":
        df_ins = plot_df.sort_values("income", ascending=False)
    elif sort_option == "High to Low (Insurance)":
        df_ins = plot_df.sort_values("insurance", ascending=False)
    else:
        df_ins = plot_df.sort_values("state", ascending=True)

    fig_ins = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.1,  
        subplot_titles=("Income by State", "Insurance Cost by State")
    )

    # Row 1
    fig_ins.add_trace(
        go.Scatter(
            x=df_ins["state"], 
            y=df_ins["income"], 
            customdata=df_ins["insurance"],
            name="Income",
            mode="lines+markers",
            line=dict(color="#00BFFF", width=1),
            hovertemplate=(
                "<b style='color:#00BFFF;'>━</b> Income: $%{y:,.0f}<br>" +
                "<b style='color:#FF7F50;'>━</b> Insurance: $%{customdata:,.0f}<extra></extra>"
            )
        ),
        row=1, col=1
    )

    # Row 2
    fig_ins.add_trace(
        go.Scatter(
            x=df_ins["state"], 
            y=df_ins["insurance"], 
            customdata=df_ins["income"],
            name="Insurance",
            mode="lines+markers",
            line=dict(color="#FF7F50", width=1),
            hovertemplate=(
                "<b style='color:#00BFFF;'>━</b> Income: $%{customdata:,.0f}<br>" +
                "<b style='color:#FF7F50;'>━</b> Insurance: $%{y:,.0f}<extra></extra>"
            )
        ),
        row=2, col=1
    )

    fig_ins.update_layout(
        height=600, 
        showlegend=False, 
        hovermode="x", 
        hoverlabel=dict(
            font=dict(
                size=24,
                color="black"
            ),
            align="left"
        )
    )
    fig_ins.update_xaxes(
        tickmode='linear', dtick=1, tickangle=-45, tickfont=dict(size=10),
        showspikes=True, spikemode="across", spikedash="solid", 
        spikecolor="rgba(150, 150, 150, 0.6)", spikethickness=1
    )
    fig_ins.update_yaxes(title_text="Income ($)", row=1, col=1)
    fig_ins.update_yaxes(title_text="Insurance ($)", row=2, col=1)
    
    fig_ins.update_xaxes(
    title_font=dict(size=20),
    tickfont=dict(size=20),
    tickmode='linear',
    dtick=1,
    tickangle=-45
    )

    fig_ins.update_yaxes(
        title_font=dict(size=20),
        tickfont=dict(size=20)
    )

    st.plotly_chart(fig_ins, use_container_width=True)

    # =========================
    # PM2.5
    # =========================
    st.subheader("🌫️ PM2.5 Air Quality")
    st.markdown("##### *The cost of every breath: Which state offers the safest and cleanest air quality?*")

    pm_sort = st.radio(
        "Sort by:",
        ["State Name (A-Z)", "High to Low", "Low to High"],
        horizontal=True
    )

    if pm_sort == "High to Low":
        df_pm = plot_df.sort_values("pm25", ascending=False)
    elif pm_sort == "Low to High":
        df_pm = plot_df.sort_values("pm25", ascending=True)
    else:
        df_pm = plot_df.sort_values("state", ascending=True)

    fig_pm = px.bar(
        df_pm,
        x="state",
        y="pm25",
        color="pm25",
        color_continuous_scale="Viridis",
        labels={"pm25": "PM2.5", "state": "State"},
    )

    fig_pm.update_traces(
        hovertemplate="<b>%{x}</b><br>PM2.5: %{y:.1f} µg/m³<extra></extra>",
        texttemplate="",
    )

    fig_pm.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        coloraxis_showscale=False,
        hoverlabel=dict(
            font=dict(
                size=24,
                color="black"
            ),
            align="left"
        )
    )
    fig_pm.update_xaxes(
    title_font=dict(size=20),
    tickfont=dict(size=20),
    tickmode='linear',
    dtick=1,
    tickangle=-45
    )

    fig_pm.update_yaxes(
        title_font=dict(size=20),
        tickfont=dict(size=20)
    )
    st.plotly_chart(fig_pm, use_container_width=True)

    # =========================
    # Integrated Risk Assessment: Climate & Crime (Combined Living Risks)
    # =========================
    st.subheader("🛡️ Integrated Risk Assessment: Climate & Crime (Combined Living Risks)")
    st.markdown("##### *Between natural disasters and crime, which states pose the highest combined threat to their residents?*")

    df_risk = plot_df.copy()
    df_risk = df_risk.rename(columns={"risk": "climate"})
    df_risk['total_risk'] = df_risk['climate'] + df_risk['crime']

    risk_sort = st.radio(
        "Sort by:",
        [ 
            "State Name (A-Z)",
            "High to low (Overall)",
            "High to low (Crime)",
            "High to low (Climate)"
        ],
        horizontal=True,
    )

    if risk_sort == "High to low (Overall)":
        df_risk = df_risk.sort_values("total_risk", ascending=False)

    elif risk_sort == "High to low (Crime)":
        df_risk = df_risk.sort_values("crime", ascending=False)
    elif risk_sort == "High to low (Climate)":
        df_risk = df_risk.sort_values("climate", ascending=False)
    else:
        df_risk = df_risk.sort_values("state", ascending=True)

    fig_risk = px.bar(
        df_risk,
        x="state",
        y=["crime", "climate"],
        labels={
            "value": "Risk Score", 
            "variable": "Risk Factors", 
            "state": "State",
        },
        color_discrete_map={"crime": "#EF553B", "climate": "#636EFA"},
        barmode="stack"
    )

    fig_risk.data[0].hovertemplate = "Crime: %{y:.0f}<extra></extra>"
    fig_risk.data[1].hovertemplate = "Climate: %{y:.0f}<extra></extra>"

    fig_risk.update_layout(
        height=500,
        hovermode="x unified",
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=1), 
        hoverlabel=dict(
            font=dict(
                size=24,
                color="black"
            ),
            align="left"
        )
    )
    fig_risk.update_xaxes(
    title_font=dict(size=20),
    tickfont=dict(size=20),
    tickmode='linear',
    dtick=1,
    tickangle=-45
    )

    fig_risk.update_yaxes(
        title_font=dict(size=20),
        tickfont=dict(size=20)
    )

    st.plotly_chart(fig_risk, use_container_width=True)

    # =========================
    # Price vs Income & The Affordability Trend
    # =========================
    st.subheader("💰 Price vs Income & The Affordability Trend")
    st.markdown("##### *Can you afford your dream home? Where in the U.S. does income actually keep up with housing costs?*")

    fig_scatter = px.scatter(
        plot_df, 
        x="income", 
        y="price", 
        color="state",
        hover_name="state", 
        trendline="ols",
        trendline_scope="overall",
        labels={
            "income": "Income ($)",
            "price": "Home Price ($)",
            "state": "State"
        }
    )

    fig_scatter.update_traces(
        marker=dict(size=20, opacity=0.6, line=dict(width=1, color="white")),
        selector=dict(mode="markers"),
        hovertemplate="<b>%{hovertext}</b><br>Income: $%{x:,.0f}<br>Price: $%{y:,.0f}<extra></extra>"
    )

    fig_scatter.update_traces(
        line=dict(color="#FF7F50", width=3, dash="dot"),
        hovertemplate="<b>📈 Trendline</b><br>Income: $%{x:,.0f}<br>Expected Price: $%{y:,.0f}<extra></extra>",
        selector=dict(mode="lines")
    )

    fig_scatter.update_layout(
    height=600,
    hovermode="closest",
    
    xaxis=dict(
        title_font=dict(size=20),
        tickfont=dict(size=20)
    ),
    
    yaxis=dict(
        title_font=dict(size=20),
        tickfont=dict(size=20)
    ),
    legend_title_text="State (Scroll)",
    legend=dict(
        title_font=dict(size=20),
        font=dict(size=14),
        itemsizing="constant"
    ), 
    hoverlabel=dict(
        font=dict(
            size=24,
            color="black"
        ),
        align="left"
    ))

    st.plotly_chart(fig_scatter, use_container_width=True)

    # =========================
    # Variable Correlation Heatmap
    # =========================
    st.subheader("🌡️ Variable Correlation Heatmap")
    st.markdown("##### *How do housing prices, income, and living risks actually influence one another behind the scenes?*")

    corr_matrix = plot_df[["price", "income", "pm25", "risk", "crime", "insurance"]].corr()

    fig_corr = px.imshow(
        corr_matrix, 
        text_auto=".2f", 
        aspect="auto",
        color_continuous_scale="RdBu_r"
    )

    fig_corr.update_traces(
        hovertemplate="<b>%{x}</b> vs <b>%{y}</b><br>Correlation: %{z:.2f}<extra></extra>",
        textfont_size=20
    )

    fig_corr.update_layout(
        height=600,
        hoverlabel=dict(
            bgcolor="white",
            font=dict(size=24, color="black"),
            align="left"
        ),
        xaxis=dict(tickfont=dict(size=20)),
        yaxis=dict(tickfont=dict(size=20)), 
        coloraxis_colorbar=dict(
        tickfont=dict(size=25),
        thickness=30
    )
    )

    fig_corr.update_xaxes(tickangle=-45)

    st.plotly_chart(fig_corr, use_container_width=True)
    pass

# ==========================================
# 2. 🏘️ House Price 
# ==========================================
elif selected_page == "🏠 House Price":
    st.subheader("🏠 House Price by State")
    
    sort_house = st.radio(
        "Sort by:",
        ["State Name (A-Z)", "High to Low"],
        horizontal=True,
        key="sort_house_btn"
    )
    
    if sort_house == "High to Low":
        df_house = plot_df.sort_values("price", ascending=False)
    else:
        df_house = plot_df.sort_values("state", ascending=True)
        
    fig_price = px.bar(
        df_house,
        x="state",
        y="price",
        text="price"
    )
    fig_price.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    
    fig_price.update_xaxes(tickmode='linear', dtick=1, tickangle=-45, tickfont=dict(size=10))
    st.plotly_chart(fig_price, use_container_width=True)
    pass


# ==========================================
# 3. 💵 Income 
# ==========================================
elif selected_page == "💵 Income":
    st.subheader("💰 Income by State")
    
    sort_income = st.radio(
        "Sort by:",
        ["State Name (A-Z)", "High to Low"],
        horizontal=True,
        key="sort_income_btn"
    )
    
    if sort_income == "High to Low":
        df_income = plot_df.sort_values("income", ascending=False)
    else:
        df_income = plot_df.sort_values("state", ascending=True)
        
    fig_income = px.bar(
        df_income,
        x="state",
        y="income",
        text="income"
    )
    fig_income.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig_income.update_xaxes(tickmode='linear', dtick=1, tickangle=-45, tickfont=dict(size=10))
    st.plotly_chart(fig_income, use_container_width=True)
    pass


# ==========================================
# 4. 🛡️ Insurance 
# ==========================================
elif selected_page == "🛡️ Insurance":
    st.subheader("🛡️ Insurance Cost by State")
    
    sort_ins = st.radio(
        "Sort by:",
        ["State Name (A-Z)", "High to Low"],
        horizontal=True,
        key="sort_ins_btn"
    )
    
    if sort_ins == "High to Low":
        df_ins = plot_df.sort_values("insurance", ascending=False)
    else:
        df_ins = plot_df.sort_values("state", ascending=True)
        
    fig_ins = px.bar(
        df_ins,
        x="state",
        y="insurance",
        text="insurance"
    )
    fig_ins.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig_ins.update_xaxes(tickmode='linear', dtick=1, tickangle=-45, tickfont=dict(size=10))
    st.plotly_chart(fig_ins, use_container_width=True)
    pass


# ==========================================
# 5. 🌪️ Climate Risk 
# ==========================================
elif selected_page == "🌪️ Climate":
    st.subheader("🌪️ Climate Risk by State")
    
    sort_risk = st.radio(
        "Sort by:",
        ["State Name (A-Z)", "High to Low"],
        horizontal=True,
        key="sort_risk_btn"
    )
    
    if sort_risk == "High to Low":
        df_risk = plot_df.sort_values("risk", ascending=False)
    else:
        df_risk = plot_df.sort_values("state", ascending=True)
        
    fig_risk = px.bar(
        df_risk,
        x="state",
        y="risk",
        text="risk"
    )
    fig_risk.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    fig_risk.update_xaxes(tickmode='linear', dtick=1, tickangle=-45, tickfont=dict(size=10))
    st.plotly_chart(fig_risk, use_container_width=True)
    pass


# ==========================================
# 6. 🚨 Crime 
# ==========================================
elif selected_page == "🚨 Crime":
    st.subheader("🚨 Crime Rate by State")
    
    sort_crime = st.radio(
        "Sort by:",
        ["State Name (A-Z)", "High to Low"],
        horizontal=True,
        key="sort_crime_btn"
    )
    
    if sort_crime == "High to Low":
        df_crime = plot_df.sort_values("crime", ascending=False)
    else:
        df_crime = plot_df.sort_values("state", ascending=True)
        
    fig_crime = px.bar(
        df_crime,
        x="state",
        y="crime",
        text="crime"
    )
    fig_crime.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    fig_crime.update_xaxes(tickmode='linear', dtick=1, tickangle=-45, tickfont=dict(size=10))
    st.plotly_chart(fig_crime, use_container_width=True)
    pass


# ==========================================
# 7. 💨 PM2.5 
# ==========================================
elif selected_page == "💨 PM2.5":
    st.subheader("💨 PM2.5 by State")
    
    sort_pm25 = st.radio(
        "Sort by:",
        ["State Name (A-Z)", "High to Low"],
        horizontal=True,
        key="sort_pm25_btn"
    )
    
    if sort_pm25 == "High to Low":
        df_pm25 = plot_df.sort_values("pm25", ascending=False)
    else:
        df_pm25 = plot_df.sort_values("state", ascending=True)
        
    fig_pm25 = px.bar(
        df_pm25,
        x="state",
        y="pm25",
        text="pm25"
    )
    fig_pm25.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_pm25.update_xaxes(tickmode='linear', dtick=1, tickangle=-45, tickfont=dict(size=10))
    st.plotly_chart(fig_pm25, use_container_width=True)
    pass

# =========================
# Insights
# =========================
st.sidebar.subheader("🧠 Insights")

df_selected = plot_df.copy()

highest_price = df_selected.loc[df_selected["price"].idxmax()]
lowest_price = df_selected.loc[df_selected["price"].idxmin()]

df_selected["affordability"] = df_selected["price"] / df_selected["income"]

best_affordable = df_selected.loc[df_selected["affordability"].idxmin()]
worst_affordable = df_selected.loc[df_selected["affordability"].idxmax()]

st.sidebar.markdown(f"""
### House Price:

- **Highest Price:** {highest_price['state']} (${highest_price['price']:,.0f})
- **Lowest Price:** {lowest_price['state']} (${lowest_price['price']:,.0f})

### Affordability:

- **Best:** {best_affordable['state']}
- **Worst:** {worst_affordable['state']}
""")
import streamlit as st
import google.generativeai as genai

# ==========================================
# AI Agent
# ==========================================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel('gemini-2.5-flash')

with st.sidebar:
    st.divider()
    st.subheader("🤖 AI Data Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    chat_container = st.container(height=450)

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("Ask me about the data..."):
        
        with chat_container:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            try:
                data_summary = plot_df.describe().to_string()
                current_filter = selected_states if 'selected_states' in locals() and selected_states else "All States"
            except NameError:
                data_summary = "No any data load yet."
                current_filter = "Unexpect"

            full_prompt = f"""
            You are a professional Data Science assistant.
            Here is the summary of the housing data the user is currently looking at:
            {data_summary}

            User current filters: {current_filter}
            User Question: {prompt}

            Please provide a concise, data-driven answer in English.
            If the user asks for a recommendation, consider variables like Crime Rate, Insurance, and PM2.5.

            IMPORTANT RULES:
            1. DO NOT use the '$' symbol for currency; use 'USD' instead to avoid rendering issues in Streamlit.
            2. Be analytical and base your answers on the provided data summary.
            """

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = model.generate_content(full_prompt)
                        ai_text = response.text
                        
                        st.markdown(ai_text)
                        
                        st.session_state.messages.append({"role": "assistant", "content": ai_text})
                    except Exception as e:
                        st.error(f"AI no reponds: {e}")
# =========================
# Footer
# =========================
st.markdown("---")
st.markdown("""
### 📌 Project Overview

**Problem Statement & Motivation:**
This dashboard aims to analyze how housing prices, income, and environmental and living risks interact to affect affordability and quality of life across U.S. states.

**Data Resources:**
- **U.S. Census:** Income & Housing Data
- **EPA:** PM2.5 (Air Quality)
- **FEMA:** Climate Risk Data
- **U.S. Crime Data:** Crime Rate
- **Insurance Data:** Home Insurance Costs

**Methodology:**
- **Python:** Pandas for data cleaning & processing
- **Plotly:** Data visualization (maps, charts, heatmaps)
- **Streamlit:** Interactive dashboard development
- **Analytical Setup:** Correlation Analysis (relationship between variables)
- **Data Preprocessing:** Handling missing values using median imputation

**Contributors:** Cheng-Han Chung & Yu-Tai Lee
""")