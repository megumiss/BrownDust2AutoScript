# BrownDust2AutoScript Agents Guide

## 1. 目标与范围
本文件用于指导在本仓库执行代码任务的代理（Agent）高效、安全地完成开发工作，重点覆盖：
- 任务执行链路与关键入口
- 高频方法（参数、作用、逻辑）
- 新任务开发标准流程
- 调度与配置回写规则
- 常见故障排查

## 2. 项目关键入口
- 调度主入口：`bd2as.py`
  - 任务命令通过 `inflection.underscore(task)` 映射到类方法执行。
  - 需提供运行控制方法：`restart/start/stop/goto_main`。
- 调度基类：`module/alas.py`
  - `loop()`：调度主循环。
  - `get_next_task()`：空队列等待策略。
  - `run(command)`：统一执行与异常处理。
- 配置与调度核心：`module/config/config.py`
  - `task_delay/task_call/task_stop` 是任务调度回写三件套。

## 3. 开发任务时必须遵循的执行模型
1. 入口对齐：`ui_ensure(page_xxx)` 把任务起点固定在稳定页面。
2. 状态循环：使用 `while 1` 或 `for _ in self.loop(...)` 执行“截图 -> 判定 -> 交互”。
3. 兜底处理：循环中持续处理弹窗（如 `handle_popup_confirm/handle_reward`）。
4. 调度回写：任务末尾必须显式调用 `task_delay/task_call/task_stop`。
5. 跨任务状态：使用 `cross_get/cross_set` 或 `stored`，避免隐式全局共享。

## 4. 高频方法速查（参数 + 作用 + 逻辑）

### 4.1 识别与交互层（`ModuleBase/UI/PopupHandler`）
| 方法 | 参数 | 作用 | 核心逻辑 |
|---|---|---|---|
| `appear(button, interval=0, similarity=0.85, static=True)` | `button` 支持模板/xpath；`interval` 节流；`similarity` 相似度；`static` 预设区域匹配 | 判定元素是否出现 | xpath 走层级判断，模板走图像匹配；命中后 `interval_reset` |
| `appear_then_click(button, interval=5, similarity=0.85, static=True)` | 同上 | 出现即点击 | `appear` 成功后 `device.click` |
| `match_template_luma(button, interval=0, similarity=0.85)` | 灰度模板参数 | 灰度匹配判定 | 节流后匹配，命中后重置节流计时 |
| `match_template_color(button, interval=0, similarity=0.85, threshold=30)` | `threshold` 颜色阈值 | 模板+颜色联合判定 | 节流后匹配，命中后重置节流计时 |
| `image_color_count(button, color, threshold=221, count=50)` | 区域、颜色、阈值、像素计数 | 用颜色像素占比判定状态 | 裁剪区域 -> 颜色掩码 -> 计数比较 |
| `ui_get_current_page(skip_first_screenshot=True)` | 首帧复用开关 | 获取当前页并处理未知页 | 识别已知页，不命中时执行弹窗与额外恢复逻辑 |
| `ui_goto(destination, skip_first_screenshot=True)` | 目标页、首帧策略 | 页面跳转 | 基于 `Page.init_connection` 的页面连边导航，可带滚动步骤 |
| `ui_ensure(destination, acquire_lang_checked=True, skip_first_screenshot=True)` | 目标页、语言检查、首帧策略 | 确保位于目标页 | 当前页即返回，否则 `ui_goto` |
| `handle_popup_confirm(interval=2)` | 节流秒数 | 处理确认弹窗 | `appear_then_click(POPUP_CONFIRM)` |

