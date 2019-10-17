# coding=utf-8
#
# 检出六星满级低成长御魂（副属性满4条的基础上加点次数不超过3）
# 控制台输出结果，同时保存到文件（同源文件目录 *-dwarf）
#
# 支持读取 NGA@火电太热 的「御魂导出器」导出的JSON数据文件
# https://nga.178.com/read.php?tid=15220479
#
# autnor: 痒痒鼠@南瓜多糖
# version: 1.0.191016
# date: 20191016

import json
import math
import os
import sys

POS = ('壹', '贰', '叁', '肆', '伍', '陆')  # 御魂位置
GROW = {'生命': (342, 114), '防御': (14, 6), '攻击': (81, 27),
        '生命加成': (0.1, 0.03), '防御加成': (0.1, 0.03), '攻击加成': (0.1, 0.03),
        '速度': (12, 3), '暴击': (0.1, 0.03), '暴击伤害': (0.14, 0.05),
        '效果命中': (0.1, 0.03), '效果抵抗': (0.1, 0.03)}  # 御魂主属性初始&成长值
FIXED = {'生命加成': 0.08, '防御加成': 0.16, '攻击加成': 0.08,
         '暴击': 0.08, '效果命中': 0.08, '效果抵抗': 0.08}  # 首领御魂固有属性


# 主属性成长
main_attr_v = lambda attr, level: GROW[attr][0] + GROW[attr][1] * level


# 加点次数
def check(item):
    if item['御魂星级'] != 6 or item['御魂等级'] != 15: return -1
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
    li.append('[%s]%s %d/%d' % (POS[item2['位置'] - 1], item2['御魂类型'], item2['御魂星级'], item2['御魂等级']))
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
    return "\n".join(li)


print('pick-dwarf v1.0.191016 @nguaduot')
p = sys.argv[1] if len(sys.argv) > 1 else input('file: ')  # 源文件路径
with open(p, 'r', encoding='utf-8') as f:
    obj = json.loads(f.read())
    if obj[0] != 'yuhun_ocr2.0': raise Exception('unsupported data file version')
    li1, li2 = [obj[0]], []
    for item in obj[1:]:
        n = check(item)
        if n < 3 and n > 0:
            t = translate(item)
            print(t, '=' * 18, sep='\n')
            li1.append(item)
            li2.append(t)
    else:
        pe = os.path.splitext(p)
        with open(pe[0] + '-dwarf' + pe[1], 'w', encoding='utf-8') as f1:
            f1.write(json.dumps(li1))
        with open(pe[0] + '-dwarf.txt', 'w', encoding='utf-8') as f2:
            f2.write('\n\n'.join(li2))
os.system('pause')
