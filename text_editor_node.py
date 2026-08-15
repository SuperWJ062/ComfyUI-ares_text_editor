import threading
import time

from comfy.model_management import processing_interrupted

_PENDING = {}
_PENDING_LOCK = threading.Lock()


def register_pending(node_id, input_text):
    with _PENDING_LOCK:
        _PENDING[node_id] = {"input": input_text, "text": None}


def pending_status(node_id):
    with _PENDING_LOCK:
        pending = _PENDING.get(node_id)
        if pending is None:
            return None
        return {"input": pending["input"], "confirmed": pending["text"] is not None}


def confirm_pending(node_id, text):
    with _PENDING_LOCK:
        if node_id in _PENDING:
            _PENDING[node_id]["text"] = text


class TextEditorWithConfirm:
    """
    文本编辑器节点 - 暂停工作流等待人工编辑
    1. input_text 接入上游文本后运行，节点会阻塞等待
    2. 前端显示输入文本，在 editable_text 中编辑
    3. 点击「确认并继续」提交编辑内容，工作流继续执行
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "forceInput": True
                }),
                "editable_text": ("STRING", {
                    "multiline": True,
                    "default": "",
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_text",)
    FUNCTION = "edit_text"
    CATEGORY = "Ares text editor"
    OUTPUT_NODE = False

    @classmethod
    def IS_CHANGED(cls, input_text, editable_text, unique_id):
        return float("nan")

    def edit_text(self, input_text, editable_text, unique_id=None):
        if editable_text and editable_text.strip() != "":
            with _PENDING_LOCK:
                _PENDING.pop(str(unique_id), None)
            output = editable_text
        elif not input_text:
            output = ""
        else:
            node_id = str(unique_id)
            register_pending(node_id, input_text)
            output = self._wait_for_confirm(node_id)
            if output is None:
                output = input_text

        return {"ui": {"text": [output]}, "result": (output,)}

    @staticmethod
    def _wait_for_confirm(node_id):
        while not processing_interrupted():
            with _PENDING_LOCK:
                pending = _PENDING.get(node_id)
                if pending is not None and pending["text"] is not None:
                    text = pending["text"]
                    del _PENDING[node_id]
                    return text
            time.sleep(0.5)
        return None


NODE_CLASS_MAPPINGS = {
    "TextEditorWithConfirm": TextEditorWithConfirm,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextEditorWithConfirm": "Ares文本再次编辑",
}
