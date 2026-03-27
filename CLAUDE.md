# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**项目名称**: 人机协同A股智能投资决策系统

**技术栈**: Python + Streamlit + akshare + scikit-learn + SQLite

**目标**: 基于7年A股历史数据，对板块龙头股进行短中长期预测，为个人投资者提供买卖建议

**当前阶段**: Stage 4 基础UI实现进行中 (4/6任务完成)

---

## 重要工作流程规则

### README.md 更新规则 ⚠️ **必须遵守**

**每次项目有变更时，同时更新 README.md 文件！**

**触发条件**：
- 任何阶段完成时
- 重大功能实现后
- 版本号变化时
- 架构结构调整后
- 里程碑达成时

**更新内容**：
- 当前进度 (Stage状态和任务完成情况)
- 功能特性变化
- 项目架构调整
- 版本号更新
- Commits记录

**检查清单**：
- [ ] 项目架构是否有变化
- [ ] 当前进度是否需要更新
- [ ] 功能列表是否有增减
- [ ] 版本号是否需要调整

---

## Repository Status

**已完成的阶段**：
- ✅ Stage 1: 项目初始化
- ✅ Stage 2: 数据层实现
- ✅ Stage 3: 预测层实现

**进行中的阶段**：
- 🔄 Stage 4: 基础UI实现 (4/6任务完成)

**未开始的阶段**：
- ⏳ Stage 5: 详情页实现
- ⏳ Stage 6: 集成测试和优化

---

## Build Commands

```bash
# 安装依赖
pip install -r requirements.txt

# 启动Streamlit应用
streamlit run app.py

# 使用国内镜像加速安装
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## Project Architecture

### 目录结构
```
wealth/
├── app.py                       # Streamlit主应用
├── requirements.txt             # Python依赖
├── PROGRESS.md                  # 项目进度和经验教训
├── docs/                        # 文档目录
│   ├── PRD.md                   # 产品需求文档
│   ├── APP_FLOW.md              # 应用流程文档
│   ├── TECH_STACK.md            # 技术栈文档
│   ├── FRONTEND_GUIDELINES.md   # 前端设计指南
│   ├── BACKEND_STRUCTURE.md     # 后端结构文档
│   └── IMPLEMENTATION_PLAN.md   # 实现计划
├── data/                        # 数据层模块
│   ├── database.py              # 数据库初始化和连接管理
│   ├── fetcher.py               # akshare数据获取
│   ├── storage.py               # SQLite存储操作
│   └── models.py                # 数据模型定义
├── analysis/                    # 分析层模块
│   ├── indicators.py            # 技术指标计算
│   ├── sector.py                # 板块识别和龙头筛选
│   └── features.py              # 特征工程
├── prediction/                  # 预测层模块
│   ├── base.py                  # 预测模型基类
│   ├── short_term.py            # 短期预测模型
│   ├── medium_term.py           # 中期预测模型
│   ├── long_term.py             # 长期预测模型
│   ├── ensemble.py              # 集成预测
│   └── trainer.py               # 模型训练
├── ui/                          # 界面层模块
│   ├── pages.py                 # 各页面组件
│   ├── components.py            # 可复用组件
│   ├── charts.py                # 图表组件
│   └── layout.py                # 布局组件
├── utils/                       # 工具模块
│   ├── config.py                # 配置管理
│   ├── logger.py                # 日志工具
│   └── helpers.py               # 辅助函数
├── models/                      # 预训练模型目录
├── data/                        # 数据文件目录
│   └── stock_data.db            # SQLite数据库
└── logs/                        # 日志目录
```

### 分层架构
```
前端层 (UI Layer - Streamlit)
         ↓ API调用
业务逻辑层 (Business Layer)
    板块分析 | 特征工程 | 预测集成
         ↓
服务层 (Service Layer)
  数据获取 | 数据存储 | 预测服务
         ↓
数据层 (Data Layer)
  akshare | SQLite | 模型文件
```

---

## Core Requirements

### 三周期预测
- **短期 (1-5天)**: 技术指标主导，量价关系
- **中期 (1-3个月)**: 趋势判断 + 技术面 + 基本面
- **长期 (3个月以上)**: 价值分析 + 行业周期

### 综合建议权重
- 短期: 30%
- 中期: 40%
- 长期: 30%

### 人机协同模式
- 系统给出明确的买入/卖出/持有建议
- 提供详细的预测结果和推理依据
- 用户自主决策是否执行

---

## 重要约定

### 颜色规范（中国股市习惯）
- 红色: 上涨、买入 (#ef4444)
- 绿色: 下跌、卖出 (#22c55e)
- 灰色: 持有、中性 (#6b7280)

### 日期格式
- 数据库: YYYY-MM-DD
- 显示: YYYY-MM-DD

### 数字格式
- 股票价格: 保留2位小数
- 市值: 使用"亿"为单位，保留1位小数
- 涨跌幅: 百分比，保留1位小数

---

## Development Workflow

### 实现阶段
1. 阶段1: 项目初始化（2天）
2. 阶段2: 数据层实现（3天）
3. 阶段3: 预测层实现（3天）
4. 阶段4: 基础UI实现（2天）
5. 阶段5: 详情页实现（2天）
6. 阶段6: 集成测试和优化（2天）

详见 IMPLEMENTATION_PLAN.md

---

## Key Design Decisions

1. **数据源选择**: akshare（免费，数据全面）
2. **界面框架**: Streamlit（开发快速，可本地运行）
3. **预测模型**: Random Forest（可解释性强，适合快速实现）
4. **数据库**: SQLite（轻量级，满足本地存储需求）

---

## Known Risks

- akshare API可能变化
- 数据获取可能受网络影响
- 基础模型准确率有待验证
- Streamlit处理大量数据时的性能

详见 PROGRESS.md

---

## Documentation

详细文档位于 docs/ 目录：
- PRD.md - 完整的功能需求
- APP_FLOW.md - 详细的操作和数据流程
- TECH_STACK.md - 技术选型和依赖
- FRONTEND_GUIDELINES.md - 界面设计和交互
- BACKEND_STRUCTURE.md - 后端架构和API
- IMPLEMENTATION_PLAN.md - 实现计划和任务分解