import json
import os
import re
import numpy as np
import pandas as pd
import requests
import yfinance as yf

# -------------------------------------------------------------
# 1. 抓取 MSTR 股價數據 (2024 至今)
# -------------------------------------------------------------
print("正在從 Yahoo Finance 抓取 MSTR 股價...")
ticker = yf.Ticker("MSTR")
df = ticker.history(start="2024-01-01")

if df.empty:
  df = ticker.history(period="2y")

try:
  btc_res = requests.get(
      "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
      timeout=10,
  )
  btc_current_price = btc_res.json()["bitcoin"]["usd"]
except Exception:
  btc_current_price = 95000.0

# -------------------------------------------------------------
# 2. 歷史增發基準庫 (標準繁體中文)
# -------------------------------------------------------------
base_events = [
    {
        "id": "ev1",
        "date": "2024-03-08",
        "type": "convertible_note",
        "typeName": "可轉換公司債",
        "badge": "0.625% 可轉債",
        "title": "發行 8 億美元 0.625% 可轉換優先公司債 (Due 2030)",
        "amount": 0.80,
        "amountStr": "$800M ($0.80B)",
        "coupon": "0.625%",
        "conversionPrice": "$149.77",
        "secForm": "Form 8-K / 424B5",
        "color": "#8b5cf6",
    },
    {
        "id": "ev2",
        "date": "2024-03-15",
        "type": "convertible_note",
        "typeName": "可轉換公司債",
        "badge": "0.875% 可轉債",
        "title": "發行 6.0375 億美元 0.875% 可轉換優先公司債 (Due 2031)",
        "amount": 0.60375,
        "amountStr": "$603.75M",
        "coupon": "0.875%",
        "conversionPrice": "$232.72",
        "secForm": "Form 8-K / 424B5",
        "color": "#8b5cf6",
    },
    {
        "id": "ev3",
        "date": "2024-06-14",
        "type": "convertible_note",
        "typeName": "可轉換公司債",
        "badge": "2.25% 可轉債",
        "title": "發行 8 億美元 2.25% 可轉換優先公司債 (Due 2032)",
        "amount": 0.80,
        "amountStr": "$800M ($0.80B)",
        "coupon": "2.25%",
        "conversionPrice": "$204.33",
        "secForm": "Form 8-K / 424B5",
        "color": "#8b5cf6",
    },
    {
        "id": "ev4",
        "date": "2024-08-08",
        "type": "corporate_action",
        "typeName": "重大資本行動",
        "badge": "1:10 拆股",
        "title": "執行 1 拆 10 股票分割",
        "amount": 0.0,
        "amountStr": "流通性翻倍",
        "coupon": "-",
        "conversionPrice": "轉股價相應除以 10",
        "secForm": "Form 8-K",
        "color": "#f59e0b",
    },
    {
        "id": "ev5",
        "date": "2024-09-18",
        "type": "convertible_note",
        "typeName": "可轉換公司債",
        "badge": "0.625% 可轉債",
        "title": "發行 10.1 億美元 0.625% 可轉換優先公司債 (Due 2028)",
        "amount": 1.01,
        "amountStr": "$1.01B",
        "coupon": "0.625%",
        "conversionPrice": "$183.19",
        "secForm": "Form 8-K / 424B5",
        "color": "#8b5cf6",
    },
    {
        "id": "ev6",
        "date": "2024-10-30",
        "type": "corporate_action",
        "typeName": "資本架構戰略",
        "badge": "420億計畫",
        "title": "發布 21/21 計畫 (3 年 420 億美元融資買幣)",
        "amount": 0.0,
        "amountStr": "$42.0B 框架",
        "coupon": "混合",
        "conversionPrice": "隨行就市 (ATM) / 債券定價",
        "secForm": "Form 8-K / 10-Q",
        "color": "#f59e0b",
    },
    {
        "id": "ev7",
        "date": "2024-11-11",
        "type": "atm_equity",
        "typeName": "ATM 普通股增發",
        "badge": "ATM 20.3億",
        "title": "ATM 增發籌資 20.3 億美元購入 27,200 BTC",
        "amount": 2.03,
        "amountStr": "$2.03B",
        "coupon": "無",
        "conversionPrice": "約 $265/股",
        "secForm": "Form 8-K / 424B5",
        "color": "#10b981",
    },
    {
        "id": "ev8",
        "date": "2024-11-18",
        "type": "atm_equity",
        "typeName": "ATM 普通股增發",
        "badge": "ATM 46.0億",
        "title": "ATM 增發籌資 46 億美元購入 51,780 BTC",
        "amount": 4.60,
        "amountStr": "$4.60B",
        "coupon": "無",
        "conversionPrice": "約 $358/股",
        "secForm": "Form 8-K / 424B5",
        "color": "#10b981",
    },
    {
        "id": "ev9",
        "date": "2024-11-21",
        "type": "convertible_note",
        "typeName": "可轉換公司債",
        "badge": "0.0% 零息債",
        "title": "發行 30 億美元 0.0% 零利率可轉換公司債 (Due 2029)",
        "amount": 3.00,
        "amountStr": "$3.00B",
        "coupon": "0.00%",
        "conversionPrice": "$672.40 (溢價 55%)",
        "secForm": "Form 8-K / 424B5",
        "color": "#8b5cf6",
    },
    {
        "id": "ev10",
        "date": "2024-12-09",
        "type": "atm_equity",
        "typeName": "ATM 普通股增發",
        "badge": "ATM 21.5億",
        "title": "ATM 增發籌資 21.5 億美元購入 21,550 BTC",
        "amount": 2.15,
        "amountStr": "$2.15B",
        "coupon": "無",
        "conversionPrice": "約 $385/股",
        "secForm": "Form 8-K / 424B5",
        "color": "#10b981",
    },
]

