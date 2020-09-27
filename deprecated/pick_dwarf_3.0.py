#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# 检出六星满级低收益御魂（由御魂分数决定，即有效属性加点次数）
# 有效属性和御魂分数线由规则文件决定，可自定义，内含详细描述（pick_dwarf_rule.txt）
# 筛选结果在控制台输出，同时保存到文件（同源文件目录 *_dwarf）
#
# 了解更多请前往 GitHub 查看项目：https://github.com/nguaduot/yys-pick-dwarf
#
# + 支持读取 NGA@火电太热 的「御魂导出器」导出的JSON数据文件
#   https://nga.178.com/read.php?tid=15220479
# + 支持读取 NGA@fluxxu 的「痒痒熊快照」导出的JSON数据文件
#   https://nga.178.com/read.php?tid=16557282
#
# author: @nguaduot 痒痒鼠@南瓜多糖
# version: 3.0.200811
# date: 20200811


import copy
import getopt
import glob
import json
import math
import os
from os import path
import re
import sys
import time
from urllib import request


PROG = 'yys-pick-dwarf'
AUTH = 'nguaduot'
VER = '3.0'
VERSION = '3.0.200811'
REL = 'github.com/nguaduot/yys-pick-dwarf'
COPYRIGHT = '%s v%s @%s %s' % (PROG, VERSION, AUTH, REL)
HELP = '''+ 选项：
  -h, --help     帮助
  -v, --version  程序版本
  -r, --rule     本地规则文件路径或直链 URL
  -d, --data     本地数据文件路径
+ 若未指定 -r，程序会自动查找本地规则文件
+ 若未指定 -d，程序会读取未知参数，若也无未知参数，不启动程序
+ 不带任何参数也可启动程序，会有参数输入引导'''

KINDS = (
    '兵主部', '狂骨', '阴摩罗', '心眼', '鸣屋', '狰', '轮入道', '蝠翼',
    '青女房', '针女', '镇墓兽', '破势', '伤魂鸟', '网切', '三味',
    '涂佛', '树妖', '薙魂', '钟灵', '镜姬', '被服', '涅槃之火', '地藏像',
    '魅妖', '珍珠', '木魅', '日女巳时', '反枕', '招财猫', '雪幽魂',
    '飞缘魔', '蚌精', '火灵',
    '幽谷响', '返魂香', '骰子鬼', '魍魉之匣',
    '鬼灵歌伎', '蜃气楼', '地震鲶', '荒骷髅', '胧车', '土蜘蛛'
)  # 全部御魂类型（截至当前版本，43 种）

ATTRS = (
    '生命', '防御', '攻击',
    '生命加成', '防御加成', '攻击加成',
    '速度', '暴击', '暴击伤害',
    '效果命中', '效果抵抗'
)  # 全部属性

POS = ('壹', '贰', '叁', '肆', '伍', '陆')  # 御魂位置

ATTRS_POS = (
    (ATTRS[2],),
    (ATTRS[3], ATTRS[4], ATTRS[5], ATTRS[6]),
    (ATTRS[1],),
    (ATTRS[3], ATTRS[4], ATTRS[5], ATTRS[9], ATTRS[10]),
    (ATTRS[0],),
    (ATTRS[3], ATTRS[4], ATTRS[5], ATTRS[7], ATTRS[8])
)  # 每个位置的主属性

ATTRS_MAIN = {
    ATTRS[0]: ((
        (35, 12), (69, 23), (137, 46), (206, 69), (274, 92), (342, 114)
    ), '{} {:.0f}'),
    ATTRS[1]: ((
        (2, 1), (3, 2), (6, 3), (8, 4), (11, 5), (14, 6)
    ), '{} {:.0f}'),
    ATTRS[2]: ((
        (9, 3), (17, 6), (33, 11), (49, 17), (65, 22), (81, 27)
    ), '{} {:.0f}'),
    ATTRS[3]: ((
        (0.01, 0.01), (0.02, 0.01), (0.04, 0.02),
        (0.06, 0.02), (0.08, 0.02), (0.1, 0.03)
    ), '{} {:.0%}'),
    ATTRS[4]: ((
        (0.01, 0.01), (0.02, 0.01), (0.04, 0.02),
        (0.06, 0.02), (0.08, 0.02), (0.1, 0.03)
    ), '{} {:.0%}'),
    ATTRS[5]: ((
        (0.01, 0.01), (0.02, 0.01), (0.04, 0.02),
        (0.06, 0.02), (0.08, 0.02), (0.1, 0.03)
    ), '{} {:.0%}'),
    ATTRS[6]: ((
        (2, 1), (4, 1), (6, 2), (8, 2), (10, 2), (12, 3)
    ), '{} {:.0f}'),
    ATTRS[7]: ((
        (0.01, 0.01), (0.02, 0.01), (0.04, 0.02),
        (0.06, 0.02), (0.08, 0.02), (0.1, 0.03)
    ), '{} {:.0%}'),
    ATTRS[8]: ((
        (0.02, 0.02), (0.03, 0.02), (0.05, 0.03),
        (0.09, 0.03), (0.11, 0.04), (0.14, 0.05)
    ), '{} {:.0%}'),
    ATTRS[9]: ((
        (0.01, 0.01), (0.02, 0.01), (0.04, 0.02),
        (0.06, 0.02), (0.08, 0.02), (0.1, 0.03)
    ), '{} {:.0%}'),
    ATTRS[10]: ((
        (0.01, 0.01), (0.02, 0.01), (0.04, 0.02),
        (0.06, 0.02), (0.08, 0.02), (0.1, 0.03)
    ), '{} {:.0%}')
}  # 一至六星御魂主属性初始值 & 加点值、可读化

ATTRS_SUB = {
    ATTRS[0]: (114, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%df}'),
    ATTRS[1]: (5, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%df}'),
    ATTRS[2]: (27, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%df}'),
    ATTRS[3]: (0.03, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%d%%}'),
    ATTRS[4]: (0.03, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%d%%}'),
    ATTRS[5]: (0.03, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%d%%}'),
    ATTRS[6]: (3, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%df}'),
    ATTRS[7]: (0.03, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%d%%}'),
    ATTRS[8]: (0.04, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%d%%}'),
    ATTRS[9]: (0.04, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%d%%}'),
    ATTRS[10]: (0.04, (
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)
    ), '{} +{:.%d%%}')
}  # 一至六星御魂副属性初始值 / 加点值、加点系数范围、可读化

