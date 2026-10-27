# VPN.lat 逆向成果 → new-api 渠道对接指南

> 给执行会话的操作手册。所有结论已静态确认（blutter 反编译），标 ⚠️ 的需对接时实测。

## 一、能力边界（先读）

VPN.lat 是 **VPN 节点分发服务**，不是 LLM/AI API。它能给 new-api 的是：

| 能力 | 对接形态 | 价值 |
|------|---------|------|
| OpenVPN/WireGuard 节点配置自动拉取 | 代理池的节点源插件 | 出口 IP 池扩容 |
| 节点元数据（国家/负载/ping/存活） | 代理池测活与调度输入 | 路由质量 |

**不能**做成 LLM 渠道（channel type）。正确落点是 **proxy-pool 模块**（本仓库已有 `relay/channel/notrack` 接共享代理池的先例）。

## 二、前置条件

1. **GeoIP 出口要求（硬性）**：hetecn.com 只对 84 支持国内、非数据中心 ASN 的 IP 返回真实节点列表。测试用出口必须满足:
   - 位于 84 国列表（见 README）
   - 住宅/移动 ISP（ip-api `hosting=false`）
   - 否则拿到的是 8 条 `category:unsupported` 静态桩
2. Python 依赖: `pip install cryptography`（AES-GCM）

## 三、核心客户端（已交付）

`tools/vpnlat_client.py`，关键签名：

```python
from vpnlat_client import get
# 代理填支持国内住宅 HTTP 代理
countries = get("/server", proxy="1.2.3.4:8080")          # CountryModel[]
cities    = get(f"/country/{cid}/server", proxy=...)       # CityModel[]
ovpn      = get(f"/opvn/server/{sid}?cx=2", proxy=...)     # OpenVPN 配置文本(JSON)
wire      = get(f"/wire/server/{sid}?cx=2", proxy=...)     # WireGuard 配置文本(JSON)
```

签名头自动生成（AES-256-GCM `info`、设备信任 `mx`、Bearer、`vpn-lat` 等），无需干预。

## 四、new-api 侧对接方案（proxy-pool 节点源）

参考现有模式：`relay/channel/notrack/adaptor.go`（接共享代理池）+ 免费源收割脚本（jetkai/roosterkid 等 31 源）。

### 方案 A：拉取脚本 → 现有代理池（推荐，改动最小）
1. 把 `vpnlat_client.py` 移植为 Go 或用 Python 侧车：
   - 定时（如 30min）拉 `/server` → 遍历国家 → `/country/<id>/server` → 收集 `active=true` 节点
   - 对每个节点拉 `/opvn/server/<id>?cx=2` 解出 `remote <ip> <port>`（OpenVPN 端点）
2. WireGuard 端点转 SOCKS5：复用 quixsocks 转换层（QuixVPN 项目已有 WG→SOCKS5 实现）
3. 端点写进代理池的 source 清单，走现有 `ProbeAlive` 测活管线

### 方案 B：new-api 内建 channel（不推荐）
把节点列表当 channel 传入不成立——new-api channel 是 LLM 上游抽象。除非走"代理池渠道"抽象，否则不要新建 channel type。

### 数据字段映射

| hetecn 字段 | 代理池语义 |
|------------|-----------|
| `ip`, `hostname` | 节点地址 |
| `country`, `shortcountry`, `city` | 出口地区标签 |
| `category` | 协议（openvpn/wireguard） |
| `premium` | 付费墙过滤（true 跳过） |
| `active` | 可用性初筛 |
| `load`, `ping` | 调度权重 |
| `vpn_config` | 配置原文（含端口/密钥） |

## 五、⚠️ 对接时必测清单

1. `info` 头签名是否被服务端强校验（静态看是发了，但服务端可能不验）——用错 key 请求一次对比
2. `?cx=2` 参数语义（疑似协议版本，cid 解析时带上即可）
3. 配置响应格式是 JSON 包裹还是裸 conf（CityModel.vpn_config 字段名暗示 JSON）
4. 节点 IP 是否可直连 1194/51820（测活）
5. 出口 IP 变化（住宅代理轮换）会导致 geo-gate 结果漂移，拉取需固定出口

## 六、合规红线（不可越）

- hetecn 节点 = 厂商付费基础设施。**凭证还原=研究披露；挂进生产池=盗用基础设施**
- 允许: demo、测活研究、协议报告
- 禁止: 把收割的 VPN.lat 节点作为生产流量出口
- 若需生产出口：走 VPNGate 等公共志愿源（已有先例）

## 七、验证锚点

- 客户端 roundtrip 自测: `python tools/vpnlat_client.py /server [proxy]`
- demo server: `VPNLAT_PROXY=<住宅代理> python demo/demo_server.py` → http://127.0.0.1:8908/demo.html
