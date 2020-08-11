#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 检出六星满级低收益御魂（由御魂分数决定，即有效属性加点次数）
# 有效属性和御魂分数线由规则文件决定，可自定义，内含详细描述（pick-dwarf-rule.txt）
# 筛选结果在控制台输出，同时保存到文件（同源文件目录 *-dwarf）
#
# 了解更多请前往GitHub查看项目：https://github.com/nguaduot/yys-pick-dwarf
#
# + 支持读取 NGA@火电太热 的「御魂导出器」导出的JSON数据文件
#   https://nga.178.com/read.php?tid=15220479
# + 支持读取 NGA@fluxxu 的「痒痒熊快照」导出的JSON数据文件
#   https://nga.178.com/read.php?tid=16557282
#
# autnor: 痒痒鼠@南瓜多糖
# version: 1.6.200212
# date: 20200212

import json
import math
import os
import sys
import re

CATES = ('兵主部', '狂骨', '阴摩罗', '心眼', '鸣屋', '狰', '轮入道', '蝠翼',
         '青女房', '针女', '镇墓兽', '破势', '伤魂鸟', '网切', '三味',
         '涂佛', '树妖', '薙魂', '钟灵', '镜姬', '被服', '涅槃之火', '地藏像',
         '魅妖', '珍珠', '木魅', '日女巳时', '反枕', '招财猫', '雪幽魂',
         '飞缘魔', '蚌精', '火灵',
         '幽谷响', '返魂香', '骰子鬼', '魍魉之匣',
         '鬼灵歌伎', '蜃气楼', '地震鲶', '荒骷髅', '胧车', '土蜘蛛')  # 全部御魂（43种）
ATTRS = ('生命', '防御', '攻击', '生命加成', '防御加成', '攻击加成',
         '速度', '暴击', '暴击伤害', '效果命中', '效果抵抗')  # 全部属性
SECTION = ('壹', '贰', '叁', '肆', '伍', '陆')  # 御魂位置
SECTION_ATTRS = ((ATTRS[2],),
                 (ATTRS[3], ATTRS[4], ATTRS[5], ATTRS[6]),
                 (ATTRS[1],),
                 (ATTRS[3], ATTRS[4], ATTRS[5], ATTRS[9], ATTRS[10]),
                 (ATTRS[0],),
                 (ATTRS[3], ATTRS[4], ATTRS[5], ATTRS[7], ATTRS[8]))  # 每个位置的主属性
GROW_MAIN = {ATTRS[0]: (342, 114), ATTRS[1]: (14, 6), ATTRS[2]: (81, 27),
             ATTRS[3]: (0.1, 0.03), ATTRS[4]: (0.1, 0.03), ATTRS[5]: (0.1, 0.03),
             ATTRS[6]: (12, 3), ATTRS[7]: (0.1, 0.03), ATTRS[8]: (0.14, 0.05),
             ATTRS[9]: (0.1, 0.03), ATTRS[10]: (0.1, 0.03)}  # 御魂主属性初始&成长值
GROW_SUB = {ATTRS[0]: (114, 0.8), ATTRS[1]: (5, 0.8), ATTRS[2]: (27, 0.8),
            ATTRS[3]: (0.03, 0.8), ATTRS[4]: (0.03, 0.8), ATTRS[5]: (0.03, 0.8),
            ATTRS[6]: (3, 0.8), ATTRS[7]: (0.03, 0.8), ATTRS[8]: (0.04, 0.8),
            ATTRS[9]: (0.04, 0.8), ATTRS[10]: (0.04, 0.8)}  # 御魂副属性最大加点值&加点系数下限
FIXED = {ATTRS[3]: 0.08, ATTRS[4]: 0.16, ATTRS[5]: 0.08,
         ATTRS[7]: 0.08, ATTRS[9]: 0.08, ATTRS[10]: 0.08}  # 首领御魂固有属性
RULES = {}  # 过滤规则
DEF_FILTER_SCORE = 5  # 默认过滤御魂分数线（有效属性加点次数低于该值将被过滤）
RULE_FILE = 'pick-dwarf-rule.txt'  # 规则文件路径


# 主属性成长
main_attr_v = lambda attr, level: GROW_MAIN[attr][0] + GROW_MAIN[attr][1] * level


# 规则 KEY
rule_key = lambda cate, section, m_attr: '%s-%d-%s' % (cate, section, m_attr)


# 加点可视化
dots = lambda n: ' ' + '.' * n if n > 1 and n <= 6 else ''


