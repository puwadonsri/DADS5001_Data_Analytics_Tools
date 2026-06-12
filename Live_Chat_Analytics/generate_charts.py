import json
import os
import re
import base64
import io

import pandas as pd
import plotly.express as px
import plotly.io as pio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from wordcloud import WordCloud

THAI_FONT = r"C:\Windows\Fonts\tahoma.ttf"

JSON_CHAT_LOG = "json_dataset/chat_log.json"
JSON_CHAT_ANALYTICS = "json_dataset/chat_analytics.json"
OUTPUT_DIR = "images"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_analytics_data():
    if os.path.exists(JSON_CHAT_ANALYTICS):
        with open(JSON_CHAT_ANALYTICS, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data:
            records = [{'Name': d['setName'], 'Total': d['setAmount']} for d in data]
            records.sort(key=lambda x: x['Total'], reverse=True)
            return pd.DataFrame(records)
    return pd.DataFrame(columns=['Name', 'Total'])


def load_chat_log_data():
    if os.path.exists(JSON_CHAT_LOG):
        with open(JSON_CHAT_LOG, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data:
            records = [{'Date': d['dateTime'][0:10], 'Name': d['authorName'], 'Chat': d['Message']} for d in data]
            return pd.DataFrame(records)
    return pd.DataFrame(columns=['Date', 'Name', 'Chat'])


def save_bar_chart(df, x_col, y_col, title, filename, color="#007bff"):
    fig = px.bar(
        df, x=x_col, y=y_col, title=title,
        text_auto=True, color_discrete_sequence=[color],
        height=500
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Number of Mentions",
        margin=dict(l=40, r=40, t=50, b=120),
        xaxis_tickangle=-45,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    pio.write_image(fig, os.path.join(OUTPUT_DIR, filename), scale=2, width=1000, height=500)
    print(f"Saved: {filename}")


# --- 1. Top 10 Stocks ---
df = load_analytics_data()
df_top10 = df.head(10)
save_bar_chart(df_top10, 'Name', 'Total', "Top 10 Most Mentioned Stocks (SET)", "top10_stocks.png")

# --- 2. All Stocks ---
save_bar_chart(df, 'Name', 'Total', "All Mentioned Stocks (SET)", "all_stocks.png")

# --- 3. Viewers by Date ---
df_log = load_chat_log_data()
if not df_log.empty:
    df_viewers = (
        df_log.groupby('Date')['Name']
        .nunique()
        .reset_index()
        .rename(columns={'Name': 'Unique Viewers', 'Date': 'Date'})
        .sort_values('Date')
    )
else:
    df_viewers = pd.DataFrame(columns=['Date', 'Unique Viewers'])
save_bar_chart(df_viewers, 'Date', 'Unique Viewers', "Unique Viewers per Live Stream", "viewers_by_date.png", color="#28a745")

# --- 4. Top Viewers ---
if not df_log.empty:
    df_top_viewers = (
        df_log.groupby('Name')['Chat']
        .count()
        .reset_index()
        .rename(columns={'Chat': 'Messages'})
        .sort_values('Messages', ascending=False)
        .head(20)
    )
else:
    df_top_viewers = pd.DataFrame(columns=['Name', 'Messages'])
save_bar_chart(df_top_viewers, 'Name', 'Messages', "Top 20 Most Active Viewers", "top_viewers.png", color="#dc3545")

# --- 5. Word Cloud ---
if not df_log.empty:
    text = ' '.join(df_log['Chat'].dropna().astype(str).str.lower())
else:
    text = ''
wc = WordCloud(
    width=800, height=400,
    background_color='white',
    max_words=100,
    colormap='viridis',
    collocations=False,
    font_path=THAI_FONT,
).generate(text if text.strip() else "no data")
wc_img = wc.to_image()
wc_img.save(os.path.join(OUTPUT_DIR, "wordcloud.png"))
print("Saved: wordcloud.png")

# --- 6. Mentions Over Time ---
if not df.empty:
    stock_names_list = df['Name'].head(10).tolist()
else:
    stock_names_list = []

if not df_log.empty and stock_names_list:
    records = []
    for _, row in df_log.iterrows():
        chat = str(row['Chat'])
        date = row['Date']
        for code in stock_names_list:
            if re.search(r'\b' + re.escape(code) + r'\b', chat, re.IGNORECASE):
                records.append({'Date': date, 'Stock': code, 'Chat': chat})
    df_ts = pd.DataFrame(records)
    if not df_ts.empty:
        df_ts = (
            df_ts.groupby(['Date', 'Stock'])
            .size()
            .reset_index(name='Count')
            .sort_values('Date')
        )
    else:
        df_ts = pd.DataFrame(columns=['Date', 'Stock', 'Count'])
else:
    df_ts = pd.DataFrame(columns=['Date', 'Stock', 'Count'])

if not df_ts.empty:
    fig = px.line(
        df_ts, x='Date', y='Count', color='Stock',
        title="Top 10 Stock Mentions Over Time",
        markers=True,
        height=500,
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Mentions",
        legend_title="Stock",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    pio.write_image(fig, os.path.join(OUTPUT_DIR, "mentions_over_time.png"), scale=2, width=1000, height=500)
    print("Saved: mentions_over_time.png")
else:
    print("Skipped: mentions_over_time.png (no data)")

print("\nAll charts generated in 'images/' folder.")
