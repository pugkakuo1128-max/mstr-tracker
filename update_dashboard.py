import json
import os
import numpy as np
import pandas as pd
import requests
import yfinance as yf

# 1. 抓取 MSTR 2024 至今最新股價數據
ticker = yf.Ticker("MSTR")
df = ticker.history(period="1y")

if df.empty:
  print("無法取得 MSTR 股價數據")
  exit(1)

# 2. 取得比特幣即時價格 (CoinGecko API)
try:
  btc_res = requests.get(
      "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
      timeout=10,
  )
  btc_current_price = btc_res.json()["bitcoin"]["usd"]
except Exception:
  btc_current_price = 95000.0  # 備用參考價

# 3. MSTR 最新核心資本數據 (可隨每季 10-Q 定期微調)
CURRENT_BTC_HELD = 423650  # 截至最新持幣量
BASIC_SHARES = 248000000  # 普通股流通股數
DILUTED_SHARES = 310000000  # 完全稀釋總股數 (含可轉債)

# 4. 歷次增發事件對照表
events = [
    {
        "date": "2024-03-08",
        "type": "note",
        "badge": "0.625% 可轉債",
        "amount": 0.80,
        "title": "發行 $800M 0.625% 可轉債 (Due 2030)",
        "color": "#8b5cf6",
    },
    {
        "date": "2024-03-15",
        "type": "note",
        "badge": "0.875% 可轉債",
        "amount": 0.60,
        "title": "發行 $604M 0.875% 可轉債 (Due 2031)",
        "color": "#8b5cf6",
    },
    {
        "date": "2024-06-14",
        "type": "note",
        "badge": "2.25% 可轉債",
        "amount": 0.80,
        "title": "發行 $800M 2.25% 可轉債 (Due 2032)",
        "color": "#8b5cf6",
    },
    {
        "date": "2024-08-08",
        "type": "corp",
        "badge": "1:10 拆股",
        "amount": 0.0,
        "title": "執行 1 拆 10 股票分割",
        "color": "#f59e0b",
    },
    {
        "date": "2024-09-18",
        "type": "note",
        "badge": "0.625% 可轉債",
        "amount": 1.01,
        "title": "發行 $1.01B 0.625% 可轉債 (Due 2028)",
        "color": "#8b5cf6",
    },
    {
        "date": "2024-10-30",
        "type": "corp",
        "badge": "420億計畫",
        "amount": 42.0,
        "title": "發布 21/21 計畫 (420 億美元融資)",
        "color": "#f59e0b",
    },
    {
        "date": "2024-11-11",
        "type": "atm",
        "badge": "ATM 20.3億",
        "amount": 2.03,
        "title": "ATM 增發籌資 20.3 億美元買 27,200 BTC",
        "color": "#10b981",
    },
    {
        "date": "2024-11-18",
        "type": "atm",
        "badge": "ATM 46.0億",
        "amount": 4.60,
        "title": "ATM 增發籌資 46 億美元買 51,780 BTC",
        "color": "#10b981",
    },
    {
        "date": "2024-11-21",
        "type": "note",
        "badge": "0.0% 可轉債",
        "amount": 3.00,
        "title": "發行 $3.0B 0.0% 零息可轉債 (轉股價 $672.4)",
        "color": "#8b5cf6",
    },
    {
        "date": "2024-12-09",
        "type": "atm",
        "badge": "ATM 21.5億",
        "amount": 2.15,
        "title": "ATM 增發籌資 21.5 億美元買 21,550 BTC",
        "color": "#10b981",
    },
]

event_dict = {e["date"]: e for e in events}

# 5. 計算均線與雙軌 mNAV
candles = []
closes = df["Close"].tolist()

for i, (ts, row) in enumerate(df.iterrows()):
  d_str = ts.strftime("%Y-%m-%d")
  close_p = round(float(row["Close"]), 2)

  # 計算 mNAV (以最新持幣和估算幣價基準)
  btc_nav = CURRENT_BTC_HELD * btc_current_price
  basic_mnav = round((BASIC_SHARES * close_p) / btc_nav, 2)
  diluted_mnav = round((DILUTED_SHARES * close_p) / btc_nav, 2)

  ev = event_dict.get(d_str)
  note_amt = ev["amount"] if ev and ev["type"] == "note" else 0.0
  atm_amt = ev["amount"] if ev and ev["type"] == "atm" else 0.0

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

