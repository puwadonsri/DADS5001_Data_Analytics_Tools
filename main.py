import json
import os
import re
import base64
import io

import pandas as pd
import pymongo
from pymongo.errors import ConnectionFailure
import plotly.express as px
import plotly.graph_objs as go
import dash
from dash import Input, Output, dcc, html, dash_table, Dash
import dash_bootstrap_components as dbc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from wordcloud import WordCloud

THAI_FONT = r"C:\Windows\Fonts\tahoma.ttf"

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "youtube"
CHAT_COLLECTION = "chat_log"
ANALYTICS_COLLECTION = "chat_analytics"
JSON_CHAT_LOG = "json_dataset/chat_log.json"
JSON_CHAT_ANALYTICS = "json_dataset/chat_analytics.json"
COMPANY_CSV = "json_dataset/company.csv"
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="Live Chat Analytics - DADS5001"
)

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "overflow-y": "auto",
}

CONTENT_STYLE = {
    "margin-left": "20rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

def try_connect_mongo():
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        return client
    except ConnectionFailure:
        return None

def load_analytics_data():
    client = try_connect_mongo()
    if client:
        try:
            db = client[DB_NAME]
            collection = db[ANALYTICS_COLLECTION]
            data = list(collection.find().sort("setAmount", -1))
            client.close()
            if data:
                records = [{'Name': d['setName'], 'Total': d['setAmount']} for d in data]
                return pd.DataFrame(records)
        except Exception:
            pass
        client.close()

    if os.path.exists(JSON_CHAT_ANALYTICS):
        with open(JSON_CHAT_ANALYTICS, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data:
            records = [{'Name': d['setName'], 'Total': d['setAmount']} for d in data]
            records.sort(key=lambda x: x['Total'], reverse=True)
            return pd.DataFrame(records)

    return pd.DataFrame(columns=['Name', 'Total'])

def load_chat_log_data():
    client = try_connect_mongo()
    if client:
        try:
            db = client[DB_NAME]
            collection = db[CHAT_COLLECTION]
            data = list(collection.find())
            client.close()
            if data:
                records = []
                for doc in data:
                    vals = list(doc.values())
                    records.append({
                        'Date': str(vals[1])[0:10],
                        'Name': vals[2],
                        'Chat': vals[3]
                    })
                return pd.DataFrame(records)
        except Exception:
            pass
        client.close()

    if os.path.exists(JSON_CHAT_LOG):
        with open(JSON_CHAT_LOG, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data:
            records = [{'Date': d['dateTime'][0:10], 'Name': d['authorName'], 'Chat': d['Message']} for d in data]
            return pd.DataFrame(records)

    return pd.DataFrame(columns=['Date', 'Name', 'Chat'])

def load_stock_names():
    if os.path.exists(COMPANY_CSV):
        df = pd.read_csv(COMPANY_CSV)
        return dict(zip(df['SET_CODE'], df['SET_NAME']))
    return {}

def make_table(df, max_rows=None):
    if df.empty:
        return html.Div("No data available.", className="text-muted")
    display_df = df.head(max_rows) if max_rows else df
    return dash_table.DataTable(
        data=display_df.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in display_df.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center', 'padding': '5px'},
        style_header={'fontWeight': 'bold'},
        page_size=10,
    )

def make_bar_chart(df, x_col, y_col, title, color="#007bff"):
    if df.empty:
        return dcc.Graph(figure=go.Figure().add_annotation(
            text="No data available", showarrow=False,
            font=dict(size=20)))
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
    return dcc.Graph(figure=fig)

def generate_wordcloud(text_series):
    text = ' '.join(text_series.dropna().astype(str).str.lower())
    if not text.strip():
        return None
    wc = WordCloud(
        width=800, height=400,
        background_color='white',
        max_words=100,
        colormap='viridis',
        collocations=False,
        font_path=THAI_FONT,
    ).generate(text)
    img_buf = io.BytesIO()
    wc.to_image().save(img_buf, format='PNG')
    img_buf.seek(0)
    encoded = base64.b64encode(img_buf.read()).decode('ascii')
    return f"data:image/png;base64,{encoded}"

sidebar = html.Div(
    [
        html.H2("Live Chat Analytics", className="display-5"),
        html.Hr(),
        html.P(
            "วิเคราะห์กระแสหุ้นจาก Live Chat",
            className="lead text-muted"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Top 10 Stocks", href="/", active="exact"),
                dbc.NavLink("All Stocks", href="/page-1", active="exact"),
                dbc.NavLink("Viewers by Date", href="/page-2", active="exact"),
                dbc.NavLink("Top Viewers", href="/page-3", active="exact"),
                dbc.NavLink("Word Cloud", href="/page-4", active="exact"),
                dbc.NavLink("Mentions Over Time", href="/page-5", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
        html.Hr(),
        html.Small(
            "DADS5001 Data Analytics Tools",
            className="text-muted"
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    stock_names = load_stock_names()

    if pathname == "/":
        df = load_analytics_data()
        df_top = df.head(10) if not df.empty else df
        table = make_table(df_top)
        chart = make_bar_chart(
            df_top, 'Name', 'Total',
            "Top 10 Most Mentioned Stocks (SET)"
        )
        return html.Div([
            html.H3("Top 10 Most Mentioned Stocks"),
            html.P("หุ้นที่ถูกพูดถึงมากที่สุด 10 อันดับ จาก Live Chat", className="text-muted"),
            html.Hr(),
            chart,
            html.Hr(),
            html.H5("Data Table"),
            table,
        ])

    elif pathname == "/page-1":
        df = load_analytics_data()
        table = make_table(df)
        chart = make_bar_chart(
            df, 'Name', 'Total',
            "All Mentioned Stocks (SET)"
        )
        return html.Div([
            html.H3("All Mentioned Stocks"),
            html.P("หุ้นทั้งหมดที่ถูกพูดถึงใน Live Chat", className="text-muted"),
            html.Hr(),
            chart,
            html.Hr(),
            html.H5("Data Table"),
            table,
        ])

    elif pathname == "/page-2":
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
        table = make_table(df_viewers)
        chart = make_bar_chart(
            df_viewers, 'Date', 'Unique Viewers',
            "Unique Viewers per Live Stream",
            color="#28a745"
        )
        return html.Div([
            html.H3("Viewers by Date"),
            html.P("จำนวนผู้ชมที่ไม่ซ้ำกันในแต่ละวันที่มี Live", className="text-muted"),
            html.Hr(),
            chart,
            html.Hr(),
            html.H5("Data Table"),
            table,
        ])

    elif pathname == "/page-3":
        df_log = load_chat_log_data()
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
        table = make_table(df_top_viewers)
        chart = make_bar_chart(
            df_top_viewers, 'Name', 'Messages',
            "Top 20 Most Active Viewers",
            color="#dc3545"
        )
        return html.Div([
            html.H3("Top Viewers"),
            html.P("ผู้ชมที่ส่งข้อความมากที่สุด 20 อันดับ", className="text-muted"),
            html.Hr(),
            chart,
            html.Hr(),
            html.H5("Data Table"),
            table,
        ])

    elif pathname == "/page-4":
        df_log = load_chat_log_data()
        img_data = generate_wordcloud(df_log['Chat'] if not df_log.empty else pd.Series(dtype=str))
        if img_data:
            wc_component = html.Img(src=img_data, style={"width": "100%", "maxWidth": "800px"})
        else:
            wc_component = html.Div("No chat data available for word cloud.", className="text-muted")
        return html.Div([
            html.H3("Word Cloud"),
            html.P("คำที่ถูกพูดถึงบ่อยที่สุดใน Live Chat (แสดงเป็น Word Cloud)", className="text-muted"),
            html.Hr(),
            wc_component,
        ])

    elif pathname == "/page-5":
        df = load_analytics_data()
        df_log = load_chat_log_data()
        stock_names_list = df['Name'].head(10).tolist() if not df.empty else []

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
            chart = dcc.Graph(figure=fig)
        else:
            chart = html.Div("No time-series data available.", className="text-muted")

        table = make_table(df_ts)

        return html.Div([
            html.H3("Stock Mentions Over Time"),
            html.P("แนวโน้มการพูดถึงหุ้น Top 10 ในแต่ละวัน", className="text-muted"),
            html.Hr(),
            chart,
            html.Hr(),
            html.H5("Data Table"),
            table,
        ])

    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )

if __name__ == "__main__":
    app.run_server(port=1111, debug=True)
