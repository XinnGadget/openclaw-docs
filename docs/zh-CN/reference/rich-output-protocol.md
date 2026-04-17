---
x-i18n:
    generated_at: "2026-04-11T12:34:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2a8884fc2c304bf96d4675f0c1d1ff781d6dc1ae8c49d92ce08040c9c7709035
    source_path: reference/rich-output-protocol.md
    workflow: 15
---

# 富输出协议

助手输出可以携带一小组传递/渲染指令：

- `MEDIA:` 用于附件传递
- `[[audio_as_voice]]` 用于音频呈现提示
- `[[reply_to_current]]` / `[[reply_to:<id>]]` 用于回复元数据
- `[embed ...]` 用于 Control UI 富渲染

这些指令彼此独立。`MEDIA:` 以及回复/语音标签仍然是传递元数据；`[embed ...]` 是仅限 Web 的富渲染路径。

## `[embed ...]`

`[embed ...]` 是面向智能体的、用于 Control UI 的唯一富渲染语法。

自闭合示例：

```text
[embed ref="cv_123" title="状态" /]
```

规则：

- `[view ...]` 不再对新输出有效。
- Embed 短代码只会在助手消息界面中渲染。
- 只有基于 URL 的 embed 会被渲染。使用 `ref="..."` 或 `url="..."`。
- 块级内联 HTML embed 短代码不会被渲染。
- Web UI 会从可见文本中移除该短代码，并以内联方式渲染 embed。
- `MEDIA:` 不是 embed 的别名，不应被用于富 embed 渲染。

## 存储渲染形状

规范化/存储后的助手内容块是一个结构化的 `canvas` 项：

```json
{
  "type": "canvas",
  "preview": {
    "kind": "canvas",
    "surface": "assistant_message",
    "render": "url",
    "viewId": "cv_123",
    "url": "/__openclaw__/canvas/documents/cv_123/index.html",
    "title": "Status",
    "preferredHeight": 320
  }
}
```

存储/渲染后的富内容块直接使用这个 `canvas` 形状。`present_view` 不会被识别。
