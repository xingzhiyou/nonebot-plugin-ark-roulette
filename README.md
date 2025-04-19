# 明日方舟干员插件

## 项目简介
这是一个基于 [NoneBot](https://github.com/nonebot/nonebot2) 的插件，用于明日方舟干员的筛选、随机选择和数据更新功能。

## 功能
- **筛选干员**：根据关键词筛选符合条件的干员。
- **随机选择干员**：从筛选结果中随机选择指定数量的干员。
- **更新数据**：从远程数据源更新干员数据。

## 安装
1. 确保已安装 Python 3.11。
2. 使用以下命令安装：
   ```bash
   pip install nonebot-plugin-ark-roulette
   ```

## 使用方法
### 筛选干员
使用 `/筛选 <关键词1> <关键词2> ...` 命令筛选干员。例如：
```bash
/筛选 六星 狙击 男
```

### 随机选择干员
使用 `/随机选择 <数量>` 命令从筛选结果中随机选择干员。例如：
```bash
/随机选择 3
```

### 更新数据
使用 `/更新数据` 命令更新干员数据：
```bash
/更新数据
```

## 许可证
本项目基于 [MIT License](./LICENSE) 许可。