ATTRS_DBL = {
    ATTRS[3]: (0.15, KINDS[15:23], '(两){} {:.0%}'),
    ATTRS[4]: (0.3, KINDS[23:30], '(两){} {:.0%}'),
    ATTRS[5]: (0.15, KINDS[:8], '(两){} {:.0%}'),
    ATTRS[7]: (0.15, KINDS[8:15], '(两){} {:.0%}'),
    ATTRS[9]: (0.15, KINDS[30:33], '(两){} {:.0%}'),
    ATTRS[10]: (0.15, KINDS[33:37], '(两){} {:.0%}'),
}  # 非首领御魂两件套属性值、包含御魂、可读化

ATTRS_SGL = {
    ATTRS[3]: (0.08, '(固){} {:.0%}'),
    ATTRS[4]: (0.16, '(固){} {:.0%}'),
    ATTRS[5]: (0.08, '(固){} {:.0%}'),
    ATTRS[7]: (0.08, '(固){} {:.0%}'),
    ATTRS[9]: (0.08, '(固){} {:.0%}'),
    ATTRS[10]: (0.08, '(固){} {:.0%}')
}  # 首领御魂固有属性（即单件效果，普通御魂无单件效果）值、可读化

DECIMAL = 6  # 数值精度，round(x, 6)，用以消除浮点数运算可能产生的“不确定尾数”

DEF_SCORE_MUL = 5  # 多腿默认过滤御魂分数线（含多条有效属性加点次数低于该值将被过滤）
DEF_SCORE_SGL = 4  # 单腿默认过滤御魂分数线（含单条有效属性加点次数低于该值将被过滤）

DEF_RULE_FILE = 'pick_dwarf_rule'  # 规则文件默认名，可识别自定义：pick_dwarf_rule*
DWARF_FILE = '%s_dwarf%s'  # 导出结果文件名格式

RULES = {}  # 过滤规则，程序运行初进行装载


def main_attr(attr, star, level):
    """主属性成长

    计算主属性目标等级的值。结果只有两种情况：整数、整百分数（即精确到小数点后两位）

    重要：Python 浮点数运算可能产生“不确定尾数”，如
        0.1 + 0.03 * 15 = 0.5499999999999999
    所以使用 round(x, 2) 消除影响。

    Args:
        attr (str): 主属性名
        star (int): 星级，1~6
        level (int): 等级

    Returns:
        float: 返回目标等级的主属性值
    """
    grow = ATTRS_MAIN[attr][0][star - 1]
    return round(grow[0] + grow[1] * level, 2)


def rule_key(kind, pos, m_attr):
    """生成规则 KEY

    生成全局变量 RULES 中的 KEY。

    Args:
        kind (str): 御魂类型
        pos (int): 御魂位置，1~6
        m_attr (str): 主属性

    Returns:
        str: 返回规则 KEY，如：火灵-6-攻击加成
    """
    return '%s-%d-%s' % (kind, pos, m_attr)


def def_rules():
    """生成默认规则

    Returns:
        list: 返回默认规则
    """
    return [{
        'attrs': ATTRS[3:11],
        'score': DEF_SCORE_MUL
    }] + [{
        'attrs': (attr,),
        'score': DEF_SCORE_SGL
    } for attr in ATTRS[3:11]]


def with_dots(score):
    """副属性强化加点可视化

    给可读御魂数据中副属性末尾追加“.”，以点数表示强化加点次数。
    初始值的 1 点不计入内。无中生有的属性均视为初始值。
    与其分数差 1。例：
        ...
        速度 +9 ..
        ...

    Args:
        score (int): 副属性分数

    Returns:
        str: 返回追加字符
    """
    return ' ' + '.' * (score - 1) if 2 <= score <= 6 else ''


def out_key(item):
    """生成可读御魂数据的排序 KEY

    用于输出大量结果时进行排序。输入如：
        [陆|6] 火灵 +15
        攻击加成 55%
        防御 +4
        攻击 +96
        生命加成 +3%
        速度 +9
    按 类型-位置 抽取关键字根据索引生成 KEY，为“325”。

    Args:
        item (str): 已被解析为可读的御魂数据

    Returns:
        str: 返回 KEY
    """
    return KINDS.index(item.split(' ', 2)[1]) * 10 + POS.index(item[1:2])


def score_attr(attr, star, value):
    """计算副属性分数

    对于一条副属性，初始值和每次加点（满级最多加点 5 次）均视为 1 分，最低 1 分，最高 6 分；
    对于视为副属性的固有属性，其分数随星级波动。如荒骷髅：
        ...
        (固)暴击 8%
    其固有属性值分数为 3 分（六星）、
    4 分（五星、四星）、5 分（三星）、6 分（二星）、7 分（一星）。

    分数还会随判定算法波动，如六星御魂副属性
        攻击加成 +14.8%
    可为高成长的 5 分（严格），也可为低成长的 6 分（宽容）。

    重要：本程序沿用 v2.0 起的严格算法。

    Args:
        attr (str): 副属性名
        star (int): 星级，1~6
        value (float): 副属性值

    Returns:
        int: 返回分数（最低 1 分）
    """
    grow = ATTRS_SUB[attr][:2]
    # return int(min(value // (grow[0] * grow[1][star - 1][0]), 6))  # 宽容
    return math.ceil(value / (grow[0] * grow[1][star - 1][1]))  # 严格