# -------------------------------------------------------------
# 3. 自動探測未來的 SEC 申報
# -------------------------------------------------------------
sec_headers = {"User-Agent": "MSTR_AutoTracker investor_research@example.com"}
existing_dates = {e["date"] for e in base_events}

try:
  sec_url = "https://data.sec.gov/submissions/CIK0001050446.json"
  sec_resp = requests.get(sec_url, headers=sec_headers, timeout=10)
  if sec_resp.status_code == 200:
    filings = sec_resp.json()["filings"]["recent"]
    forms = filings["form"]
    dates = filings["filingDate"]
    accession_nos = filings["accessionNumber"]
    primary_docs = filings["primaryDocument"]

    for idx, form in enumerate(forms[:20]):
      f_date = dates[idx]
      if f_date > "2024-12-10" and f_date not in existing_dates:
        if form in ["8-K", "424B5"]:
          acc_clean = accession_nos[idx].replace("-", "")
          doc_name = primary_docs[idx]
          doc_url = f"https://www.sec.gov/Archives/edgar/data/1050446/{acc_clean}/{doc_name}"
          try:
            doc_res = requests.get(
                doc_url, headers=sec_headers, timeout=8
            ).text.lower()
            if "convertible" in doc_res and "notes" in doc_res:
              amt_match = re.search(
                  r"\$(\d+(?:\.\d+)?)\s*(billion|million)", doc_res
              )
              amt_val = 0.5
              if amt_match:
                val = float(amt_match.group(1))
                amt_val = (
                    val if amt_match.group(2) == "billion" else val / 1000.0
                )
              amt_val = min(amt_val, 5.0)

              base_events.append({
                  "id": f"auto_sec_{f_date}",
                  "date": f_date,
                  "type": "convertible_note",
                  "typeName": "可轉換公司債 (SEC自動抓取)",
                  "badge": f"可轉債 ${amt_val:.1f}B",
                  "title": f"SEC 申報：發行約 {amt_val:.2f} 億美元可轉債",
                  "amount": round(amt_val, 2),
                  "amountStr": f"${amt_val:.2f}B",
                  "coupon": "見申報",
                  "conversionPrice": "見申報",
                  "secForm": f"Form {form}",
                  "color": "#8b5cf6",
              })
              existing_dates.add(f_date)

            elif (
                "sold" in doc_res
                and "shares" in doc_res
                and ("sales agreement" in doc_res or "net proceeds" in doc_res)
            ):
              amt_match = re.search(
                  r"\$(\d+(?:\.\d+)?)\s*(billion|million)", doc_res
              )
              amt_val = 1.0
              if amt_match:
                val = float(amt_match.group(1))
                amt_val = (
                    val if amt_match.group(2) == "billion" else val / 1000.0
                )
              amt_val = min(amt_val, 6.0)

              base_events.append({
                  "id": f"auto_sec_{f_date}",
                  "date": f_date,
                  "type": "atm_equity",
                  "typeName": "ATM 增發 (SEC自動抓取)",
                  "badge": f"ATM ${amt_val:.1f}B",
                  "title": f"SEC 申報：ATM 增發售股約 {amt_val:.2f} 億美元",
                  "amount": round(amt_val, 2),
                  "amountStr": f"${amt_val:.2f}B",
                  "coupon": "無",
                  "conversionPrice": "隨行就市",
                  "secForm": f"Form {form}",
                  "color": "#10b981",
              })
              existing_dates.add(f_date)
          except Exception:
            pass
except Exception as e:
  print(f"SEC 檢查略過: {e}")

event_dict = {e["date"]: e for e in base_events}

# -------------------------------------------------------------
# 4. 組裝 K 線與 mNAV 計算
# -------------------------------------------------------------
candles = []
df = df.dropna()
closes = [float(c) for c in df["Close"]]

try:
  current_shares = ticker.info.get("sharesOutstanding", 248000000)
except Exception:
  current_shares = 248000000

