# 抖音视频下载与文案提取工具

一款功能强大的抖音视频下载工具，专注于视频下载、音频提取和文案转写，支持批量处理，操作简单高效。

## ✨ 主要功能

- **视频下载**：通过API接口下载抖音视频，无水印高清版本
- **音频提取**：自动从视频中提取独立音频文件
- **文案识别**：使用先进的语音识别技术从音频中提取文案
- **批量处理**：支持批量导入链接、视频或音频文件进行处理
- **多引擎支持**：支持多种语音识别引擎，满足不同需求

## 🖥️ 系统要求

- Windows 10/11
- Python 3.8+ (推荐Python 3.9)
- 核心依赖：
  - PyQt6：用于图形界面
  - aiohttp：用于异步网络请求
  - ffmpeg：用于音频处理 (需单独安装)
  - openai-whisper：用于语音识别

## 📥 安装方法

### 方法一：从源码安装

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/douyin-downloader.git
   cd douyin-downloader
   ```

2. 创建虚拟环境 (推荐)：
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 安装FFmpeg:
   - Windows: 下载[FFmpeg](https://ffmpeg.org/download.html)并设置路径
   - Linux: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`

### 方法二：直接下载发布版本

1. 从[Releases](https://github.com/yourusername/douyin-downloader/releases)页面下载最新版本
2. 解压文件
3. 运行`douyindownloader.exe`

## 🚀 使用指南

### 下载抖音视频

本工具支持多种链接格式：

| 链接类型 | 示例 |
|---------|------|
| 短链接 | `https://v.douyin.com/iRNBho6u/` |
| 标准链接 | `https://www.douyin.com/video/7298145681699622182` |
| 分享文本 | `0.53 02/26 I@v.sE Fus:/ 你别太帅了# 现场版live # 音乐节 # 复制此链接，打开Dou音搜索，直接观看视频!` |

操作步骤：

1. 启动应用程序
2. 在文本框中粘贴一个或多个抖音链接（每行一个）
3. 点击"开始下载"按钮
4. 在日志窗口查看下载进度
5. 完成后，点击"查看视频"按钮打开下载目录

### 音频提取和文案识别

#### 方法一：从网络链接开始

1. 输入抖音链接，点击"开始下载"
2. 系统会自动下载视频、提取音频并识别文案
3. 完成后可点击"查看音频"或"查看文案"按钮查看结果

#### 方法二：从本地视频开始

1. 点击"导入视频"按钮
2. 选择要处理的视频文件（支持.mp4, .mov等格式）
3. 系统将自动提取音频并识别文案

#### 方法三：直接处理音频

1. 点击"导入音频"按钮
2. 选择要处理的音频文件（支持.mp3, .wav, .m4a等格式）
3. 系统将自动识别文案

## ⚙️ 高级设置

### API 参数配置

本工具使用远程API获取视频数据，默认接口：`http://47.83.189.189:1001/api/hybrid/video_data`

如果需要更改API设置：

1. 打开`config.json`文件
2. 修改以下参数：
   - `api_timeout`: API请求超时时间 (秒)
   - `max_retries`: 最大重试次数

### Cookie 设置

添加抖音Cookie可以提高下载成功率：

1. 点击"设置"按钮
2. 在Cookie设置区域粘贴您的抖音Cookie
3. 点击"确定"保存设置

### 语音识别引擎

#### Whisper (OpenAI)

本地离线识别，支持多种模型大小：

| 模型 | 内存需求 | 精度 | 速度 |
|-----|--------|-----|-----|
| tiny | 低 | 一般 | 极快 |
| base | 低 | 良好 | 快速 |
| small | 中 | 很好 | 中等 |
| medium | 高 | 优秀 | 较慢 |
| large | 极高 | 最佳 | 慢 |

设置方法：
1. 点击"设置"按钮
2. 选择"Whisper (OpenAI)"引擎
3. 选择合适的模型大小
4. 点击"确定"保存

#### PaddleSpeech

百度开源的语音识别引擎，中文支持良好：

```bash
# 安装PaddlePaddle
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple

# 安装PaddleSpeech
pip install paddlespeech -i https://mirror.baidu.com/pypi/simple
```

设置方法同上，选择"PaddleSpeech"引擎即可。

## 🔍 问题排查

### 下载失败

| 问题 | 可能原因 | 解决方法 |
|-----|---------|---------|
| API返回错误 | 链接格式错误 | 确保链接正确，优先使用短链接 |
| 未找到视频 | 视频已被删除或设为私密 | 尝试其他视频 |
| 请求超时 | 网络问题或服务器压力大 | 增加`api_timeout`值，检查网络 |
| Cookie无效 | Cookie已过期 | 更新Cookie |

### 音频提取失败

1. 检查FFmpeg路径是否正确设置
2. 检查视频文件是否完整
3. 尝试手动运行：
   ```bash
   ffmpeg -i [视频路径] -vn -acodec libmp3lame -q:a 4 [音频路径]
   ```

### 文案识别失败

1. 检查音频文件是否包含人声
2. 对于噪音大的音频，尝试使用更大的Whisper模型
3. 如使用PaddleSpeech出错，尝试切换到Whisper

## 📂 目录结构

```
douyin-downloader/
├── audio/             # 提取的音频文件
├── core/              # 核心功能模块
│   └── downloader.py  # 下载器核心代码
├── controllers/       # 控制器
├── lib/               # 第三方库
│   └── ffmpeg.exe     # FFmpeg程序(Windows)
├── text/              # 识别后的文案文件
├── ui/                # 用户界面
├── video/             # 下载的视频文件
├── config.json        # 配置文件
├── config.py          # 配置管理
├── main.py            # 程序入口
└── requirements.txt   # 依赖列表
```

## 🆕 更新日志

### v1.2.0 (当前版本)
- 移除浏览器依赖，全面使用API接口
- 优化下载逻辑和错误处理
- 完善文件命名和保存机制

### v1.1.0
- 添加PaddleSpeech引擎支持
- 改进用户界面
- 优化语音识别功能

### v1.0.0
- 初始版本发布

## 🤝 贡献指南

欢迎贡献代码或提出建议！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 📜 许可证

本项目采用 MIT 许可证 - 详情见 [LICENSE](LICENSE) 文件
