# UPGRADE

## V1.1 M3 → V1.1 RC

本次升级不改变 REPEAT_CASE 业务算法，主要完成工程收敛：

- README 改为当前工程唯一使用入口。
- 历史交付文档归档至 `docs/history/`。
- Knowledge 默认接口修正为 `/v1/knowledge/query`。
- Knowledge 环境变量优先级高于插件默认配置，便于跨进程联调。
- 增加统一检查与 E2E 脚本。

旧版运行命令仍然保留；推荐统一使用：

```bash
python main.py list-agents
python main.py run-agent --agent repeat_case ...
```
