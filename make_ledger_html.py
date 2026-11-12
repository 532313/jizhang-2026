#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把月度账本渲染成单文件 HTML（无外部依赖，双击即可看）。"""

import calendar
import datetime as dt
from collections import defaultdict
from html import escape
from pathlib import Path

import ledger_data as d

OUT = Path("/Users/gsy/Documents/记账/2026年11月账单.html")
INDEX = OUT.with_name("index.html")

WEEK = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
CN_NUM = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
TYPES = [d.DAILY, d.FIXED, d.PREPAID]
TYPE_TOTAL = {d.DAILY: d.TOTAL_DAILY, d.FIXED: d.TOTAL_FIXED, d.PREPAID: d.TOTAL_PREPAID}
TYPE_ITEMS = {d.DAILY: d.DAILY_ENTRIES, d.FIXED: d.FIXED_ENTRIES, d.PREPAID: d.PREPAID_ENTRIES}
TYPE_KEY = {d.DAILY: "daily", d.FIXED: "fixed", d.PREPAID: "prepaid"}
TYPE_NAME = {d.DAILY: "日常", d.FIXED: "固定", d.PREPAID: "预付"}
TYPE_TITLE = {d.DAILY: "日常开销", d.FIXED: "固定支出", d.PREPAID: "预付 / 专项"}
TYPE_DESC = {
    d.DAILY: "吃喝出行，当天花掉",
    d.FIXED: "房租、水电、话费，每月照付",
    d.PREPAID: "钱已付，以后才用",
}

DIGITS = "零壹贰叁肆伍陆柒捌玖"
SMALL = ["", "拾", "佰", "仟"]
BIG = ["", "万", "亿"]


def _four(n):
    out = []
    zero = False
    for i in range(4):
        digit = n // 10 ** (3 - i) % 10
        if digit:
            if zero and out:
                out.append("零")
            out.append(DIGITS[digit] + SMALL[3 - i])
            zero = False
        elif out:
            zero = True
    return "".join(out)


def _int_upper(n):
    if n == 0:
        return "零"
    groups = []
    while n:
        groups.append(n % 10000)
        n //= 10000
    out = []
    for i in range(len(groups) - 1, -1, -1):
        g = groups[i]
        if g == 0:
            if out and out[-1] != "零":
                out.append("零")
            continue
        if out and g < 1000 and out[-1] != "零":
            out.append("零")
        out.append(_four(g) + BIG[i])
    return "".join(out).rstrip("零")


def rmb_upper(amount):
    cents = int(round(amount * 100))
    yuan, rest = divmod(cents, 100)
    jiao, fen = divmod(rest, 10)
    head = (_int_upper(yuan) + "元") if yuan else ""
    if not jiao and not fen:
        return (head or "零元") + "整"
    body = head
    if jiao:
        body += DIGITS[jiao] + "角"
    elif fen and yuan:
        body += "零"
    body += (DIGITS[fen] + "分") if fen else "整"
    return body


def money(v):
    return f"{v:,.2f}"


def e(text):
    return escape(text or "")


def mark(kind):
    return f'<i class="mark m-{TYPE_KEY[kind]}" aria-hidden="true"></i>'


def cn_month(month):
    if month == 10:
        return "十"
    if month > 10:
        return "十" + CN_NUM[month - 10]
    return CN_NUM[month]


