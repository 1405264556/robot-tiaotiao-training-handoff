# 基于 GitHub 的虚拟机开发与训练提示词

日期：2026-10-11。将本文件完整内容交给虚拟机智能体执行。

你负责从 GitHub 获取“蟹小管家 / Jumper”训练输入，并继续实现、训练、评估和交付。
仓库是私有的： https://github.com/1405264556/robot-tiaotiao-training-handoff
输入发布标签：handoff-2026-10-11。
开始前读取本文件全部要求；以下下载和训练步骤都是本次任务范围。

## 从 GitHub 获取与校验输入

1. 检测虚拟机操作系统与工具。Ubuntu 缺少工具时安装 Git、GitHub CLI 和 Python 3：

```bash
sudo apt update
sudo apt install -y git gh python3 python3-venv
```

若系统仓库未提供 gh，使用 GitHub CLI 官方安装指引，不从无来源脚本安装。
先运行 `gh auth status`。私有仓库需要有访问权限的 GitHub 身份；未登录时请让
用户在虚拟机终端运行 `gh auth login` 完成认证，不要求用户把密码或 token 发到聊天。
不得把凭证写入代码、日志、训练配置或仓库，也不得把仓库改为公开来绕过认证。

2. 在用户可写的新工作目录下载仓库。现有目录存在时先核对 remote 和改动，
不得删除或覆盖已有工作。以下命令示范全新目录：

```bash
mkdir -p ~/projects
cd ~/projects
gh repo clone 1405264556/robot-tiaotiao-training-handoff
cd robot-tiaotiao-training-handoff
gh release download handoff-2026-10-11 --repo 1405264556/robot-tiaotiao-training-handoff --pattern '*.zip*' --dir downloads
python3 tools/verify_inputs.py downloads/desk-helper-training-inputs-2026-10-11.zip
```

必须取得 ZIP 与同名 `.zip.sha256`；校验器检查总包 SHA-256、23 个归档条目、
安全路径和逐文件哈希。失败时停止解压/训练，报告实际错误。
本次固定 ZIP SHA-256：
`f2c8ed1ba2871b7177c5962a0b0e6c507cd281d3e74f0c8ff0f2af119dbcdc5d`。
同时核对本固定值，不能只相信下载到的可变校验文件。

3. 校验通过后解压至尚未使用的 inputs 目录：

```bash
python3 -m zipfile -e downloads/desk-helper-training-inputs-2026-10-11.zip inputs
```

读取 inputs/AGENTS.md、inputs/versions.json、inputs/references/sources.lock.json、
inputs/docs/design-brief.zh.md、inputs/docs/training-handoff.zh.md 和场景说明。
保持 inputs 中的版本化模型原字节；它是精简训练输入，不是完整原工作区。
仓库中 docs/ 的提示词与 ZIP 内初次交接说明可互相核对。

4. 用固定 revision 建立两个独立上游 checkout。可在工作区 `references/` 下复用
正确版本的现有 checkout；没有时按如下示例创建，不把它们加入交接仓库 Git：

```bash
mkdir -p references
git clone https://github.com/KingKongRobotics/jumper.git references/jumper
git -C references/jumper checkout 78966f45de6f2b6de3f7cea017f32a39f8b993e6
git clone https://github.com/KingKongRobotics/jumper-design.git references/jumper-design
git -C references/jumper-design checkout 918d192857fcea1678c2a40b339501004a94d838
```

需要完整 LFS 模型时依官方文档安装 git-lfs 并获取实际资源；LFS 文本指针不能
代替真实模型。下载失败就报告具体错误，不静默转到不同来源或新版本。
两个 checkout 保留为来源，不直接在 detached HEAD 的来源副本里开展无记录改动。
需要实现新任务时创建有名称的开发分支或独立工作副本，并记录基线与差异。

## 官方环境、任务、训练与验收

以下完整要求继续适用。文中的场景输入相对路径在 inputs/ 下；Train/Design
代码路径在各自 checkout 下。先输出资源、输入校验、安装分支，再实际执行。

你负责继续“蟹小管家 / Jumper 桌面整理助手”的控制与训练工作。
请实际安装、实现、训练、回放和记录，不要只给建议或把安装成功说成任务成功。
用户已选择：以生活书桌场景为基础，配套本地网页 App，支持电脑和手机浏览器。
本轮优先完成训练与策略交付；网页 App 作为后续消费者保留接口需求。

