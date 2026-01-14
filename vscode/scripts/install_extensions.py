import argparse, os, glob, logging, json
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[%(asctime)s - %(levelname)s %(funcName)s:%(lineno)d]: %(message)s")

filepath = str(Path(__file__).resolve().parent)
logging.debug(f"workpath: {filepath}")


class ExtensionInfo:
    def __init__(self, name: str):
        self.version = (name.split("@")[1]) if "@" in name else None
        self.name = (name.split("@")[0]) if "@" in name else name
        self.vendor = self.name.split(".")[0]
        self.name = self.name.split(".")[1]

        # TODO: to lower
        self.name = self.name.lower()
        self.vendor = self.vendor.lower()

    def get_without_version(self):
        return f"{self.vendor}.{self.name}"

    def equals(self, other, is_compare_version=True) -> bool:
        return (self.vendor == other.vendor and self.name == other.name) and (self.version == other.version if is_compare_version else True)

    def __repr__(self):
        return f"{self.vendor}.{self.name}@{self.version}" if self.version else f"{self.vendor}.{self.name}"


def GetInstalledExtensionsList() -> list:
    """
    code --list-extensions --show-versions
    """
    cmd = "code --list-extensions --show-versions"
    result = os.popen(cmd).readlines()
    extensions = [line.strip() for line in result if line.strip()]
    # pattern like EFanZh.graphviz-preview@1.7.2
    pattern = f"^([a-zA-Z0-9_.-]+)@([0-9.]+)$"
    import re

    valid_extensions = []
    for ext in extensions:
        match = re.match(pattern, ext)
        if match:
            valid_extensions.append(ext)
        else:
            logging.debug(f"warning: Invalid extension format: {ext}")
    logging.debug(f"Installed extensions: {valid_extensions}")

    return valid_extensions


class ExtensionInstaller:
    def __init__(self):
        # get installed extensions [ExtensionInfo]
        self.installed_extensions = [ExtensionInfo(ext) for ext in GetInstalledExtensionsList()]
        self.extensions_files = ExtensionInstaller.list_extensions_files()
        # dict {file_shortname: (file,[extensions])}
        self.extensions_file_context_dict = {Path(file).stem: (file, ExtensionInstaller.list_extensions_file_context(file)) for file in self.extensions_files}
        logging.debug(f"Extensions files context dict: {self.extensions_file_context_dict}")

    def is_installed(self, extension: ExtensionInfo, is_compare_version=True) -> bool:
        ret = [ext for ext in self.installed_extensions if ext.equals(extension, is_compare_version=is_compare_version)]
        return len(ret) > 0

    def get_installed_extension(self, extension: ExtensionInfo, is_compare_version=True) -> ExtensionInfo:
        ret = [ext for ext in self.installed_extensions if ext.equals(extension, is_compare_version=is_compare_version)]
        return ret[0] if len(ret) > 0 else None

    def get_target_group_settings(self, group: str):
        """
        file in ../language-settings/[group].json
        """

        file = os.path.join(filepath, "../language-settings/", f"{group}.json")
        if not os.path.exists(file):
            return None

        with open(file, "r") as f:
            try:
                settings = json.load(f)
                logging.info(f"Loaded settings for group {group} from {file}: {settings}")
            except json.JSONDecodeError:
                logging.error(f"errSettings file [{file}] is not a valid JSON.")
                exit(1)
            return settings
        return None

    def install_extension(self, extension: ExtensionInfo):
        if self.is_installed(extension):
            logging.debug(f"Extension {extension} is already installed.")
            return

        cmd = f"code --install-extension {str(extension)}"
        logging.info(f"Installing extension:  with command: {cmd}")
        result = os.popen(cmd).read()
        logging.info(f"result: {result}")

    def list_extensions_files() -> list:
        """
        list extensions file in ../extensions/*.txt
        """
        files = glob.glob(os.path.join(filepath, "../extensions/*.txt"))
        # return absolute paths
        files = [os.path.abspath(f) for f in files]
        logging.debug(f"Found extension files: {files}")
        return files

    def list_extensions_file_context(file: str):
        """
        list extensions in the given file
        """
        if not os.path.exists(file):
            logging.error(f"File {file} does not exist.")
            return []

        with open(file, "r") as f:
            lines = f.readlines()

        extensions = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
        logging.debug(f"Extensions in file {file}: {extensions}")
        return extensions


###
class GroupExtensionsInstallDetail:
    def __init__(self, installer: ExtensionInstaller, group: str):
        path, group_exts = installer.extensions_file_context_dict[args.group]

        # installed and version compatible
        self.install_exts = [ext for ext in group_exts if installer.is_installed(ExtensionInfo(ext))]

        # installed but version not compatible
        self.install_exts_version_not_compatible = [ExtensionInfo(ext) for ext in group_exts if installer.is_installed(ExtensionInfo(ext), is_compare_version=False) and ext not in self.install_exts]

        # not installed
        self.not_install_exts = [ext for ext in group_exts if not installer.is_installed(ExtensionInfo(ext), is_compare_version=False)]


#####