def score_attrs(item, attrs_useful):
    """计算御魂分数

    对于一颗普通六星御魂，其分数为每条有效副属性分数之和，最低 0 分，最高 9 分；
    而一颗首领六星御魂，其固有属性也会参与评分，分三种情况，固有属性为：
        防御加成
    此类总分 0~15 分；固有属性为：
        生命加成、攻击加成、暴击
    此类总分 0~12 分；固有属性为：
        效果命中、效果抵抗
    此类总分 0~11 分。
    对于低星普通御魂，由于初始副属性条数最高不会达到 4，所以其分数上限天然低；
    对于低星首领御魂，由于各星级属性成长差异，而固有属性值不随星级变动，
    所以其分数上限也会随星级变动。

    Args:
        item (dict): 单颗御魂的元数据
        attrs_useful (list): 有效副属性集（固有属性也视为副属性）

    Returns:
        int: 返回分数（最低 0 分）
    """
    total_score = 0
    attrs = {attr['attr']: attr['value'] for attr in item['attrs']['subs']}
    if 'sgl' in item['attrs']:
        if item['attrs']['sgl']['attr'] in attrs:
            attrs[item['attrs']['sgl']['attr']] += item['attrs']['sgl']['value']
        else:
            attrs[item['attrs']['sgl']['attr']] = item['attrs']['sgl']['value']
    for attr, value in attrs.items():
        if attr in attrs_useful:
            total_score += score_attr(attr, item['star'], value)
    return total_score


def grow_attr(attr, star, value):
    """计算副属性成长系数

    在副属性分数的基础上，计算其成长系数（来自每 1 分的成长系数均值），
    范围 30~100%，与星级相关。如六星御魂副属性
        攻击加成 +14.8%
    其分数为 6，成长为 82%。

    Args:
        attr (str): 副属性名
        star (int): 星级，1~6
        value (float): 副属性值

    Returns:
        float: 返回成长系数（30~100%）
    """
    score = score_attr(attr, star, value)
    grow = ATTRS_SUB[attr][:2]
    # return ((value / score - grow[0] * grow[1][star - 1][0])
    #         / (grow[0] * (grow[1][star - 1][1] - grow[1][star - 1][0])))
    return value / score / grow[0]


def grow_attrs(item, attrs_useful):
    """计算御魂成长系数

    在御魂分数的基础上，计算其成长系数（来自每条副属性每 1 分的成长系数均值），
    范围 30~100%，与星级相关。
    例：一颗真 17 满速御魂，其速度成长得超过 94%。

    Args:
        item (dict): 单颗御魂的元数据
        attrs_useful (list): 有效副属性（固有属性也视为副属性）

    Returns:
        float: 返回成长系数（30~100%）
    """
    total_grow = []
    attrs = {attr['attr']: attr['value'] for attr in item['attrs']['subs']}
    if 'sgl' in item['attrs']:
        if item['attrs']['sgl']['attr'] in attrs:
            attrs[item['attrs']['sgl']['attr']] += item['attrs']['sgl']['value']
        else:
            attrs[item['attrs']['sgl']['attr']] = item['attrs']['sgl']['value']
    for attr, value in attrs.items():
        if attr in attrs_useful:
            total_grow.append(grow_attr(attr, item['star'], value))
    return sum(total_grow) / len(total_grow) if total_grow else 0


def dwarf(item):
    """根据御魂分数判定低收益御魂
    
    御魂分数储存在全局变量 RULES，程序运行初通过解析规则文件获得。
    仅对六星满级御魂进行判定。判定成功（即为低收益御魂），结果例：
        {
            'rule': None,
            'score': None,
            'result': True
        }
    判定失败（即非低收益御魂），结果例：
        {
            'rule': {
                'attrs': ('攻击加成', '速度'),
                'score': 5
            },
            'score': 5,
            'result': False
        }
    若该类型御魂未设定任何规则，会跳过判定，结果例：
        {
            'rule': None,
            'score': None,
            'result': False
        }
    
    Args:
        item (dict): 单颗御魂的元数据
    
    Returns:
        dict: 返回详细结果
    """
    if item['star'] != 6 or item['level'] != 15:  # 未六星未满级御魂不作判定
        return {'rule': None, 'score': None, 'result': False}
    k = rule_key(item['kind'], item['pos'], item['attrs']['main']['attr'])
    if k not in RULES:  # 该类型御魂未设定任何规则，跳过判定
        return {'rule': None, 'score': None, 'result': False}
    for rule in RULES[k]:
        total_score = score_attrs(item, rule['attrs'])
        if total_score >= rule['score']:
            return {
                'rule': rule.copy(),
                'score': total_score,
                'result': False
            }
    return {'rule': None, 'score': None, 'result': True}


def translate(item, with_dbl=False, with_sgl=True,
              with_up=False, with_grow=False, magnify=0):
    """将单颗御魂数据解析为可阅读样式

    结果例：
        [陆|6] 火灵 +15
        攻击加成 55%
        防御 +4
        攻击 +96 ...
        生命加成 +3%
        速度 +9 ..
    头部信息为：位置、星级、类型、等级（0 级不显示）
    第二部分为主属性行：主属性、属性值
    第三部分为副属性，1~4 行，每行为：副属性、属性值、强化加点（可选）、成长系数（可选）
    第四部分为固有属性行（若有）：“(固)”、固有属性、属性值
    
    Args:
        item (dict): 单颗御魂的元数据
        with_dbl (bool): 是否显示普通御魂的两件套属性（默认不显示）
        with_sgl (bool): 是否显示首领御魂的固有属性（默认显示）
        with_up (bool): 是否在副属性末尾追加指示强化加点次数的小点（默认不追加）
        with_grow (bool): 是否在副属性末尾追加指示成长的百分比系数（默认不追加）
        magnify (int): 模拟「阴阳师放大镜」效果，指定放大倍数，仅对副属性生效（默认不放大）
    
    Returns:
        str: 返回“翻译”好的御魂数据
    """
    out = ['[%s|%d] %s' % (POS[item['pos'] - 1], item['star'], item['kind'])]
    if item['level'] > 0:
        out[0] += ' +%d' % item['level']
    attr = item['attrs']['main']
    out.append(ATTRS_MAIN[attr['attr']][1].format(attr['attr'], attr['value']))
    attrs_sub = sorted(
        item['attrs']['subs'],
        key=lambda x: ATTRS.index(x['attr'])
    )  # 副属性按序显示
    for attr in attrs_sub:
        out_format = ATTRS_SUB[attr['attr']][2] % magnify  # 设定放大倍数
        line = out_format.format(attr['attr'], attr['value'])
        if with_up:
            line += with_dots(score_attr(attr['attr'], item['star'],
                                         attr['value']))
        if with_grow:
            line += ' ({:.0%})'.format(grow_attr(
                attr['attr'], item['star'], attr['value']
            ))
        out.append(line)
    if with_dbl:
        for attr, preset in ATTRS_DBL.items():
            if item['kind'] in preset[1]:
                out.append(preset[2].format(attr, preset[0]))
                break
    if with_sgl and 'sgl' in item['attrs']:
        attr = item['attrs']['sgl']
        out.append(ATTRS_SGL[attr['attr']][1].format(attr['attr'],
                                                     attr['value']))
    return '\n'.join(out)


