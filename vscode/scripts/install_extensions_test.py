import unittest
import install_extensions
import logging
from install_extensions import ExtensionInstaller
from install_extensions import ExtensionInfo

class TestInstallExtensions(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.installer = ExtensionInstaller()
        
    def test_GetInstalledExtensionsList(self):
        extensions = install_extensions.GetInstalledExtensionsList()
        self.assertIsInstance(extensions, list)
        
        
        for ext in extensions:
            ext_info = ExtensionInfo(ext)  # Should not raise any exception
            self.assertEqual(str(ext_info), ext)    
            logging.info(f"Extension Info: {ext_info}")
            
    def test_is_installed(self):
        extensions = install_extensions.GetInstalledExtensionsList()
        if extensions:
            ext_info = ExtensionInfo(extensions[0])
            self.assertTrue(self.installer.is_installed(ext_info))
        else:
            self.skipTest("No extensions installed to test is_installed method.")
            
    def test_list_extensions_files(self):
        files = install_extensions.ExtensionInstaller.list_extensions_files()
        for file in files:
            logging.info(f"Extension file found: {file}")
            
    def test_list_extensions_file_context(self):
        files = install_extensions.ExtensionInstaller.list_extensions_files()
        for file in files:
            context = install_extensions.ExtensionInstaller.list_extensions_file_context(file)
            # logging.info(f"Extension file context for {file}: {context}")

            
        
if __name__ == '__main__':
    unittest.main()