CSS = """
:root{
  --paper:#FCFCFA;
  --ink:#1A1917;
  --ink-2:#3E3A33;
  --muted:#6E6A61;
  --hair:#E8E4DB;
  --hair-2:#D6D1C6;
  --faint:#F3F0E9;
  --red:#A6382B;
  --serif:"Songti SC","STSong","SimSun","Noto Serif CJK SC",serif;
  --sans:"PingFang SC","Hiragino Sans GB","Microsoft YaHei","DengXian",sans-serif;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;background:var(--paper)}
body{
  margin:0;background:var(--paper);color:var(--ink);
  font:15px/1.7 var(--sans);
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;
}
.page{max-width:880px;margin:0 auto;padding:56px 36px 72px}
.sr-only{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
:focus-visible{outline:2px solid var(--ink);outline-offset:3px}

/* masthead */
.masthead{display:flex;justify-content:space-between;align-items:flex-start;gap:48px;padding-bottom:26px;border-bottom:1.5px solid var(--ink)}
.h-title{display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;margin:0}
.h-month{font-family:var(--serif);font-size:56px;font-weight:600;line-height:1;letter-spacing:.01em}
.h-year{font-size:13px;font-weight:400;color:var(--muted);letter-spacing:.02em}
.h-meta{margin:14px 0 0;font-size:12.5px;line-height:1.75;color:var(--muted);text-wrap:pretty}
.nowrap{white-space:nowrap}
.tally{flex:none;width:300px;padding-top:6px}
.tally-row{display:flex;align-items:baseline;gap:9px;padding:4px 0}
.tally-row .mark{align-self:center}
.tally-label{font-size:13px}
.tally-count{font-size:11px;color:var(--muted)}
.tally-amt{margin-left:auto;font-size:15px;font-variant-numeric:tabular-nums}
.tally-total{display:flex;align-items:baseline;gap:10px;margin-top:9px;padding-top:10px;border-top:2px solid var(--ink)}
.tally-total .label{font-size:13px}
.tally-total .amt{margin-left:auto;font-family:var(--serif);font-size:44px;font-weight:600;line-height:1.05;letter-spacing:-.01em;font-variant-numeric:lining-nums}
.tally-upper{margin-top:7px;text-align:right;font-size:11.5px;line-height:1.6;color:var(--muted);letter-spacing:.02em}

/* marks */
.mark{width:7px;height:7px;flex:none;display:inline-block;box-sizing:border-box}
.m-daily{background:var(--ink)}
.m-fixed{background:var(--red)}
.m-prepaid{border:1px solid var(--ink);background:transparent}

/* month page */
.month{margin-top:30px}
.month-cap{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;font-size:11.5px;color:var(--muted);margin-bottom:9px}
.cal{width:100%;border-collapse:collapse;table-layout:fixed}
.cal th{font:400 11px/1 var(--sans);color:var(--muted);text-align:left;padding:0 8px 8px 0;border-bottom:1px solid var(--hair-2)}
.cal td{vertical-align:top;border-top:1px solid var(--hair);padding:9px 8px 10px 0;height:78px}
.cal tbody tr:first-child td{border-top:0}
.cal tbody tr:last-child td{border-bottom:1px solid var(--hair)}
.cal .cell{display:block}
.cal .d{font-family:var(--serif);font-size:21px;line-height:1;font-variant-numeric:lining-nums}
.cal .amt{display:block;margin-top:7px;font-size:12.5px;line-height:1.25;color:var(--ink-2);font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.cal .is-today .amt{font-family:var(--sans);font-size:11px;color:var(--muted);letter-spacing:.04em}
.cal .is-future .d{color:#726D63}
.cal .is-blank .d{color:#726D63}
.cal .marks{display:flex;gap:3px;height:7px;margin-top:7px}
.cal .marks .mark{width:5px;height:5px}
.legend{display:flex;flex-wrap:wrap;gap:8px 20px;align-items:center;font-size:11px;color:var(--muted);margin-top:11px}
.legend span{display:inline-flex;align-items:center;gap:6px}
.legend .mark{width:6px;height:6px}

/* fold control */
.controls{display:flex;justify-content:flex-end;margin:28px 0 0}
.btn{font:inherit;font-size:12px;line-height:1.4;color:var(--muted);background:none;border:0;padding:10px 0 10px 14px;min-height:44px;cursor:pointer}
.btn:hover{color:var(--ink)}

/* sections */
details{display:block}
summary{list-style:none;cursor:pointer}
summary::-webkit-details-marker{display:none}
summary::marker{content:""}
.sec{margin-top:30px}
.sec + .sec{margin-top:38px}
.sec-head{display:grid;grid-template-columns:12px 8px minmax(0,1fr) auto auto;gap:12px;align-items:center;padding:14px 0 12px;border-top:1.5px solid var(--ink)}
.fold{font-size:15px;line-height:1;color:var(--muted);align-self:center;text-align:left;font-family:var(--sans)}
.fold::before{content:"+"}
details[open] > summary .fold::before{content:"−"}
summary:hover .fold{color:var(--ink)}
.sec-title{min-width:0}
.sec-title h2{margin:0;font-family:var(--serif);font-size:23px;font-weight:600;line-height:1.3;letter-spacing:.01em}
.sec-title p{margin:3px 0 0;font-size:12px;line-height:1.5;color:var(--muted)}
.sec-meta{font-size:11px;color:var(--muted);white-space:nowrap}
.sec-sum{font-size:17px;font-variant-numeric:tabular-nums;white-space:nowrap}
.sec-body{padding:2px 0 6px}
.mark-gap{width:7px;height:7px}

/* day groups */
.day + .day{border-top:1px solid var(--hair-2)}
.day-head{display:grid;grid-template-columns:12px 64px minmax(0,1fr) auto auto;gap:12px;align-items:baseline;padding:13px 0 9px}
.day-date{font-family:var(--serif);font-size:17px;line-height:1.2;font-variant-numeric:tabular-nums}
.day-date small{display:block;margin-top:2px;font-family:var(--sans);font-size:10.5px;color:var(--muted);letter-spacing:.04em}
.day-count{font-size:11px;color:var(--muted);white-space:nowrap}
.day-sum{font-size:15px;font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap}
.items{padding:0 0 6px}
.item{display:grid;grid-template-columns:12px 64px minmax(0,1fr) 64px 82px;gap:12px;align-items:baseline;padding:8px 0}
.item + .item{border-top:1px solid var(--faint)}
.item-date{font-family:var(--serif);font-size:14px;line-height:1.25;font-variant-numeric:tabular-nums}
.item-date small{display:block;margin-top:1px;font-family:var(--sans);font-size:10px;color:var(--muted);letter-spacing:.04em}
.iname{min-width:0;font-size:14.5px;line-height:1.45}
.note{display:block;margin-top:1px;font-size:11px;line-height:1.5;color:var(--muted)}
.icat{font-size:10.5px;color:var(--muted);text-align:right;white-space:nowrap}
.iamt{font-size:14.5px;text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}

/* composition */
.cat-group + .cat-group{margin-top:20px;padding-top:16px;border-top:1px solid var(--hair-2)}
.cat-head{display:grid;grid-template-columns:112px minmax(0,1fr) 78px 46px;gap:14px;align-items:baseline;margin-bottom:6px;padding-left:20px}
.cat-head h3{margin:0;font-family:var(--serif);font-size:17px;font-weight:600;line-height:1.4;white-space:nowrap}
.cat-head .ct{margin-left:9px;font-family:var(--sans);font-size:11px;font-weight:400;color:var(--muted)}
.cat-share{font-size:11px;color:var(--muted);white-space:nowrap;font-variant-numeric:tabular-nums;text-align:right}
.cat-sum{font-size:15px;font-variant-numeric:tabular-nums;white-space:nowrap}
.cat-row{display:grid;grid-template-columns:112px minmax(0,1fr) 78px 46px;gap:14px;align-items:center;padding:7px 0 7px 20px}
.cat-name{font-size:13px}
.track{position:relative;height:4px;background:var(--faint)}
.fill{position:absolute;left:0;top:0;bottom:0;background:var(--ink)}
.fill.f-fixed{background:var(--red)}
.fill.f-prepaid{background:transparent;border:1px solid var(--ink)}
.cat-amt{font-size:13px;text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.cat-pct{font-size:11px;text-align:right;color:var(--muted);font-variant-numeric:tabular-nums;white-space:nowrap}
.recon{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-top:22px;padding-top:12px;border-top:1px solid var(--hair-2);font-size:11.5px;color:var(--muted);font-variant-numeric:tabular-nums}
.recon b{font-weight:600;color:var(--ink)}

.foot{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-top:56px;padding-top:14px;border-top:1px solid var(--hair-2);font-size:11px;color:var(--muted)}

@media (max-width:700px){
  .page{padding:30px 18px 56px}
  .masthead{flex-direction:column;align-items:stretch;gap:26px;padding-bottom:22px}
  .h-month{font-size:44px}
  .h-year{font-size:12.5px}
  .h-meta{margin-top:11px;font-size:12px}
  .tally{width:auto}
  .tally-total .amt{font-size:40px}
  .month{margin-top:24px}
  .month-cap{font-size:11px}
  .cal th{padding:0 4px 7px 0;font-size:10.5px}
  .cal td{padding:7px 4px 8px 0;height:66px}
  .cal .d{font-size:18px}
  .cal .amt{font-size:10px;margin-top:5px;letter-spacing:0}
  .cal .is-today .amt{font-size:9.5px;letter-spacing:0}
  .cal .marks{margin-top:5px;gap:2px;height:6px}
  .cal .marks .mark{width:4px;height:4px}
  .legend{gap:7px 14px;font-size:10.5px}
  .controls{margin-top:20px}
  .sec,.sec + .sec{margin-top:30px}
  .sec-head{grid-template-columns:12px 7px minmax(0,1fr) auto auto;gap:9px;padding:12px 0 10px}
  .sec-title h2{font-size:20px}
  .sec-title p{font-size:11.5px}
  .sec-meta{font-size:10.5px}
  .sec-sum{font-size:15px}
  .day-head{grid-template-columns:12px 46px minmax(0,1fr) auto auto;gap:8px}
  .day-date{font-size:15px}
  .day-date small{font-size:10px}
  .day-sum{font-size:14px;font-weight:600}
  .item{grid-template-columns:12px 46px minmax(0,1fr) auto auto;gap:8px;padding:7px 0}
  .item-date{font-size:12.5px}
  .iname{font-size:14px}
  .icat{font-size:10px}
  .iamt{font-size:14px}
  .cat-head{grid-template-columns:minmax(0,1fr) auto 44px;gap:10px;padding-left:20px}
  .cat-share{display:none}
  .cat-row{grid-template-columns:minmax(0,1fr) auto 44px;grid-template-areas:"name amt pct" "track track track";gap:5px 10px;padding:8px 0 10px 20px}
  .cat-name{grid-area:name}
  .cat-amt{grid-area:amt}
  .cat-pct{grid-area:pct}
  .track{grid-area:track;margin-top:2px}
  .recon{margin-top:18px;font-size:11px}
  .foot{margin-top:40px;font-size:10.5px}
}
@media print{
  @page{size:A4;margin:16mm 16mm 18mm}
  :root{--paper:#fff}
  html,body{background:#fff}
  .page{max-width:none;padding:0}
  .btn,.controls{display:none}
  .fold{visibility:hidden}
  .masthead{padding-bottom:16px}
  .h-month{font-size:40px}
  .tally-total .amt{font-size:34px}
  .month{margin-top:20px}
  .cal td{height:auto;padding:5px 6px 6px 0}
  .sec,.sec + .sec{margin-top:24px}
  .day,.cat-group,.recon{break-inside:avoid}
  .sec-fixed,.sec-prepaid,.sec-cat{break-inside:avoid}
  .sec-cat{break-before:page}
  .sec-head,.cat-head{break-after:avoid}
  summary{cursor:default}
  details > *:not(summary){display:revert}
  a{color:inherit;text-decoration:none}
}
"""