def meta_hdtr2std(item):
    """将「御魂导出器」格式元数据重封装为标准格式

    标准格式：
        {
            'id': ...,
            'kind': ...,
            'pos': ...,
            'star': ...,
            'level': ...,
            'attrs': {
                'main': {
                    'attr': ...,
                    'value': ...
                },
                'subs': [{
                    'attr': ...,
                    'value': ...
                }, ...],
                'sgl': {
                    'attr': ...,
                    'value': ...
                }
            }
        }
    如何判断首领御魂：
        正：if 'sgl' in item['attrs']
        误：if item['attrs']['sgl']

    Args:
        item (dict): 「御魂导出器」导出数据中单颗御魂的元数据

    Returns:
        dict: 标准格式的御魂元数据
    """
    item2 = item.copy()
    sgl_name, sgl_value = None, 0  # 固有属性、固有属性值
    if '固有属性' in item2:  # 剥离固有属性
        sgl_name = item2['固有属性']
        sgl_value = ATTRS_SGL[sgl_name][0]
        item2[sgl_name] -= sgl_value
        if round(item2[sgl_name], DECIMAL) == 0:
            del item2[sgl_name]
    m_name, m_value = None, 0  # 主属性、主属性值
    for attr in ATTRS_POS[item2['位置'] - 1]:  # 剥离主属性
        m_value = main_attr(attr, item2['御魂星级'], item2['御魂等级'])
        if attr in item2 and item2[attr] >= m_value:
            item2[attr] -= m_value
            if round(item2[attr], DECIMAL) == 0:
                del item2[attr]
            m_name = attr
            break
    item_std = {
        'id': item2['御魂ID'],
        'kind': item2['御魂类型'],
        'pos': item2['位置'],
        'star': item2['御魂星级'],
        'level': item2['御魂等级'],
        'attrs': {
            'main': {
                'attr': m_name,
                'value': m_value
            },
            'subs': []
        }
    }
    for attr in ATTRS:
        if attr in item2:
            item_std['attrs']['subs'].append({
                'attr': attr,
                'value': item2[attr]
            })
    if sgl_name:
        item_std['attrs']['sgl'] = {
            'attr': sgl_name,
            'value': sgl_value
        }
    return item_std


def meta_fluxxu2std(item):
    """将「痒痒熊快照」格式元数据重封装为标准格式

    Args:
        item (dict): 「痒痒熊快照」导出数据中单颗御魂的元数据

    Returns:
        dict: 标准格式的御魂元数据
    """
    kinds_id_name = {
        300074: KINDS[0], 300048: KINDS[1], 300027: KINDS[2],
        300022: KINDS[3], 300020: KINDS[4], 300018: KINDS[5],
        300012: KINDS[6], 300004: KINDS[7], 300075: KINDS[8],
        300036: KINDS[9], 300031: KINDS[10], 300030: KINDS[11],
        300029: KINDS[12], 300026: KINDS[13], 300007: KINDS[14],
        300076: KINDS[15], 300024: KINDS[16], 300021: KINDS[17],
        300015: KINDS[18], 300014: KINDS[19], 300009: KINDS[20],
        300006: KINDS[21], 300003: KINDS[22], 300035: KINDS[23],
        300032: KINDS[24], 300023: KINDS[25], 300013: KINDS[26],
        300011: KINDS[27], 300010: KINDS[28], 300002: KINDS[29],
        300073: KINDS[30], 300034: KINDS[31], 300019: KINDS[32],
        300049: KINDS[33], 300039: KINDS[34], 300033: KINDS[35],
        300008: KINDS[36], 300077: KINDS[37], 300054: KINDS[38],
        300053: KINDS[39], 300052: KINDS[40], 300051: KINDS[41],
        300050: KINDS[42]
    }  # 「痒痒熊快照」御魂 ID - 名字表
    attrs_id_name = {
        'Hp': ATTRS[0], 'Defense': ATTRS[1], 'Attack': ATTRS[2],
        'HpRate': ATTRS[3], 'DefenseRate': ATTRS[4], 'AttackRate': ATTRS[5],
        'Speed': ATTRS[6], 'CritRate': ATTRS[7], 'CritPower': ATTRS[8],
        'EffectHitRate': ATTRS[9], 'EffectResistRate': ATTRS[10]
    }  # 「痒痒熊快照」属性 ID - 名字表
    item_std = {
        'id': item['id'],
        'kind': kinds_id_name[item['suit_id']],
        'pos': item['pos'] + 1,
        'star': item['quality'],
        'level': item['level'],
        'attrs': {
            'main': {
                'attr': attrs_id_name[item['base_attr']['type']],
                'value': item['base_attr']['value']
            },
            'subs': []
        }
    }
    for attr in item['attrs']:
        item_std['attrs']['subs'].append({
            'attr': attrs_id_name[attr['type']],
            'value': attr['value']
        })
    if item['single_attrs']:
        item_std['attrs']['sgl'] = {
            'attr': attrs_id_name[item['single_attrs'][0]['type']],
            'value': item['single_attrs'][0]['value']
        }
    return item_std


