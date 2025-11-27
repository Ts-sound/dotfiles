import argparse, os, glob, logging, json
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[%(asctime)s - %(levelname)s %(funcName)s:%(lineno)d]: %(message)s")

filepath = str(Path(__file__).resolve().parent)
logging.info(f"workpath: {filepath}")

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
            logging.warning(f"Invalid extension format: {ext}")
    logging.info(f"Installed extensions: {valid_extensions}")
    
    return valid_extensions

class ExtensionInstaller:
    def __init__(self):
        # get installed extensions [ExtensionInfo]
        self.installed_extensions = [ExtensionInfo(ext) for ext in GetInstalledExtensionsList()]
        self.extensions_files = ExtensionInstaller.list_extensions_files()
        # dict {file_shortname: (file,[extensions])}
        self.extensions_file_context_dict = [{  Path(file).stem : (file,ExtensionInstaller.list_extensions_file_context(file))} for file in self.extensions_files]
        logging.info(f"Extensions files context dict: {self.extensions_file_context_dict}")
        
    def is_installed(self, extension:ExtensionInfo) -> bool:
        ret = [ext for ext in self.installed_extensions if ext.equals(extension, is_compare_version=True)]
        return len(ret) > 0
    
    def install_extension(self, extension:ExtensionInfo):
        if self.is_installed(extension):
            logging.info(f"Extension {extension} is already installed.")
            return
        
        cmd = f"code --install-extension {str(extension)}"
        logging.info(f"Installing extension: {extension} with command: {cmd}")
        result = os.popen(cmd).read()
        logging.info(f"Installation result: {result}")
        
    def list_extensions_files() -> list:
        '''
            list extensions file in ../extensions/*.txt
        '''
        files = glob.glob(os.path.join(filepath, '../extensions/*.txt'))
        # return absolute paths
        files = [os.path.abspath(f) for f in files]
        logging.info(f"Found extension files: {files}")
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
        logging.info(f"Extensions in file {file}: {extensions}")
        return extensions