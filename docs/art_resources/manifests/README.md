# Manifest 目录

每个资产版本使用 `<asset_id>/<version>.yaml`，内容以 `../asset_manifest_template.yaml` 为模板。未知的来源、校验和、UE 路径或证据必须明确写 `unknown` 或 `null`，不得用猜测值填充。

`verification.historical` 记录旧流程已经做过的视口/关卡检查，`verification.governance` 记录当前资源治理准入；二者不能互相替代。治理状态不是 `passed` 时，生命周期不得写为“已验证”或“已用于 Demo”，也不得填写正式 `storage.approved_path`。