def meta_cbg2std(item):
    """将藏宝阁格式元数据重封装为标准格式

    Args:
        item (dict): 藏宝阁数据中单颗御魂的元数据

    Returns:
        dict: 标准格式的御魂元数据
    """
    attrs_id_name = {
        'maxHpAdditionVal': ATTRS[0], 'defenseAdditionVal': ATTRS[1],
        'attackAdditionVal': ATTRS[2], 'maxHpAdditionRate': ATTRS[3],
        'defenseAdditionRate': ATTRS[4], 'attackAdditionRate': ATTRS[5],
        'speedAdditionVal': ATTRS[6], 'critRateAdditionVal': ATTRS[7],
        'critPowerAdditionVal': ATTRS[8], 'debuffEnhance': ATTRS[9],
        'debuffResist': ATTRS[10]
    }  # 属性 ID - 名字表
    attrs_base_r = (
        (ATTRS[2], ATTRS[5]),
        (ATTRS[1], ATTRS[4]),
        (ATTRS[0], ATTRS[3]),
        (ATTRS[6], ATTRS[8], ATTRS[9]),
        (ATTRS[7], ATTRS[10])
    )  # 源数据 base_rindex 键对应的全部属性，结合 pos 键可确定主属性
    attr_m = list(set(ATTRS_POS[item['pos'] - 1])
                  & set(attrs_base_r[item['base_rindex']]))[0]
    item_std = {
        'id': item['uuid'],
        'kind': item['name'],
        'pos': item['pos'],
        'star': item['qua'],
        'level': item['level'],
        'attrs': {
            'main': {
                'attr': attr_m,
                'value': main_attr(attr_m, item['qua'], item['level'])
            },
            'subs': []
        }
    }
    attrs_sub = {}
    for grow in item['rattr']:
        if grow[0] in attrs_sub:
            attrs_sub[grow[0]] += grow[1]
        else:
            attrs_sub[grow[0]] = grow[1]
    for attr_id, value_ratio in attrs_sub.items():
        item_std['attrs']['subs'].append({
            'attr': attrs_id_name[attr_id],
            'value': ATTRS_SUB[attrs_id_name[attr_id]][0] * value_ratio
        })
    if 'single_attr' in item:
        item_std['attrs']['sgl'] = {
            'attr': item['single_attr'][0],
            'value': ATTRS_SGL[item['single_attr'][0]][0]
        }
    return item_std


def check_data_hdtr(data):
    """检查 JSON 数据是否为「御魂导出器」数据

    Args:
        data (list): JSON 数据

    Returns:
        bool: 合法返回 True
    """
    return data and isinstance(data, list) and data[0] == 'yuhun_ocr2.0'


def check_data_fluxxu(data):
    """检查 JSON 数据是否为「痒痒熊快照」数据

    Args:
        data (dict): JSON 数据

    Returns:
        bool: 合法返回 True
    """
    return (data and isinstance(data, dict)
            and 'data' in data and 'hero_equips' in data['data'])


def check_data_cbg(data):
    """检查 JSON 数据是否为藏宝阁数据

    Args:
        data (dict): JSON 数据

    Returns:
        bool: 合法返回 True
    """
    return (data and isinstance(data, dict)
            and 'equip' in data and 'equip_desc' in data['equip'])


def extract_data_hdtr(data):
    """从「御魂导出器」数据中抽取御魂数据集并封装为标准格式

    NGA@火电太热 的「御魂导出器」数据仅包含御魂基础信息，整个数据文件封装为 list：
        [
            'yuhun_ocr2.0',
            {}, {}, {}, ...
        ]
    可通过第一项验证来源。

    Args:
        data (list): 「御魂导出器」导出文件的 JSON 数据

    Returns:
        list: 返回封装为标准格式的御魂数据集
    """
    if not check_data_hdtr(data):
        return []
    return list(map(meta_hdtr2std, data[1:]))


def extract_data_fluxxu(data):
    """从「痒痒熊快照」数据中抽取御魂数据集并封装为标准格式

    相较于「御魂导出器」的简略数据，NGA@fluxxu 的「痒痒熊快照」的数据更详实，
    额外包含御魂获得时间、强化过程、弃置状态等信息。
    整个数据文件封装为 dict：
        {
            'data': {
                'hero_equips': [...],
                ...
            },
            'timestamp': ...,
            'version': "0.99.2"
        }
    囊括了帐号多方面数据，御魂数据在 hero_equips。

    Args:
        data (dict): 「痒痒熊快照」导出文件的 JSON 数据

    Returns:
        list: 返回封装为标准格式的御魂数据集
    """
    if not check_data_fluxxu(data):
        print(log('无法识别的「痒痒熊快照」数据内容', 'error'))
        return []
    return list(map(meta_fluxxu2std, data['data']['hero_equips']))


def extract_data_cbg(data):
    """从藏宝阁数据中抽取御魂数据集并封装为标准格式

    藏宝阁数据包含商品信息和游戏帐号本体信息，整个数据文件封装为 dict：
        {
            'status': ...,
            'equip': {
                'equip_desc': {
                    'inventory': {...},
                    ...
                },
                ...
            }
        }
    御魂数据在 inventory。

    Args:
        data (dict): 藏宝阁导出文件的 JSON 数据

    Returns:
        list: 返回封装为标准格式的御魂数据集
    """
    if not check_data_cbg(data):
        print(log('无法识别的藏宝阁数据内容', 'error'))
        return []
    data_game = json.loads(
        data['equip']['equip_desc']
    )  # 非 dict，而是 str
    data_yuhun = list(
        data_game['inventory'].values()
    )  # 非 list，而是以御魂 ID 为 key 的 dict
    return list(map(meta_cbg2std, data_yuhun))


