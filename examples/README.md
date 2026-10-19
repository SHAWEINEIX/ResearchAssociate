# examples · 格式演示

`format-demo.md` 与 `format-demo.html` 只用于看**结构和版式**：

- 所有数字都是虚构的，用来展示结论卡、关键发现、表格、反方、待核与来源的写法。
- 来源链接指向 `example.com`，不是真实报告，**不可引用**。
- 真实课题在 `topics/`，证据在各自的 `evidence.md`。

重新生成：

```bash
python3 scripts/build_report.py examples/format-demo.md
```

HTML 是自包含的，直接在浏览器打开；手机上看、打印 PDF 都可以。
