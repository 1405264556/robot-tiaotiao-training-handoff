# Jumper 桌面整理训练交接

本私有仓库保存“蟹小管家”桌面整理项目的训练提示词与输入清单。
当前参考外观为 v0.6.0，生活书桌场景草稿为 v0.2.0。
尚未开始本任务训练；没有本任务 checkpoint、控制器、网页 App 或可执行策略 `.app`。

- [完整虚拟机智能体提示词](docs/training-handoff.zh.md)
- [包含 GitHub 下载步骤的完整提示词](docs/github-training-prompt.zh.md)
- [下载训练输入](https://github.com/1405264556/robot-tiaotiao-training-handoff/releases/tag/handoff-2026-10-11)
- [逐文件哈希与交接范围](handoff-manifest.json)

Release 附件包含完整当前场景目录、冰蓝猫耳参考 `.skin`、来源锁定记录、设计说明与提示词。
ZIP 约 22 MB，含真实模型文件，保留原字节；不是完整历史工作区，也不是官方策略 `.app`。
上游仓库需按来源锁定记录另行获取。依赖、Windows venv、缓存及凭证不包含在输入包中。

## 在虚拟机下载

私有仓库需要使用有权限的 GitHub 账号登录。以下命令使用 GitHub CLI：

```bash
gh auth login
gh repo clone 1405264556/robot-tiaotiao-training-handoff
cd robot-tiaotiao-training-handoff
gh release download handoff-2026-10-11 --repo 1405264556/robot-tiaotiao-training-handoff --pattern '*.zip*' --dir downloads
python3 tools/verify_inputs.py downloads/desk-helper-training-inputs-2026-10-11.zip
python3 -m zipfile -e downloads/desk-helper-training-inputs-2026-10-11.zip inputs
```

只有校验通过后才执行解压命令。如果虚拟机没有 GitHub CLI，也可在浏览器登录 GitHub，
从 Release 下载 ZIP 与 `.zip.sha256`，放入仓库的 `downloads/` 后运行相同校验。

把下面这段发给虚拟机智能体：

```text
请读取 inputs/docs/training-handoff.zh.md，执行其中“提示词”的完整要求。
先检查输入完整性、虚拟机资源与官方依赖，再实际实现和训练桌面整理任务，
逐阶段报告验证结果。inputs 是训练输入，不是完整历史工作区。
```

## 官方协议与范围

Train 当前导入 `.map` 仅支持回放；它不直接用任意导入地图进行并行训练，也不加载 `.skin`。
必须依官方任务/场景机制建立可训练的环境，再分别验证控制、接触抓取和回放。
数字模型、包有效性与仿真不构成实体安装或硬件运行证据。

当前锁定来源：

- [Jumper Train](https://github.com/KingKongRobotics/jumper/tree/78966f45de6f2b6de3f7cea017f32a39f8b993e6)
- [Jumper Design](https://github.com/KingKongRobotics/jumper-design/tree/918d192857fcea1678c2a40b339501004a94d838)

保留上游来源与权利声明。此私有交接不重新授权上游资产，也不覆盖原版本。