def handle_list_installed_with_group(installer: ExtensionInstaller, group: str):
    group_detail = GroupExtensionsInstallDetail(installer, group)

    logging.info(f"{group} Installed Extensions --- :] ")
    for ext in group_detail.install_exts:
        logging.info(f"{ext}")

    logging.info(f"\n{group} Installed Extensions with different version --- :] ")
    for ext in group_detail.install_exts_version_not_compatible:
        logging.info(f"installed: [{installer.get_installed_extension(ext,False)}], wanted version: [{ext.version}]")

    logging.info(f"\n{group} Not Installed Extensions --- :] ")
    for ext in group_detail.not_install_exts:
        logging.info(f"{ext}")
    return


def handle_install_target_group(installer: ExtensionInstaller, install_pattern: str, group: str, dot_vscode_work_dir, force: bool = False):
    group_detail = GroupExtensionsInstallDetail(installer, group)

    # install not installed extensions
    for ext in group_detail.not_install_exts:
        if install_pattern == "*" or ext == install_pattern:
            installer.install_extension(ExtensionInfo(ext))

    # force reinstall extensions with different version
    if force:
        for ext in group_detail.install_exts_version_not_compatible:
            installer.install_extension(ext)

    # add recommendations settins to .vscode/settings.json
    settings = installer.get_target_group_settings(group)
    if settings and dot_vscode_work_dir:
        # add to dot_vscode_work_dir/.vscode/settings.json
        vscode_settings_file = os.path.join(dot_vscode_work_dir, ".vscode", "settings.json")
        os.makedirs(os.path.dirname(vscode_settings_file), exist_ok=True)
        if os.path.exists(vscode_settings_file):
            with open(vscode_settings_file, "r") as f:
                try:
                    existing_settings = json.load(f)
                except json.JSONDecodeError:
                    logging.error(f"err: Existing settings file [{vscode_settings_file}] is not a valid JSON.")
                    exit(1)

        else:
            existing_settings = {}

        # merge settings , -force replace existing keys
        for key, value in settings.items():
            if key in existing_settings:
                if force:
                    logging.info(f"Overriding existing setting {key} in {vscode_settings_file}")
                    existing_settings[key] = value
                else:
                    logging.info(f"Setting {key} already exists in {vscode_settings_file}, skipping. Use --force to override.")
                    continue
            else:
                logging.debug(f"Adding new setting {key} to {vscode_settings_file}")
                existing_settings[key] = value

        with open(vscode_settings_file, "w") as f:
            json.dump(existing_settings, f, indent=4)
            logging.info(f"Updated settings written to {vscode_settings_file}")
    return


def handle_install_specific_extension(installer: ExtensionInstaller, install_extension: str, force: bool = False):
    ext_info = ExtensionInfo(install_extension)

    if not installer.is_installed(ext_info):
        installer.install_extension(ext_info)
    else:
        if force:
            installer.install_extension(ext_info)
        else:
            logging.info(f"Extension {install_extension} is already installed. Use --force to reinstall.")
    return


def main(args=None):

    logging.basicConfig(level=logging.INFO, format="%(message)s", force=True)

    # args empty
    if args is None:
        argparse.print_help()
        return

    # args
    list_installed = args.list_installed
    group = args.group
    install = args.install
    dot_vscode_work_dir = args.dot_vscode_work_dir
    if (dot_vscode_work_dir) and (dot_vscode_work_dir.strip() == "."):
        # get terminal current working dir
        dot_vscode_work_dir = os.getcwd()
    elif dot_vscode_work_dir:
        if not os.path.exists(dot_vscode_work_dir):
            logging.error(f"dot_vscode_work_dir {dot_vscode_work_dir} does not exist!")
            return

    else:
        dot_vscode_work_dir = None

    installer = ExtensionInstaller()

    if list_installed and not group:
        extensions = GetInstalledExtensionsList()
        logging.info("Installed Extensions --- :] ")
        for ext in extensions:
            logging.info(f"{ext}")

        logging.info("Installed Extensions but not in recommendations(ignore version) --- :] ")
        recommendations = set()
        for exts in installer.extensions_file_context_dict.values():
            recommendations = recommendations | set(exts[1])

        not_in_func = lambda ext, rec_set: all([not ExtensionInfo(ext).equals(ExtensionInfo(rec), is_compare_version=False) for rec in rec_set])

        not_in_recommendations = [ext for ext in extensions if not_in_func(ext, recommendations)]
        for ext in not_in_recommendations:
            logging.info(f"{ext}")

        return

    if list_installed and group:
        handle_list_installed_with_group(installer, group)
    elif install and group:
        handle_install_target_group(installer, install, group=group, dot_vscode_work_dir=dot_vscode_work_dir, force=(args.force if args.force is None else False))
    elif install and not group:
        handle_install_specific_extension(installer, install, force=(args.force if args.force is None else False))
    else:
        argparse.print_help()
    return


if __name__ == "__main__":
    argparse = argparse.ArgumentParser(description="VSCode Extension Installer Script")
    argparse.add_argument("--install", "-i", type=str, help="Install the specified extension (format: vendor.name@version) , * for all")
    argparse.add_argument("--group", "-g", type=str, help="all,cpp,python,rust ..., group name to install extensions from  extensions/[group].txt")
    argparse.add_argument("--list-installed", "-l", action="store_true", help="List all installed extensions")
    argparse.add_argument("--force", "-f", action="store_true", help="Force reinstall even if the extension is already installed")
    argparse.add_argument("--dot_vscode_work_dir", "-dir", type=str, help="work dir with .vscode directory in, default is None")
    args = argparse.parse_args()
    main(args)
