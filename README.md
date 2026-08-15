# ComfyUI-ares_text_editor

A ComfyUI node that pauses the workflow for manual text editing before continuing.

## Node

- **Ares文本再次编辑** (`TextEditorWithConfirm`)

## Usage

1. Connect upstream text to `input_text` and run the workflow.
2. The node blocks and waits for editing; the input text is shown in `editable_text`.
3. Edit the text, then click **确认并继续** to submit and resume the workflow.

## Install

```
git clone https://github.com/SuperWJ062/ComfyUI-ares_text_editor custom_nodes/ComfyUI-ares_text_editor
```

Restart ComfyUI.
