移除“各种模组转 AE-ui 材质”合集内的全部 8 个独立资源包，并删除仓库 README。

本版仅合并：
- GToTextureBackportGTL v3.2
- XingLuo AE2 Refreshed 2.7.9
- 多功能机械方块重置

优先级：方块重置 > XingLuo > GTo。XingLuo 本身包含的其他模组美化仍保留。
与 v1.0.0 相比移除 760 个 assets 路径，包大小约 6.02 MiB。
保留原作者署名、许可证及此前两处资源修复。Photon 光影仍不包含。
已检查 ZIP 完整性、JSON 语法及 3169 张 PNG 解码；尚未进行客户端进服渲染测试。

停服后更新 server.properties 中的资源包 URL 和 SHA-1，再重新启动：

```properties
resource-pack=https://github.com/MoxueF/gtl-server-resources/releases/download/v1.0.1/GTL-Server-Resources-1.20.1-v1.0.1.zip
resource-pack-sha1=be33a4123c1b4fc8d6f83fc222848a8761223673
require-resource-pack=false
resource-pack-prompt={"text":"GTL server textures and AE-style interfaces"}
```
