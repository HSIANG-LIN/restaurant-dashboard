# 餐廳美食地圖 Dashboard — activeContext

> 個人美食地圖，用戶丟連結 → 判斷是否餐廳 → 存入 pending.json → 批次處理 → GitHub Pages
> 上次更新：2026-04-30

---

## 流程

```
使用者丟連結 (Telegram)
  ↓
Hermes 判斷是否餐廳
  ↓ 是
存入 pending.json
  ↓
Cron 每天 24:00 批次處理
  ├── geocode（OpenStreetMap）
  ├── 寫入 restaurants.json
  └── git push → GitHub Pages 自動更新
```

---

## 目錄結構

| 檔案 | 說明 |
|------|------|
| `restaurants.json` | 已處理的餐廳資料（含座標、地圖、筆記） |
| `pending.json` | 待處理佇列（名稱、連結、地址、備註、時間） |
| `index.html` | 地圖 Dashboard（Leaflet + Google Maps 導航） |
| `batch_process.py` | 批次處理腳本（geocode + 寫入 + push） |
| `server.py` | 開發用 HTTP Server port 8788 |

---

## 排程任務

| 任務 | 時程 | job_id |
|------|------|--------|
| 美食批次處理 | 每天 24:00 | `8803a1d0c9d6` |

- **GitHub Pages：** `https://github.com/HSIANG-LIN/restaurant-dashboard` (public)
- **開發 Server：** `python3 server.py` → port 8788

---

## 技術上下文

| 項目 | 值 |
|------|-----|
| 根目錄 | `~/workspace/hermes_project/restaurant-dashboard/` |
| 地圖 | OpenStreetMap + Leaflet |
| 座標 | 手動 geocode 後寫入 |
| 匯出格式 | static JSON（GitHub Pages friendly） |
| 導航 | Google Maps 一鍵直達（popup + 側欄列表） |

---

## 使用者偏好

- 住在台北信義區象山站附近（25.030, 121.575）
- 偏好透過 Telegram 丟連結收錄新餐廳
- 目前的 pending 佇列包含：波WAVE 鷹嘴豆泥屋（pending.json）
