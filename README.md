# 人机协同A股智能投资决策系统

> 基于7年A股历史数据的本地化智能投资辅助工具，为个人投资者提供AI驱动的买卖建议

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 项目简介

这是一个本地桌面应用，通过AI模型对A股板块龙头股进行短中长期预测，为个人投资者提供买卖操作建议。系统采用人机协同模式——系统给出明确的建议和推理依据，最终决策权在用户手中。

**核心特点：**
- 🏠 **本地化**：所有数据存储在本地，保护隐私
- 🤖 **AI驱动**：基于7年历史数据的机器学习预测
- 📊 **三周期预测**：短期(1-5天)、中期(1-3个月)、长期(3个月+)
- 🎯 **板块聚焦**：自动识别各板块龙头股
- 💡 **可解释**：每个预测都提供推理依据

## 功能特性

### 数据管理
- **数据源**：akshare（免费开源）
- **历史数据**：7年A股历史行情
- **板块覆盖**：行业板块、概念板块
- **技术指标**：MA、MACD、KDJ、RSI、BOLL、OBV等
- **自动更新**：每日收盘后手动触发更新

### 预测功能
- **短期预测**：1-5天涨跌方向，技术指标主导
- **中期预测**：1-3个月趋势，趋势+技术面+基本面
- **长期预测**：3个月+价值，价值分析+行业周期
- **置信度**：0-100%的可信程度展示
- **推理依据**：提供可解释的预测理由

### 人机协同
- **系统建议**：明确的买入/卖出/持有信号
- **用户决策**：最终操作由用户自主决定
- **风险提示**：提示投资风险，仅供参考

## 快速开始

### 环境要求

- Python 3.10+
- 4GB+ 内存（建议8GB）
- 2GB+ 可用磁盘空间
- 稳定网络连接（用于数据更新）

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/wealth.git
cd wealth

# 2. 创建虚拟环境（推荐）
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 或使用国内镜像加速
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 5. 启动应用
streamlit run app.py
```

应用将在浏览器中打开，默认地址：`http://localhost:8501`

## 使用指南

### 首次使用

1. **初始化数据库**：进入"数据更新"页面，点击"初始化数据库"
2. **更新板块数据**：点击"更新板块数据"获取板块列表和龙头股
3. **更新股票数据**：点击"更新股票数据"获取历史行情
4. **更新技术指标**：点击"更新技术指标"计算各类指标

### 日常使用

1. **板块总览**：
   - 选择关注的板块
   - 查看板块龙头股列表
   - 点击股票名称查看详情

2. **股票详情**：
   - 查看基本信息、历史价格
   - 选择时间范围查看K线图
   - 切换技术指标分析
   - 查看预测建议（Stage 5）

3. **数据更新**：
   - 每日收盘后更新数据
   - 检查数据库状态

## 项目架构

```
wealth/
├── app.py                    # Streamlit主应用
├── requirements.txt          # Python依赖
├── PROGRESS.md               # 项目进度
├── docs/                     # 文档目录
├── data/                     # 数据层
│   ├── database.py          # 数据库管理
│   ├── fetcher.py           # 数据获取(akshare)
│   ├── storage.py           # 数据存储(SQLite)
│   └── models.py            # 数据模型
├── analysis/                 # 分析层
│   ├── indicators.py        # 技术指标计算
│   ├── sector.py            # 板块分析
│   └── features.py          # 特征工程
├── prediction/               # 预测层
│   ├── base.py              # 预测基类
│   ├── short_term.py        # 短期预测
│   ├── medium_term.py       # 中期预测
│   ├── long_term.py         # 长期预测
│   ├── ensemble.py          # 集成预测
│   └── trainer.py           # 模型训练
├── ui/                       # 界面层
│   ├── layout.py            # 布局组件
│   ├── charts.py            # 图表组件
│   └── pages.py             # 页面组件
└── utils/                    # 工具模块
    ├── config.py            # 配置管理
    ├── logger.py            # 日志工具
    └── helpers.py           # 辅助函数
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 界面 | Streamlit, Plotly |
| 后端 | Python 3.10+ |
| 数据处理 | pandas, numpy |
| 机器学习 | scikit-learn |
| 数据获取 | akshare |
| 数据存储 | SQLite |
| 技术指标 | pandas-ta |

## 当前进度

- ✅ Stage 1: 项目初始化
- ✅ Stage 2: 数据层实现
- ✅ Stage 3: 预测层实现
- ✅ Stage 4: 基础UI实现
- ⏳ Stage 5: 详情页实现
- ⏳ Stage 6: 集成测试和优化

详见 [PROGRESS.md](PROGRESS.md)

## 最新更新

### Stage 4 基础UI实现 (v0.4.0)

- ✅ 布局组件：footer、render_card、颜色辅助函数
- ✅ 图表组件：K线图、成交量图、技术指标图（MACD/RSI/KDJ/BOLL）
- ✅ 首页：板块选择、龙头股列表、点击导航
- ✅ 股票详情：历史数据、图表展示、时间范围筛选、预测占位符
- ✅ 数据更新：板块数据、技术指标更新功能

**代码质量改进**：
- 数据库连接资源管理（try-finally）
- 价格计算使用前日收盘价
- 完整的类型提示和文档

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 免责声明

⚠️ **重要提示**：
- 本系统提供的预测和建议仅供参考，不构成投资建议
- 股票投资有风险，入市需谨慎
- 系统预测基于历史数据，不代表未来表现
- 用户应根据自身情况独立判断，投资风险自担

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目主页：[GitHub](https://github.com/yourusername/wealth)
- 问题反馈：[Issues](https://github.com/yourusername/wealth/issues)

---

**人机协同A股智能投资决策系统 v0.4.0** | 预测仅供参考，投资风险自担