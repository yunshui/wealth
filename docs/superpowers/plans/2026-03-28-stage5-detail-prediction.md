# Stage 5 Detail Page Prediction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement prediction display on stock detail page with short/medium/long-term forecasts, ensemble recommendation, and historical review

**Architecture:**
- Integrate EnsemblePredictor from prediction/ensemble.py into UI
- Create prediction display components in ui/prediction.py
- Modify ui/pages.py to show predictions instead of placeholder
- Add history review page with accuracy statistics

**Tech Stack:** Streamlit, pandas, numpy, existing prediction modules

---

## File Structure

### Files to Create:
- `ui/prediction.py` - Prediction display components (render_prediction_card, render_ensemble_card)

### Files to Modify:
- `ui/pages.py` - Replace placeholder with actual prediction display, add show_history page
- `app.py` - Add history page to sidebar navigation

---

## Task 1: Create Prediction Display Components

**Files:**
- Create: `ui/prediction.py`

- [ ] **Step 1: Create prediction.py with imports**

```python
"""Prediction display components for the application."""

import streamlit as st
from typing import Dict
```

- [ ] **Step 2: Implement action display function**

```python
def _display_action(action: str, confidence: float) -> str:
    """Get display text and color for an action.

    Args:
        action: Action string ('buy', 'sell', 'hold')
        confidence: Confidence value (0-1)

    Returns:
        Tuple of (display_text, color)
    """
    action_map = {
        'buy': ('买入', '#ef4444'),
        'sell': ('卖出', '#22c55e'),
        'hold': ('持有', '#6b7280')
    }
    return action_map.get(action, ('持有', '#6b7280'))
```

- [ ] **Step 3: Implement progress bar component**

```python
def _confidence_bar(confidence: float) -> str:
    """Generate confidence bar HTML.

    Args:
        confidence: Confidence value (0-1)

    Returns:
        HTML string for progress bar
    """
    percent = int(confidence * 100)
    filled = '█' * int(percent / 5)
    empty = '░' * (20 - len(filled))
    return f"{filled}{empty} {percent}%"
```

- [ ] **Step 4: Implement single horizon card**

```python
def render_horizon_card(title: str, prediction: Dict, icon: str = None):
    """Render prediction card for a single time horizon.

    Args:
        title: Card title
        prediction: Prediction dictionary with 'action', 'confidence', 'reasoning'
        icon: Optional emoji icon
    """
    action_text, action_color = _display_action(prediction.get('action', 'hold'), prediction.get('confidence', 0))
    confidence = prediction.get('confidence', 0)

    with st.container():
        title_with_icon = f"{icon} {title}" if icon else title
        st.markdown(f"### {title_with_icon}")

        # Display action with confidence
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"<h2 style='text-align: center; color: {action_color}'>{action_text}</h2>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<p style='text-align: center; color: {action_color}'>{_confidence_bar(confidence)}</p>", unsafe_allow_html=True)

        # Display reasoning
        reasoning = prediction.get('reasoning', [])
        if reasoning:
            st.markdown("**推理依据:**")
            for reason in reasoning:
                st.markdown(f"• {reason}")

        st.divider()
```

- [ ] **Step 5: Implement ensemble card**

```python
def render_ensemble_card(prediction: Dict):
    """Render ensemble prediction card.

    Args:
        prediction: Prediction dictionary with ensemble data
    """
    ensemble = prediction.get('ensemble', {})
    action_text, action_color = _display_action(ensemble.get('action', 'hold'), ensemble.get('confidence', 0))
    confidence = ensemble.get('confidence', 0)

    with st.container():
        st.markdown("### 🎯 综合建议")

        # Display action with confidence (larger)
        st.markdown(f"<h1 style='text-align: center; color: {action_color}'>{action_text}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: {action_color}; font-size: 1.5em;'>{_confidence_bar(confidence)}</p>", unsafe_allow_html=True)

        # Display breakdown summary
        breakdown = ensemble.get('breakdown', {})
        if breakdown:
            st.markdown("**各周期建议:**")
            for horizon in ['短期', '中期', '长期']:
                pred = prediction.get(horizon if horizon in prediction else '', {})
                if pred:
                    action = pred.get('action', 'hold')
                    conf = pred.get('confidence', 0)
                    st.caption(f"{horizon}: {action} ({int(conf*100)}%)")

        # Display reasoning
        reasoning = ensemble.get('reasoning', [])
        all_reasoning = ensemble.get('all_reasoning', [])

        if reasoning:
            st.markdown("**💡 操作提示:**")
            for reason in reasoning:
                st.markdown(reason)

        st.divider()
```

- [ ] **Step 6: Verify imports work**

Run: `python -c "from ui.prediction import render_horizon_card, render_ensemble_card"`
Expected: No import errors

- [ ] **Step 7: Commit**

```bash
git add ui/prediction.py
git commit -m "feat: implement prediction display components"
```

---

## Task 2: Integrate Prediction into Stock Detail Page

**Files:**
- Modify: `ui/pages.py`

- [ ] **Step 1: Add prediction imports**

```python
from prediction.ensemble import EnsemblePredictor
from ui.prediction import render_horizon_card, render_ensemble_card
```

- [ ] **Step 2: Create prediction helper function**

```python
def _get_prediction(symbol: str, storage: StockStorage) -> Dict:
    """Get prediction for a stock.

    Args:
        symbol: Stock symbol
        storage: StockStorage instance

    Returns:
        Prediction dictionary
    """
    predictor = EnsemblePredictor(storage)
    predictor.load_models()
    return predictor.predict(symbol)
```

- [ ] **Step 3: Replace prediction placeholder with actual display**

