# ComfyUI-ares_text_editor

## English Overview

A ComfyUI custom node that **pauses the workflow for manual text editing** before continuing. Connect upstream text to `input_text`, run the workflow, and the node blocks until you edit the text and click **确认并继续 (Confirm & Continue)** to resume with your edited content.

- True blocking pause - the workflow does not continue until you confirm
- Keeps your edited text - it is never overwritten
- Single-pass execution - downstream runs once with the edited text
- Fully local, uses only ComfyUI's built-in server

> 中文文档见下方，以下为中文完整说明。

---

## 简介

一个 ComfyUI 自定义节点插件，用于在生成流程中暂停工作流、人工编辑文本后再继续执行。

适合用于：AI 生成提示词后人工润色、批量工作流中间需要人工确认的文本内容。

## 功能特性

- **真正的暂停等待**：节点执行时会阻塞在编辑状态，工作流不会继续，等待人工编辑完成后才往下执行
- **保留编辑内容**：已编辑的文本不会被覆盖；通过「加载新输入」可清空编辑框以重新获取输入
- **单次通过**：点击「确认并继续」提交后工作流只继续执行一次，下游不会重复运行
- **本地 API**：通过 ComfyUI 内置服务器提供接口，无任何外部网络请求

## 节点

### Ares文本再次编辑 (`TextEditorWithConfirm`)

| 名称 | 类型 | 说明 |
| ---- | ---- | ---- |
| `input_text` | STRING (强制输入) | 上游接入的文本 |
| `editable_text` | STRING | 可编辑文本（留空时节点进入等待编辑状态） |

输出：`output_text` (STRING)

## 安装

### 方式一：Git Clone

```bash
git clone https://github.com/SuperWJ062/ComfyUI-ares_text_editor custom_nodes/ComfyUI-ares_text_editor
```

### 方式二：ComfyUI Manager

在 ComfyUI Manager 的 **Install Custom Nodes** 中搜索 `ares_text_editor` 进行安装。

安装完成后**重启 ComfyUI**。本插件无第三方依赖，不需要额外的 `requirements.txt`。

## 使用流程

1. 将上游节点（如文本生成、`Show Text` 等）的文本输出连接到 `input_text`
2. 运行工作流，节点会进入等待编辑状态，编辑框中自动填入输入的文本
3. 在编辑框中修改文本
4. 点击 **确认并继续**，工作流携带编辑后的文本继续执行下游节点

> 提示：如果浏览器端缓存了旧版前端脚本，请强制刷新页面（Ctrl+F5）。

## 工作机制

- 当 `editable_text` 为空且存在输入时，后端节点进入阻塞等待状态，并通过 `_PENDING` 记录当前输入
- 前端在节点执行期间通过状态接口拉取输入文本填入编辑框
- 点击「确认并继续」后，前端将编辑内容 POST 到服务器，后端解除阻塞并返回该文本

### 本地 API

| 方法 | 路径 | 说明 |
| ---- | ---- | ---- |
| POST | `/ares_text_editor/confirm` | 提交编辑文本 `{ "node_id": "...", "text": "..." }`，解除节点阻塞 |
| GET  | `/ares_text_editor/status/{node_id}` | 查询节点等待状态，返回 `{ "input": "...", "confirmed": bool }` |

## 常见问题

- **节点一直显示执行中？** 说明节点正在等待编辑确认，请在编辑框中确认内容后点击「确认并继续」。
- **想跳过人工编辑？** 在编辑框中直接填入文本后排队执行，节点会直接使用该文本继续（不进入等待状态）。

## 许可证

[MIT](LICENSE)
