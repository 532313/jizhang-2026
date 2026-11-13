#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11 月账本的数据（唯一数据源），HTML 和 Excel 都从这里取数。"""

import datetime as dt

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

DAILY, FIXED, PREPAID = "日常", "固定", "预付"

# (日期, 项目, 分类, 金额, 备注, 类型)
ENTRIES = [
    (dt.date(2026, 11, 1), "DeepSeek 充值", "数字服务", 100.00, "余额充值", PREPAID),
    (dt.date(2026, 11, 1), "外卖", "餐饮", 21.70, "", DAILY),
    (dt.date(2026, 11, 1), "特仑苏（6 瓶）", "餐饮", 4.90, "6 瓶合计 4.9 元", DAILY),
    (dt.date(2026, 11, 1), "矿泉水", "餐饮", 3.00, "", DAILY),
    (dt.date(2026, 11, 1), "共享单车", "交通", 1.00, "骑行 1 次", DAILY),
    (dt.date(2026, 11, 1), "羽毛球（AA）", "运动", 50.00, "AA 分摊，自己出 50 元", DAILY),
    (dt.date(2026, 11, 1), "矿泉水", "餐饮", 6.00, "", DAILY),
    (dt.date(2026, 11, 2), "香港往返路费", "交通", 30.00, "往返，约 30 元", DAILY),
    (dt.date(2026, 11, 2), "特仑苏（6 瓶）", "餐饮", 4.90, "6 瓶合计 4.9 元", DAILY),
    (dt.date(2026, 11, 2), "电费", "居住", 99.00, "本月电费", FIXED),
    (dt.date(2026, 11, 2), "肯德基", "餐饮", 51.00, "晚饭", DAILY),
    (dt.date(2026, 11, 3), "香港往返路费", "交通", 30.00, "往返，约 30 元", DAILY),
    (dt.date(2026, 11, 3), "外卖", "餐饮", 13.40, "", DAILY),
    (dt.date(2026, 11, 3), "外卖", "餐饮", 24.90, "晚饭", DAILY),
    (dt.date(2026, 11, 3), "饮料", "餐饮", 2.00, "", DAILY),
    (dt.date(2026, 11, 4), "外卖", "餐饮", 20.00, "午饭", DAILY),
    (dt.date(2026, 11, 4), "话费", "通讯", 33.00, "手机充值", FIXED),
    (dt.date(2026, 11, 4), "水龙头套", "购物", 6.80, "", DAILY),
    (dt.date(2026, 11, 4), "公交车", "交通", 4.00, "", DAILY),
    (dt.date(2026, 11, 4), "冲锋衣", "购物", 118.00, "耐用品", PREPAID),
    (dt.date(2026, 11, 5), "交通", "交通", 22.00, "", DAILY),
    (dt.date(2026, 11, 5), "吃饭", "餐饮", 60.00, "", DAILY),
    (dt.date(2026, 11, 5), "买菜", "餐饮", 56.00, "食材", DAILY),
    (dt.date(2026, 11, 6), "羽毛球拉线", "运动", 80.00, "拍子维护，以后还用", PREPAID),
    (dt.date(2026, 11, 6), "租球拍", "运动", 20.00, "", DAILY),
    (dt.date(2026, 11, 6), "场地费", "运动", 31.00, "", DAILY),
    (dt.date(2026, 11, 6), "球费", "运动", 34.00, "", DAILY),
    (dt.date(2026, 11, 6), "共享单车", "交通", 5.00, "", DAILY),
    (dt.date(2026, 11, 6), "矿泉水", "餐饮", 3.00, "", DAILY),
    (dt.date(2026, 11, 6), "外卖", "餐饮", 18.60, "午饭", DAILY),
    (dt.date(2026, 11, 7), "买菜", "餐饮", 48.00, "食材", DAILY),
    (dt.date(2026, 11, 7), "房租", "居住", 2900.00, "本月房租", FIXED),
    (dt.date(2026, 11, 7), "打球", "运动", 50.00, "", DAILY),
    (dt.date(2026, 11, 7), "KFC", "餐饮", 25.00, "", DAILY),
    (dt.date(2026, 11, 7), "打车", "交通", 14.00, "", DAILY),
    (dt.date(2026, 11, 7), "外卖", "餐饮", 12.00, "", DAILY),
    (dt.date(2026, 11, 9), "KFC", "餐饮", 31.00, "", DAILY),
    (dt.date(2026, 11, 9), "羽毛球（2 桶）", "运动", 234.00, "两桶：112 + 122，囤着以后打", PREPAID),
    (dt.date(2026, 11, 10), "港深通勤", "交通", 30.00, "", DAILY),
    (dt.date(2026, 11, 10), "午饭", "餐饮", 39.00, "", DAILY),
    (dt.date(2026, 11, 10), "晚饭", "餐饮", 32.00, "", DAILY),
    (dt.date(2026, 11, 11), "外卖", "餐饮", 12.00, "", DAILY),
    (dt.date(2026, 11, 11), "公交车", "交通", 4.00, "", DAILY),
    (dt.date(2026, 11, 12), "午饭", "餐饮", 22.00, "", DAILY),
    (dt.date(2026, 11, 12), "KFC", "餐饮", 42.00, "晚饭", DAILY),
    (dt.date(2026, 11, 13), "物业费", "居住", 115.00, "本月物业费", FIXED),
    (dt.date(2026, 11, 13), "打球", "运动", 21.00, "", DAILY),
    (dt.date(2026, 11, 13), "午饭", "餐饮", 22.00, "", DAILY),
    (dt.date(2026, 11, 13), "晚饭", "餐饮", 13.50, "", DAILY),
    (dt.date(2026, 11, 13), "买菜", "餐饮", 43.50, "食材", DAILY),
]

DAILY_ENTRIES = [e for e in ENTRIES if e[5] == DAILY]
FIXED_ENTRIES = [e for e in ENTRIES if e[5] == FIXED]
PREPAID_ENTRIES = [e for e in ENTRIES if e[5] == PREPAID]

TOTAL_DAILY = round(sum(e[3] for e in DAILY_ENTRIES), 2)
TOTAL_FIXED = round(sum(e[3] for e in FIXED_ENTRIES), 2)
TOTAL_PREPAID = round(sum(e[3] for e in PREPAID_ENTRIES), 2)
TOTAL = round(TOTAL_DAILY + TOTAL_FIXED + TOTAL_PREPAID, 2)
COUNT = len(ENTRIES)
DATA_THROUGH = max(e[0] for e in ENTRIES)


def cat_sum(cat):
    return round(sum(e[3] for e in ENTRIES if e[2] == cat), 2)


def cat_count(cat):
    return sum(1 for e in ENTRIES if e[2] == cat)


def cat_kind(cat):
    """分类颜色：取该分类里金额占比更大的那种类型（一个分类可能同时有日常和预付）。"""
    sums = {}
    for e in ENTRIES:
        if e[2] == cat:
            sums[e[5]] = sums.get(e[5], 0) + e[3]
    return max(sums, key=sums.get)


CATS = sorted({e[2] for e in ENTRIES}, key=lambda c: -cat_sum(c))


def daily_groups():
    out = []
    for day in dict.fromkeys(e[0] for e in DAILY_ENTRIES):
        out.append((day, [e for e in DAILY_ENTRIES if e[0] == day]))
    return out


def day_sum(items):
    return round(sum(i[3] for i in items), 2)