def pick_dwarf_hdtr(data, data_f):
    """从「御魂导出器」数据检出低收益御魂
    
    Args:
        data (list): 「御魂导出器」导出文件的 JSON 数据
        data_f (str): 「御魂导出器」导出文件的路径
    """
    data_yuhun = extract_data_hdtr(data)
    if not data_yuhun:
        print(log('无法识别的「御魂导出器」数据内容', 'error'))
        return
    print(log('已检测到数据文件来自「御魂导出器」', 'info'))
    out_s, out_r = [], []  # 检出结果集（源格式、标准格式）
    for i, item in enumerate(data_yuhun):
        if not dwarf(item)['result']:  # 跳过非低收益御魂
            continue
        out_s.append(data[i + 1])
        t = translate(item, with_up=True)
        out_r.append(t)
        if not run_as_exe():  # 非 EXE 运行不输出进度
            continue
        print(log('已检出 %d 颗低收益御魂：%s%s' % (
            len(out_r), t.split('\n', 1)[0], ' ' * 7
        ), 'info'), end='\r')
        time.sleep(0.016)
    print(log('已检出 %d 颗低收益御魂%s' % (len(out_r), ' '*19), 'info'))
    if not out_r:  # 未检出御魂则不导出结果
        return
    pe = path.splitext(data_f)
    o = DWARF_FILE % pe
    with open(o, 'w', encoding='utf-8') as f:  # 按源格式导出
        data_out = [data[0]] + out_s
        json.dump(data_out, f)
        print(log('已将结果导出 \'%s\'' % path.basename(o), 'info'))
    o = DWARF_FILE % (pe[0], '.txt')
    with open(o, 'w', encoding='utf-8') as f:  # 可读化导出
        f.write('\n\n'.join(sorted(out_r, key=out_key)))
        print(log('已将结果导出 \'%s\'' % path.basename(o), 'info'))
    input(log('输入任意字符于此展开全部结果：', 'input'))
    print('\n' + '\n\n'.join(sorted(out_r, key=out_key)) + '\n')


def pick_dwarf_fluxxu(data, data_f):
    """从「痒痒熊快照」数据检出低收益御魂
    
    Args:
        data (dict): 「痒痒熊快照」导出文件的 JSON 数据
        data_f (str): 「痒痒熊快照」导出文件的路径
    """
    data_yuhun = extract_data_fluxxu(data)
    if not data_yuhun:
        print(log('无法识别的「痒痒熊快照」数据内容', 'error'))
        return
    print(log('已检测到数据文件来自「痒痒熊快照」', 'info'))
    out_s, out_r = [], []  # 检出结果集（源格式、标准格式）
    for i, item in enumerate(data_yuhun):
        if not dwarf(item)['result']:  # 跳过非低收益御魂
            continue
        out_s.append(data['data']['hero_equips'][i])
        t = translate(item, with_up=True)
        out_r.append(t)
        if not run_as_exe():  # 非 EXE 运行不输出进度
            continue
        print(log('已检出 %d 颗低收益御魂：%s%s' % (
            len(out_r), t.split('\n', 1)[0], ' ' * 7
        ), 'info'), end='\r')
        time.sleep(0.016)
    print(log('已检出 %d 颗低收益御魂%s' % (len(out_r), ' ' * 19), 'info'))
    if not out_r:  # 未检出御魂则不导出结果
        return
    pe = path.splitext(data_f)
    o = DWARF_FILE % pe
    with open(o, 'w', encoding='utf-8') as f:  # 按源格式导出
        data_out = copy.deepcopy(data)
        data_out['data']['hero_equips'] = out_s
        json.dump(data_out, f)
        print(log('已将结果导出 \'%s\'' % path.basename(o), 'info'))
    o = DWARF_FILE % (pe[0], '.txt')
    with open(o, 'w', encoding='utf-8') as f:  # 可读化导出
        f.write('\n\n'.join(sorted(out_r, key=out_key)))
        print(log('已将结果导出 \'%s\'' % path.basename(o), 'info'))
    input(log('输入任意字符于此展开全部结果：', 'input'))
    print('\n' + '\n\n'.join(sorted(out_r, key=out_key)) + '\n')


def pick_dwarf_cbg(data, data_f):
    """从藏宝阁数据检出低收益御魂

    Args:
        data (dict): 藏宝阁导出文件的 JSON 数据
        data_f (str): 藏宝阁导出文件的路径
    """
    data_yuhun = extract_data_cbg(data)
    if not data_yuhun:
        print(log('无法识别的藏宝阁数据内容', 'error'))
        return
    print(log('已检测到数据文件来自藏宝阁', 'info'))
    data_game = json.loads(data['equip']['equip_desc'])
    out_s, out_r = {}, []  # 检出结果集（源格式、标准格式）
    for i, item in enumerate(data_yuhun):
        if not dwarf(item)['result']:  # 跳过非低收益御魂
            continue
        out_s[item['id']] = data_game['inventory'][item['id']]
        t = translate(item, with_up=True)
        out_r.append(t)
        if not run_as_exe():  # 非 EXE 运行不输出进度
            continue
        print(log('已检出 %d 颗低收益御魂：%s%s' % (
            len(out_r), t.split('\n', 1)[0], ' ' * 7
        ), 'info'), end='\r')
        time.sleep(0.016)
    print(log('已检出 %d 颗低收益御魂%s' % (len(out_r), ' ' * 19), 'info'))
    if not out_r:  # 未检出御魂则不导出结果
        return
    pe = path.splitext(data_f)
    o = DWARF_FILE % pe
    with open(o, 'w', encoding='utf-8') as f:  # 按源格式导出
        data_out = copy.deepcopy(data)
        data_game['inventory'] = out_s
        data_out['equip']['equip_desc'] = json.dumps(data_game)
        json.dump(data_out, f)
        print(log('已将结果导出 \'%s\'' % path.basename(o), 'info'))
    o = DWARF_FILE % (pe[0], '.txt')
    with open(o, 'w', encoding='utf-8') as f:  # 可读化导出
        f.write('\n\n'.join(sorted(out_r, key=out_key)))
        print(log('已将结果导出 \'%s\'' % path.basename(o), 'info'))
    input(log('输入任意字符于此展开全部结果：', 'input'))
    print('\n' + '\n\n'.join(sorted(out_r, key=out_key)) + '\n')


