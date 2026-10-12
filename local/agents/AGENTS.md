# iController 仓库规则

- OpenCode 及所有 agent 在隔离容器中运行；仓库版本控制由用户在容器外处理。
- 绝不运行任何 Git 命令，包括只读命令；不读取或修改 `.git`。
- 使用 Read/Glob/Grep、明确的文件清单和项目测试/build 验证变更。
- 向任何 subagent 委派任务时，必须传递本规则。
