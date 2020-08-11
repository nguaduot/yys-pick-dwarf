#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 检出六星满级低收益御魂（副属性满4条的基础上加点次数不超过3）
# 控制台输出结果，同时保存到文件（同源文件目录 *-dwarf）
#
# + 支持读取 NGA@火电太热 的「御魂导出器」导出的JSON数据文件
#   https://nga.178.com/read.php?tid=15220479
# + 支持读取 NGA@fluxxu 的「痒痒熊快照」导出的JSON数据文件
#   https://nga.178.com/read.php?tid=16557282
#
# autnor: 痒痒鼠@南瓜多糖
# version: 1.4.191022
# date: 20191022

import json
import math
import os
import sys

SECTION = ('壹', '贰', '叁', '肆', '伍', '陆')  # 御魂位置
GROW = {'生命': (342, 114), '防御': (14, 6), '攻击': (81, 27),
        '生命加成': (0.1, 0.03), '防御加成': (0.1, 0.03), '攻击加成': (0.1, 0.03),
        '速度': (12, 3), '暴击': (0.1, 0.03), '暴击伤害': (0.14, 0.05),
        '效果命中': (0.1, 0.03), '效果抵抗': (0.1, 0.03)}  # 御魂主属性初始&成长值
FIXED = {'生命加成': 0.08, '防御加成': 0.16, '攻击加成': 0.08,
         '暴击': 0.08, '效果命中': 0.08, '效果抵抗': 0.08}  # 首领御魂固有属性
DEF_FILTER_HIT_TIMES = 2  # 有效属性加点次数默认过滤值


# 主属性成长
main_attr_v = lambda attr, level: GROW[attr][0] + GROW[attr][1] * level


# 加点次数
def check(item):
    item2, n = item.copy(), 0
    if '固有属性' in item2:
        item2[item2['固有属性']] -= FIXED[item2['固有属性']]
        if item2[item2['固有属性']] < 0.024: del item2[item2['固有属性']]
    if '生命加成' in item2:
        mainv, v = main_attr_v('生命加成', item2['御魂等级']), item2['生命加成']
        if v >= mainv: v -= mainv
        if v > 0.024: n += math.ceil(v / 0.03) - 1
    if '防御加成' in item2:
        mainv, v = main_attr_v('防御加成', item2['御魂等级']), item2['防御加成']
        if v >= mainv: v -= mainv
        if v > 0.024: n += math.ceil(v / 0.03) - 1
    if '攻击加成' in item2:
        mainv, v = main_attr_v('攻击加成', item2['御魂等级']), item2['攻击加成']
        if v >= mainv: v -= mainv
        if v > 0.024: n += math.ceil(v / 0.03) - 1
    if '速度' in item2:
        mainv, v = main_attr_v('速度', item2['御魂等级']), item2['速度']
        if v >= mainv: v -= mainv
        if v > 2.4: n += math.ceil(v / 3) - 1
    if '暴击' in item2:
        mainv, v = main_attr_v('暴击', item2['御魂等级']), item2['暴击']
        if v >= mainv: v -= mainv
        if v > 0.024: n += math.ceil(v / 0.03) - 1
    if '暴击伤害' in item2:
        mainv, v = main_attr_v('暴击伤害', item2['御魂等级']), item2['暴击伤害']
        if v >= mainv: v -= mainv
        if v > 0.032: n += math.ceil(v / 0.04) - 1
    if '效果命中' in item2:
        mainv, v = main_attr_v('效果命中', item2['御魂等级']), item2['效果命中']
        if v >= mainv: v -= mainv
        if v > 0.032: n += math.ceil(v / 0.04) - 1
    if '效果抵抗' in item2:
        mainv, v = main_attr_v('效果抵抗', item2['御魂等级']), item2['效果抵抗']
        if v >= mainv: v -= mainv
        if v > 0.032: n += math.ceil(v / 0.04) - 1
    return n


