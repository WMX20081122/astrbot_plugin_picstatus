# AstrBot Plugin: PicStatus

以精美的卡片图片形式展示 AstrBot 运行设备的系统状态。

## 移植说明

本插件移植自 [nonebot-plugin-picstatus](https://github.com/yuexps/nonebot-plugin-picstatus)，原作者：**yuexps**。感谢原作者的出色工作！

## 功能

- CPU 使用率、型号、频率、核心数
- 内存（RAM）使用率与详情
- SWAP 交换分区信息
- 磁盘分区使用率与 IO 速度
- 网络流量监控（上传/下载速度）
- 网络连通性测试
- 进程占用排行
- 系统运行时间、Bot 运行时间
- 精美卡片式图片输出

## 安装

### 前置要求

首次使用前需要安装 Playwright 浏览器：

```bash
pip install playwright
playwright install chromium
```

### 方式一：WebUI 安装（推荐）

1. 打开 AstrBot 管理面板
2. 进入「插件」页面
3. 点击「安装插件」，选择本地 ZIP 文件
4. 选择 `astrbot_plugin_picstatus.zip` 上传安装
5. 重启 AstrBot

### 方式二：手动安装

```bash
cd <AstrBot目录>/data/plugins
unzip astrbot_plugin_picstatus.zip
# 重启 AstrBot
```

## 使用

发送指令 `状态` 或 `status` 即可获取系统状态图片。

## 配置

本版本为简化版，**不包含 WebUI 配置面板**。如需修改配置，请直接编辑 `config.py` 文件中的默认值。

## 鸣谢

- [nonebot-plugin-picstatus](https://github.com/yuexps/nonebot-plugin-picstatus) 原版插件作者：**yuexps**