JS = """
(function () {
  var btn = document.getElementById("foldAll");
  function all() {
    return Array.prototype.slice.call(document.querySelectorAll("details"));
  }
  function sync() {
    var every = all().every(function (d) { return d.open; });
    btn.textContent = every ? "全部收起" : "全部展开";
    btn.setAttribute("aria-expanded", every ? "true" : "false");
  }
  btn.addEventListener("click", function () {
    var every = all().every(function (d) { return d.open; });
    all().forEach(function (d) { d.open = !every; });
    sync();
  });
  document.addEventListener("toggle", sync, true);
  var beforePrint = null;
  window.addEventListener("beforeprint", function () {
    beforePrint = all().map(function (d) { return d.open; });
    all().forEach(function (d) { d.open = true; });
  });
  window.addEventListener("afterprint", function () {
    if (beforePrint) {
      all().forEach(function (d, i) { d.open = beforePrint[i]; });
      beforePrint = null;
    }
    sync();
  });
  sync();
})();
"""


def day_entries(ref):
    by_day = defaultdict(list)
    for row in d.ENTRIES:
        if (row[0].year, row[0].month) == (ref.year, ref.month):
            by_day[row[0]].append(row)
    return by_day


def calendar_cell(day_num, ref, by_day, today):
    if day_num is None:
        return '<td class="is-blank"><span class="cell"></span></td>'
    date = dt.date(ref.year, ref.month, day_num)
    rows = by_day.get(date, [])
    total = round(sum(r[3] for r in rows), 2)
    kinds = [k for k in TYPES if any(r[5] == k for r in rows)]
    is_today = date == today
    future = date > d.DATA_THROUGH and not rows
    cls = ["cal-day"]
    if future and not is_today:
        cls.append("is-future")
    if is_today:
        cls.append("is-today")
    if rows:
        sr = (
            f"{date.month} 月 {day_num} 日{d.WEEKDAYS[date.weekday()]}，"
            f"支出 {money(total)} 元，含" + "、".join(TYPE_NAME[k] for k in kinds)
        )
        visual = (
            f'<span class="d">{day_num}</span>'
            f'<span class="amt">{money(total)}</span>'
            '<span class="marks">' + "".join(mark(k) for k in kinds) + "</span>"
        )
    elif is_today:
        sr = f"{date.month} 月 {day_num} 日{d.WEEKDAYS[date.weekday()]}，今天，尚未记账"
        visual = f'<span class="d">{day_num}</span><span class="amt">今天</span><span class="marks"></span>'
    elif future:
        sr = f"{date.month} 月 {day_num} 日{d.WEEKDAYS[date.weekday()]}，尚未记账"
        visual = f'<span class="d">{day_num}</span><span class="amt"></span><span class="marks"></span>'
    else:
        sr = f"{date.month} 月 {day_num} 日{d.WEEKDAYS[date.weekday()]}，无支出"
        visual = f'<span class="d">{day_num}</span><span class="amt" style="color:var(--muted)">—</span><span class="marks"></span>'
    return (
        f'<td class="{" ".join(cls)}"><span class="sr-only">{sr}</span>'
        f'<span class="cell" aria-hidden="true">{visual}</span></td>'
    )


