# QAE V1.0

QAE 是用于提升增量代码包安装效率、降低人工覆盖出错风险的轻量工具。

## 首次安装

将本交付包中的 `engineering/` 目录复制到 `quality-ai` 仓库根目录。

## 使用

在 `quality-ai` 仓库根目录执行：

```bash
python3 engineering/tools/qae/qae.py install XXX_INCREMENT.zip
python3 engineering/tools/qae/qae.py verify
python3 engineering/tools/qae/qae.py rollback
```

## 标准增量包

```text
XXX_INCREMENT.zip
├── manifest.json
└── files/
    └── <仓库相对路径文件>
```

Manifest 必填字段：

```json
{
  "package_name": "BUSINESS_AGENT_ENGINE_V1.2_M1_P03_INCREMENT",
  "target_project": "quality-ai",
  "target_scope": "business_agent",
  "version": "1.2.0",
  "milestone": "M1",
  "files": [
    "business_agent/example.py"
  ]
}
```

QAE 只依赖 Python 3.9+ 标准库。