# 生成可读御魂数据的排序关键字，按 类型-位置 排序。输入如：[陆]破势 6/15 ……
sort_key = lambda item: CATES.index(item.split(' ', 1)[0][3:]) * 10 + SECTION.index(item[1:2])


# 根据御魂分数判断低收益御魂
def dwarf(item):
    item2, n = item.copy(), 0
    if '固有属性' in item2:
        item2[item2['固有属性']] -= FIXED[item2['固有属性']]
        if item2[item2['固有属性']] < 0.024: del item2[item2['固有属性']]
    main, mainv = '', 0  # 主属性、主属性值
    for attr in SECTION_ATTRS[item2['位置'] - 1]:
        mainv = main_attr_v(attr, item2['御魂等级'])
        if attr in item2 and item2[attr] >= mainv:
            item2[attr] -= mainv
            if item2[attr] < 0.024: del item2[attr]
            main = attr
            break
    high_yield = False
    k = rule_key(item2['御魂类型'], item2['位置'] - 1, main)
    if k not in RULES: RULES[k] = [{'attrs': ATTRS[3:11], 'score': DEF_FILTER_SCORE}]
    for rule in RULES[k]:
        score = 0
        if '固有属性' in item2 and item2['固有属性'] in rule['attrs']:
            score += math.ceil(FIXED[item2['固有属性']] / GROW_SUB[item2['固有属性']][0])
        for attr in rule['attrs']:
            if attr in item2: score += math.ceil(item2[attr] / GROW_SUB[attr][0])
        high_yield = score >= rule['score']
        if high_yield: break
    return not high_yield


# 将单个御魂数据解析为可阅读样式
def translate(item):
    item2, li = item.copy(), []
    if '固有属性' in item2:
        item2[item2['固有属性']] -= FIXED[item2['固有属性']]
        if item2[item2['固有属性']] < 0.024: del item2[item2['固有属性']]
    li.append('[%s]%s %d/%d' % (SECTION[item2['位置'] - 1], item2['御魂类型'], item2['御魂星级'], item2['御魂等级']))
    if item2['御魂星级'] < 6: return li[0]
    if ATTRS[0] in item2:  # 生命
        mainv, v = main_attr_v(ATTRS[0], item2['御魂等级']), item2[ATTRS[0]]
        if v >= mainv:
            li.insert(1, '%s %d' % (ATTRS[0], mainv))
            v -= mainv
        if v > 90: li.append('%s +%d' % (ATTRS[0], round(v)))
    if ATTRS[1] in item2:  # 防御
        mainv, v = main_attr_v(ATTRS[1], item2['御魂等级']), item2[ATTRS[1]]
        if v >= mainv:
            li.insert(1, '%s %d' % (ATTRS[1], mainv))
            v -= mainv
        if v > 3: li.append('%s +%d' % (ATTRS[1], round(v)))
    if ATTRS[2] in item2:  # 攻击
        mainv, v = main_attr_v(ATTRS[2], item2['御魂等级']), item2[ATTRS[2]]
        if v >= mainv:
            li.insert(1, '%s %d' % (ATTRS[2], mainv))
            v -= mainv
        if v > 21: li.append('%s +%d' % (ATTRS[2], round(v)))
    if ATTRS[3] in item2:  # 生命加成
        mainv, v = main_attr_v(ATTRS[3], item2['御魂等级']), item2[ATTRS[3]]
        if v >= mainv:
            li.insert(1, '%s %d%%' % (ATTRS[3], round(mainv * 100)))
            v -= mainv
        if v > 0.024: li.append('%s +%d%%%s' % (ATTRS[3], round(v * 100), dots(math.ceil(v / 0.03))))
    if ATTRS[4] in item2:  # 防御加成
        mainv, v = main_attr_v(ATTRS[4], item2['御魂等级']), item2[ATTRS[4]]
        if v >= mainv:
            li.insert(1, '%s %d%%' % (ATTRS[4], round(mainv * 100)))
            v -= mainv
        if v > 0.024: li.append('%s +%d%%%s' % (ATTRS[4], round(v * 100), dots(math.ceil(v / 0.03))))
    if ATTRS[5] in item2:  # 攻击加成
        mainv, v = main_attr_v(ATTRS[5], item2['御魂等级']), item2[ATTRS[5]]
        if v >= mainv:
            li.insert(1, '%s %d%%' % (ATTRS[5], round(mainv * 100)))
            v -= mainv
        if v > 0.024: li.append('%s +%d%%%s' % (ATTRS[5], round(v * 100), dots(math.ceil(v / 0.03))))
    if ATTRS[6] in item2:  # 速度
        mainv, v = main_attr_v(ATTRS[6], item2['御魂等级']), item2[ATTRS[6]]
        if v >= mainv:
            li.insert(1, '%s %d' % (ATTRS[6], mainv))
            v -= mainv
        if v > 2.4: li.append('%s +%d%s' % (ATTRS[6], round(v), dots(math.ceil(v / 3))))
    if ATTRS[7] in item2:  # 暴击
        mainv, v = main_attr_v(ATTRS[7], item2['御魂等级']), item2[ATTRS[7]]
        if v >= mainv:
            li.insert(1, '%s %d%%' % (ATTRS[7], round(mainv * 100)))
            v -= mainv
        if v > 0.024: li.append('%s +%d%%%s' % (ATTRS[7], round(v * 100), dots(math.ceil(v / 0.03))))
    if ATTRS[8] in item2:  # 暴击伤害
        mainv, v = main_attr_v(ATTRS[8], item2['御魂等级']), item2[ATTRS[8]]
        if v >= mainv:
            li.insert(1, '%s %d%%' % (ATTRS[8], round(mainv * 100)))
            v -= mainv
        if v > 0.032:
            li.append('%s +%d%%%s' % (ATTRS[8], round(v * 100), dots(math.ceil(v / 0.04))))
    if ATTRS[9] in item2:  # 效果命中
        mainv, v = main_attr_v(ATTRS[9], item2['御魂等级']), item2[ATTRS[9]]
        if v >= mainv:
            li.insert(1, '%s %d%%' % (ATTRS[9], round(mainv * 100)))
            v -= mainv
        if v > 0.032: li.append('%s +%d%%%s' % (ATTRS[9], round(v * 100), dots(math.ceil(v / 0.04))))
    if ATTRS[10] in item2:  # 效果抵抗
        mainv, v = main_attr_v(ATTRS[10], item2['御魂等级']), item2[ATTRS[10]]
        if v >= mainv:
            li.insert(1, '%s %d%%' % (ATTRS[10], round(mainv * 100)))
            v -= mainv
        if v > 0.032: li.append('%s +%d%%%s' % (ATTRS[10], round(v * 100), dots(math.ceil(v / 0.04))))
    if '固有属性' in item2: li.append('(固)%s %d%%' % (item2['固有属性'], FIXED[item2['固有属性']] * 100))
    return '\n'.join(li)