一、接手现状与文件

1. 先定位收到的工作区或交接包，读取 AGENTS.md、versions.json、
   references/sources.lock.json 和 docs/design-brief.zh.md。
   不沿用 Windows 的 F: 路径；全部路径相对于你实际接收的目录。
2. 当前正式外观 v0.6.0，当前场景草稿 v0.2.0。原版本不可覆盖。
   首个任务：从固定取物台抓取单个积木，搬运到低边收纳盘，释放后返回。
3. 关键输入：
   scenes/drafts/v0.2.0/maps/living-study-desk.map
   scenes/drafts/v0.2.0/source/living-study-desk.scene.json
   scenes/drafts/v0.2.0/README.zh-CN.md 及 reports/
   releases/v0.6.0/skins/desk-helper-ice-blue-cat-ears.skin
4. 单位为米、千克、弧度；地图 spawn.yaw 为度。桌面 1.80 × 1.10 m，支撑面 z=0。
   出生点 (-0.34,-0.22,0)，朝 +X；spawn 的 z 是支撑面，不是浮动基座高度。
   sorting_block 中心 (0.07,-0.22,0.0861)，边长 0.03，质量 0.012 kg。
   取物面 z=0.071。target_base 中心 (0.48,-0.22,0.003)，顶面 z=0.006。
   收纳盘尺寸、内壁、其他障碍及摩擦等参数必须从源码和碰撞模型读取。
   这些是暂定仿真参数，不是已验证的可达空间或实物规格。
5. 已有证据包括原生加载、前向计算、出生支撑、积木静态稳定及包资源检查。
   尚无机器人行走/抓取/搬运的任务验收，也没有本任务可续训的 checkpoint。
   上游 out/bundle_example 等示例不是本任务训练成果。
   本机合成检查发现完整机器人有 22 个机械关节、虚拟浮动基座，模型执行器数为 0。
   不要把外观展示姿态当作控制 HOME，不要假设地图或 skin 自动带有控制器。

二、官方来源与安装

1. 使用独立官方上游，优先复现 sources.lock.json 锁定的版本：
   https://github.com/KingKongRobotics/jumper
   revision 78966f45de6f2b6de3f7cea017f32a39f8b993e6
   https://github.com/KingKongRobotics/jumper-design
   revision 918d192857fcea1678c2a40b339501004a94d838
   Design trusted profile SHA-256：
   051e5c98ae4d948604bf095667f7eeb329a21b43885cc912c5f4dcbbeb83aef9
   需要更新版本时另建工作副本并记录新 revision 与差异，不静默覆盖锁定来源。
2. 读取各上游 AGENTS.md。Train 还须读取 CLAUDE.md、docs/WORKFLOWS.md、
   docs/AGENT_SETUP.md、docs/USAGE.md、docs/CONTROLS.md、deploy/BUNDLE.md。
   按实际任务读取并使用 .claude/skills/setup-env、new-task、controls；
   导出/打包时读取部署文档，构建 .app 后按 bundle-manual 添加中文手册。
3. 运行官方 .claude/skills/setup-env/scripts/detect.py，检测虚拟机自身的
   OS、Python、CPU、内存、GPU、驱动、compute capability、磁盘和工具链。
   宿主机有显卡不代表虚拟机能用 GPU；用 VM 内 nvidia-smi、torch 实际运算和
   Warp 设备枚举验证透传。不沿用本机 GTX 1650 Ti 的安装分支。
4. 用 Python 3.10—3.13 与标准库 venv，Train 和 Design 环境隔离。
   依赖放 .venv/，下载放 .cache/，临时构建放 .build/。
   在独立上游中遵守其仓库根 .venv 约定，避免混装导致 MuJoCo 版本冲突。
   每次 pip 前确认 sys.prefix 指向目标环境。
5. 根据官方文档和检测到的 GPU 选择 PyTorch wheel，不盲目安装最新 CUDA wheel。
   必须对 Train 做 pip install -e .（开发检查安装相应 dev 依赖）。
   禁止 pip install mjlab 或 rsl-rl-lib，它们是 rl/ 下的 vendored 副本。
   Design 按其文档安装 -e ".[sim,dev]"；需要真实模型时获取实际 Git LFS 资源。
