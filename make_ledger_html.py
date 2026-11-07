#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 11 月账本渲染成单文件 HTML（无外部依赖，双击即可看）。"""

import datetime as dt
from html import escape
from pathlib import Path

import ledger_data as d

OUT = Path("/Users/gsy/Documents/记账/2026年11月账单.html")
INDEX = OUT.with_name("index.html")

CSS = """
:root{
  --bg:#F4F5F7;
  --card:#FFFFFF;
  --ink:#131720;
  --muted:#8B94A3;
  --line:#ECEFF3;
  --hair:#F5F6F9;
  --daily:#2F6FEB;
  --fixed:#7C5CD6;
  --prepaid:#DE8B2C;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0;background:var(--bg);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased;
}
.page{max-width:780px;margin:0 auto;padding:44px 20px 72px}
.eyebrow{margin:0;font-size:12px;letter-spacing:.18em;color:var(--muted)}
.hero{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;flex-wrap:wrap;margin-bottom:26px}
.hero h1{margin:6px 0 0;font-size:34px;font-weight:700;letter-spacing:-.01em}
.hero-total{text-align:right}
.hero-total .label{display:block;font-size:12px;color:var(--muted)}
.hero-total strong{display:block;font-size:40px;font-weight:700;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.hero-total .sub{font-size:12px;color:var(--muted)}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:18px}
.stat{background:var(--card);border-radius:14px;padding:14px 16px;border:1px solid rgba(19,23,32,.045);box-shadow:0 1px 2px rgba(19,23,32,.04)}
.stat .name{display:flex;align-items:center;gap:7px;font-size:12px;color:var(--muted)}
.stat strong{display:block;font-size:21px;margin-top:6px;font-variant-numeric:tabular-nums}
.stat .meta{font-size:11px;color:var(--muted)}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;flex:none}
.card{background:var(--card);border-radius:18px;padding:24px 24px 12px;margin-bottom:16px;border:1px solid rgba(19,23,32,.045);border-top:3px solid var(--accent,transparent);box-shadow:0 1px 3px rgba(19,23,32,.05)}
.card-daily{--accent:var(--daily)}
.card-fixed{--accent:var(--fixed)}
.card-prepaid{--accent:var(--prepaid)}
.card-cat{--accent:#D7DCE5}
.card-head{display:flex;justify-content:space-between;align-items:baseline;gap:12px}
.card-head h2{margin:0;font-size:17px;font-weight:650;display:flex;align-items:center;gap:8px}
.card-total{font-size:17px;font-weight:650;font-variant-numeric:tabular-nums}
.card-desc{margin:3px 0 14px;font-size:12px;color:var(--muted)}
.day{padding:2px 0 6px}
.day + .day{border-top:1px solid var(--line)}
.day-head{display:flex;align-items:baseline;gap:8px;padding:12px 0 4px}
.day-date{font-size:13px;font-weight:650}
.day-week{font-size:12px;color:var(--muted)}
.day-sum{margin-left:auto;font-size:13px;font-weight:650;font-variant-numeric:tabular-nums}
.day-count{font-size:11px;color:var(--muted);min-width:34px;text-align:right}
.items{list-style:none;margin:0;padding:0}
.item{padding:8px 0}
.item + .item{border-top:1px solid var(--hair)}
.item-row{display:grid;grid-template-columns:1fr auto auto;gap:12px;align-items:center}
.item-left{display:flex;flex-direction:column;gap:2px;min-width:0}
.item-name{font-size:14px}
.item-date{font-size:11px;color:var(--muted);margin-right:7px;font-variant-numeric:tabular-nums}
.item-note{font-size:11.5px;color:var(--muted)}
.item-cat{font-size:11px;color:#6B7280;background:#F3F4F7;border-radius:999px;padding:2px 9px;white-space:nowrap}
.item-amount{font-size:14px;font-variant-numeric:tabular-nums;text-align:right;min-width:82px}
.legend{display:flex;gap:14px;align-items:center;font-size:11px;color:var(--muted);margin:0 0 10px;flex-wrap:wrap}
.legend span{display:flex;align-items:center;gap:5px}
.cat-row{display:grid;grid-template-columns:82px 1fr 86px 60px;gap:14px;align-items:center;padding:9px 0}
.cat-row + .cat-row{border-top:1px solid var(--hair)}
.cat-name{font-size:13px}
.track{height:6px;background:#F1F3F7;border-radius:999px;overflow:hidden}
.fill{display:block;height:100%;border-radius:999px}
.cat-amount{font-size:13px;text-align:right;font-variant-numeric:tabular-nums}
.cat-pct{font-size:11.5px;color:var(--muted);text-align:right;font-variant-numeric:tabular-nums}
.foot{margin-top:22px;text-align:center;font-size:11px;color:var(--muted)}
@media (max-width:640px){
  .page{padding:28px 14px 56px}
  .hero{flex-direction:column;align-items:flex-start;gap:10px}
  .hero h1{font-size:28px}
  .hero-total{text-align:left}
  .hero-total strong{font-size:32px}
  .stats{grid-template-columns:1fr}
  .card{padding:18px 16px 10px;border-radius:14px}
  .cat-row{grid-template-columns:72px 1fr 80px}
  .cat-pct{display:none}
  .item-cat{font-size:10.5px;padding:1px 7px}
}
@media print{
  body{background:#fff}
  .page{max-width:none;padding:0}
  .card{box-shadow:none;break-inside:avoid;margin-bottom:12px}
}
"""