for i, (ts, row) in enumerate(df.iterrows()):
  d_str = ts.strftime("%Y-%m-%d")
  close_p = round(float(row["Close"]), 2)

  if d_str < "2024-03-10":
    b_held, b_sh, d_sh = 193000, 170000000, 195000000
  elif d_str < "2024-06-20":
    b_held, b_sh, d_sh = 214246, 175000000, 208000000
  elif d_str < "2024-09-20":
    b_held, b_sh, d_sh = 226331, 182000000, 222000000
  elif d_str < "2024-11-11":
    b_held, b_sh, d_sh = 252220, 192000000, 238000000
  elif d_str < "2024-11-18":
    b_held, b_sh, d_sh = 279420, 205000000, 251000000
  elif d_str < "2024-11-25":
    b_held, b_sh, d_sh = 331200, 224000000, 279000000
  elif d_str < "2024-12-09":
    b_held, b_sh, d_sh = 386700, 238000000, 296000000
  else:
    b_held = 423650
    b_sh = current_shares
    d_sh = int(current_shares * 1.25)

  btc_nav = b_held * btc_current_price
  basic_mnav = round((b_sh * close_p) / btc_nav, 2)
  diluted_mnav = round((d_sh * close_p) / btc_nav, 2)

  ev = event_dict.get(d_str)
  note_amt = (
      ev["amount"] if ev and ev["type"] == "convertible_note" else 0.0
  )
  atm_amt = ev["amount"] if ev and ev["type"] == "atm_equity" else 0.0

  candles.append({
      "date": d_str,
      "open": round(float(row["Open"]), 2),
      "high": round(float(row["High"]), 2),
      "low": round(float(row["Low"]), 2),
      "close": close_p,
      "volume": int(row["Volume"]),
      "ma20": (
          round(float(np.mean(closes[i - 19 : i + 1])), 2) if i >= 19 else None
      ),
      "ma50": (
          round(float(np.mean(closes[i - 49 : i + 1])), 2) if i >= 49 else None
      ),
      "basic_mnav": basic_mnav,
      "diluted_mnav": diluted_mnav,
      "note_amt": note_amt,
      "atm_amt": atm_amt,
      "badge": ev["badge"] if ev else None,
      "badge_color": ev["color"] if ev else None,
      "event_title": ev["title"] if ev else None,
  })