### 4.2 设备层（`Device/Control/Screenshot`）
| 方法 | 参数 | 作用 | 核心逻辑 |
|---|---|---|---|
| `device.screenshot()` | 无 | 获取当前截图 | 截图前卡死检查，失败时按能力降级 |
| `device.dump_hierarchy()` | 无 | 获取 UI 层级树 | 先卡死检查，再抓 hierarchy |
| `device.click(button, control_check=True)` | 按钮、是否控制检查 | 点击操作 | 先做点击安全检查，再按控制方式分发 |
| `device.multi_click(button, n, interval=(0.1, 0.2))` | 次数、间隔 | 连续点击 | 首次做检查，后续复用 `click(..., False)` |
| `device.swipe_vector(vector, box=..., random_range=..., padding=..., duration=...)` | 向量、区域、时长等 | 滑动操作 | 先生成轨迹，再调用底层 `swipe` |
| `device.drag(p1, p2, ...)` | 起终点与拖拽参数 | 拖拽操作 | 按控制方式选择实现，不支持时降级 |
| `device.screenshot_interval_set(interval=None)` | `None/'combat'/float` | 设置截图频率 | 读取配置并限制边界后应用 |
| `device.click_record_clear()` | 无 | 清点击记录 | 避免误触发“过多点击”保护 |
| `device.stuck_record_clear()` | 无 | 清卡死记录 | 重置等待目标与计时器 |

### 4.3 调度与配置层（`AzurLaneConfig`）
| 方法 | 参数 | 作用 | 核心逻辑 |
|---|---|---|---|
| `multi_set()` | 无（上下文） | 批量更新配置 | `with` 中集中修改，减少重复保存 |
| `task_delay(success=None, server_update=None, target=None, minute=None, task=None)` | 延迟策略参数 | 设置 `Scheduler.NextRun` | 计算候选时间并取最近值写回 |
| `task_call(task, force_call=True)` | 任务名、是否强制 | 触发任务尽快执行 | 置 `NextRun=now`，可强制启用任务 |
| `task_stop(message='')` | 文本信息 | 结束当前任务 | 抛 `TaskEnd`，交回调度器 |
| `task_switched()` / `check_task_switch(message='')` | 可选信息 | 检查并响应任务切换 | 对比当前与下一任务，不一致则停止 |
| `cross_get(keys, default=None)` | 跨任务路径 | 读其他任务配置 | 从 `self.data` 深层读取 |
| `cross_set(keys, value)` | 跨任务路径与值 | 写其他任务配置 | 写 `modified`，必要时自动 `update()` |

## 5. 新任务开发流程（标准）
1. 新建任务类并选择基类：
   - 页面类任务：继承 `tasks.base.ui.UI`
   - 纯逻辑类任务：继承 `module.base.base.ModuleBase`
2. 在 `run()` 中实现流程：
   - 起点 `ui_ensure(...)`
   - 主循环“判定优先，动作次之，弹窗兜底”
3. 收尾回写调度：
   - 成功路径：`task_delay(...)`
   - 需要串联：`task_call('OtherTask')`
   - 当前任务结束：`task_stop()`
4. 在 `bd2as.py` 接入任务入口方法（确保命令可映射到方法）。
5. 如新增配置项：
   - 修改 `module/config/argument/*.yaml`
   - 执行 `python -m module.config.config_updater`

## 6. 配置与调度规则
- 优先级（低 -> 高）：
  1. 配置文件原始值
  2. `config_override()` 动态修正
  3. `modified` 内存改动
  4. `bind()` 绑定值
  5. `override(**kwargs)` 运行时覆盖
- 调度关键字段：
  - `*.Scheduler.Enable`
  - `*.Scheduler.NextRun`
- 任务未回写调度字段通常会导致“执行一次后卡在当前状态”。

## 7. 质量门槛（提交前）
- 任务逻辑中避免单帧多点击；优先 `appear_then_click`。
- 长循环任务需具备弹窗处理与超时/切换检查。
- 对跨任务依赖，必须显式 `cross_get/cross_set`。
- 修改配置定义后，必须重新生成配置产物。

## 8. 常用命令
```powershell
# 运行调度
python bd2as.py

# 启动 WebUI
python gui.py

# 配置生成
python -m module.config.config_updater

# 代码检查
ruff check .
ruff format .
```

## 9. 故障排查优先顺序
1. 页面识别异常：先检查 `similarity/threshold` 与模板区域。
2. 点击异常：检查 `Emulator_ControlMethod` 与 `click_record` 保护。
3. 不调度或调度错乱：核对 `Scheduler.Enable/NextRun` 和 `task_delay/task_call/task_stop` 是否正确执行。
4. 卡死：检查 `stuck_record` 相关日志与错误截图输出。
