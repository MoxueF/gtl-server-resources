# GTL Server Resources

用于 GregTech Leisure / Minecraft 1.20.1 的合并资源包。通过 GitHub Release 提供服务端资源包直链。

[下载 v1.0.0](https://github.com/MoxueF/gtl-server-resources/releases/download/v1.0.0/GTL-Server-Resources-1.20.1-v1.0.0.zip) · [Release 页面](https://github.com/MoxueF/gtl-server-resources/releases/tag/v1.0.0)

## 内容与优先级

优先级由高到低：

1. 多功能机械方块重置。
2. XingLuo AE2 Refreshed 2.7.9。
3. GToTextureBackportGTL v3.2。
4. 各种模组转 AE-ui 合集内的 8 个独立资源包，用于补充其余资源。

同路径文件使用高优先级版本。Photon GAMS 是独立光影，未包含在此资源包中。

包含 6459 个 assets 文件；压缩包约 9.74 MiB。
处理了 228 次同路径覆盖，移除 13 个备份、绘图源文件或旧崩溃日志。
修复浮选槽连接纹理元数据中多余的括号，以及建筑工具创造建筑膏容器贴图的损坏重复颜色配置块；贴图像素数据保持不变。

## 服务端配置

停止服务端后，将下面四项合并到现有 server.properties，保留文件里的其他配置，随后重新启动：

```properties
resource-pack=https://github.com/MoxueF/gtl-server-resources/releases/download/v1.0.0/GTL-Server-Resources-1.20.1-v1.0.0.zip
resource-pack-sha1=02521ba1c47538325059ebf3e2bb63c721feb61f
require-resource-pack=false
resource-pack-prompt={"text":"GTL server textures and AE-style interfaces"}
```

require-resource-pack=false 表示允许玩家拒绝；若希望拒绝资源包就无法进入服务器，可设为 true。
客户端将从 GitHub 下载，而不是由 Minecraft 游戏端口传输 ZIP。
首次连接可能需要玩家接受，或将该服务器的“服务器资源包”设置为启用。

下载 ZIP 后 SHA-1 应为 `02521ba1c47538325059ebf3e2bb63c721feb61f`。
更新时发布新版本，并同步修改 URL 和 SHA-1；不要覆盖同版本资产后保留旧校验值。

## 验证与兼容性

目标资源包格式为 15（Minecraft 1.20–1.20.1）。
已经检查 ZIP 完整性、重复条目、JSON/元数据语法及 3863 张 PNG 的完整解码。
尚未完成实际客户端进服、界面布局和渲染测试。
部分补充资源的原始格式为 34/35，合并不等于对这些资源进行了完整版本移植；需要在实际模组版本中确认界面槽位与图标。
建议先在客户端单独启用本包，检查 AE 终端、JEI、GT 机器界面及多功能机械方块。

## 来源与署名

原始署名、许可证和 pack.mcmeta 随 ZIP 保存在 sources/ 下；汇总见 [CREDITS.txt](CREDITS.txt)。
GTo 包声明 CC BY-NC-SA 4.0；其他资源维持各自原作者权利，本仓库不对第三方资源授予统一的新许可证。
本仓库借鉴 Nomi 资源仓库的 Release 托管方式，不包含 Nomi 1.12.2 资源。

## 重新构建

准备原始的四个资源包 ZIP（不需要 Photon），运行：

```text
python build_pack.py "原始压缩包所在目录"
```

脚本只需要 Python 标准库。产物位于 dist/，详细覆盖与修复记录在 merge-report.json。
