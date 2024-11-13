import os
import tarfile
import unittest
from io import StringIO
from contextlib import redirect_stdout
import tkinter as tk

# Импортируем ваши классы из основного кода
from config1 import VirtualFileSystem, ShellEmulator


class TestShellEmulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Путь к тестируемому архиву
        tar_path = r'C:\Users\Vovawork\PycharmProjects\config1\adm.tar'

        # Загружаем виртуальную файловую систему
        cls.vfs = VirtualFileSystem(tar_path)

        # Создаем фальшивое окно для работы Tkinter
        cls.root = tk.Tk()
        cls.shell = ShellEmulator(cls.root, "testuser", cls.vfs)

    def test_cd_root(self):
        """Тест команды cd на переход к корню (/)"""
        with redirect_stdout(StringIO()) as output:
            self.shell.execute_command('cd /')
            self.assertEqual(self.shell.vfs.current_dir, '/bs')  # Проверяем, что перешли в корень
            output_content = output.getvalue()
            self.assertNotIn("no such file or directory", output_content)

    def test_cd_media(self):
        """Тест команды cd на переход в каталог ~/names"""
        with redirect_stdout(StringIO()) as output:
            self.shell.execute_command('cd /names')  # Используем абсолютный путь вместо относительного ~/media
            self.assertEqual(self.shell.vfs.current_dir, '/bs/names')  # Проверяем, что перешли в нужную директорию
            output_content = output.getvalue()
            self.assertNotIn("no such file or directory", output_content)

    def test_ls(self):
        """Тест команды ls"""
        self.shell.execute_command('ls')
        output_content = self.shell.get_output_content()
        self.assertTrue(len(output_content) > 0)  # Проверяем, что вывод не пуст

    def test_ls_with_flags(self):
        """Тест команды ls с флагами"""
        self.shell.execute_command('ls -l')
        output_content = self.shell.get_output_content()
        self.assertTrue(len(output_content) > 0)  # Проверяем, что вывод не пуст

    def test_copy_file(self):
        """Тест команды cp"""
        self.vfs.copy('names/vadim.txt', 'names/vadim_copy.txt')
        self.assertIn('vadim_copy.txt', self.vfs.file_tree['bs']['names'])

    def test_exit(self):
        """Тест команды exit"""
        with self.assertRaises(SystemExit):  # Проверяем, что программа завершает работу
            self.shell.execute_command('exit')

    def test_command_not_found(self):
        """Тест неизвестной команды"""
        self.shell.execute_command('unknown_command')
        output_content = self.shell.get_output_content()
        self.assertIn("command not found", output_content)  # Проверяем вывод об ошибке

    @classmethod
    def tearDownClass(cls):
        cls.root.quit()


if __name__ == "__main__":
    unittest.main()