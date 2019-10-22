# 御魂检出器

[![Release](https://img.shields.io/badge/Release-v1.4-brightgreen.svg)]()
[![Download](https://img.shields.io/badge/Download-EXE-brightgreen.svg)](pick-dwarf-1.4.exe)

检出六星满级低收益御魂（副属性满4条的基础上加点次数不超过3）

低收益如：
```
[陆]火灵 6/15
攻击加成 55%
防御 +4 
攻击 +96 
生命加成 +3% 
速度 +9 ..
```

控制台输出结果，同时保存到文件（同源文件目录 `*-dwarf`）

+ 支持读取 NGA@火电太热 的[**御魂导出器**](https://nga.178.com/read.php?tid=15220479)导出的JSON数据文件
+ 支持读取 NGA@fluxxu 的[**痒痒熊快照**](https://nga.178.com/read.php?tid=16557282)导出的JSON数据文件

该工具同时发布到NGA论坛阴阳师板块：[https://nga.178.com/read.php?tid=18917735&_ff=538](https://nga.178.com/read.php?tid=18917735&_ff=538)

### 使用

+ 有 Python3 环境

  可直接下载 [pick-dwarf.py](pick-dwarf-1.4.py) 运行

+ 无 Python3 环境但有 Windows PC

  下载 [pick-dwarf.exe](pick-dwarf-1.4.exe)，将**御魂导出器**导出的数据文件拖到该EXE上即可，或双击运行后手动输入数据文件路径。

### 作者

「初心未改」区@**南瓜多糖**，痒痒鼠相关问题欢迎来找我讨论，代码改进或漏洞也欢迎一起交流。

![本PVE玩家有一个梦想：全图鉴六星](https://ws1.sinaimg.cn/large/007vdiFCgy1g8715z2dh8j30eo03pq3l.jpg)

### 更新日志

v1.4.191022
+ 支持读取「痒痒熊快照」的数据文件
+ 新增可调参数：有效属性加点次数过滤值
+ 生成的检出御魂文本文件内容经过排序（按位置、类型）
+ 修复：部分低收益御魂漏输出（有效0次加点）

v1.0.191016
+ 第一版发布