def parse_rule(path_or_url, dir_prior, dir_prog):
    """解析规则文件
    
    优先从数据文件目录查找，其次本程序目录。
    解析结果不作返回，储存在全局变量 RULES。
    RULES 例：
        {
            '火灵-5-攻击加成': [{
                'attrs': ('攻击加成', '速度'),
                'score': 5
            }]
        }
    规则文件：
        多条规则之间以换行符分隔，单条格式：
            [御魂]-[位置]-[主属性]：[有效副属性]，[分数线]
        注：
            御魂：御魂类型名
            位置：1~6，可并写（未指定则为全部）
            主属性：（未指定则为该位置的全部）
            有效副属性：（多个用“、”隔开）
            分数线：1~15，有效属性加点次数界限，低于则被视为低收益
        
        例：
            破势-24-攻击加成：攻击加成、速度、暴击、暴击伤害，5
            蚌精-135：速度、效果命中，4
            荒骷髅-135：攻击加成、速度、暴击、暴击伤害，8
            招财猫：生命加成、防御加成、攻击加成、速度、暴击、暴击伤害、效果命中、效果抵抗，5
        
        同一御魂类型可设定多条规则（不止细分的 1+4+1+5+1+5=17 条），如：
            蚌精-135：速度、效果命中，5
            蚌精-135：生命加成、速度、暴击、暴击伤害，5
        
        未设定规则（没写）的御魂类型不会参与筛选。若想粗筛，可为其配置这些默认规则：
            [御魂]-[位置]-[主属性]：生命加成、防御加成、攻击加成、速度、暴击、暴击伤害、效果命中、效果抵抗，5
            [御魂]-[位置]-[主属性]：生命加成，4
            [御魂]-[位置]-[主属性]：防御加成，4
            [御魂]-[位置]-[主属性]：攻击加成，4
            [御魂]-[位置]-[主属性]：速度，4
            [御魂]-[位置]-[主属性]：暴击，4
            [御魂]-[位置]-[主属性]：暴击伤害，4
            [御魂]-[位置]-[主属性]：效果命中，4
            [御魂]-[位置]-[主属性]：效果抵抗，4
        或简写为：
            [御魂]-[位置]-[主属性]：默认
        已设定规则的御魂类型，若有遗漏，将自动补上默认规则。
        
        使用“#”开头可注释行，该行规则不会生效。
    
    Args:
        path_or_url (str): 指定本地规则文件路径或直链 URL（若未指定则自动在本地查找）
        dir_prior (str): 数据文件目录
        dir_prog (str): 本程序目录
    """
    print(log('数据文件目录 \'%s\'' % dir_prior, 'info'))
    print(log('本程序目录 \'%s\'' % dir_prog, 'info'))
    generate_def_rule(dir_prog)
    RULES.clear()
    kinds_ruled = {kind: False for kind in KINDS}
    data_rules = read_rule_data(path_or_url, dir_prior, dir_prog)
    for rule in filter(lambda x: x.strip() and not x.startswith('#'),
                       data_rules.split('\n')):
        m = re.match(r'(.+?)(?:-(\d+))?(?:-(.+?))?：(.+?)，(\d+)', rule)
        if m:
            kinds_ruled[m.group(1)] = True
            for pos in list(m.group(2) if m.group(2) else '123456'):
                for attr in ATTRS_POS[int(pos) - 1]:
                    if not m.group(3) or attr == m.group(3):
                        k = rule_key(m.group(1), int(pos), attr)
                        if k not in RULES:
                            RULES[k] = []
                        RULES[k].append({
                            'attrs': tuple(m.group(4).split('、')),
                            'score': int(m.group(5))
                        })
        else:
            m = re.match(r'(.+?)(?:-(\d+))?(?:-(.+?))?：默认', rule)
            if m:
                kinds_ruled[m.group(1)] = True
                for pos in list(m.group(2) if m.group(2) else '123456'):
                    for attr in ATTRS_POS[int(pos) - 1]:
                        if not m.group(3) or attr == m.group(3):
                            k = rule_key(m.group(1), int(pos), attr)
                            if k not in RULES:
                                RULES[k] = []
                            RULES[k] += def_rules()
            else:
                print(log('已跳过非法规则 \'%s\'' % rule, 'warn'))
    # 对已设定规则的御魂类型，漏掉的部分补上默认规则
    for kind in (kind for kind, ruled in kinds_ruled.items() if ruled):
        for pos, attrs in enumerate(ATTRS_POS):
            for attr in attrs:
                k = rule_key(kind, pos + 1, attr)
                if k not in RULES:
                    RULES[k] = def_rules()


def generate_def_rule(dir_prog):
    """生成默认规则文件
    
    在本程序目录创建默认规则文件，包含简略注释和默认规则。
    默认规则：
        [御魂]-[位置]-[主属性]：生命加成、防御加成、攻击加成、速度、暴击、暴击伤害、效果命中、效果抵抗，5
        [御魂]-[位置]-[主属性]：生命加成，4
        [御魂]-[位置]-[主属性]：防御加成，4
        [御魂]-[位置]-[主属性]：攻击加成，4
        [御魂]-[位置]-[主属性]：速度，4
        [御魂]-[位置]-[主属性]：暴击，4
        [御魂]-[位置]-[主属性]：暴击伤害，4
        [御魂]-[位置]-[主属性]：效果命中，4
        [御魂]-[位置]-[主属性]：效果抵抗，4
    
    Args:
        dir_prog (str): 本程序目录
    """
    rule_f = path.join(dir_prog, DEF_RULE_FILE + '.txt')
    if path.exists(rule_f):
        return
    print(log('本程序目录通用规则文件缺失，已创建 \'%s\'' %
              path.basename(rule_f), 'warn'))
    with open(rule_f, 'w', encoding='utf-8') as f:
        f.write('# %s for %s v%s\n# ' % (DEF_RULE_FILE, PROG, VER))
        f.write('\n# [御魂]-[位置]-[主属性]：[有效副属性]，[分数线]\n# ')
        f.write('\n#     [御魂]-[位置]-[主属性]：默认\n# 等同\n# ')
        for rule in def_rules():
            f.write('    [御魂]-[位置]-[主属性]：%s，%d\n# ' %
                    ('、'.join(rule['attrs']), rule['score']))
        for kind in KINDS:
            f.write('\n# %s\n%s：默认' % (kind, kind))


