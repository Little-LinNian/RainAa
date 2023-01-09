<div align="center">

# RainAa

_Raining?_

[![GitHub](https://img.shields.io/github/license/Little-LinNian/RainAa)](https://www.gnu.org/licenses/agpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Python version: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)

</div>

## 目录

* [目录](#目录)
  * [项目结构](#项目结构)
  * [许可证](#许可证)
  * [鸣谢](#鸣谢)

## 项目结构

```
* 为启动后生成
RainAa
├───kayaku 动静态配置文件中心
│       kayaku.jsonc 主配置 *
│       kayaku.schema.json 配置行为 * 
│
├───module 模块
│   │   balance.py
│   │   fm.py
│   │   helper.py
│   │   hsoer.py
│   │   mc_query.py
│   │   mm.py
│   │   sv.py
│   │   tasks.py
│   │   __init__.py
│
├───rainaa 核心组件
│   │   all.py 载入所有模块
│   │   config.py 配置管理
│   │   perm.py 权限管理
│   │   services.py 服务管理
│   │
│   ├───tools
│   │   │   alc_sender.py Alconna 消息发送工具
│   │   │   strings.py 字符串工具配套 text2image
│   │   │   text2image.py 图片转文字工具
│
└───static 静态资源
    └───font 字体
            sarasa-mono-sc-semibold.ttf


```

## 许可证

```
    Copyright (C) 2022 linnian

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

## 鸣谢

### 框架

* [mirai](https://github.com/mamoe/mirai), 高效率 QQ 机器人框架 / High-performance bot framework for Tencent QQ
* [mirai-api-http](https://github.com/project-mirai/mirai-api-http), Mirai HTTP API (console) plugin
* [Graia Ariadne](https://github.com/GraiaProject/Ariadne), 一个优雅且完备的 Python QQ 自动化框架。基于 Mirai API HTTP v2。