# 将单个御魂数据解析为可阅读样式
def translate(item):
    item2, li = item.copy(), []
    if '固有属性' in item2:
        item2[item2['固有属性']] -= FIXED[item2['固有属性']]
        if item2[item2['固有属性']] < 0.024: del item2[item2['固有属性']]
    li.append('[%s]%s %d/%d' % (SECTION[item2['位置'] - 1], item2['御魂类型'], item2['御魂星级'], item2['御魂等级']))
    if item2['御魂星级'] < 6: return li[0]
    if '生命' in item2:
        mainv, v = main_attr_v('生命', item2['御魂等级']), item2['生命']
        if v >= mainv:
            li.insert(1, '生命 %d' % mainv)
            v -= mainv
        if v > 90: li.append('生命 +%d ' % round(v))
    if '防御' in item2:
        mainv, v = main_attr_v('防御', item2['御魂等级']), item2['防御']
        if v >= mainv:
            li.insert(1, '防御 %d' % mainv)
            v -= mainv
        if v > 3: li.append('防御 +%d ' % round(v))
    if '攻击' in item2:
        mainv, v = main_attr_v('攻击', item2['御魂等级']), item2['攻击']
        if v >= mainv:
            li.insert(1, '攻击 %d' % mainv)
            v -= mainv
        if v > 21: li.append('攻击 +%d ' % round(v))
    if '生命加成' in item2:
        mainv, v = main_attr_v('生命加成', item2['御魂等级']), item2['生命加成']
        if v >= mainv:
            li.insert(1, '生命加成 %d%%' % round(mainv * 100))
            v -= mainv
        if v > 0.024: li.append('生命加成 +%d%% %s' % (round(v * 100), '.' * (math.ceil(v / 0.03) - 1)))
    if '防御加成' in item2:
        mainv, v = main_attr_v('防御加成', item2['御魂等级']), item2['防御加成']
        if v >= mainv:
            li.insert(1, '防御加成 %d%%' % round(mainv * 100))
            v -= mainv
        if v > 0.024: li.append('防御加成 +%d%% %s' % (round(v * 100), '.' * (math.ceil(v / 0.03) - 1)))
    if '攻击加成' in item2:
        mainv, v = main_attr_v('攻击加成', item2['御魂等级']), item2['攻击加成']
        if v >= mainv:
            li.insert(1, '攻击加成 %d%%' % round(mainv * 100))
            v -= mainv
        if v > 0.024: li.append('攻击加成 +%d%% %s' % (round(v * 100), '.' * (math.ceil(v / 0.03) - 1)))
    if '速度' in item2:
        mainv, v = main_attr_v('速度', item2['御魂等级']), item2['速度']
        if v >= mainv:
            li.insert(1, '速度 %d' % mainv)
            v -= mainv
        if v > 2.4: li.append('速度 +%d %s' % (round(v), '.' * (math.ceil(v / 3) - 1)))
    if '暴击' in item2:
        mainv, v = main_attr_v('暴击', item2['御魂等级']), item2['暴击']
        if v >= mainv:
            li.insert(1, '暴击 %d%%' % round(mainv * 100))
            v -= mainv
        if v > 0.024: li.append('暴击 +%d%% %s' % (round(v * 100), '.' * (math.ceil(v / 0.03) - 1)))
    if '暴击伤害' in item2:
        mainv, v = main_attr_v('暴击伤害', item2['御魂等级']), item2['暴击伤害']
        if v >= mainv:
            li.insert(1, '暴击伤害 %d%%' % round(mainv * 100))
            v -= mainv
        if v > 0.032:
            li.append('暴击伤害 +%d%% %s' % (round(v * 100), '.' * (math.ceil(v / 0.04) - 1)))
    if '效果命中' in item2:
        mainv, v = main_attr_v('效果命中', item2['御魂等级']), item2['效果命中']
        if v >= mainv:
            li.insert(1, '效果命中 %d%%' % round(mainv * 100))
            v -= mainv
        if v > 0.032: li.append('效果命中 +%d%% %s' % (round(v * 100), '.' * (math.ceil(v / 0.04) - 1)))
    if '效果抵抗' in item2:
        mainv, v = main_attr_v('效果抵抗', item2['御魂等级']), item2['效果抵抗']
        if v >= mainv:
            li.insert(1, '效果抵抗 %d%%' % round(mainv * 100))
            v -= mainv
        if v > 0.032: li.append('效果抵抗 +%d%% %s' % (round(v * 100), '.' * (math.ceil(v / 0.04) - 1)))
    if '固有属性' in item2: li.append('(固)%s %d%%' % (item2['固有属性'], FIXED[item2['固有属性']] * 100))
    return '\n'.join(li)