def read_rule_data(path_or_url, dir_prior, dir_prog):
    """读取规则文件数据

    若指定规则文件直链 URL，则读取网络数据；
    若指定的是规则文件本地路径，则直接读取；
    若均未指定，则优先从数据文件目录查找，其次本程序目录。
    规则文件基本命名定义在全局变量 DEF_RULE_FILE，可扩展字符。
    也就是说可以存在多个规则文件，但仅识别一个，除以上提到优先数据文件目录，
    若同一目录下有多份，按去后缀文件名降序排序后取第一个。
    如数据文件目录下有两份：
        pick_dwarf_rule.txt
        pick_dwarf_rule_nguaduot-200715.txt
    后者生效。
    
    Args:
        path_or_url (str): 指定本地规则文件路径或直链 URL（若未指定则自动在本地查找）
        dir_prior (str): 数据文件目录
        dir_prog (str): 本程序目录
    
    Returns:
        str: 规则文件内容
    """
    # 解析在线规则文件
    if path_or_url and path_or_url.startswith('http'):
        print(log('正在尝试解析在线规则文件... timeout: 10s \'%s\'' % path_or_url, 'info'))
        req = request.Request(url=path_or_url, headers={
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                           ' AppleWebKit/537.36 (KHTML, like Gecko)'
                           ' Chrome/84.0.4147.89 Safari/537.36')
        })
        data = request.urlopen(req, timeout=10).read()
        print(log('已解析并使用在线规则文件', 'info'))
        return data.decode('utf-8')
    # 查找本地规则文件
    if path_or_url and path.isfile(path_or_url):
        files = [path_or_url]
        print(log('已使用指定规则文件 \'%s\'' % path_or_url, 'info'))
    else:
        files = sorted(glob.glob(path.join(dir_prior, DEF_RULE_FILE + '*.txt')),
                       key=lambda x: path.splitext(x)[0], reverse=True)
        if len(files) > 0:
            print(log('已使用数据文件目录的首个规则文件 %s' %
                      list(map(lambda x: path.basename(x), files)), 'info'))
        else:
            files = sorted(
                glob.glob(path.join(dir_prog, DEF_RULE_FILE + '*.txt')),
                key=lambda x: path.splitext(x)[0], reverse=True
            )
            print(log('未在数据文件目录发现规则文件，将使用本程序目录的首个通用规则文件 %s' %
                      list(map(lambda x: path.basename(x), files)), 'info'))
    with open(files[0], 'r', encoding='utf-8') as f:
        return f.read()


def parse_args(args):
    try:
        opts, args = getopt.getopt(
            args,
            'hvr:d:',
            ['help', 'version', 'rule=', 'data=']
        )
    except getopt.GetoptError:
        opts, args = [('-h', '')], []
    data_file, rule_path_or_url, helped = '', '', False
    for opt, value in opts:
        if opt in ('-h', '--help'):
            print(COPYRIGHT)
            print(HELP)
            helped = True
        elif opt in ('-v', '--version'):
            print(VERSION)
            helped = True
        elif opt in ('-r', '--rule'):
            rule_path_or_url = value
        elif opt in ('-d', '--data'):
            data_file = value
    if not data_file and args:
        data_file = args[0]
    if not helped and not data_file:
        print(COPYRIGHT)
        print(HELP)
    return data_file, rule_path_or_url


def run_as_exe():
    """判断本程序运行环境

    判断本程序是否已被封装为 EXE 执行，若如此可实现一些特性，如控制台进度条效果。
    IDE 中执行原生 .py 一般无法实现此效果。

    Returns:
        bool: True 为 Windows EXE，False 视为原生 .py 脚本
    """
    return path.splitext(sys.argv[0])[1] == '.exe'


def log(content, level):
    """封装单行日志内容

    Args:
        content (str): 日志内容
        level (str): 日志等级 ['info', 'warn', 'error', 'input']

    Returns:
        str: 返回封装好的日志
    """
    # 在 Win10 上着色似乎不生效
    # log_prefix = {
    #     'info': '\033[32m[日志]\033[0m',  # green
    #     'warn': '\033[33m[警告]\033[0m',  # yellow
    #     'error': '\033[31m[出错]\033[0m',  # red
    #     'input': '\033[34m[输入]\033[0m'  # blue
    # }
    log_prefix = {
        'info': '[日志]',
        'warn': '[警告]',
        'error': '[出错]',
        'input': '[输入]'
    }
    return '{} {}'.format(log_prefix[level], content)


def main():
    if len(sys.argv) > 1:  # 通过命令行参数运行
        data_file, rule_path_or_url = parse_args(sys.argv[1:])
        if not data_file:  # 若无关键参数，不启动程序主体
            return
        print(COPYRIGHT)
        print(log('数据文件路径：%s' % data_file, 'info'))
    else:  # 直接运行（不带任何参数）
        print(COPYRIGHT)
        data_file = input(log('数据文件路径：', 'input')).strip('"\'')
        rule_path_or_url = input(
            log('规则文件路径或 URL（若省略即自动查找）：', 'input')
        ).strip('"\'')
    try:
        parse_rule(rule_path_or_url,
                   path.dirname(path.abspath(data_file)),
                   path.dirname(path.abspath(sys.argv[0])))
        with open(data_file, 'r', encoding='utf-8') as f:
            obj = json.loads(f.read())
            if check_data_hdtr(obj):  # 按「御魂导出器」数据处理
                pick_dwarf_hdtr(obj, data_file)
            elif check_data_fluxxu(obj):  # 按「痒痒熊快照」数据处理
                pick_dwarf_fluxxu(obj, data_file)
            elif check_data_cbg(obj):  # 按藏宝阁数据处理
                pick_dwarf_cbg(obj, data_file)
            else:
                print(log('无法识别数据文件内容', 'error'))
    except (FileNotFoundError, UnicodeDecodeError,
            json.decoder.JSONDecodeError) as e:
        print(log('非法数据文件或不存在', 'error'))
        print(repr(e))
    except Exception:
        print(log('未知错误，请将以下错误信息反馈给作者', 'error'))
        raise
    finally:
        if run_as_exe():  # 避免窗口一闪而逝
            os.system('pause')


if __name__ == '__main__':
    main()