COLORS = {"日常": "var(--daily)", "固定": "var(--fixed)", "预付": "var(--prepaid)"}


def money(v):
    return f"¥{v:,.2f}"


def e(text):
    return escape(text or "")


def item_row(row, show_date=False):
    day, item, cat, amount, note, _ = row
    date_html = (
        f'<span class="item-date">{day.month} 月 {day.day} 日</span>'
        if show_date
        else ""
    )
    note_html = f'<span class="item-note">{e(note)}</span>' if note else ""
    return f"""
          <li class="item">
            <div class="item-row">
              <div class="item-left">
                <span class="item-name">{date_html}{e(item)}</span>
                {note_html}
              </div>
              <span class="item-cat">{e(cat)}</span>
              <span class="item-amount">{money(amount)}</span>
            </div>
          </li>"""


def day_block(day, items):
    rows = "".join(item_row(i) for i in items)
    return f"""
      <div class="day">
        <div class="day-head">
          <span class="day-date">{day.month} 月 {day.day} 日</span>
          <span class="day-week">{d.WEEKDAYS[day.weekday()]}</span>
          <span class="day-sum">{money(d.day_sum(items))}</span>
          <span class="day-count">{len(items)} 笔</span>
        </div>
        <ul class="items">{rows}
        </ul>
      </div>"""


CARD_COLORS = {"daily": "var(--daily)", "fixed": "var(--fixed)", "prepaid": "var(--prepaid)"}


def card(title, key, desc, total, body):
    return f"""
    <section class="card card-{key}">
      <div class="card-head">
        <h2><span class="dot" style="background:{CARD_COLORS[key]}"></span>{title}</h2>
        <span class="card-total">{money(total)}</span>
      </div>
      <p class="card-desc">{desc}</p>{body}
    </section>"""


