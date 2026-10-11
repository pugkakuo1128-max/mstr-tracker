import json
import os
import numpy as np
import pandas as pd
import requests
import yfinance as yf

# 1. 抓取從 2024 年至今的所有歷史股價 (確保涵蓋所有增發日期)
print("正在抓取 MSTR 股價數據...")
ticker = yf.Ticker("MSTR")
df = ticker.history(start="2024-01-01")

if df.empty:
  print("抓取失敗，使用備用週期重試...")
  df = ticker.history(period="2y")

# 2. 取得比特幣即時價格 (CoinGecko API)
try:
  btc_res = requests.get(
      "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
      timeout=10,
  )
  btc_current_price = btc_res.json()["bitcoin"]["usd"]
except Exception:
  btc_current_price = 95000.0

# 3. MSTR 最新核心資本數據
CURRENT_BTC_HELD = 423650  # 最新比特幣持倉 (枚)
BASIC_SHARES = 248000000  # 普通股流通股數 (Basic Shares)
DILUTED_SHARES = 310000000  # 完全稀釋總股數 (含可轉債轉股)
TOTAL_DEBT_NOTES = 6.21  # 可轉債未償總面額 (十億美元 $B)

# 4. 歷次增發詳細數據庫 (可轉債 + ATM 普通股 + 重大行動)
events = [
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
        "conversionPrice": "$149.77 (拆股前 $1,497.68)",
        "premium": "42.5%",
        "maturity": "2030-03-15",
        "btcUsage": "購入 12,000 枚比特幣 (約 $8.2 億)",
        "secForm": "Form 8-K (Item 1.01, 3.02) / 424B5",
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
        "amountStr": "$603.75M ($0.60B)",
        "coupon": "0.875%",
        "conversionPrice": "$232.72 (拆股前 $2,327.21)",
        "premium": "40.0%",
        "maturity": "2031-03-15",
        "btcUsage": "購入 9,245 枚比特幣 (約 $6.23 億)",
        "secForm": "Form 8-K (Item 1.01, 3.02) / 424B5",
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
        "conversionPrice": "$204.33 (拆股前 $2,043.32)",
        "premium": "35.0%",
        "maturity": "2032-06-15",
        "btcUsage": "購入 11,931 枚比特幣 (均價約 $65,883)",
        "secForm": "Form 8-K (Item 1.01, 3.02) / 424B5",
        "color": "#8b5cf6",
    },
    {
        "id": "ev4",
        "date": "2024-08-08",
        "type": "corporate_action",
        "typeName": "重大資本行動",
        "badge": "1:10 拆股",
        "title": "執行 1 拆 10 股票分割 (10-for-1 Stock Split)",
        "amount": 0.0,
        "amountStr": "流通性翻倍",
        "coupon": "-",
        "conversionPrice": "所有轉股價相應除以 10",
        "premium": "-",
        "maturity": "-",
        "btcUsage": "大幅降低投資門檻，使零售與衍生品流動性暴增",
        "secForm": "Form 8-K (Item 5.03)",
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
        "conversionPrice": "$183.19 (拆股後市價)",
        "premium": "40.0%",
        "maturity": "2028-09-15",
        "btcUsage": "置換舊有 6.125% 高利抵押債並加購 7,420 枚 BTC",
        "secForm": "Form 8-K (Item 1.01, 3.02) / 424B5",
        "color": "#8b5cf6",
    },
    {
        "id": "ev6",
        "date": "2024-10-30",
        "type": "corporate_action",
        "typeName": "資本架構戰略",
        "badge": "420億計畫",
        "title": "重磅發布「21/21 計畫」：3 年籌資 420 億美元買幣",
        "amount": 42.0,
        "amountStr": "$42.0B 總額度",
        "coupon": "混合",
        "conversionPrice": "隨行就市 (ATM) / 債券定價",
        "premium": "-",
        "maturity": "2025 ~ 2027 年",
        "btcUsage": "210 億普通股 ATM + 210 億固定收益，全面開啟瘋狂買幣",
        "secForm": "Form 8-K / Q3 10-Q",
        "color": "#f59e0b",
    },
    {
        "id": "ev7",
        "date": "2024-11-11",
        "type": "atm_equity",
        "typeName": "ATM 普通股增發",
        "badge": "ATM 20.3億",
        "title": "ATM 增發普通股籌資 20.3 億美元購入 27,200 枚 BTC",
        "amount": 2.03,
        "amountStr": "$2.03B",
        "coupon": "無 (股票權益)",
        "conversionPrice": "售股均價約 $265/股",
        "premium": "高溢價售股",
        "maturity": "永久性權益資本",
        "btcUsage": "購入 27,200 枚 BTC，持倉達 279,420 枚",
        "secForm": "Form 8-K (Item 8.01) / 424B5",
        "color": "#10b981",
    },
    {
        "id": "ev8",
        "date": "2024-11-18",
        "type": "atm_equity",
        "typeName": "ATM 普通股增發",
        "badge": "ATM 46.0億",
        "title": "ATM 增發普通股籌資 46 億美元購入 51,780 枚 BTC",
        "amount": 4.60,
        "amountStr": "$4.60B",
        "coupon": "無 (股票權益)",
        "conversionPrice": "售股均價約 $358/股",
        "premium": "高溢價售股",
        "maturity": "永久性權益資本",
        "btcUsage": "單週增發 46 億美元，購入 51,780 枚 BTC，成交量超越輝達",
        "secForm": "Form 8-K (Item 8.01) / 424B5",
        "color": "#10b981",
    },
    {
        "id": "ev9",
        "date": "2024-11-21",
        "type": "convertible_note",
        "typeName": "可轉換公司債",
        "badge": "0.0% 零息債",
        "title": "發行 30 億美元 0.0% 零利率可轉換優先公司債 (Due 2029)",
        "amount": 3.00,
        "amountStr": "$3.00B (從 17.5億追加)",
        "coupon": "0.00% (完全零息！)",
        "conversionPrice": "$672.40 (創下歷史最高轉股價)",
        "premium": "55.0% 溢價",
        "maturity": "2029-12-01",
        "btcUsage": "零成本借貸 30 億美元，全數注入比特幣購買基金",
        "secForm": "Form 8-K (Item 1.01, 3.02) / 424B5",
        "color": "#8b5cf6",
    },
    {
        "id": "ev10",
        "date": "2024-12-09",
        "type": "atm_equity",
        "typeName": "ATM 普通股增發",
        "badge": "ATM 21.5億",
        "title": "ATM 增發籌資 21.5 億美元購入 21,550 枚 BTC",
        "amount": 2.15,
        "amountStr": "$2.15B",
        "coupon": "無 (股票權益)",
        "conversionPrice": "售股均價約 $385/股",
        "premium": "高溢價售股",
        "maturity": "永久性權益資本",
        "btcUsage": "購入 21,550 枚 BTC，總持倉正式突破 423,650 枚",
        "secForm": "Form 8-K (Item 8.01) / 424B5",
        "color": "#10b981",
    },
]

