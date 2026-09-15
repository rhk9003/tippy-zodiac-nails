# tippy 星座幸運甲

tippy 官網「12 星座 × 穿戴甲」內容區塊。不綁月份的常青頁：每個星座寫適合風格、適合顏色、幸運物，並放 2 款推薦戴甲。

- **預覽網址**：https://rhk9003.github.io/tippy-zodiac-nails/
- **嵌入碼**：[`embed.html`](embed.html)
- **Repo**：`rhk9003/tippy-zodiac-nails`（public，GitHub Pages 從 `main` 根目錄發布；預覽頁有 `noindex`）

## 放進官網

1. 打開 `embed.html`，全選複製。
2. 在 Shopline 頁面加一個自訂 HTML 區塊，整段貼上。
3. 頁面標題、網址、SEO 設定在 Shopline 後台另外填。

嵌入碼沒有 script。樣式全部在 `.tpz` 底下，不會影響官網其他區塊；字體沿用官網。

## 提品／換商品

1. 在 `data/zodiac.json` 找到星座，把商品網址填進 `products` 的 `url`（每個星座 2 款）。
2. 執行：

```bash
python3 tools/build.py --fetch
```

會從商品頁抓商品名稱與圖片，重新產生 `embed.html` 與 `index.html`。

3. commit、push 後預覽網址會更新；官網那段要重新貼一次 `embed.html`。

商品下架或想換款，只要改 `url` 並清空該格的 `name`、`image` 再跑一次。沒填網址的格子會顯示「待提品」。

## 檔案

| 檔案 | 用途 |
|---|---|
| `data/zodiac.json` | 文字、顏色、幸運物、推薦商品、延伸閱讀連結 |
| `tools/build.py` | 產生 `embed.html` 與 `index.html` |
| `embed.html` | 貼進官網的內容 |
| `index.html` | 預覽頁（外面多一條預覽說明） |
