# 御魂检出器

[![Release](https://img.shields.io/badge/Release-v3.0-brightgreen.svg)](https://github.com/nguaduot/yys-pick-dwarf)
[![Download](https://img.shields.io/badge/Download-EXE-brightgreen.svg)](yys-pick-dwarf.exe)

### 这是个啥，我用得上吗？

[**阴阳师**](https://yys.163.com/)游戏衍生小工具，用于检出六星满级低收益御魂（由**御魂分数**决定，即有效属性加点次数）。

如果你有在使用御魂导出器这类工具，并且游戏里好的差的满级御魂较多又纠结于弃置( 比如我)，那么这个小工具应该可以派上用场。

低收益御魂如：
```
[陆|6] 火灵 +15
攻击加成 55%
防御 +4
攻击 +96 ...
生命加成 +3%
速度 +9 ..
```

### 何为御魂分数？

副属性参与评分，每条初始副属性和每次属性加点（升满 15 级加点 5 次）均视为`1`分，最高`9`分（首领御魂算上固有属性则分数更高）。而并非每`1`分都符合预期，通常先选定有效属性再评分。例：选定**攻击加成**、**速度**、**暴击**、**暴击伤害**为有效属性来评定以下这颗御魂，当有`4`分。
```
[肆|6] 破势 +15
攻击加成 55%
攻击 +74
速度 +2
暴击伤害 +11% ..
效果抵抗 +7% .
```

在规则`破势-24-攻击加成：攻击加成、速度、暴击、暴击伤害，5`判定下，这颗御魂没救了。若一颗御魂评分在预期分数以下，则可视为低收益御魂了。

> 御魂分数的设定来自 NGA@YYSKernel 大佬的[这篇帖子](https://bbs.nga.cn/read.php?tid=15818432&fav=38632a10)，特此感谢。

### 规则文件

有效属性和御魂分数线由规则文件`pick_dwarf_rule.txt`决定，可自定义。

```
# pick_dwarf_rule for yys-pick-dwarf v3.0
#
# 多条规则之间以换行符分隔，单条格式：
#     [御魂]-[位置]-[主属性]：[有效副属性]，[分数线]
# 注：
#     御魂：御魂类型名
#     位置：1~6，可并写（未指定则为全部）
#     主属性：（未指定则为该位置的全部）
#     有效副属性：（多个用“、”隔开）
#     分数线：1~15，有效属性加点次数界限，低于则被视为低收益
#
# 例：
#     破势-24-攻击加成：攻击加成、速度、暴击、暴击伤害，5
#     蚌精-135：速度、效果命中，4
#     荒骷髅-135：攻击加成、速度、暴击、暴击伤害，8
#     招财猫：生命加成、防御加成、攻击加成、速度、暴击、暴击伤害、效果命中、效果抵抗，5
#
# 同一御魂类型可设定多条规则（不止细分的 1+4+1+5+1+5=17 条），如：
#     蚌精-135：速度、效果命中，5
#     蚌精-135：生命加成、速度、暴击、暴击伤害，5
#
# 未设定规则（没写）的御魂类型不会参与筛选。若想粗筛，可为其配置这些默认规则：
#     [御魂]-[位置]-[主属性]：生命加成、防御加成、攻击加成、速度、暴击、暴击伤害、效果命中、效果抵抗，5
#     [御魂]-[位置]-[主属性]：生命加成，4
#     [御魂]-[位置]-[主属性]：防御加成，4
#     [御魂]-[位置]-[主属性]：攻击加成，4
#     [御魂]-[位置]-[主属性]：速度，4
#     [御魂]-[位置]-[主属性]：暴击，4
#     [御魂]-[位置]-[主属性]：暴击伤害，4
#     [御魂]-[位置]-[主属性]：效果命中，4
#     [御魂]-[位置]-[主属性]：效果抵抗，4
# 或简写为：
#     [御魂]-[位置]-[主属性]：默认
# 已设定规则的御魂类型，若有遗漏，将自动补上默认规则。
#
# 使用“#”开头可注释行，该行规则不会生效。
# 
# 破势
破势-135：生命加成、速度、暴击、暴击伤害，5
破势-135：攻击加成、速度、暴击、暴击伤害，5
破势-135：暴击，4
破势-246-生命加成：生命加成、速度、暴击、暴击伤害，5
破势-24-攻击加成：攻击加成、速度、暴击、暴击伤害，4
破势-2-速度：生命加成、速度、暴击、暴击伤害，5
破势-2-速度：攻击加成、速度、暴击、暴击伤害，4
破势-4-效果抵抗：速度、效果抵抗，5
破势-6-暴击：生命加成、速度、暴击、暴击伤害，5
破势-6-暴击：攻击加成、速度、暴击、暴击伤害，4
破势-6-暴击伤害：生命加成、速度、暴击、暴击伤害，5
破势-6-暴击伤害：攻击加成、速度、暴击、暴击伤害，4
破势：速度、效果命中，5
破势：速度，4
# 更多略……
```

此处提供一套根据我的御魂整理策略转化的规则文件：[pick_dwarf_rule.txt](pick_dwarf_rule_nguaduot_200715.txt)

### 输入

「御魂检出器」的本质为处理其他小工具导出的数据文本，并非与[阴阳师桌面版](https://yys.163.com/zmb/)有直接关联，也不会影响游戏运行，请放心使用。

+ 支持读取 NGA@火电太热 大佬的[**御魂导出器**](https://nga.178.com/read.php?tid=15220479)导出的 JSON 数据文件
+ 支持读取 NGA@fluxxu 大佬的[**痒痒熊快照**](https://nga.178.com/read.php?tid=16557282)导出的 JSON 数据文件
+ 支持读取藏宝阁数据

### 发布 & 使用

「御魂检出器」同时发布到 NGA 论坛阴阳师板块：[https://bbs.nga.cn/read.php?tid=20363227&_ff=538](https://bbs.nga.cn/read.php?tid=20363227&_ff=538)，有疑问可以评论交流。

该工具以 Python3 编写，

+ 有 Python3 环境

  可直接下载 [pick_dwarf.py](pick_dwarf.py) 运行

+ 无 Python3 环境但有 Windows PC

  可下载`pick_dwarf.py`打包生成的 [yys-pick-dwarf.exe](yys-pick-dwarf.exe)，将**御魂导出器**或**痒痒熊快照**导出的数据文件拖到该 EXE 上即可，或双击运行后手动输入数据文件路径。

+ 都没有

  也能行，下载 [pick_dwarf.py](pick_dwarf.py) 到 [Repl.it](https://repl.it/repls/BlissfulOrganicDeclaration) 中在线运行，同时将数据文件传上去即可进行解析。

筛选结果会在控制台输出，同时在源数据文件目录下保存两份文件（均缀以`*-dwarf`），一份便于直接查看的 TXT 可读文本，另一份与源数据文件格式相同，可作后续使用，比如导入[**御魂Hub**](https://yuhunhub.tql8.com/)查看。

### 作者

> “不会在记事本用 Python 写小工具的程序猿的不是好痒痒鼠！”
>
> —「初心未改」区@**南瓜多糖**

痒痒鼠相关问题欢迎来找我讨论，代码改进或漏洞也欢迎一起交流。

![本PVE玩家有一个梦想：全图鉴六星](https://i.loli.net/2020/02/11/QgnHXcG4jZMBzp5.png)

### 更新日志

v3.0.200811
* NGA@高冷少年w 大佬的御魂 Hub 最近上线的「奉纳」功能太赞了！可以按规则筛选未强化的御魂。但不会筛选强化过的御魂，看来本鼠这个筛选满级御魂的小工具仍有用武之地，所以又掏出来更新一波
+ 程序代码重构，可独立运行，也可做为模块另作他用，并追加大量注释（300+ ==>> 1200+ 行）
+ 未设定规则的御魂类型将不再参与筛选，便于快速检出某一类或几类的低收益御魂（如规则文件中只添加“破势”的规则，筛选结果中将只出现低收益“破势”）
+ 可在数据文件目录创建规则文件（适用于当前目录下所有数据文件），其将优先于本程序目录的通用规则文件
+ 更新默认规则（稍放宽）；同时更新本鼠在用的规则文件（更细致了）
+ 输出结果中御魂“翻译”微调：
  + 头部：“[陆]火灵 6/15” ==>> “[陆|6] 火灵 +15”
  + 加点：小属性加点不再隐藏；初始值的 1 点不再显示。便于更清晰看出强化加点分布（至多 5 点）
+ 文件命名微调：“-” ==>> “_”，请留意因此造成的旧规则文件识别问题
+ 控制台不再默认输出结果，便于更清晰看到关键日志（结果导出不受影响）
+ 支持更多命令行参数“-h -v -r -d”，可一并设定数据文件和规则文件，详细请执行“-h”查看帮助
+ 规则文件支持读取文件直链 ULR
+ 不再检查弃置状态（即弃置御魂也会参与筛选）
+ 支持读取藏宝阁数据文件
+ 支持判定低星满级御魂

v2.0.200212
+ 重构：调整低收益御魂判定逻辑，依据为御魂分数（何为御魂分数，可以参考 NGA@YYSKernel 大佬的[这篇帖子](https://bbs.nga.cn/read.php?tid=15818432&fav=38632a10)）
+ 增设规则文件，可为每颗御魂设定有效属性和分数线（提供一套根据我的御魂整理策略转化的规则文件）
+ 补充新御魂数据：兵主部、青女房、涂佛、飞缘魔
+ 异常捕获，若出现未知错误请将信息反馈给作者

v1.4.191022
+ 支持读取「痒痒熊快照」的数据文件
+ 新增可调参数：有效属性加点次数过滤值
+ 生成的检出御魂文本文件内容经过排序（按位置、类型）
+ 修复：部分低收益御魂漏输出（有效0次加点）

v1.0.191016
+ 第一版发布