# 「痒痒熊快照」导出数据转「御魂导出器」数据格式
def fluxxu2hdtr(fluxxu):
    CATES_ID_NAME = {300048: '狂骨', 300027: '阴摩罗', 300022: '心眼', 300020: '鸣屋',
                     300018:'狰', 300012: '轮入道', 300004: '蝠翼', 300036: '针女',
                     300031: '镇墓兽', 300030: '破势', 300029: '伤魂鸟', 300026: '网切',
                     300007: '三味', 300024: '树妖', 300021: '薙魂', 300015: '钟灵',
                     300014: '镜姬', 300009: '被服', 300006: '涅槃之火', 300003: '地藏像',
                     300035: '魅妖', 300032: '珍珠', 300023: '木魅', 300013: '日女巳时',
                     300011: '反枕', 300010: '招财猫', 300002: '雪幽魂', 300034: '蚌精',
                     300019: '火灵', 300049: '幽谷响', 300039: '返魂香', 300033: '骰子鬼',
                     300008: '魍魉之匣', 300077: '鬼灵歌伎', 300054: '蜃气楼', 300053: '地震鲶',
                     300052: '荒骷髅', 300051: '胧车', 300050: '土蜘蛛'}  # 「痒痒熊快照」御魂ID-名字表
    ATTRS_ID_NAME = {'Hp': '生命', 'Defense': '防御', 'Attack': '攻击',
                     'HpRate': '生命加成', 'DefenseRate': '防御加成', 'AttackRate': '攻击加成',
                     'Speed': '速度', 'CritRate': '暴击', 'CritPower': '暴击伤害',
                     'EffectHitRate': '效果命中', 'EffectResistRate': '效果抵抗'}  # 「痒痒熊快照」属性ID-名字表
    hdtr = {'御魂ID': fluxxu['id'],
            '御魂类型': CATES_ID_NAME[fluxxu['suit_id']],
            '位置': fluxxu['pos'] + 1,
            '御魂等级': fluxxu['level'],
            '御魂星级': fluxxu['quality']}
    for attr in fluxxu['attrs'] + [fluxxu['base_attr']] + fluxxu['single_attrs']:
        if ATTRS_ID_NAME[attr['type']] in hdtr:
            hdtr[ATTRS_ID_NAME[attr['type']]] += attr['value']
        else:
            hdtr[ATTRS_ID_NAME[attr['type']]] = attr['value']
    if len(fluxxu['single_attrs']) > 0: hdtr['固有属性'] = ATTRS_ID_NAME[fluxxu['single_attrs'][0]['type']]
    return hdtr


# 解析 NGA@火电太热 的「御魂导出器」数据
def parse_data_hdtr(data, filter_hit_times):
    if data[0] != 'yuhun_ocr2.0': raise Exception('unsupported data file version')
    li1, li2 = [data[0]], []
    for item in data[1:]:
        if item['御魂星级'] != 6 or item['御魂等级'] != 15: continue
        if check(item) <= filter_hit_times:
            t = translate(item)
            print(t, '=' * 18, sep='\n')
            li1.append(item)
            li2.append(t)
    else:
        pe = os.path.splitext(p)
        o = pe[0] + '-dwarf' + pe[1]
        with open(o, 'w', encoding='utf-8') as f1:  # 按源格式导出
            f1.write(json.dumps(li1))
            print('按源格式导出：%s' % o)
        o = pe[0] + '-dwarf.txt'
        with open(o, 'w', encoding='utf-8') as f2:  # 可读化导出
            f2.write('\n\n'.join(sorted(li2, key=lambda item: '%d%s' % (SECTION.index(item[1:2]), item[3:5]))))
            print('可读化导出：%s' % o)


# 解析 NGA@fluxxu 的「痒痒熊快照」数据
def parse_data_fluxxu(data, filter_hit_times):
    if 'data' not in data or 'hero_equips' not in data['data']: raise Exception('unsupported data file version')
    li1, li2 = [], []
    for item in data['data']['hero_equips']:
        if item['quality'] != 6 or item['level'] != 15: continue
        item2 = fluxxu2hdtr(item)
        if check(item2) <= filter_hit_times:
            t = translate(item2)
            print(t, '=' * 18, sep='\n')
            li1.append(item)
            li2.append(t)
    else:
        pe = os.path.splitext(p)
        o = pe[0] + '-dwarf' + pe[1]
        with open(o, 'w', encoding='utf-8') as f1:  # 按源格式导出
            data['data']['hero_equips'] = li1
            f1.write(json.dumps(data))
            print('按源格式导出：%s' % o)
        o = pe[0] + '-dwarf.txt'
        with open(o, 'w', encoding='utf-8') as f2:  # 可读化导出
            f2.write('\n\n'.join(sorted(li2, key=lambda item: '%d%s' % (SECTION.index(item[1:2]), item[3:5]))))
            print('可读化导出：%s' % o)


print('pick-dwarf v1.4.191022 @nguaduot')
if len(sys.argv) > 1:  # 自带参数则不请求输入
    p = sys.argv[1]
    h = sys.argv[2] if len(sys.argv) > 2 else ''
else:
    p = input('数据文件路径：')  # 源文件路径
    h = input('过滤值（0~4，默认2）：')  # 有效属性加点次数过滤值
p = p.strip('"\'')
h = int(h) if h.isdigit() and int(h) < 5 else DEF_FILTER_HIT_TIMES
with open(p, 'r', encoding='utf-8') as f:
    obj = json.loads(f.read())
    if isinstance(obj, dict):  # 按「痒痒熊快照」数据处理
        parse_data_fluxxu(obj, h)
    else:  # 按「御魂导出器」数据处理
        parse_data_hdtr(obj, h)
os.system('pause')
