# VPN.lat 逆向工程报告 (v3.9.57 b7789)

> 安全研究用途。本项目还原 VPN.lat Android 客户端的完整通信协议，用于互操作性与安全评估。

## 状态表

| 模块 | 状态 | 说明 |
|------|------|------|
| 架构识别 | ✅ 完成 | Flutter AOT (Dart 3.10.8) + OpenVPN3 + WireGuard 双协议 |
| 后端定位 | ✅ 完成 | `hetecn.com`（Firebase RTDB `vpn-lat.firebaseio.com` 已被厂商弃用，423） |
| 403 防护分析 | ✅ 完成 | 服务端 IP GeoIP 白名单（84 国）+ 数据中心 ASN 疑似拦截 |
| Flutter AOT 反编译 | ✅ 完成 | blutter（需 ICU/MSVC 补丁，见 docs/blutter-build.md） |
| 请求签名还原 | ✅ 完成 | 6 请求头全部还原，含 AES-256-GCM `info` 头 |
| 密钥提取 | ✅ 完成 | 4×8 字节硬编码密钥拼接，`base64(cipher+nonce+tag)` |
| API 端点图谱 | ✅ 完成 | 4 端点全链路（见下） |
| 节点列表获取 | ⚠️ 受限 | 需 84 支持国内住宅出口（数据中心 IP 被拒） |
| demo server | ✅ 完成 | `demo/demo_server.py` :8908 |
| 动态验证 | ⛔ 受阻 | APK 仅 arm64-v8a，x86_64 模拟器 ndk_translation 下 SIGILL 自毁 |

## 后端 API（还原自 `VpnLatApi`）

```
GET https://hetecn.com/server                  # 国家列表 (CountryModel[])
GET https://hetecn.com/country/<id>/server     # 城市列表 (CityModel[])
GET https://hetecn.com/opvn/server/<id>?cx=2   # OpenVPN 配置
GET https://hetecn.com/wire/server/<id>?cx=2   # WireGuard 配置
```

### 请求头（`_getHeaders` 完整还原）

| Header | 值 | 来源 |
|--------|-----|------|
| `Content-Type` | `application/json` | 硬编码 |
| `vpn-lat` | `<base64彩蛋>/_VPN.lat-/-com.vpn.lat-/wg/-0003` | 硬编码（base64 解码为西语嘲弄句，纯彩蛋） |
| `Accept-Language` | `es` / `en` / ... | `contractorLanguage()` |
| `info` | AES-256-GCM 加密串 | `checkInfo()`：`"com.vpn.lat - <ver> - <build> - _android - <n>"` |
| `mx` | 设备信任 JSON | `isRooted/isRealDevice/hasCorrectlyInstalled/rootedOrJailbroken/fridaSuspected/emulator/debuggerAttached/compromised/system/seenAds/loadAds/isPro` |
| `Corp` | `2` | 硬编码 |
| `Authorization` | `Bearer V1ZO...VT0=` | 硬编码（三层 base64 解码仍是西语嘲弄句——**它就是真 token**） |

### AES-256-GCM 密钥

`_assembleEncryptionKey()` 顺序拼接 4 个 8 字节常量缓冲：

```
LocaleConfig.getDefaultBuffer    [228,106,158,106,164,178,100,138]
NetworkConfig.getValidationBytes [242,202,206,238,96,148,128,232]
CacheConfig.getIntegrityBuffer   [220,128,210,98,206,160,222,236]
MetricsConfig.getCalibrationData [210,168,128,198,66,72,216,174]
```

加密输出：`base64(cipherText || nonce(12) || tag(16))`，无 AAD。

### 数据模型字段

`id, hostname, ip, country, shortcountry, city, category(openvpn|wireguard), premium, ping, load, active, timezone, zip, vpn_config, protocol`

## Geo-Gate 机制（实测）

- 受限国家出口 → 任何路径统一 `403 {"error":"Forbidden"}`
- 非受限但不在 84 国白名单 → `/server` 返回 8 条多语言 `category:unsupported` 静态桩
- 官网列出 84 支持国（美洲/欧洲/非洲/中东/大洋洲），判定基于请求出口 IP GeoIP
- 数据中心 ASN（Hetzner/OVH/阿里云等）即使位于支持国也被拒（待真机流量最终确认）

## 目录

- `tools/` — 还原的 Python 客户端 + blutter 构建脚本
- `demo/` — OpenAI 风格 demo server + 网页
- `docs/` — 详细文档（构建坑、new-api 对接、合规评估）

## 合规结论

hetecn 节点为厂商自租基础设施。凭证还原仅用于研究披露；**不可将厂商节点接入生产代理池**。公共志愿节点源（VPNGate 等）除外。

## License

研究用途，见 LICENSE。
