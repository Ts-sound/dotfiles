import argparse, os, glob, logging, json
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[%(asctime)s - %(levelname)s %(funcName)s:%(lineno)d]: %(message)s")

filepath = str(Path(__file__).resolve().parent)
logging.debug(f"workpath: {filepath}")

class ExtensionInfo:
    def __init__(self, name:str):
        self.version = name.split('@')[1]
        self.name = name.split('@')[0]
        self.vendor = self.name.split('.')[0]
        self.name =  self.name.split('.')[1]
        
    def get_without_version(self):
        return f"{self.vendor}.{self.name}"
    
    def equals(self, other,is_compare_version=True) -> bool:
        return (self.vendor == other.vendor and self.name == other.name) and (self.version == other.version if is_compare_version else True)

    def __repr__(self):
        return f"{self.vendor}.{self.name}@{self.version}" if self.version else f'{self.vendor}.{self.name}'
    

def GetInstalledExtensionsList() -> list:
    '''
     code --list-extensions --show-versions
    '''
    cmd = "code --list-extensions --show-versions"
    result = os.popen(cmd).readlines()
    extensions = [line.strip() for line in result if line.strip()]
    # pattern like EFanZh.graphviz-preview@1.7.2
    pattern = f'^([a-zA-Z0-9_.-]+)@([0-9.]+)$'
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
        
    def is_installed(self, extension:ExtensionInfo,is_compare_version=True) -> bool:
        ret = [ext for ext in self.installed_extensions if ext.equals(extension, is_compare_version=is_compare_version)]
        return len(ret) > 0
    
    def get_installed_extension(self, extension:ExtensionInfo,is_compare_version=True) -> ExtensionInfo:
        ret = [ext for ext in self.installed_extensions if ext.equals(extension, is_compare_version=is_compare_version)]
        return ret[0] if len(ret) > 0 else None
    
    def install_extension(self, extension:ExtensionInfo):
        if self.is_installed(extension):
            logging.debug(f"Extension {extension} is already installed.")
            return
        
        cmd = f"code --install-extension {str(extension)}"
        logging.info(f"Installing extension:  with command: {cmd}")
        result = os.popen(cmd).read()
        logging.info(f"result: {result}")
        
    def list_extensions_files() -> list:
        '''
            list extensions file in ../extensions/*.txt
        '''
        files = glob.glob(os.path.join(filepath, '../extensions/*.txt'))
        # return absolute paths
        files = [os.path.abspath(f) for f in files]
        logging.debug(f"Found extension files: {files}")
        return files
    
    def list_extensions_file_context(file:str):
        '''
            list extensions in the given file
        '''
        if not os.path.exists(file):
            logging.error(f"File {file} does not exist.")
            return []
        
        with open(file, 'r') as f:
            lines = f.readlines()
        
        extensions = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
        logging.debug(f"Extensions in file {file}: {extensions}")
        return extensions

###
class GroupExtensionsInstallDetail:
    def __init__(self, installer:ExtensionInstaller, group:str):
        path,group_exts = installer.extensions_file_context_dict[args.group]
        
        # installed and version compatible
        self.install_exts=[ext for ext in group_exts if installer.is_installed(ExtensionInfo(ext))]
        
        # installed but version not compatible
        self.install_exts_version_not_compatible = [ExtensionInfo(ext) for ext in group_exts if installer.is_installed(ExtensionInfo(ext),is_compare_version=False) and  ext not in self.install_exts]
        
        # not installed
        self.not_install_exts = [ext for ext in group_exts if not installer.is_installed(ExtensionInfo(ext),is_compare_version=False)]

#####


def handle_list_installed_with_group(installer:ExtensionInstaller, group:str):
    group_detail = GroupExtensionsInstallDetail(installer,group)
    
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

def handle_install_target_group(installer:ExtensionInstaller,install_pattern:str, group:str, force:bool=False):
    group_detail = GroupExtensionsInstallDetail(installer,group)
    
    # install not installed extensions
    for ext in group_detail.not_install_exts:
        if(install_pattern=="*" or ext==install_pattern):
            installer.install_extension(ExtensionInfo(ext))
    
    # force reinstall extensions with different version
    if(force):
        for ext in group_detail.install_exts_version_not_compatible:
            installer.install_extension(ext)
    return

def main(args=None):
    
    logging.basicConfig(level=logging.INFO, format="%(message)s",force=True)
    
    # args empty
    if args is None:
        argparse.print_help()
        return
    
    # args
    list_installed = args.list_installed
    group = args.group
    install = args.install
   
    if(list_installed and not group):
        extensions = GetInstalledExtensionsList()
        logging.info("Installed Extensions --- :] ")
        for ext in extensions:
            logging.info(f"{ext}")
        return
    
    installer = ExtensionInstaller()
    
    if(list_installed and group):
        handle_list_installed_with_group(installer, group)
    elif(install and group):
        handle_install_target_group(installer,install, group, force= (args.force  if args.force is None else False))
    return

if __name__ == '__main__':
    argparse = argparse.ArgumentParser(description="VSCode Extension Installer Script")
    argparse.add_argument('--install','-i', type=str, help="Install the specified extension (format: vendor.name@version) , * for all")
    argparse.add_argument('--group','-g', type=str, help="all,cpp,python,rust ..., group name to install extensions from  extensions/[group].txt")
    argparse.add_argument('--list-installed','-l', action='store_true', help="List all installed extensions")
    argparse.add_argument('--force','-f', type=bool, help="Force reinstall even if the extension is already installed")
    args = argparse.parse_args()
    main(args)