In `show_stock_detail()` function, replace the call to `_render_prediction_placeholder()` with:

```python
# Prediction section
st.markdown("---")

# Get prediction
try:
    prediction = _get_prediction(symbol, storage)

    # Display horizon predictions in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        render_horizon_card("📈 短期预测", prediction['short'])

    with col2:
        render_horizon_card("📊 中期预测", prediction['medium'])

    with col3:
        render_horizon_card("📉 长期预测", prediction['long'])

    # Display ensemble
    render_ensemble_card(prediction)

except Exception as e:
    st.error(f"预测获取失败: {e}")
    st.info("请确保模型已训练 (models/ 目录下有 .pkl 文件)")
```

- [ ] **Step 4: Test prediction display**

Run: `streamlit run app.py`
Expected: Stock detail page shows prediction cards

- [ ] **Step 5: Commit**

```bash
git add ui/pages.py
git commit -m "feat: integrate prediction display into stock detail page"
```

---

## Task 3: Add History Review Page

**Files:**
- Modify: `ui/pages.py`
- Modify: `app.py`

- [ ] **Step 1: Add show_history placeholder function to pages.py**

```python
def show_history():
    """Display history review page."""
    st.header("📜 历史预测回顾")
    st.info("🚀 历史回顾功能将在后续实现")
    st.write("""
    本页面将展示:
    - 预测准确率统计
    - 准确率趋势图
    - 历史预测记录
    """)
```

- [ ] **Step 2: Add history page to sidebar in app.py**

Update the radio button options at the top of app.py:

```python
page = st.radio(
    "导航",
    ["首页/板块总览", "股票详情", "数据更新", "历史回顾"],
    index=["首页/板块总览", "股票详情", "数据更新", "历史回顾"].index(st.session_state.page)
)
```

- [ ] **Step 3: Update import statement in app.py**

Update the import line to include show_history:

```python
from ui.pages import show_homepage, show_stock_detail, show_data_update, show_history
```

- [ ] **Step 4: Add history page handling in app.py**

Add after data update section:

```python
elif st.session_state.page == "历史回顾":
    show_history()
```

- [ ] **Step 5: Test history page**

Run: `streamlit run app.py`
Expected: New "历史回顾" page accessible from sidebar

- [ ] **Step 6: Commit**

```bash
git add ui/pages.py app.py
git commit -m "feat: add history review page placeholder"
```

---

## Task 4: Interface Optimization

**Files:**
- Modify: `ui/pages.py`
- Modify: `ui/charts.py`

- [ ] **Step 1: Add loading state for prediction**

```python
# In show_stock_detail(), before prediction call
with st.spinner("正在分析预测..."):
    prediction = _get_prediction(symbol, storage)
```

- [ ] **Step 2: Add prediction error handling**

Replace the except block with:

```python
except FileNotFoundError:
    st.warning("⚠️ 模型文件未找到")
    st.info("请先训练模型: python prediction/trainer.py")
except Exception as e:
    st.error(f"预测失败: {e}")
```

- [ ] **Step 3: Add prediction cache**

Replace `_get_prediction()` function with:

```python
@st.cache_data(ttl=3600)
def _get_prediction_cached(symbol: str) -> Dict:
    """Cached prediction getter (creates storage inside).

    Args:
        symbol: Stock symbol

    Returns:
        Prediction dictionary
    """
    from data.storage import StockStorage
    from data.database import DatabaseManager

    storage = StockStorage(DatabaseManager())
    predictor = EnsemblePredictor(storage)
    predictor.load_models()
    return predictor.predict(symbol)
```

Then update the prediction call:

```python
# Get prediction (using cached function)
with st.spinner("正在分析预测..."):
    prediction = _get_prediction_cached(symbol)
```

- [ ] **Step 4: Optimize chart rendering**

In `ui/charts.py`, add check for data size:

```python
# At start of each chart function
if len(df) > 1000:
    # Sample data for performance
    df = df.sample(n=1000)
```

- [ ] **Step 5: Commit**

```bash
git add ui/pages.py ui/charts.py
git commit -m "refactor: optimize prediction and chart rendering"
```

---

## Task 5: Update Documentation

**Files:**
- Modify: `PROGRESS.md`
- Modify: `README.md`

- [ ] **Step 1: Update PROGRESS.md with Stage 5 completion**

Add section after Stage 4:

```markdown
### 2026-03-28 - Stage 5 详情页实现完成 ✅

**已完成 (4/4 tasks)**:
1. Prediction Display Components (ui/prediction.py)
2. Stock Detail Prediction Integration
3. History Review Page (placeholder)
4. Interface Optimization

**当前状态**: Stage 1 完成，Stage 2 完成，Stage 3 完成，Stage 4 完成，Stage 5 完成

**下一步**: 开始实现 Stage 6 - 集成测试和优化
```

- [ ] **Step 2: Update README.md with Stage 5 features**

Update "当前进度" and "最新更新" sections.

- [ ] **Step 3: Commit**

```bash
git add PROGRESS.md README.md
git commit -m "docs: update PROGRESS.md and README.md with Stage 5 completion"
```

---

## Final Verification

After completing all tasks:

- [ ] **Run the application**: `streamlit run app.py`
- [ ] **Verify prediction display**: Go to stock detail page, check predictions show
- [ ] **Verify history page**: Check history page is accessible
- [ ] **Test with no models**: Verify error handling works
- [ ] **Update CLAUDE.md**: Update current stage

---

## Notes

- Models must be trained before predictions work: `streamlit run prediction/trainer.py`
- Model files should be in `models/` directory
- Prediction is cached for 1 hour to improve performance
- Chart data is sampled if > 1000 rows for performance