def calendar_block(ref, today):
    first = dt.date(ref.year, ref.month, 1)
    n_days = calendar.monthrange(ref.year, ref.month)[1]
    by_day = day_entries(ref)
    lead = (first.weekday() + 1) % 7  # 周日开头
    cells = [None] * lead + list(range(1, n_days + 1))
    while len(cells) % 7:
        cells.append(None)
    week_rows = []
    for i in range(0, len(cells), 7):
        tds = "".join(calendar_cell(n, ref, by_day, today) for n in cells[i:i + 7])
        week_rows.append(f"<tr>{tds}</tr>")
    head = "".join(f'<th scope="col">{w}</th>' for w in WEEK)
    return f"""
  <section class="month" aria-label="{ref.year} 年 {ref.month} 月每日支出">
    <div class="month-cap">
      <span>{ref.year} 年 {ref.month} 月每日支出（元）</span>
      <span>浅色日期尚未记账</span>
    </div>
    <table class="cal">
      <caption class="sr-only">{ref.year} 年 {ref.month} 月每日支出</caption>
      <thead><tr>{head}</tr></thead>
      <tbody>{"".join(week_rows)}</tbody>
    </table>
    <div class="legend">
      <span>{mark(d.DAILY)}日常</span>
      <span>{mark(d.FIXED)}固定</span>
      <span>{mark(d.PREPAID)}预付</span>
      <span>— 当日无支出</span>
    </div>
  </section>"""