6. 依官方要求安装 Rust/stable、C linker、wasm32-unknown-unknown、与 Cargo.lock
   精确匹配的 wasm-bindgen CLI；此锁定版本为 0.2.128，仍以实际 lock 为准。
   device 检查按文档安装 CycloneDDS 11.0.1、libclang 和官方校验的 NPU header。
   Docker/RKNN 是硬件完整包环节的依赖，按实际交付范围检查。
7. 运行官方 gates.py 的 A—F 检查。逐项记录输出，失败按官方已知故障处理。
   不允许用跳过 Rust 或 device 测试的绿色 pytest 冒充完整环境通过。
   门槛未通过时报告具体阻塞，不启动正式长训练。
8. 门槛通过后跑官方短训练：
   无可用 GPU：
   python scripts/train.py --task jumper.flat --backend native --device cpu --num_envs 64 --max-iterations 3 --headless
   GPU 分支按官方文档与显存适当设置环境数，不默认 4096。
   正式训练前报告实际后端、GPU/CPU 使用、显存和每迭代耗时。

三、正确处理场景与机器人边界

1. 官方 Train 当前不加载 .skin；导入 .map 只用于回放，train.py 不支持导入
   任意 .map 进行并行训练，也不会采用地图内默认机器人替换训练任务机器人。
   禁止编造 train.py --scene xxx.map 的训练命令，或声称导入外观就是训练整合。
2. 以场景 JSON 的任务物件、支撑面和碰撞为依据，按官方新任务/内建场景机制
   建立可并行复制的训练环境。处理每个环境的起点、积木、取物台、托盘、
   障碍以及 reset，不能让不同环境共享一个自由刚体。
3. 对比当前 Train 机器人与 Design trusted profile：22 关节名称和顺序、限位、
   HOME、质量惯性、碰撞、坐标系及执行器映射。特别核对 LM_J0_joint。
   用当前真实参数给出差异报告，不用历史版本差异代替此次检查。
   新增仿真执行器作为版本化的训练模型配置，并记录控制类型、限幅、PD/
   torque 参数依据；不能修改既有 skin/map 的源物理参数来掩盖差异。
4. 先测夹爪真实几何可达空间、夹口与积木尺寸、取物高度、碰撞间隙、
   完整足端支撑和桌沿余量。位置 IK 可达不等于姿态、碰撞或动态抓取成功。
   路径通道必须用完整机器人占地/活动范围检查，不能只检查中心点。
5. 无法达到原任务布置时，给出测量结果和最小调整方案；新几何/场景进入
   新版本，按 Design 官方编译/导出/原生与视觉验收流程处理，保留 v0.2.0。

四、训练与控制实现顺序

1. 先验证低速接近、刹停、站稳与姿态控制，再验证单侧夹爪抓取与抬升，
   再做搬运/释放，最后串联成完整整理任务。可复用有来源、已验证的官方
   策略或 checkpoint，但不能把五足/夹爪模式演示称为自主整理已完成。
2. 按官方 new-task 规范注册任务、编写 env_cfg.py、rl_cfg.py 与 mdp 项。
   controls.yaml 必须通过 controls skill 的写入工具生成，并通过词典检查。
   参数归属和现有步态 parity 要求按官方规范处理。
3. 设计奖励、终止、超时、掉落、翻倒、桌沿、碰撞与关节限位检查。
   明确训练观测、动作、控制频率、随机化范围、种子和 curriculum。
   先用固定场景调通，再引入有限位置、摩擦和质量变化；不要同时扩大所有因素。
4. 自动控制状态机应包含检查、接近、对准、闭爪、抬升、运输、释放、
   验收、返回，以及暂停、急停、失败恢复。转换以观测/接触等条件驱动，
   带超时；不能仅靠定时器把状态跳到成功。
5. 用脚本移动对象、焊接/吸附约束、外力或直接设置 qpos 的辅助演示，
   必须单独标记，不能计为接触抓取成功。读取仿真真实状态也要明确标记。
   可先使用特权状态开展仿真研究，但后续可部署观测需另验证传感来源；
   没有真实视觉感知验证时，不声称已实现图像识别或硬件自主整理。