# -------------------------------------------------------------
# 5. 純淨 HTML 模板 (採用 .replace() 替換，完全杜絕語法與轉義衝突)
# -------------------------------------------------------------
html_template = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MicroStrategy (MSTR) 增發數據與全景 K 線儀表板</title>
    <style>
        :root {
            --bg-primary: #0b1120;
            --bg-secondary: #131d31;
            --border-color: #26354f;
            --accent-purple: #8b5cf6;
            --accent-green: #10b981;
            --accent-amber: #f59e0b;
            --accent-blue: #38bdf8;
            --accent-pink: #ec4899;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: var(--bg-primary);
            color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang TC", "Microsoft JhengHei", sans-serif;
            padding: 24px;
            line-height: 1.5;
        }
        .container { max-width: 1480px; margin: 0 auto; }
        .header { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px; margin-bottom: 20px; }
        .header h1 { font-size: 24px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 10px; }
        .header span.tag { font-size: 12px; background: rgba(56, 189, 248, 0.15); color: var(--accent-blue); padding: 3px 8px; border-radius: 6px; border: 1px solid rgba(56, 189, 248, 0.3); }
        
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 20px; }
        .stat-card { background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 10px; padding: 14px 18px; }
        .stat-title { font-size: 12px; color: #94a3b8; text-transform: uppercase; margin-bottom: 4px; }
        .stat-val { font-size: 22px; font-weight: 700; color: #fff; }
        .stat-sub { font-size: 12px; margin-top: 3px; color: #94a3b8; }

        .chart-box { background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px; margin-bottom: 24px; }
        .chart-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 12px; }
        .legend-group { display: flex; align-items: center; gap: 14px; font-size: 13px; color: #94a3b8; flex-wrap: wrap; }
        .legend-item { display: flex; align-items: center; gap: 6px; }
        .legend-box { width: 12px; height: 4px; border-radius: 2px; display: inline-block; }
        .legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
        
        .btn-group { display: flex; gap: 6px; }
        .btn { background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
        .btn:hover { background: #334155; color: #fff; }
        .btn.active { background: #0284c7; color: #fff; border-color: #38bdf8; }

        .canvas-wrapper { position: relative; width: 100%; height: 720px; background: #070d18; border-radius: 8px; border: 1px solid #1c2b44; overflow: hidden; cursor: crosshair; user-select: none; }
        canvas { display: block; width: 100%; height: 100%; }

        #chartTooltip {
            position: absolute; display: none; background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(8px);
            border: 1px solid #475569; border-radius: 8px; padding: 12px 16px; font-size: 12px; color: #fff;
            pointer-events: none; box-shadow: 0 10px 20px rgba(0,0,0,0.5); z-index: 100; min-width: 250px;
        }
        #chartTooltip .tt-title { font-weight: 700; margin-bottom: 6px; border-bottom: 1px solid #334155; padding-bottom: 4px; color: #38bdf8; }
        #chartTooltip .tt-row { display: flex; justify-content: space-between; margin: 3px 0; }
        #chartTooltip .tt-badge { margin-top: 8px; padding: 4px 8px; border-radius: 4px; font-weight: 600; text-align: center; }

        .hint-bar { font-size: 12px; color: #64748b; margin-top: 8px; display: flex; justify-content: space-between; }

        .grid-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
        @media (max-width: 1024px) { .grid-2col { grid-template-columns: 1fr; } }
        .panel-card { background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; }
        .panel-card h2 { font-size: 17px; font-weight: 700; margin-bottom: 14px; color: #fff; display: flex; align-items: center; gap: 8px; }

        .event-item { border-left: 3px solid #64748b; padding: 8px 12px; margin-bottom: 10px; cursor: pointer; transition: all 0.2s; border-radius: 0 6px 6px 0; background: rgba(255,255,255,0.01); }
        .event-item:hover, .event-item.selected { border-left-color: var(--accent-blue); background: rgba(56, 189, 248, 0.08); }
        .event-item .date { font-size: 12px; color: #94a3b8; display: flex; align-items: center; gap: 6px; }
        .event-item .title { font-size: 14px; font-weight: 600; color: #f1f5f9; margin: 2px 0; }
        .event-item .meta { font-size: 12px; color: #94a3b8; }

        .table-responsive { overflow-x: auto; margin-top: 10px; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th { background: #0d1525; color: #94a3b8; font-weight: 600; text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border-color); }
        td { padding: 10px 12px; border-bottom: 1px solid #1e2c43; color: #e2e8f0; }
        tr:hover td { background: rgba(255,255,255,0.02); }
        .badge { display: inline-block; font-size: 11px; font-weight: 600; padding: 2px 7px; border-radius: 4px; }
        .badge-purple { background: rgba(139, 92, 246, 0.2); color: #c4b5fd; border: 1px solid rgba(139, 92, 246, 0.4); }
        .badge-green { background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4); }
        .badge-amber { background: rgba(245, 158, 11, 0.2); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.4); }
        code { background: #0b1120; padding: 2px 5px; border-radius: 4px; color: #f472b6; font-family: monospace; font-size: 12px; }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <div>
            <h1>MicroStrategy (MSTR) 增發數據與全景 K 線儀表板 <span class="tag">繁體中文純淨版</span></h1>
            <p>已整合：時間自定義縮放（1個月 / 半年 / 今年 / 全部）、滑鼠滾輪縮放、滑鼠拖曳、增發直條圖與雙軌 mNAV。</p>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 13px; color: #94a3b8;">最新收盤價: <strong style="color:#fff; font-size:16px;">__LATEST_PRICE__</strong></div>
            <div style="font-size: 12px; color: #f59e0b;">BTC 參考估價: __BTC_PRICE__ USD</div>
        </div>
    </div>

    <!-- 4 Stats Cards -->
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-title">普通股流通總數 (Basic)</div>
            <div class="stat-val" style="color: #38bdf8;">__BASIC_SHARES__</div>
            <div class="stat-sub">即時普通股股本</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">完全稀釋總股數 (Diluted)</div>
            <div class="stat-val" style="color: #ec4899;">__DILUTED_SHARES__</div>
            <div class="stat-sub">計入所有可轉債轉股稀釋</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">增發事件總數</div>
            <div class="stat-val" style="color: #8b5cf6;">__EVENT_COUNT__ 筆</div>
            <div class="stat-sub">包含可轉債與 ATM 申報</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">比特幣總持倉量</div>
            <div class="stat-val" style="color: #10b981;">423,650+ BTC</div>
            <div class="stat-sub">全球第一大企業持幣儲備</div>
        </div>
    </div>

    <!-- Multi-Panel Chart -->
    <div class="chart-box">
        <div class="chart-toolbar">
            <div class="legend-group">
                <div class="legend-item"><span class="legend-box" style="background: #38bdf8;"></span><span>MA 20</span></div>
                <div class="legend-item"><span class="legend-box" style="background: #f59e0b;"></span><span>MA 50</span></div>
                <div class="legend-item"><span class="legend-dot" style="background: #8b5cf6;"></span><span>可轉債 (Notes)</span></div>
                <div class="legend-item"><span class="legend-dot" style="background: #10b981;"></span><span>ATM 普通股 (Equity)</span></div>
                <div class="legend-item"><span class="legend-box" style="background: #38bdf8; height:2px;"></span><span>舊版 Basic mNAV</span></div>
                <div class="legend-item"><span class="legend-box" style="background: #ec4899; height:2px;"></span><span>新版 Diluted mNAV</span></div>
            </div>
            
            <div class="btn-group">
                <button class="btn" id="btn1m" onclick="setTimeframe('1m')">1 個月內</button>
                <button class="btn" id="btn6m" onclick="setTimeframe('6m')">半年</button>
                <button class="btn" id="btnytd" onclick="setTimeframe('ytd')">今年 (YTD)</button>
                <button class="btn active" id="btnall" onclick="setTimeframe('all')">全部歷史</button>
            </div>
        </div>

        <div class="canvas-wrapper" id="canvasWrapper">
            <canvas id="klineCanvas"></canvas>
            <div id="chartTooltip"></div>
        </div>
        <div class="hint-bar">
            <span>💡 提示：支援<strong>滑鼠滾輪直接縮放</strong>放大/縮小，按住滑鼠左鍵可<strong>左右拖曳平移</strong>歷史走勢。</span>
            <span id="rangeLabel">當前範圍: 全部歷史</span>
        </div>
    </div>

    <!-- 2 Column Breakdown -->
    <div class="grid-2col">
        <div class="panel-card">
            <h2><span>📌</span> 歷次增發詳細數據清單（點選定位圖表）</h2>
            <div id="eventList" style="max-height: 480px; overflow-y: auto; padding-right: 6px;"></div>
        </div>

        <div class="panel-card">
            <h2><span>📊</span> 增發與重大資本事件完整對照表</h2>
            <div class="table-responsive" style="max-height: 480px; overflow-y: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>公告日期</th>
                            <th>增發工具</th>
                            <th>規格與名稱</th>
                            <th>規模</th>
                            <th>轉股價 / 發行價</th>
                            <th>申報文件</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody"></tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<script>
const rawData = __CANDLES_DATA__;
const events = __EVENTS_DATA__;

let viewStart = 0;
let viewEnd = rawData.length - 1;
let currentData = [...rawData];
let hoveredIndex = -1;

const canvas = document.getElementById('klineCanvas');
const ctx = canvas.getContext('2d');
const wrapper = document.getElementById('canvasWrapper');
const tooltip = document.getElementById('chartTooltip');
const rangeLabel = document.getElementById('rangeLabel');

function updateViewRange(start, end) {
    viewStart = Math.max(0, Math.min(rawData.length - 5, start));
    viewEnd = Math.max(viewStart + 4, Math.min(rawData.length - 1, end));
    currentData = rawData.slice(viewStart, viewEnd + 1);
    rangeLabel.innerText = '當前範圍: ' + currentData[0].date + ' ~ ' + currentData[currentData.length - 1].date + ' (' + currentData.length + ' 根K棒)';
    renderChart();
}

function initSize() {
    const dpr = window.devicePixelRatio || 1;
    const rect = wrapper.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
    renderChart();
}

window.addEventListener('resize', initSize);

function setTimeframe(tf) {
    document.querySelectorAll('.btn-group .btn').forEach(b => b.classList.remove('active'));
    const activeBtn = document.getElementById('btn' + tf);
    if (activeBtn) activeBtn.classList.add('active');

    const total = rawData.length;
    if (tf === '1m') {
        updateViewRange(total - 22, total - 1);
    } else if (tf === '6m') {
        updateViewRange(total - 128, total - 1);
    } else if (tf === 'ytd') {
        const latestDate = rawData[total - 1].date;
        const currentYear = latestDate.substring(0, 4);
        let ytdIdx = rawData.findIndex(d => d.date.startsWith(currentYear));
        if (ytdIdx === -1) ytdIdx = Math.max(0, total - 200);
        updateViewRange(ytdIdx, total - 1);
    } else if (tf === 'all') {
        updateViewRange(0, total - 1);
    }
}

wrapper.addEventListener('wheel', function(e) {
    e.preventDefault();
    const zoomFactor = e.deltaY > 0 ? 1.15 : 0.85;
    const currentSpan = viewEnd - viewStart;
    let newSpan = Math.round(currentSpan * zoomFactor);
    newSpan = Math.max(8, Math.min(rawData.length, newSpan));

    const rect = canvas.getBoundingClientRect();
    const mouseRatio = Math.max(0, Math.min(1, (e.clientX - rect.left - 10) / (rect.width - 75)));

    const centerIdx = viewStart + Math.round(currentSpan * mouseRatio);
    let newStart = Math.max(0, Math.round(centerIdx - newSpan * mouseRatio));
    let newEnd = Math.min(rawData.length - 1, newStart + newSpan - 1);
    if (newEnd - newStart < newSpan - 1) {
        newStart = Math.max(0, newEnd - newSpan + 1);
    }
    updateViewRange(newStart, newEnd);
}, { passive: false });

let isDragging = false;
let dragStartX = 0;
let dragStartViewStart = 0;
let dragStartViewEnd = 0;

wrapper.addEventListener('mousedown', function(e) {
    if (e.button === 0) {
        isDragging = true;
        dragStartX = e.clientX;
        dragStartViewStart = viewStart;
        dragStartViewEnd = viewEnd;
        wrapper.style.cursor = 'grabbing';
    }
});

window.addEventListener('mouseup', function() {
    if (isDragging) {
        isDragging = false;
        wrapper.style.cursor = 'crosshair';
    }
});

wrapper.addEventListener('mousemove', function(e) {
    const rect = canvas.getBoundingClientRect();
    const chartW = rect.width - 70;
    const n = currentData.length;

    if (isDragging) {
        const deltaX = e.clientX - dragStartX;
        const currentSpan = dragStartViewEnd - dragStartViewStart;
        const barShift = Math.round((deltaX / chartW) * currentSpan);

        let newStart = dragStartViewStart - barShift;
        let newEnd = dragStartViewEnd - barShift;

        if (newStart < 0) {
            newEnd += -newStart;
            newStart = 0;
        }
        if (newEnd >= rawData.length) {
            newStart -= (newEnd - (rawData.length - 1));
            newEnd = rawData.length - 1;
        }
        updateViewRange(Math.max(0, newStart), newEnd);
        return;
    }

    const x = e.clientX - rect.left;
    const step = chartW / n;
    
    if (x >= 10 && x <= chartW) {
        hoveredIndex = Math.floor((x - 10) / step);
        if (hoveredIndex >= n) hoveredIndex = n - 1;
        if (hoveredIndex < 0) hoveredIndex = 0;
        showTooltipAt(hoveredIndex, e.clientX, e.clientY);
    } else {
        hoveredIndex = -1;
        tooltip.style.display = 'none';
    }
    renderChart();
});

wrapper.addEventListener('mouseleave', function() {
    hoveredIndex = -1;
    tooltip.style.display = 'none';
    renderChart();
});

function showTooltipAt(idx, mouseX, mouseY) {
    const item = currentData[idx];
    const ev = events.find(e => e.date === item.date);
    
    let html = `
        <div class="tt-title">${item.date}</div>
        <div class="tt-row"><span>MSTR 收盤:</span><span style="font-weight:700; color:${item.close >= item.open ? '#10b981' : '#ef4444'}">$${item.close.toFixed(2)}</span></div>
        <div class="tt-row"><span>開 / 高 / 低:</span><span>${item.open.toFixed(1)} / ${item.high.toFixed(1)} / ${item.low.toFixed(1)}</span></div>
        <div class="tt-row"><span>舊版 Basic mNAV:</span><span style="color:#38bdf8; font-weight:700;">${item.basic_mnav.toFixed(2)}x</span></div>
        <div class="tt-row"><span>新版 Diluted mNAV:</span><span style="color:#ec4899; font-weight:700;">${item.diluted_mnav.toFixed(2)}x</span></div>
    `;

    if (item.note_amt > 0) {
        html += `<div class="tt-row" style="color:#c4b5fd;"><span>可轉債增發:</span><span>$${item.note_amt.toFixed(2)}B</span></div>`;
    }
    if (item.atm_amt > 0) {
        html += `<div class="tt-row" style="color:#6ee7b7;"><span>ATM 股票增發:</span><span>$${item.atm_amt.toFixed(2)}B</span></div>`;
    }

    if (ev) {
        html += `
            <div class="tt-badge" style="background:${ev.color}22; color:${ev.color}; border:1px solid ${ev.color}">
                ★ ${ev.badge} (${ev.amountStr})
            </div>
            <div style="font-size:11px; color:#cbd5e1; margin-top:4px;">${ev.title}</div>
        `;
    }

    tooltip.innerHTML = html;
    tooltip.style.display = 'block';

    const wrapperRect = wrapper.getBoundingClientRect();
    let left = mouseX - wrapperRect.left + 15;
    let top = mouseY - wrapperRect.top + 10;
    if (left + 260 > wrapperRect.width) left -= 280;
    if (top + 220 > wrapperRect.height) top -= 200;

    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
}

function renderChart() {
    const rect = wrapper.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    ctx.clearRect(0, 0, width, height);

    const chartLeft = 10;
    const chartRight = width - 65;
    const chartWidth = chartRight - chartLeft;

    const p1Top = 20, p1H = height * 0.44;
    const p2Top = p1Top + p1H + 25, p2H = height * 0.18;
    const p3Top = p2Top + p2H + 25, p3H = height * 0.18;
    const xAxisY = p3Top + p3H + 18;

    const n = currentData.length;
    if (n === 0) return;

    let minPrice = Infinity, maxPrice = -Infinity;
    currentData.forEach(d => {
        if (d.low < minPrice) minPrice = d.low;
        if (d.high > maxPrice) maxPrice = d.high;
    });
    const pBuf = (maxPrice - minPrice) * 0.08;
    maxPrice += pBuf;
    minPrice = Math.max(0, minPrice - pBuf * 0.5);

    const priceToY = (p) => p1Top + p1H - ((p - minPrice) / (maxPrice - minPrice)) * p1H;
    const step = chartWidth / n;
    const candleWidth = Math.max(2, Math.min(22, step * 0.7));

    // Panel 1: K 線圖 (Clip 保護)
    ctx.save();
    ctx.beginPath();
    ctx.rect(chartLeft, p1Top - 10, chartWidth, p1H + 15);
    ctx.clip();

    ctx.strokeStyle = '#1e293b'; ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const p = minPrice + (maxPrice - minPrice) * (i / 4);
        const y = priceToY(p);
        ctx.beginPath(); ctx.moveTo(chartLeft, y); ctx.lineTo(chartRight, y); ctx.stroke();
    }

    currentData.forEach((d, i) => {
        const x = chartLeft + i * step + step / 2;
        const isUp = d.close >= d.open;
        const color = isUp ? '#10b981' : '#ef4444';

        ctx.strokeStyle = color; ctx.lineWidth = 1.2;
        ctx.beginPath(); ctx.moveTo(x, priceToY(d.high)); ctx.lineTo(x, priceToY(d.low)); ctx.stroke();

        const yOpen = priceToY(d.open);
        const yClose = priceToY(d.close);
        ctx.fillStyle = color;
        ctx.fillRect(x - candleWidth / 2, Math.min(yOpen, yClose), candleWidth, Math.max(2, Math.abs(yClose - yOpen)));
    });

    // MA20 & MA50
    ctx.strokeStyle = '#38bdf8'; ctx.lineWidth = 1.5; ctx.beginPath();
    let s20 = false;
    currentData.forEach((d, i) => {
        if (d.ma20) {
            const x = chartLeft + i * step + step / 2;
            const y = priceToY(d.ma20);
            if (!s20) { ctx.moveTo(x, y); s20 = true; } else { ctx.lineTo(x, y); }
        }
    });
    ctx.stroke();

    ctx.strokeStyle = '#f59e0b'; ctx.lineWidth = 1.5; ctx.beginPath();
    let s50 = false;
    currentData.forEach((d, i) => {
        if (d.ma50) {
            const x = chartLeft + i * step + step / 2;
            const y = priceToY(d.ma50);
            if (!s50) { ctx.moveTo(x, y); s50 = true; } else { ctx.lineTo(x, y); }
        }
    });
    ctx.stroke();

    // Event Pins (交錯高度防重疊)
    let pinCounter = 0;
    events.forEach(ev => {
        const idx = currentData.findIndex(d => d.date === ev.date);
        if (idx !== -1) {
            pinCounter++;
            const d = currentData[idx];
            const x = chartLeft + idx * step + step / 2;
            const yHigh = priceToY(d.high);
            const pinYOffset = (pinCounter % 2 === 0) ? 42 : 24;
            const pinY = Math.max(p1Top + 20, yHigh - pinYOffset);

            ctx.setLineDash([2, 2]);
            ctx.strokeStyle = ev.color; ctx.lineWidth = 1.2;
            ctx.beginPath(); ctx.moveTo(x, yHigh - 2); ctx.lineTo(x, pinY + 6); ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = ev.color;
            ctx.beginPath(); ctx.arc(x, pinY, 5, 0, Math.PI * 2); ctx.fill();
            ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.2; ctx.stroke();

            ctx.font = 'bold 10px sans-serif';
            const badgeW = ctx.measureText(ev.badge).width + 8;
            ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
            ctx.strokeStyle = ev.color; ctx.lineWidth = 1;
            ctx.beginPath(); ctx.roundRect(x - badgeW / 2, pinY - 18, badgeW, 16, 4); ctx.fill(); ctx.stroke();

            ctx.fillStyle = '#ffffff';
            ctx.textAlign = 'center';
            ctx.fillText(ev.badge, x, pinY - 6);
        }
    });
    ctx.restore();

    ctx.fillStyle = '#64748b'; ctx.font = '11px sans-serif'; ctx.textAlign = 'left';
    for (let i = 0; i <= 4; i++) {
        const p = minPrice + (maxPrice - minPrice) * (i / 4);
        ctx.fillText('$' + p.toFixed(0), chartRight + 6, priceToY(p) + 4);
    }
    ctx.fillStyle = '#94a3b8';
    ctx.fillText('MSTR 股價 K 線 (日線)', chartLeft + 4, p1Top - 6);

    // Panel 2: 增發直條圖 (Clip 保護)
    ctx.save();
    ctx.beginPath();
    ctx.rect(chartLeft, p2Top - 8, chartWidth, p2H + 12);
    ctx.clip();

    let maxAmt = 5.0;
    currentData.forEach(d => {
        if (d.note_amt > maxAmt) maxAmt = d.note_amt;
        if (d.atm_amt > maxAmt) maxAmt = d.atm_amt;
    });
    maxAmt = Math.min(8.0, Math.max(5.0, maxAmt));

    const amtToH = (a) => Math.min(p2H - 5, (a / maxAmt) * (p2H - 10));

    for (let b = 1; b <= Math.floor(maxAmt); b += 2) {
        const yLine = p2Top + p2H - amtToH(b);
        ctx.strokeStyle = 'rgba(30, 41, 59, 0.6)';
        ctx.beginPath(); ctx.moveTo(chartLeft, yLine); ctx.lineTo(chartRight, yLine); ctx.stroke();
    }

    currentData.forEach((d, i) => {
        const x = chartLeft + i * step + step / 2;
        const barW = Math.max(3, Math.min(18, step * 0.8));

        if (d.note_amt > 0) {
            const h = amtToH(d.note_amt);
            ctx.fillStyle = '#8b5cf6';
            ctx.fillRect(x - barW / 2, p2Top + p2H - h, barW, h);
            ctx.strokeStyle = '#c4b5fd'; ctx.lineWidth = 1;
            ctx.strokeRect(x - barW / 2, p2Top + p2H - h, barW, h);
        }
        if (d.atm_amt > 0) {
            const h = amtToH(d.atm_amt);
            ctx.fillStyle = '#10b981';
            ctx.fillRect(x - barW / 2, p2Top + p2H - h, barW, h);
            ctx.strokeStyle = '#6ee7b7'; ctx.lineWidth = 1;
            ctx.strokeRect(x - barW / 2, p2Top + p2H - h, barW, h);
        }
    });
    ctx.restore();

    ctx.fillStyle = '#94a3b8'; ctx.textAlign = 'left';
    ctx.fillText('增發規模直條圖 ($B) — 紫色: 可轉債, 綠色: ATM 股票', chartLeft + 4, p2Top - 4);
    ctx.strokeStyle = '#1e293b'; ctx.beginPath();
    ctx.moveTo(chartLeft, p2Top + p2H); ctx.lineTo(chartRight, p2Top + p2H); ctx.stroke();

    for (let b = 1; b <= Math.floor(maxAmt); b += 2) {
        const yLine = p2Top + p2H - amtToH(b);
        ctx.fillStyle = '#64748b';
        ctx.fillText('$' + b + 'B', chartRight + 6, yLine + 3);
    }

    // Panel 3: mNAV (Clip 保護)
    ctx.save();
    ctx.beginPath();
    ctx.rect(chartLeft, p3Top - 6, chartWidth, p3H + 12);
    ctx.clip();

    const maxMNav = 4.0, minMNav = 0.5;
    const mnavToY = (m) => p3Top + p3H - ((m - minMNav) / (maxMNav - minMNav)) * (p3H - 10);

    const y1x = mnavToY(1.0);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.setLineDash([4, 4]);
    ctx.beginPath(); ctx.moveTo(chartLeft, y1x); ctx.lineTo(chartRight, y1x); ctx.stroke();
    ctx.setLineDash([]);

    ctx.strokeStyle = '#38bdf8'; ctx.lineWidth = 1.8; ctx.beginPath();
    currentData.forEach((d, i) => {
        const x = chartLeft + i * step + step / 2;
        const y = mnavToY(d.basic_mnav);
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();

    ctx.strokeStyle = '#ec4899'; ctx.lineWidth = 1.8; ctx.beginPath();
    currentData.forEach((d, i) => {
        const x = chartLeft + i * step + step / 2;
        const y = mnavToY(d.diluted_mnav);
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();
    ctx.restore();

    ctx.fillStyle = '#94a3b8'; ctx.textAlign = 'left';
    ctx.fillText('mNAV 溢價倍數 (藍色: Basic, 粉色: Diluted)', chartLeft + 4, p3Top - 4);
    ctx.strokeStyle = '#1e293b'; ctx.beginPath();
    ctx.moveTo(chartLeft, p3Top + p3H); ctx.lineTo(chartRight, p3Top + p3H); ctx.stroke();

    ctx.fillStyle = '#f8fafc';
    ctx.fillText('1.0x 基準', chartRight + 6, y1x + 3);
    [2.0, 3.0].forEach(m => {
        const yM = mnavToY(m);
        ctx.fillStyle = '#64748b';
        ctx.fillText(m + '.0x', chartRight + 6, yM + 3);
    });

    // 底部 X 軸時間刻度
    ctx.fillStyle = '#64748b';
    ctx.font = '11px sans-serif';
    ctx.textAlign = 'center';

    const tickInterval = Math.max(1, Math.floor(n / 6));
    for (let i = 0; i < n; i += tickInterval) {
        const x = chartLeft + i * step + step / 2;
        const dateStr = currentData[i].date;
        const labelText = (n <= 45) ? dateStr.substring(5) : dateStr.substring(0, 7);
        ctx.fillText(labelText, x, xAxisY);

        ctx.strokeStyle = 'rgba(30, 41, 59, 0.4)';
        ctx.setLineDash([2, 4]);
        ctx.beginPath(); ctx.moveTo(x, p1Top); ctx.lineTo(x, p3Top + p3H); ctx.stroke();
        ctx.setLineDash([]);
    }

    // Crosshair
    if (hoveredIndex >= 0 && hoveredIndex < n && !isDragging) {
        const x = chartLeft + hoveredIndex * step + step / 2;
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
        ctx.setLineDash([4, 4]); ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(x, 15); ctx.lineTo(x, p3Top + p3H); ctx.stroke();
        ctx.setLineDash([]);
    }
}

// 歷次增發清單
const eventListEl = document.getElementById('eventList');
eventListEl.innerHTML = events.map(ev => `
    <div class="event-item" onclick="focusDate('${ev.date}')" id="item_${ev.id}">
        <div class="date">
            <span class="badge" style="background:${ev.color}22; color:${ev.color}; border:1px solid ${ev.color}44;">${ev.typeName}</span>
            <span>${ev.date}</span>
        </div>
        <div class="title">${ev.title}</div>
        <div class="meta">
            • 規模: <strong style="color:#fff;">${ev.amountStr}</strong> | 成本: <strong>${ev.coupon}</strong><br>
            • 轉股價: <strong>${ev.conversionPrice}</strong><br>
            • 申報文件: <code>${ev.secForm}</code>
        </div>
    </div>
`).join('');

// 完整表格
const tableBodyEl = document.getElementById('tableBody');
tableBodyEl.innerHTML = events.map(ev => `
    <tr>
        <td style="font-weight:600;">${ev.date}</td>
        <td><span class="badge badge-${ev.type === 'convertible_note' ? 'purple' : ev.type === 'atm_equity' ? 'green' : 'amber'}">${ev.typeName}</span></td>
        <td style="font-weight:600; color:#fff;">${ev.title}</td>
        <td style="color:#38bdf8; font-weight:700;">${ev.amountStr}</td>
        <td>${ev.conversionPrice}</td>
        <td><code>${ev.secForm}</code></td>
    </tr>
`).join('');

function focusDate(targetDate) {
    document.querySelectorAll('.event-item').forEach(el => el.classList.remove('selected'));
    const targetItem = document.getElementById('item_' + events.find(e => e.date === targetDate).id);
    if (targetItem) targetItem.classList.add('selected');

    const rawIdx = rawData.findIndex(d => d.date === targetDate);
    if (rawIdx !== -1) {
        updateViewRange(Math.max(0, rawIdx - 20), Math.min(rawData.length - 1, rawIdx + 20));
        document.querySelectorAll('.btn-group .btn').forEach(b => b.classList.remove('active'));

        const idx = currentData.findIndex(d => d.date === targetDate);
        if (idx !== -1) {
            hoveredIndex = idx;
            const rect = canvas.getBoundingClientRect();
            const chartLeft = 10;
            const chartWidth = rect.width - 75;
            const step = chartWidth / currentData.length;
            const mouseX = rect.left + chartLeft + idx * step + step / 2;
            const mouseY = rect.top + 160;
            showTooltipAt(idx, mouseX, mouseY);
            renderChart();
        }
    }
}

initSize();
</script>

</body>
</html>"""

# -------------------------------------------------------------
# 6. 安全替換並以 UTF-8-SIG (帶 BOM 標頭) 寫入檔案
# -------------------------------------------------------------
final_html = html_template.replace(
    "__CANDLES_DATA__", json.dumps(candles, ensure_ascii=False)
)
final_html = final_html.replace(
    "__EVENTS_DATA__", json.dumps(base_events, ensure_ascii=False)
)
final_html = final_html.replace("__LATEST_PRICE__", str(candles[-1]["close"]))
final_html = final_html.replace(
    "__BTC_PRICE__", f"{int(btc_current_price):,}"
)
final_html = final_html.replace(
    "__BASIC_SHARES__", f"{(current_shares / 1000000):.1f}M 股"
)
final_html = final_html.replace(
    "__DILUTED_SHARES__", f"{(current_shares * 1.25 / 1000000):.1f}M 股"
)
final_html = final_html.replace("__EVENT_COUNT__", str(len(base_events)))

with open("index.html", "w", encoding="utf-8-sig") as f:
  f.write(final_html)

print("✅ 成功生成純淨 UTF-8-SIG index.html，徹底解決亂碼與字串衝突！")
