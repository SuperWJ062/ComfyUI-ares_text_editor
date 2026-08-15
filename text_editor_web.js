import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "TextEditor.ConfirmButton",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "TextEditorWithConfirm") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = onNodeCreated?.apply(this, arguments);

            const editableWidget = this.widgets?.find((w) => w.name === "editable_text");
            if (!editableWidget) return result;

            editableWidget.type = "text";
            editableWidget.options = editableWidget.options || {};
            editableWidget.options.multiline = true;

            let fillTimer = null;
            const editableIsEmpty = () =>
                !editableWidget.value || editableWidget.value.trim() === "";
            const stopFill = () => {
                if (fillTimer !== null) {
                    clearInterval(fillTimer);
                    fillTimer = null;
                }
            };
            const startFill = () => {
                if (fillTimer !== null || !editableIsEmpty()) return;
                fillTimer = setInterval(async () => {
                    try {
                        const res = await api.fetchApi(`/ares_text_editor/status/${this.id}`);
                        if (!res.ok) return;
                        const data = await res.json();
                        if (editableIsEmpty()) {
                            editableWidget.value = data.input;
                            app.graph.setDirtyCanvas(true);
                            stopFill();
                        }
                    } catch (e) {
                        console.error("[Text Editor] 拉取输入失败:", e);
                    }
                }, 400);
            };

            // 确认并继续：提交当前编辑内容，后端解除阻塞并继续执行
            const confirmButton = this.addWidget("button", "确认并继续", null, async () => {
                confirmButton.name = "提交中...";
                try {
                    const res = await api.fetchApi("/ares_text_editor/confirm", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            node_id: String(this.id),
                            text: editableWidget.value || "",
                        }),
                    });
                    if (!res.ok) throw new Error(`HTTP ${res.status}`);
                    // 节点当前未在执行时（首次运行），重新排队触发执行
                    if (!this.nodeIsExecuting) {
                        app.queuePrompt(0, 1);
                    }
                } catch (e) {
                    console.error("[Text Editor] 提交失败:", e);
                    alert("提交失败，请重试");
                } finally {
                    confirmButton.name = "确认并继续";
                }
            });
            confirmButton.serialize = false;

            // 加载新输入：清空编辑框，下次运行将重新等待输入
            const refreshButton = this.addWidget("button", "加载新输入", null, () => {
                editableWidget.value = "";
                app.graph.setDirtyCanvas(true);
            });
            refreshButton.serialize = false;

            // 节点执行期间，若编辑框为空，从后端拉取输入文本供编辑
            const onExecuting = (event) => {
                if (event.detail === null || event.detail === undefined) {
                    this.nodeIsExecuting = false;
                    stopFill();
                    return;
                }
                if (String(event.detail) !== String(this.id)) return;
                this.nodeIsExecuting = true;
                startFill();
            };
            api.addEventListener("executing", onExecuting);

            const onRemoved = this.onRemoved;
            this.onRemoved = function () {
                api.removeEventListener("executing", onExecuting);
                if (onRemoved) onRemoved.apply(this, arguments);
            };

            const onExecuted = this.onExecuted;
            this.onExecuted = function (message) {
                this.nodeIsExecuting = false;
                stopFill();
                if (onExecuted) onExecuted.apply(this, arguments);
            };

            return result;
        };
    },
});
