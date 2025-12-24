# vscode scripts

## 添加到环境变量

```bash
export PATH="$PATH:/opt/tong/dotfiles/vscode/scripts"

# echo to ~/.bashrc
echo 'export PATH="$PATH:/opt/tong/dotfiles/vscode/scripts"' >> ~/.bashrc
```

## 使用说明

- [√] 查看所以已安装组件 : `install_vscode_extensions.sh -l`
- [√] 查看指定 group 安装信息 : `install_vscode_extensions.sh -l -g cpp`
    - group 列表在 `extesions` 下
    - [已安装，版本有变化，未安装]

- [√] 安装指定 extension 组件  : `install_vscode_extensions.sh -i alefragnani.bookmarks`
    - `-f` 强制更新版本不一致组件
- [√] 安装指定 group 组件列表  : `install_vscode_extensions.sh -i '*' -g cpp`
    - `-f` 强制更新版本不一致组件
    - 加 `-dir .` (vscode工作目录) ，会添加`language-settings`下对应group相关设置到 `./.vscode/settings.json`

---

### TODO

- [-] 安装指定 group 的 `lauch` 默认配置；
- [-] 安装指定 group 的 `snippets` 默认配置；
- [-] 安装指定 group 的 所需包到系统 `apt`；

---

## vscode 相关指令

```bash
code --list-extensions
code --list-extensions --show-versions

code --install-extension $extension
```

## mermaid.min.js

- 11.12.2
- <https://cdn.jsdelivr.net/npm/mermaid@11.12.2/dist/mermaid.min.js>
- file:///opt/tong/ws/git_repo/dotfiles/vscode/assets/mermaid.min.js

- 启动 web服务 （浏览器安全问题，不能直接 import 文件）
    - 直接启动脚本 `python3 scripts/start_http.py`

```bash
python3 -m http.server 8000 --bind localhost
```