def daily_item(row):
    _, item, cat, amount, note, _ = row
    note_html = f'<span class="note">{e(note)}</span>' if note else ""
    return f"""
        <div class="item">
          <span></span>
          <span></span>
          <div class="iname">{e(item)}{note_html}</div>
          <span class="icat">{e(cat)}</span>
          <span class="iamt">{money(amount)}</span>
        </div>"""


def flat_item(row):
    day, item, cat, amount, note, _ = row
    note_html = f'<span class="note">{e(note)}</span>' if note else ""
    return f"""
        <div class="item">
          <span></span>
          <span class="item-date">{day.month}.{day.day:02d}<small>{d.WEEKDAYS[day.weekday()]}</small></span>
          <div class="iname">{e(item)}{note_html}</div>
          <span class="icat">{e(cat)}</span>
          <span class="iamt">{money(amount)}</span>
        </div>"""


def day_block(day, items):
    rows = "".join(daily_item(i) for i in items)
    return f"""
      <details class="day" open id="d-{day.month:02d}{day.day:02d}">
        <summary class="day-head">
          <span class="fold" aria-hidden="true"></span>
          <span class="day-date">{day.month}.{day.day:02d}<small>{d.WEEKDAYS[day.weekday()]}</small></span>
          <span></span>
          <span class="day-count">{len(items)} 笔</span>
          <span class="day-sum">{money(d.day_sum(items))}</span>
        </summary>
        <div class="items">{rows}
        </div>
      </details>"""


def section(kind, body):
    return f"""
    <details class="sec sec-{TYPE_KEY[kind]}" open>
      <summary class="sec-head">
        <span class="fold" aria-hidden="true"></span>
        {mark(kind)}
        <div class="sec-title"><h2>{TYPE_TITLE[kind]}</h2><p>{TYPE_DESC[kind]}</p></div>
        <span class="sec-meta">{len(TYPE_ITEMS[kind])} 笔</span>
        <span class="sec-sum">{money(TYPE_TOTAL[kind])}</span>
      </summary>
      <div class="sec-body">{body}
      </div>
    </details>"""


