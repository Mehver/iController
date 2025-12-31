# Security

## 1 Development 开发阶段

### 1.1 Dev environment security vulnerability 开发环境安全漏洞

https://github.com/Mehver/iController/security/dependabot/50

This vulnerability only affects the `webpack-dev-server` used during development via `npm start`. If a developer’s machine visits a malicious website using a non-Chromium browser, the attacker may be able to exfiltrate source code through the local dev server.
 At present, there is no suitable upgrade path while retaining the existing `react-scripts`.
 The production environment serves pre-built static files via Flask and is not affected by this vulnerability.

At worst, only in-development source code could be exposed, which is not expected to contain sensitive or valuable data.

该漏洞仅影响开发阶段 `npm start` 使用的 `webpack-dev-server`：当开发设备在非 Chromium 浏览器中访问恶意网站时，对方可能通过本地 dev server 窃取源码。当前在保留现有 `react-scripts` 的前提下暂无合适的升级方案。生产环境使用 Flask 提供已构建的静态文件，不受该漏洞影响。

不论如何，恶意攻击最严重的后果也只是调试中的源码被获取，这不应该包含有价值内容。