event_dict = {e["date"]: e for e in events}

# 5. 組裝每日資料並動態推算雙軌 mNAV
candles = []
closes = [float(c) for c in df["Close"]]

for i, (ts, row) in enumerate(df.iterrows()):
  d_str = ts.strftime("%Y-%m-%d")
  close_p = round(float(row["Close"]), 2)

  # 動態推算當期持幣量與流通股數
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
    b_held, b_sh, d_sh = CURRENT_BTC_HELD, BASIC_SHARES, DILUTED_SHARES

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
      "ev_id": ev["id"] if ev else None,
      "badge": ev["badge"] if ev else None,
      "badge_color": ev["color"] if ev else None,
      "event_title": ev["title"] if ev else None,
  })

# 6. 生成完整多面板交互 HTML 頁面
html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MicroStrategy (MSTR) 增發數據與全景 K 線儀表板</title>
    <style>
        :root {{
            --bg-primary: #0b1120;
            --bg-secondary: #131d31;
            --border-color: #26354f;
            --accent-purple: #8b5cf6;
            --accent-green: #10b981;
            --accent-amber: #f59e0b;
            --accent-blue: #38bdf8;
            --accent-pink: #ec4899;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-primary);
            color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang TC", "Microsoft JhengHei", sans-serif;
            padding: 24px;
            line-height: 1.5;
        }}
        .container {{ max-width: 1480px; margin: 0 auto; }}
        .header {{ display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px; margin-bottom: 20px; }}
        .header h1 {{ font-size: 24px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 10px; }}
        .header span.tag {{ font-size: 12px; background: rgba(56, 189, 248, 0.15); color: var(--accent-blue); padding: 3px 8px; border-radius: 6px; border: 1px solid rgba(56, 189, 248, 0.3); }}
        
        /* Stats Grid */
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 20px; }}
        .stat-card {{ background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 10px; padding: 14px 18px; }}
        .stat-title {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; margin-bottom: 4px; }}
        .stat-val {{ font-size: 22px; font-weight: 700; color: #fff; }}
        .stat-sub {{ font-size: 12px; margin-top: 3px; color: #94a3b8; }}

        /* Chart Canvas */
        .chart-box {{ background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px; margin-bottom: 24px; }}
        .chart-toolbar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 12px; }}
        .legend-group {{ display: flex; align-items: center; gap: 14px; font-size: 13px; color: #94a3b8; flex-wrap: wrap; }}
        .legend-item {{ display: flex; align-items: center; gap: 6px; }}
        .legend-box {{ width: 12px; height: 4px; border-radius: 2px; display: inline-block; }}
        .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
        .btn-group {{ display: flex; gap: 6px; }}
        .btn {{ background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 5px 12px; border-radius: 6px; font-size: 12px; cursor: pointer; }}
        .btn.active {{ background: #334155; color: #fff; border-color: var(--accent-blue); }}

        .canvas-wrapper {{ position: relative; width: 100%; height: 680px; background: #070d18; border-radius: 8px; border: 1px solid #1c2b44; overflow: hidden; }}
        canvas {{ display: block; width: 100%; height: 100%; }}

        /* Tooltip */
        #chartTooltip {{
            position: absolute; display: none; background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(8px);
            border: 1px solid #475569; border-radius: 8px; padding: 12px 16px; font-size: 12px; color: #fff;
            pointer-events: none; box-shadow: 0 10px 20px rgba(0,0,0,0.5); z-index: 100; min-width: 240px;
        }}
        #chartTooltip .tt-title {{ font-weight: 700; margin-bottom: 6px; border-bottom: 1px solid #334155; padding-bottom: 4px; color: #38bdf8; }}
        #chartTooltip .tt-row {{ display: flex; justify-content: space-between; margin: 3px 0; }}
        #chartTooltip .tt-badge {{ margin-top: 8px; padding: 4px 8px; border-radius: 4px; font-weight: 600; text-align: center; }}

        /* Bottom Grid */
        .grid-2col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }}
        @media (max-width: 1024px) {{ .grid-2col {{ grid-template-columns: 1fr; }} }}
        .panel-card {{ background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; }}
        .panel-card h2 {{ font-size: 17px; font-weight: 700; margin-bottom: 14px; color: #fff; display: flex; align-items: center; gap: 8px; }}

        .event-item {{ border-left: 3px solid #64748b; padding: 8px 12px; margin-bottom: 10px; cursor: pointer; transition: all 0.2s; border-radius: 0 6px 6px 0; background: rgba(255,255,255,0.01); }}
        .event-item:hover, .event-item.selected {{ border-left-color: var(--accent-blue); background: rgba(56, 189, 248, 0.08); }}
        .event-item .date {{ font-size: 12px; color: #94a3b8; display: flex; align-items: center; gap: 6px; }}
        .event-item .title {{ font-size: 14px; font-weight: 600; color: #f1f5f9; margin: 2px 0; }}
        .event-item .meta {{ font-size: 12px; color: #94a3b8; }}

        .concept-card {{ background: #10192d; border: 1px solid #1d2e4d; border-radius: 10px; padding: 16px; margin-bottom: 14px; }}
        .concept-card h3 {{ font-size: 15px; color: var(--accent-blue); margin-bottom: 8px; }}
        .concept-card p {{ font-size: 13px; color: #cbd5e1; line-height: 1.6; }}

        /* Table */
        .table-responsive {{ overflow-x: auto; margin-top: 10px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th {{ background: #0d1525; color: #94a3b8; font-weight: 600; text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border-color); }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #1e2c43; color: #e2e8f0; }}
        tr:hover td {{ background: rgba(255,255,255,0.02); }}
        .badge {{ display: inline-block; font-size: 11px; font-weight: 600; padding: 2px 7px; border-radius: 4px; }}
        .badge-purple {{ background: rgba(139, 92, 246, 0.2); color: #c4b5fd; border: 1px solid rgba(139, 92, 246, 0.4); }}
        .badge-green {{ background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4); }}
        .badge-amber {{ background: rgba(245, 158, 11, 0.2); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.4); }}
        code {{ background: #0b1120; padding: 2px 5px; border-radius: 4px; color: #f472b6; font-family: monospace; font-size: 12px; }}
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <div>
            <h1>MicroStrategy (MSTR) 增發數據與全景 K 線儀表板 <span class="tag">每日自動更新</span></h1>
            <p>已整合：可轉債（利率/轉股價）、ATM 普通股增發直條圖、雙軌 mNAV（舊版 Basic vs 新版 Diluted）與 SEC 申報代號。</p>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 13px; color: #94a3b8;">最新收盤價: <strong style="color:#fff; font-size:16px;">${candles[-1]['close']}</strong></div>
            <div style="font-size: 12px; color: #f59e0b;">BTC 參考估價: ${int(btc_current_price):,} USD</div>
        </div>
    </div>

    <!-- 4 Stats Cards -->
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-title">普通股流通總數 (Basic)</div>
            <div class="stat-val" style="color: #38bdf8;">{(BASIC_SHARES / 1000000):.1f}M 股</div>
            <div class="stat-sub">1:10 拆股後普通股股本</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">完全稀釋總股數 (Diluted)</div>
            <div class="stat-val" style="color: #ec4899;">{(DILUTED_SHARES / 1000000):.1f}M 股</div>
            <div class="stat-sub">計入所有可轉債轉股稀釋</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">可轉債總餘額 (Notes)</div>
            <div class="stat-val" style="color: #8b5cf6;">${TOTAL_DEBT_NOTES}B</div>
            <div class="stat-sub">5 筆可轉債 (利率 0% ~ 2.25%)</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">比特幣總持倉量</div>
            <div class="stat-val" style="color: #10b981;">{CURRENT_BTC_HELD:,} BTC</div>
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
                <button class="btn active" onclick="setTimeframe('all')">全景 (2024至今)</button>
                <button class="btn" onclick="setTimeframe('h1')">2024 上半年</button>
                <button class="btn" onclick="setTimeframe('h2')">2024 下半年狂飆期</button>
            </div>
        </div>

        <div class="canvas-wrapper" id="canvasWrapper">
            <canvas id="klineCanvas"></canvas>
            <div id="chartTooltip"></div>
        </div>
    </div>

    <!-- 2 Column Breakdown -->
    <div class="grid-2col">
        <!-- Event List -->
        <div class="panel-card">
            <h2><span>📌</span> 歷次增發詳細數據清單（點選定位圖表）</h2>
            <div id="eventList" style="max-height: 480px; overflow-y: auto; padding-right: 6px;"></div>
        </div>

        <!-- Concept Knowledge -->
        <div class="panel-card">
            <h2><span>💡</span> 什麼是 ATM 與新舊 mNAV？</h2>
            
            <div class="concept-card">
                <h3>1. ATM（At-The-Market）市價增發是什麼？</h3>
                <p>
                    <strong>「隨行就市、在市場上直接賣股票換現金」</strong>。<br>
                    傳統增發需要低價折價賣給投行機構，會造成股價大跌；而 ATM 增發是 MSTR 先跟 SEC 登記額度（例如「21/21 計畫」中的 210 億美元普通股），然後<strong>每天依照即時市價，像散戶一樣掛單賣給二級市場買盤</strong>。<br>
                    • 買氣旺就多賣，買氣弱就隨時停賣，完全不引起市場恐慌！
                </p>
            </div>

            <div class="concept-card">
                <h3>2. 舊版 mNAV vs 新版 mNAV 的盲點與進化</h3>
                <p>
                    <code>mNAV</code> 代表 MSTR 股價相對於持幣淨值的溢價倍數：<br>
                    • <strong>舊版（Basic mNAV）</strong>：<code>(普通股股數 × 股價) ÷ 比特幣總淨值</code><br>
                    <strong>盲點</strong>：完全忽略了發行的巨額可轉債！當股價大幅高於轉股價時，債券會轉成新股票，舊版會「低估總市值、顯得虛假便宜」。<br><br>
                    • <strong>新版（Diluted mNAV，現行標準）</strong>：<code>(完全稀釋總股數 × 股價) ÷ 比特幣總淨值</code><br>
                    <strong>核心</strong>：將所有已發行的可轉債全數視為<strong>已轉成普通股</strong>，真實反映完全稀釋後的市場溢價倍數！
                </p>
            </div>
        </div>
    </div>

    <!-- Complete Table -->
    <div class="panel-card" style="margin-bottom: 30px;">
        <h2><span>📊</span> MSTR 增發與重大資本事件完整對照表</h2>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>公告日期</th>
                        <th>增發工具</th>
                        <th>規格與名稱</th>
                        <th>增發規模</th>
                        <th>票面利率</th>
                        <th>轉股價格 / 發行價</th>
                        <th>比特幣購入 / 用途</th>
                        <th>SEC 申報案號</th>
                    </tr>
                </thead>
                <tbody id="tableBody"></tbody>
            </table>
        </div>
    </div>
</div>

<script>
const rawData = {json.dumps(candles)};
const events = {json.dumps(events)};

let currentData = [...rawData];
let hoveredIndex = -1;

const canvas = document.getElementById('klineCanvas');
const ctx = canvas.getContext('2d');
const wrapper = document.getElementById('canvasWrapper');
const tooltip = document.getElementById('chartTooltip');

function initSize() {{
    const dpr = window.devicePixelRatio || 1;
    const rect = wrapper.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
    renderChart();
}}

window.addEventListener('resize', initSize);

function setTimeframe(tf) {{
    document.querySelectorAll('.btn-group .btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    if (tf === 'all') {{
        currentData = [...rawData];
    }} else if (tf === 'h1') {{
        currentData = rawData.filter(d => d.date <= '2024-06-30');
    }} else if (tf === 'h2') {{
        currentData = rawData.filter(d => d.date >= '2024-07-01' && d.date <= '2024-12-31');
    }}
    renderChart();
}}

wrapper.addEventListener('mousemove', function(e) {{
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const chartW = rect.width - 70;
    const n = currentData.length;
    const step = chartW / n;
    
    if (x >= 10 && x <= chartW) {{
        hoveredIndex = Math.floor((x - 10) / step);
        if (hoveredIndex >= n) hoveredIndex = n - 1;
        if (hoveredIndex < 0) hoveredIndex = 0;
        showTooltipAt(hoveredIndex, e.clientX, e.clientY);
    }} else {{
        hoveredIndex = -1;
        tooltip.style.display = 'none';
    }}
    renderChart();
}});

wrapper.addEventListener('mouseleave', function() {{
    hoveredIndex = -1;
    tooltip.style.display = 'none';
    renderChart();
}});

function showTooltipAt(idx, mouseX, mouseY) {{
    const item = currentData[idx];
    const ev = events.find(e => e.date === item.date);
    
    let html = `
        <div class="tt-title">${{item.date}}</div>
        <div class="tt-row"><span>MSTR 收盤:</span><span style="font-weight:700; color:${{item.close >= item.open ? '#10b981' : '#ef4444'}}">$${{item.close.toFixed(2)}}</span></div>
        <div class="tt-row"><span>開 / 高 / 低:</span><span>${{item.open.toFixed(1)}} / ${{item.high.toFixed(1)}} / ${{item.low.toFixed(1)}}</span></div>
        <div class="tt-row"><span>舊版 Basic mNAV:</span><span style="color:#38bdf8; font-weight:700;">${{item.basic_mnav.toFixed(2)}}x</span></div>
        <div class="tt-row"><span>新版 Diluted mNAV:</span><span style="color:#ec4899; font-weight:700;">${{item.diluted_mnav.toFixed(2)}}x</span></div>
    `;

    if (item.note_amt > 0) {{
        html += `<div class="tt-row" style="color:#c4b5fd;"><span>可轉債增發:</span><span>$${{item.note_amt.toFixed(2)}}B</span></div>`;
    }}
    if (item.atm_amt > 0) {{
        html += `<div class="tt-row" style="color:#6ee7b7;"><span>ATM 股票增發:</span><span>$${{item.atm_amt.toFixed(2)}}B</span></div>`;
    }}

    if (ev) {{
        html += `
            <div class="tt-badge" style="background:${{ev.color}}22; color:${{ev.color}}; border:1px solid ${{ev.color}}">
                ★ ${{ev.badge}} (${{ev.amountStr}})
            </div>
            <div style="font-size:11px; color:#cbd5e1; margin-top:4px;">${{ev.title}}</div>
        `;
    }}

    tooltip.innerHTML = html;
    tooltip.style.display = 'block';

    const wrapperRect = wrapper.getBoundingClientRect();
    let left = mouseX - wrapperRect.left + 15;
    let top = mouseY - wrapperRect.top + 10;
    if (left + 260 > wrapperRect.width) left -= 280;
    if (top + 220 > wrapperRect.height) top -= 200;

    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
}}

function renderChart() {{
    const rect = wrapper.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    ctx.clearRect(0, 0, width, height);

    const chartLeft = 10;
    const chartRight = width - 65;
    const chartWidth = chartRight - chartLeft;

    const p1Top = 20, p1H = height * 0.48;
    const p2Top = height * 0.54, p2H = height * 0.18;
    const p3Top = height * 0.77, p3H = height * 0.18;

    const n = currentData.length;
    if (n === 0) return;

    let minPrice = Infinity, maxPrice = -Infinity;
    currentData.forEach(d => {{
        if (d.low < minPrice) minPrice = d.low;
        if (d.high > maxPrice) maxPrice = d.high;
    }});
    const pBuf = (maxPrice - minPrice) * 0.08;
    maxPrice += pBuf;
    minPrice = Math.max(0, minPrice - pBuf * 0.5);

    const priceToY = (p) => p1Top + p1H - ((p - minPrice) / (maxPrice - minPrice)) * p1H;
    const step = chartWidth / n;
    const candleWidth = Math.max(2, step * 0.65);

    // Panel 1: Price Grid
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 1;
    ctx.fillStyle = '#64748b';
    ctx.font = '11px sans-serif';
    ctx.textAlign = 'left';

    for (let i = 0; i <= 5; i++) {{
        const p = minPrice + (maxPrice - minPrice) * (i / 5);
        const y = priceToY(p);
        ctx.beginPath(); ctx.moveTo(chartLeft, y); ctx.lineTo(chartRight, y); ctx.stroke();
        ctx.fillText('$' + p.toFixed(0), chartRight + 6, y + 4);
    }}
    ctx.fillStyle = '#94a3b8';
    ctx.fillText('MSTR 股價 K 線 (日線)', chartLeft + 4, p1Top - 5);

    // Draw K-line
    currentData.forEach((d, i) => {{
        const x = chartLeft + i * step + step / 2;
        const isUp = d.close >= d.open;
        const color = isUp ? '#10b981' : '#ef4444';

        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.moveTo(x, priceToY(d.high)); ctx.lineTo(x, priceToY(d.low)); ctx.stroke();

        const yOpen = priceToY(d.open);
        const yClose = priceToY(d.close);
        ctx.fillStyle = color;
        ctx.fillRect(x - candleWidth / 2, Math.min(yOpen, yClose), candleWidth, Math.max(2, Math.abs(yClose - yOpen)));
    }});

    // Draw MA20 & MA50
    ctx.strokeStyle = '#38bdf8'; ctx.lineWidth = 1.5; ctx.beginPath();
    let s20 = false;
    currentData.forEach((d, i) => {{
        if (d.ma20) {{
            const x = chartLeft + i * step + step / 2;
            const y = priceToY(d.ma20);
            if (!s20) {{ ctx.moveTo(x, y); s20 = true; }} else {{ ctx.lineTo(x, y); }}
        }}
    }});
    ctx.stroke();

    ctx.strokeStyle = '#f59e0b'; ctx.lineWidth = 1.5; ctx.beginPath();
    let s50 = false;
    currentData.forEach((d, i) => {{
        if (d.ma50) {{
            const x = chartLeft + i * step + step / 2;
            const y = priceToY(d.ma50);
            if (!s50) {{ ctx.moveTo(x, y); s50 = true; }} else {{ ctx.lineTo(x, y); }}
        }}
    }});
    ctx.stroke();

    // Event Pins on Panel 1
    events.forEach(ev => {{
        const idx = currentData.findIndex(d => d.date === ev.date);
        if (idx !== -1) {{
            const d = currentData[idx];
            const x = chartLeft + idx * step + step / 2;
            const yHigh = priceToY(d.high);
            const pinY = Math.max(24, yHigh - 32);

            ctx.setLineDash([3, 3]);
            ctx.strokeStyle = ev.color;
            ctx.lineWidth = 1.5;
            ctx.beginPath(); ctx.moveTo(x, yHigh - 2); ctx.lineTo(x, pinY + 6); ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = ev.color;
            ctx.beginPath(); ctx.arc(x, pinY, 6, 0, Math.PI * 2); ctx.fill();
            ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.5; ctx.stroke();

            ctx.font = 'bold 10px sans-serif';
            const badgeW = ctx.measureText(ev.badge).width + 8;
            ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
            ctx.strokeStyle = ev.color;
            ctx.lineWidth = 1;
            ctx.beginPath(); ctx.roundRect(x - badgeW / 2, pinY - 20, badgeW, 16, 4); ctx.fill(); ctx.stroke();

            ctx.fillStyle = '#ffffff';
            ctx.textAlign = 'center';
            ctx.fillText(ev.badge, x, pinY - 8);
        }}
    }});

    // Panel 2: Offering Amounts Bar Chart ($B)
    ctx.strokeStyle = '#1e293b'; ctx.lineWidth = 1; ctx.beginPath();
    ctx.moveTo(chartLeft, p2Top + p2H); ctx.lineTo(chartRight, p2Top + p2H); ctx.stroke();

    ctx.fillStyle = '#94a3b8'; ctx.textAlign = 'left';
    ctx.fillText('增發規模直條圖 (十億美元 $B) — 紫色: 可轉債, 綠色: ATM 股票', chartLeft + 4, p2Top - 4);

    const maxAmt = 5.0;
    const amtToH = (a) => (a / maxAmt) * (p2H - 10);

    for (let b = 1; b <= 4; b++) {{
        const yLine = p2Top + p2H - amtToH(b);
        ctx.strokeStyle = 'rgba(30, 41, 59, 0.6)';
        ctx.beginPath(); ctx.moveTo(chartLeft, yLine); ctx.lineTo(chartRight, yLine); ctx.stroke();
        ctx.fillStyle = '#64748b';
        ctx.fillText('$' + b + 'B', chartRight + 6, yLine + 3);
    }}

    currentData.forEach((d, i) => {{
        const x = chartLeft + i * step + step / 2;
        const barW = Math.max(5, step * 0.85);

        if (d.note_amt > 0) {{
            const h = amtToH(d.note_amt);
            ctx.fillStyle = '#8b5cf6';
            ctx.fillRect(x - barW / 2, p2Top + p2H - h, barW, h);
            ctx.strokeStyle = '#c4b5fd';
            ctx.strokeRect(x - barW / 2, p2Top + p2H - h, barW, h);
        }}
        if (d.atm_amt > 0) {{
            const h = amtToH(d.atm_amt);
            ctx.fillStyle = '#10b981';
            ctx.fillRect(x - barW / 2, p2Top + p2H - h, barW, h);
            ctx.strokeStyle = '#6ee7b7';
            ctx.strokeRect(x - barW / 2, p2Top + p2H - h, barW, h);
        }}
    }});

    // Panel 3: mNAV Lines (Basic vs Diluted)
    ctx.strokeStyle = '#1e293b'; ctx.lineWidth = 1; ctx.beginPath();
    ctx.moveTo(chartLeft, p3Top + p3H); ctx.lineTo(chartRight, p3Top + p3H); ctx.stroke();

    ctx.fillStyle = '#94a3b8'; ctx.textAlign = 'left';
    ctx.fillText('mNAV 溢價倍數 (藍色: 舊版 Basic, 粉色: 新版 Diluted)', chartLeft + 4, p3Top - 4);

    const maxMNav = 4.0, minMNav = 0.5;
    const mnavToY = (m) => p3Top + p3H - ((m - minMNav) / (maxMNav - minMNav)) * (p3H - 10);

    const y1x = mnavToY(1.0);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.setLineDash([4, 4]);
    ctx.beginPath(); ctx.moveTo(chartLeft, y1x); ctx.lineTo(chartRight, y1x); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = '#f8fafc';
    ctx.fillText('1.0x 基準線', chartRight + 6, y1x + 3);

    [2.0, 3.0].forEach(m => {{
        const yM = mnavToY(m);
        ctx.strokeStyle = 'rgba(30, 41, 59, 0.6)';
        ctx.beginPath(); ctx.moveTo(chartLeft, yM); ctx.lineTo(chartRight, yM); ctx.stroke();
        ctx.fillStyle = '#64748b';
        ctx.fillText(m + '.0x', chartRight + 6, yM + 3);
    }});

    // Basic mNAV (Blue)
    ctx.strokeStyle = '#38bdf8'; ctx.lineWidth = 2; ctx.beginPath();
    currentData.forEach((d, i) => {{
        const x = chartLeft + i * step + step / 2;
        const y = mnavToY(d.basic_mnav);
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }});
    ctx.stroke();

    // Diluted mNAV (Pink)
    ctx.strokeStyle = '#ec4899'; ctx.lineWidth = 2; ctx.beginPath();
    currentData.forEach((d, i) => {{
        const x = chartLeft + i * step + step / 2;
        const y = mnavToY(d.diluted_mnav);
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }});
    ctx.stroke();

    // Crosshair
    if (hoveredIndex >= 0 && hoveredIndex < n) {{
        const x = chartLeft + hoveredIndex * step + step / 2;
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.setLineDash([4, 4]); ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(x, 15); ctx.lineTo(x, height - 10); ctx.stroke();
        ctx.setLineDash([]);
    }}
}}

// Event List
const eventListEl = document.getElementById('eventList');
eventListEl.innerHTML = events.map(ev => `
    <div class="event-item" onclick="focusDate('${{ev.date}}')" id="item_${{ev.id}}">
        <div class="date">
            <span class="badge" style="background:${{ev.color}}22; color:${{ev.color}}; border:1px solid ${{ev.color}}44;">${{ev.typeName}}</span>
            <span>${{ev.date}}</span>
        </div>
        <div class="title">${{ev.title}}</div>
        <div class="meta">
            • 規模: <strong style="color:#fff;">${{ev.amountStr}}</strong> | 成本: <strong>${{ev.coupon}}</strong><br>
            • 轉股價: <strong>${{ev.conversionPrice}}</strong> (${{ev.premium}})<br>
            • 申報文件: <code>${{ev.secForm}}</code>
        </div>
    </div>
`).join('');

// Table
const tableBodyEl = document.getElementById('tableBody');
tableBodyEl.innerHTML = events.map(ev => `
    <tr>
        <td style="font-weight:600;">${{ev.date}}</td>
        <td><span class="badge badge-${{ev.type === 'convertible_note' ? 'purple' : ev.type === 'atm_equity' ? 'green' : 'amber'}}">${{ev.typeName}}</span></td>
        <td style="font-weight:600; color:#fff;">${{ev.title}}</td>
        <td style="color:#38bdf8; font-weight:700;">${{ev.amountStr}}</td>
        <td>${{ev.coupon}}</td>
        <td>${{ev.conversionPrice}}</td>
        <td style="font-size:12px; color:#94a3b8;">${{ev.btcUsage}}</td>
        <td><code>${{ev.secForm}}</code></td>
    </tr>
`).join('');

function focusDate(targetDate) {{
    document.querySelectorAll('.event-item').forEach(el => el.classList.remove('selected'));
    const targetItem = document.getElementById('item_' + events.find(e => e.date === targetDate).id);
    if (targetItem) targetItem.classList.add('selected');

    const idx = currentData.findIndex(d => d.date === targetDate);
    if (idx !== -1) {{
        hoveredIndex = idx;
        const rect = canvas.getBoundingClientRect();
        const chartLeft = 10;
        const chartWidth = rect.width - 75;
        const step = chartWidth / currentData.length;
        const mouseX = rect.left + chartLeft + idx * step + step / 2;
        const mouseY = rect.top + 160;
        showTooltipAt(idx, mouseX, mouseY);
        renderChart();
    }}
}}

initSize();
</script>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
  f.write(html_content)

print(f"成功生成完整 index.html！檔案大小: {len(html_content.encode('utf-8'))} bytes")