def cat_group(kind):
    acc = defaultdict(float)
    for row in TYPE_ITEMS[kind]:
        acc[row[2]] += row[3]
    rows = sorted(acc.items(), key=lambda kv: -kv[1])
    total = TYPE_TOTAL[kind]
    share = total / d.TOTAL * 100 if d.TOTAL else 0
    body = []
    for name, amount in rows:
        pct = amount / total * 100 if total else 0
        body.append(f"""
        <div class="cat-row">
          <span class="cat-name">{e(name)}</span>
          <span class="track"><i class="fill f-{TYPE_KEY[kind]}" style="width:{pct:.2f}%"></i></span>
          <span class="cat-amt">{money(round(amount, 2))}</span>
          <span class="cat-pct">{pct:.1f}%</span>
        </div>""")
    return f"""
      <div class="cat-group">
        <div class="cat-head">
          <h3>{TYPE_TITLE[kind]}<span class="ct">{len(TYPE_ITEMS[kind])} 笔</span></h3>
          <span class="cat-share">占本月 {share:.1f}%</span>
          <span class="cat-sum">{money(total)}</span>
        </div>{"".join(body)}
      </div>"""


def cat_section():
    body = "".join(cat_group(k) for k in TYPES)
    recon = (
        f'<div class="recon"><span>三组小计相加</span>'
        f'<span>{money(d.TOTAL_DAILY)} ＋ {money(d.TOTAL_FIXED)} ＋ {money(d.TOTAL_PREPAID)} ＝ <b>{money(d.TOTAL)}</b></span></div>'
    )
    return f"""
    <details class="sec sec-cat" open>
      <summary class="sec-head">
        <span class="fold" aria-hidden="true"></span>
        <span class="mark-gap" aria-hidden="true"></span>
        <div class="sec-title"><h2>分类构成</h2><p>条形与百分比均按本组小计计算</p></div>
        <span class="sec-meta">3 组</span>
        <span class="sec-sum">{money(d.TOTAL)}</span>
      </summary>
      <div class="sec-body">{body}{recon}
      </div>
    </details>"""


def masthead(ref):
    rows = []
    for kind in TYPES:
        rows.append(f"""
      <div class="tally-row">
        {mark(kind)}
        <span class="tally-label">{TYPE_NAME[kind]}</span>
        <span class="tally-count">{len(TYPE_ITEMS[kind])} 笔</span>
        <span class="tally-amt">{money(TYPE_TOTAL[kind])}</span>
      </div>""")
    return f"""
  <header class="masthead">
    <div>
      <h1 class="h-title"><span class="h-month">{cn_month(ref.month)}月</span><span class="h-year">{ref.year} 年支出账</span></h1>
      <p class="h-meta"><span class="nowrap">共 {d.COUNT} 笔，{len(d.daily_groups())} 个支出日。</span><span class="nowrap">数据截至 {d.DATA_THROUGH.month} 月 {d.DATA_THROUGH.day} 日。</span><span class="nowrap">金额单位：元。</span></p>
    </div>
    <div class="tally" aria-label="本月支出构成">
      {"".join(rows)}
      <div class="tally-total">
        <span class="label">本月合计</span>
        <span class="amt">{money(d.TOTAL)}</span>
      </div>
      <div class="tally-upper">人民币{rmb_upper(d.TOTAL)}</div>
    </div>
  </header>"""


def build():
    today = dt.date.today()
    ref = d.DATA_THROUGH
    groups = d.daily_groups()
    days = "".join(day_block(day, items) for day, items in groups)
    fixed = "".join(flat_item(r) for r in sorted(d.FIXED_ENTRIES, key=lambda r: r[0]))
    prepaid = "".join(flat_item(r) for r in sorted(d.PREPAID_ENTRIES, key=lambda r: r[0]))

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{ref.year} 年 {ref.month} 月支出账</title>
<style>{CSS}</style>
</head>
<body>
<main class="page">

  {masthead(ref)}

  {calendar_block(ref, today)}

  <div class="controls"><button class="btn" id="foldAll" type="button" aria-expanded="true">全部收起</button></div>

  {section(d.DAILY, days)}
  {section(d.FIXED, fixed)}
  {section(d.PREPAID, prepaid)}
  {cat_section()}

  <footer class="foot">
    <span>共 {d.COUNT} 笔，合计 {money(d.TOTAL)} 元。</span>
    <span>更新于 {today.month} 月 {today.day} 日。</span>
  </footer>
</main>
<script>{JS}</script>
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
