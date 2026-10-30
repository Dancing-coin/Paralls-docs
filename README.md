# Guoshang

Unreal Engine 5.8 县城守城 Demo。项目目标、正式范围与验收标准见 [PRD 入口](docs/PRD/README.md)，协作规范见 [AGENTS.md](AGENTS.md)。

## 获取项目

先安装 Git、Git LFS 和项目所需的 Unreal Engine 5.8：

```sh
git lfs install
git clone https://github.com/Dancing-coin/Paralls-.git
cd Paralls-
git lfs pull
```

打开 `Guoshang.uproject`。这是包含 C++ 源码的项目，需要安装适用于 Unreal Engine 的编译工具链；可从 `.uproject` 生成 IDE 工程文件，再编译编辑器目标。

## 版本控制

- `Config/`、`Content/`、`Source/`、`Scripts/`、`docs/` 和项目描述文件纳入版本控制。
- UE 二进制资产及部分美术源文件通过 Git LFS 保存，克隆时需要下载 LFS 对象。
- `Binaries/`、`DerivedDataCache/`、`Intermediate/`、`Saved/` 和 IDE 生成文件由本机生成，不上传。
- 外部美术资源的来源及授权记录见 `docs/art_resources/`；资源许可按各自记录执行。
