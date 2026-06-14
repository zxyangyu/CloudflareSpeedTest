# EdgeTunnel bestip.txt

这个仓库已经可以把 CloudflareSpeedTest 的 `result.csv` 转成 EdgeTunnel 可读取的普通文本 API：

```text
104.27.200.69:443#LAX
172.67.60.78:443#SEA
```

## GitHub Actions 自动更新

1. 把这个 `CloudflareSpeedTest` 目录推送到你自己的 GitHub 仓库。
2. 在仓库的 `Settings -> Actions -> General` 中确认 `Workflow permissions` 允许 `Read and write permissions`。
3. 进入 `Actions -> Update EdgeTunnel Best IP -> Run workflow` 手动跑一次。
4. 之后工作流会每 8 小时自动更新仓库根目录的 `bestip.txt`。

EdgeTunnel 优选 API 填这个地址：

```text
https://raw.githubusercontent.com/<你的GitHub用户名>/<你的仓库名>/master/bestip.txt
```

如果你的默认分支是 `main`，把 URL 里的 `master` 改成 `main`。

## 本地手动更新

```bash
bash script/update_edgetunnel_bestip.sh
```

常用参数可以用环境变量覆盖：

```bash
CFST_PORT=443 CFST_COLO=HKG,NRT,LAX CFST_DOWNLOAD_COUNT=20 bash script/update_edgetunnel_bestip.sh
```

说明：

- `CFST_PORT`：EdgeTunnel 节点端口，默认 `443`。
- `CFST_COLO`：可选地区过滤，比如 `HKG,NRT,LAX`；为空则不过滤。
- `CFST_DOWNLOAD_COUNT`：测速并发布的数量，默认 `20`。
- `CFST_MAX_DELAY`：平均延迟上限，默认 `300` ms。
- `CFST_MIN_SPEED`：下载速度下限，默认 `0` MB/s。

GitHub Actions 测到的是 GitHub runner 所在网络的结果。如果你想按自己的宽带/VPS 线路优选，就在对应机器上定时运行本地脚本，然后提交 `bestip.txt`。