# 「痒痒熊快照」导出数据转「御魂导出器」数据格式
def fluxxu2hdtr(fluxxu):
    CATES_ID_NAME = {300074: CATES[0], 300048: CATES[1], 300027: CATES[2], 300022: CATES[3],
                     300020: CATES[4], 300018: CATES[5], 300012: CATES[6], 300004: CATES[7],
                     300075: CATES[8], 300036: CATES[9], 300031: CATES[10], 300030: CATES[11],
                     300029: CATES[12], 300026: CATES[13], 300007: CATES[14], 300076: CATES[15],
                     300024: CATES[16], 300021: CATES[17], 300015: CATES[18], 300014: CATES[19],
                     300009: CATES[20], 300006: CATES[21], 300003: CATES[22], 300035: CATES[23],
                     300032: CATES[24], 300023: CATES[25], 300013: CATES[26], 300011: CATES[27],
                     300010: CATES[28], 300002: CATES[29], 300073: CATES[30], 300034: CATES[31],
                     300019: CATES[32], 300049: CATES[33], 300039: CATES[34], 300033: CATES[35],
                     300008: CATES[36], 300077: CATES[37], 300054: CATES[38], 300053: CATES[39],
                     300052: CATES[40], 300051: CATES[41], 300050: CATES[42]}  # 「痒痒熊快照」御魂ID-名字表
    ATTRS_ID_NAME = {'Hp': ATTRS[0], 'Defense': ATTRS[1], 'Attack': ATTRS[2],
                     'HpRate': ATTRS[3], 'DefenseRate': ATTRS[4], 'AttackRate': ATTRS[5],
                     'Speed': ATTRS[6], 'CritRate': ATTRS[7], 'CritPower': ATTRS[8],
                     'EffectHitRate': ATTRS[9], 'EffectResistRate': ATTRS[10]}  # 「痒痒熊快照」属性ID-名字表
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
def parse_data_hdtr(data):
    if data[0] != 'yuhun_ocr2.0':
        print('[出错]数据文件有误或不受支持')
        return
    li1, li2 = [data[0]], []
    print('=' * 20)
    for item in data[1:]:
        if item['御魂星级'] != 6 or item['御魂等级'] != 15: continue
        if dwarf(item):
            li1.append(item)
            t = translate(item)
            li2.append(t)
            if len(li2) > 1: print('=' * 20)
            print(t)
    else:
        print('=' * 20)
        pe = os.path.splitext(p)
        o = pe[0] + '-dwarf' + pe[1]
        with open(o, 'w', encoding='utf-8') as f1:  # 按源格式导出
            f1.write(json.dumps(li1))
            print('[日志]已将结果导出：%s' % o)
        o = pe[0] + '-dwarf.txt'
        with open(o, 'w', encoding='utf-8') as f2:  # 可读化导出
            f2.write('\n\n'.join(sorted(li2, key=sort_key)))
            print('[日志]已将结果导出：%s' % o)