# 6. 讀取並替換 HTML 模板
html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>MSTR 每日自動更新分析儀表板</title>
    <style>
        body {{ background:#0b1120; color:#f8fafc; font-family:-apple-system,BlinkMacSystemFont,sans-serif; margin:0; padding:20px; }}
        .card {{ background:#131d31; border:1px solid #26354f; border-radius:10px; padding:16px; margin-bottom:20px; }}
        .header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; }}
        .tag {{ background:rgba(56,189,248,0.15); color:#38bdf8; padding:4px 8px; border-radius:6px; font-size:12px; }}
        canvas {{ width:100%; height:620px; background:#070d18; border-radius:8px; border:1px solid #1c2b44; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <h2>MicroStrategy (MSTR) 全景儀表板 <span class="tag">自動每日更新</span></h2>
            <div>最新收盤: <strong>${candles[-1]['close']}</strong> | BTC 估價: <strong>${int(btc_current_price):,}</strong></div>
        </div>
        <p style="color:#94a3b8; font-size:13px;">上圖：股價 K 線與增發標記 ｜ 中圖：增發規模直條圖 ($B) ｜ 下圖：舊版 (Basic) vs 新版 (Diluted) mNAV</p>
        <canvas id="cv"></canvas>
    </div>
    <script>
        const data = {json.dumps(candles)};
        const cv = document.getElementById('cv');
        const ctx = cv.getContext('2d');
        function draw() {{
            const dpr = window.devicePixelRatio || 1;
            const r = cv.getBoundingClientRect();
            cv.width = r.width * dpr; cv.height = r.height * dpr;
            ctx.scale(dpr, dpr);
            const w = r.width - 60, h = r.height;
            const p1H = h * 0.5, p2H = h * 0.2, p3H = h * 0.2;
            const step = w / data.length;
            let minP = Math.min(...data.map(d=>d.low)), maxP = Math.max(...data.map(d=>d.high));
            minP *= 0.95; maxP *= 1.05;

            // 1. K-line
            data.forEach((d, i) => {{
                const x = 10 + i * step + step/2;
                const isUp = d.close >= d.open;
                ctx.strokeStyle = isUp ? '#10b981' : '#ef4444';
                ctx.fillStyle = ctx.strokeStyle;
                const yH = p1H - ((d.high - minP)/(maxP - minP))*p1H + 20;
                const yL = p1H - ((d.low - minP)/(maxP - minP))*p1H + 20;
                const yO = p1H - ((d.open - minP)/(maxP - minP))*p1H + 20;
                const yC = p1H - ((d.close - minP)/(maxP - minP))*p1H + 20;
                ctx.beginPath(); ctx.moveTo(x, yH); ctx.lineTo(x, yL); ctx.stroke();
                ctx.fillRect(x - Math.max(1, step*0.3), Math.min(yO, yC), Math.max(2, step*0.6), Math.max(2, Math.abs(yC - yO)));

                if(d.badge) {{
                    ctx.fillStyle = d.badge_color;
                    ctx.beginPath(); ctx.arc(x, yH - 12, 4, 0, Math.PI*2); ctx.fill();
                }}
            }});

            // 2. Offering Bars (Middle)
            const p2Top = p1H + 40;
            ctx.fillStyle = '#64748b'; ctx.font = '11px sans-serif';
            ctx.fillText('增發金額直條圖 ($B)', 10, p2Top - 6);
            data.forEach((d, i) => {{
                const x = 10 + i * step + step/2;
                const amt = d.note_amt || d.atm_amt;
                if(amt > 0) {{
                    const barH = (amt / 5.0) * p2H;
                    ctx.fillStyle = d.note_amt > 0 ? '#8b5cf6' : '#10b981';
                    ctx.fillRect(x - 3, p2Top + p2H - barH, 6, barH);
                }}
            }});

            // 3. mNAV (Bottom)
            const p3Top = p2Top + p2H + 30;
            ctx.fillText('mNAV (藍: Basic, 粉: Diluted)', 10, p3Top - 6);
            ctx.strokeStyle = '#38bdf8'; ctx.lineWidth = 1.5; ctx.beginPath();
            data.forEach((d, i) => {{
                const x = 10 + i * step + step/2;
                const y = p3Top + p3H - (d.basic_mnav / 4.0)*p3H;
                if(i===0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.stroke();

            ctx.strokeStyle = '#ec4899'; ctx.beginPath();
            data.forEach((d, i) => {{
                const x = 10 + i * step + step/2;
                const y = p3Top + p3H - (d.diluted_mnav / 4.0)*p3H;
                if(i===0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.stroke();
        }}
        window.addEventListener('resize', draw);
        draw();
    </script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
  f.write(html_content)

print("index.html 生成成功！")
