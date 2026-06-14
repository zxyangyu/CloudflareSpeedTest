# EdgeTunnel bestip.txt

这个仓库已经可以把 CloudflareSpeedTest 的 `result.csv` 转成 EdgeTunnel 可读取的普通文本 API：

```text
104.27.200.69:443#LAX-01-146.23ms-28.64MBps-loss0
172.67.60.78:443#SEA-02-139.82ms-15.02MBps-loss0
```

## 推荐用法：本地测速，GitHub 只托管文件

不要用 GitHub Actions 跑测速。Actions 运行在 GitHub 的云端 runner 上，测到的是 GitHub 机房网络，不是你的本地网络。

这个仓库现在推荐在你的电脑、VPS、软路由或实际使用代理的机器上运行测速脚本，然后把生成的 `bestip.txt` 推送到 GitHub。GitHub 只负责提供 Raw URL。

EdgeTunnel 优选 API 填这个地址：

```text
https://raw.githubusercontent.com/<你的GitHub用户名>/<你的仓库名>/master/bestip.txt
```

如果你的默认分支是 `main`，把 URL 里的 `master` 改成 `main`。

## 本地手动更新

只生成 `bestip.txt`，不提交：

```bash
bash script/update_edgetunnel_bestip.sh
```

生成 `bestip.txt`，并自动 commit + push 到 GitHub：

```bash
bash script/local_update_and_push.sh
```

常用参数可以用环境变量覆盖：

```bash
CFST_PORT=443 CFST_COLO=HKG,NRT,LAX CFST_DOWNLOAD_COUNT=20 bash script/local_update_and_push.sh
```

说明：

- `CFST_PORT`：EdgeTunnel 节点端口，默认 `443`。
- `CFST_COLO`：可选地区过滤，比如 `HKG,NRT,LAX`；为空则不过滤。
- `CFST_DOWNLOAD_COUNT`：下载测速并发布的数量，默认 `20`。
- `CFST_MAX_DELAY`：平均延迟上限，默认 `100` ms。
- `CFST_EARLY_COUNT`：延迟测速早停数量，默认等于 `CFST_DOWNLOAD_COUNT`。例如默认拿到 20 个 100ms 内、0 丢包的 IP 后停止继续扫描。
- `CFST_THREADS`：延迟测速并发，默认 `20`。并发越高越容易一次性扫太多 IP。候选 IP 会在测速前随机打乱，早停不会固定从 `ip.txt` 前面的网段开始。
- `CFST_MIN_SPEED`：发布结果的下载速度下限，默认 `0` MB/s。默认会只发布有实际下载测速速度的节点；如果全部速度都是 0，才回退发布延迟结果。
- `CFST_REBUILD`：是否每次运行前重新编译本仓库里的 CloudflareST，默认 `1`。这样源码里的早停逻辑会生效。

## 定时运行

Linux crontab 示例，每 8 小时用当前机器网络测速并推送：

```cron
15 */8 * * * cd /home/zengxy/workspace/system_tool/CloudflareSpeedTest && bash script/local_update_and_push.sh >> local_update.log 2>&1
```

如果你是在另一台 VPS 或软路由上使用，请把仓库 clone 到那台机器，并在那台机器上配置定时任务。