6. 记录失败原因并修正后再扩大训练。定期保存 checkpoint 与 resume 信息。
   尚无本任务 checkpoint 时从头训练；若发现可用 checkpoint，先核对任务、
   观测/动作维度、关节顺序、归一化、配置和来源，再通过官方 --checkpoint
   或 --resume 续训。官方 --max-iterations 表示本次追加的迭代数。

五、验收与交付

1. 成功必须是连续物理仿真中通过真实夹爪接触抓起、搬运、松开，积木完整
   落在托盘有效内区，释放后稳定停留；机器人不翻倒、不掉桌、不明显穿模。
   检查对象完整体积、位置/姿态和速度，不能只凭中心点或进入 release 状态评分。
2. 对固定任务与随机化任务分别评估。最终尽量各运行至少 100 次独立种子，
   报告实际次数、成功/失败、耗时、掉落、碰撞、最终位置、翻倒/桌沿事件。
   成功率未达预期就如实交付失败分析，不修改统计定义或隐去失败回合。
3. 交付 source/config 差异、来源与输入 SHA、依赖锁定、训练命令、运行日志、
   best/final checkpoint、评估逐回合 CSV/JSON、回放视频及续训命令。
   不凭 reward 曲线宣称抓取完成。回放性能和物理接触必须另有证据。
4. 策略通过后按官方 export.py 做 ONNX/torch 数值检查与 layout 合约导出。
   .app 只能由官方 deploy.py 按 kk-policy-bundle/1 构建和校验，不自造 ZIP
   改后缀。网页/仿真可用官方 --allow-incomplete，但必须保留缺失运行时的
   notes 并明确它不等于硬件完整包；不伪造 reference.json 或 RKNN 转换结果。
   包含官方 runtime/web controller.js/wasm、模型、合约、FSM 和中文操作手册。
5. 配套本地网页 App 的接口需求：加载经过验证的包、连接/运行状态、任务开始、
   暂停/恢复、急停、复位、当前阶段、任务日志及评估记录导出；响应式电脑/
   手机界面。浏览器加载和传感接入需要实际验证，不能由包有效性推断。
6. 保留原 releases/v*/ 与 scenes/drafts/v*/ 字节。更新新版本清单哈希、
   版本索引与 changelog；验证后再提交/打标签，不改历史标签。
   使用完整工作区时执行 python tools/verify_release.py 与相关场景/任务检查。
   精简包没有完整历史文件，不能靠它通过全部历史发布校验。
7. 无需等待逐项确认即可推进已授权的安装、任务实现和训练；遇到付费服务、
   破坏性操作、真实设备部署或明确门槛阻塞时，报告具体原因。
   每个阶段报告实测结果、剩余风险和下一步，不把未跑过的检查写成 passed。

请先输出接手路径、输入完整性、检测到的 VM 资源与官方安装分支，随后实际执行。

## 将训练成果交回此 GitHub 仓库

保留原输入发布 handoff-2026-10-11 与其附件。不得重打该标签或替换旧附件。
开发源码、配置、参数依据、来源差异与评估记录放入有明确版本的目录，
在交接仓库新建 `codex/desk-sorting-training` 分支提交；已有同名分支时先核对状态。
不要把完整第三方 checkout、venv、缓存、密钥或训练临时文件加入 Git。
对于上游 checkout 中实现的任务，保留可应用到固定 revision 的源码补丁或项目层文件，
说明应用与复现方法，不要求原作者仓库接收你的改动。

检查通过后将 checkpoint、回放视频、策略导出和官方打包产物作为新的训练结果
Release 附件交付，采用新的版本/标签；记录附件 SHA-256、源代码 commit、训练
运行配置和实际验收结果。上传前核对访问权限、GitHub 文件限制与可用空间，
遇到配额或付费要求先报告，不自动购买。
禁止把未通过验收的实验命名为正式成功策略。可以交付明确标记的实验结果，
但要报告不足和继续训练命令。`.app` 必须按官方协议与工具构建并验证。

最终报告：官方门槛 A—F 的结果、实际训练时长与迭代、checkpoint 来源、
接触抓取评估与失败原因、可复现训练/续训/回放命令，以及 GitHub 成果链接。
本轮完成定义是有实际训练与评估证据，不是只完成依赖安装或绘制 reward 曲线。