# 解析 NGA@fluxxu 的「痒痒熊快照」数据
def parse_data_fluxxu(data):
    if 'data' not in data or 'hero_equips' not in data['data']:
        print('[出错]数据文件有误或不受支持')
        return
    li1, li2 = [], []
    print('=' * 20)
    for item in data['data']['hero_equips']:
        if item['quality'] != 6 or item['level'] != 15: continue
        if item['garbage']: continue  # 跳过已弃置御魂
        item2 = fluxxu2hdtr(item)
        if dwarf(item2):
            li1.append(item)
            t = translate(item2)
            li2.append(t)
            if len(li2) > 1: print('=' * 20)
            print(t)
    else:
        print('=' * 20)
        pe = os.path.splitext(p)
        o = pe[0] + '-dwarf' + pe[1]
        with open(o, 'w', encoding='utf-8') as f1:  # 按源格式导出
            data['data']['hero_equips'] = li1
            f1.write(json.dumps(data))
            print('[日志]已将结果导出：%s' % o)
        o = pe[0] + '-dwarf.txt'
        with open(o, 'w', encoding='utf-8') as f2:  # 可读化导出
            f2.write('\n\n'.join(sorted(li2, key=sort_key)))
            print('[日志]已将结果导出：%s' % o)


# 解析规则文件
def parse_rule():
    generate_def_rule()
    RULES.clear()
    with open(RULE_FILE, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            if len(line.strip()) == 0 or line.startswith('#'): continue
            m = re.match('(.+?)(?:-(\d+))?(?:-(.+?))?：(.+?)，(\d+)', line)
            if m:
                for pos in list(m.group(2) if m.group(2) else '123456'):
                    for attr in SECTION_ATTRS[int(pos) - 1]:
                        if not m.group(3) or attr == m.group(3):
                            k = rule_key(m.group(1), int(pos) - 1, attr)
                            if k not in RULES: RULES[k] = []
                            RULES[k].append({'attrs': m.group(4).split('、'), 'score': int(m.group(5))})
            else: print('[警告]已跳过非法规则“%s”' % line)


# 生成默认规则文件
def generate_def_rule():
    if os.path.exists(RULE_FILE): return
    print('[警告]未在程序运行目录下发现规则文件，将新建默认规则文件')
    with open(RULE_FILE, 'w', encoding='utf-8') as f:
        f.write('# pick-dwarf-rule for pick-dwarf v2.0\n# ')
        f.write('\n# [御魂]-[位置]-[主属性]：[有效副属性]，[分数线]\n# ')
        for cate in CATES:
            f.write('\n%s：%s，%d' % (cate, '、'.join(ATTRS[3:11]), DEF_FILTER_SCORE))


print('pick-dwarf', 'v2.0.200212', '@nguaduot', 'github.com/nguaduot/yys-pick-dwarf')
parse_rule()
p = (sys.argv[1] if len(sys.argv) > 1 else input('[输入]数据文件路径：')).strip('"\'')
try:
    with open(p, 'r', encoding='utf-8') as f:
        obj = json.loads(f.read())
        if isinstance(obj, dict):  # 按「痒痒熊快照」数据处理
            parse_data_fluxxu(obj)
        else:  # 按「御魂导出器」数据处理
            parse_data_hdtr(obj)
except (FileNotFoundError, UnicodeDecodeError, json.decoder.JSONDecodeError) as e:
    print('[出错]非法数据文件或不存在')
    print(repr(e))
except:
    print('[出错]未知错误，请将以下错误信息反馈给作者')
    raise
os.system('pause')