def cat_card():
    daily_cats = [c for c in d.CATS if d.cat_kind(c) != d.FIXED]
    fixed_cats = [c for c in d.CATS if d.cat_kind(c) == d.FIXED]

    def block(title, key, desc, cats, kinds):
        total = round(sum(d.cat_sum(c) for c in cats), 2)
        top = max((d.cat_sum(c) for c in cats), default=0)
        rows = []
        for c in cats:
            amount = d.cat_sum(c)
            pct = amount / total * 100 if total else 0
            width = amount / top * 100 if top else 0
            rows.append(
                f"""
        <div class="cat-row">
          <span class="cat-name">{e(c)}</span>
          <div class="track"><i class="fill" style="width:{width:.1f}%;background:{COLORS[d.cat_kind(c)]}"></i></div>
          <span class="cat-amount">{money(amount)}</span>
          <span class="cat-pct">{pct:.2f}%</span>
        </div>"""
            )
        legend = "".join(
            f'<span><i class="dot" style="background:{COLORS[k]}"></i>{k}</span>'
            for k in kinds
            if any(d.cat_kind(c) == k for c in cats)
        )
        return f"""
    <section class="card card-{key}">
      <div class="card-head">
        <h2>{title}</h2>
        <span class="card-total">{money(total)}</span>
      </div>
      <p class="card-desc">{desc}</p>
      <div class="legend">{legend}</div>{''.join(rows)}
    </section>"""

    return (
        block("分类合计", "cat", "日常与预付，不含房租水电话费", daily_cats, ("日常", "预付"))
        + block("固定支出构成", "fixed", "房租 · 水电 · 话费，按月必交", fixed_cats, ("固定",))
    )


def build():
    days = "".join(day_block(day, items) for day, items in d.daily_groups())
    fixed = '<ul class="items">' + "".join(
        item_row(r, True) for r in d.FIXED_ENTRIES
    ) + "\n        </ul>"
    prepaid = '<ul class="items">' + "".join(
        item_row(r, True) for r in d.PREPAID_ENTRIES
    ) + "\n        </ul>"

    today = dt.date.today()
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>2026 年 11 月 · 支出记账</title>
<style>{CSS}</style>
</head>
<body>
<main class="page">

  <header class="hero">
    <div>
      <p class="eyebrow">支出账本</p>
      <h1>2026 年 11 月</h1>
    </div>
    <div class="hero-total">
      <span class="label">本月总计</span>
      <strong>{money(d.TOTAL)}</strong>
      <span class="sub">共 {d.COUNT} 笔 · 数据截至 {d.DATA_THROUGH.month} 月 {d.DATA_THROUGH.day} 日</span>
    </div>
  </header>

  <div class="stats">
    <div class="stat">
      <span class="name"><i class="dot" style="background:var(--daily)"></i>日常开销</span>
      <strong>{money(d.TOTAL_DAILY)}</strong>
      <span class="meta">{len(d.DAILY_ENTRIES)} 笔 · 每天吃喝出行</span>
    </div>
    <div class="stat">
      <span class="name"><i class="dot" style="background:var(--fixed)"></i>固定支出</span>
      <strong>{money(d.TOTAL_FIXED)}</strong>
      <span class="meta">{len(d.FIXED_ENTRIES)} 笔 · 每月都要交</span>
    </div>
    <div class="stat">
      <span class="name"><i class="dot" style="background:var(--prepaid)"></i>预付 / 专项</span>
      <strong>{money(d.TOTAL_PREPAID)}</strong>
      <span class="meta">{len(d.PREPAID_ENTRIES)} 笔 · 以后才会用</span>
    </div>
  </div>

  {card("日常开销", "daily", "吃 · 喝 · 行 · 用，当天或几天内就消耗掉", d.TOTAL_DAILY, days)}
  {card("固定支出", "fixed", "房租 · 水电 · 话费，每月都要交", d.TOTAL_FIXED, fixed)}
  {card("预付 / 专项", "prepaid", "充值 · 机票 · 酒店 · 大件，钱付了、以后才用", d.TOTAL_PREPAID, prepaid)}
  {cat_card()}

  <p class="foot">共 {d.COUNT} 笔 · 合计 {money(d.TOTAL)} · 更新于 {today.month} 月 {today.day} 日</p>
</main>
</body>
</html>
"""


def main():
    html = build()
    OUT.write_text(html, encoding="utf-8")
    INDEX.write_text(html, encoding="utf-8")  # GitHub Pages 用
    print(f"saved: {OUT} + {INDEX}  total={d.TOTAL}  entries={d.COUNT}")


if __name__ == "__main__":
    main()
