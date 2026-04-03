# Security

## 1 Development 开发阶段

### 1.1 Dev environment security vulnerability 开发环境安全漏洞

> [!NOTE]
>
> For source codes `<= commit c7671cccc4da7e21fd288521a515b011197ac18c (2026-04-03)`, the frontend of this project was built using CRA (react-scripts).
>
> Since CRA/react-scripts is no longer maintained, it contains multiple known vulnerabilities in its dependency tree, which mainly affect the development environment.
>
> The project has since migrated to Vite.
>
> Important notes:
>
> - Frontend code is built into static assets during release
> - Release builds do not include CRA/react-scripts as a runtime dependency
>
> Therefore, these vulnerabilities **do not affect distributed releases**, but may impact development environments in older versions.
>
> ---
>
> 在 `<= commit c7671cccc4da7e21fd288521a515b011197ac18c (2026-04-03)` 的源码中，项目的前端基于 CRA (react-scripts) 构建。
>
> 由于 CRA/react-scripts 已停止维护，其依赖中存在多个已知漏洞，这些问题主要影响开发环境的安全性。
>
> 项目已在后续版本迁移至 Vite。
>
> 需要说明的是：
>
> - 前端代码在发布时会被构建为静态资源
> - Release 版本不包含 CRA/react-scripts 运行时依赖
>
> 因此，这些漏洞**不会影响已发布的程序**，仅可能影响历史版本的开发环境。

