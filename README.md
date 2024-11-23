# Конфигурационное управление
Домашнее задание №1
## Вариант 21
### Задание 1
Разработать эмулятор для языка оболочки ОС. Необходимо сделать работу эмулятора как можно более похожей на сеанс shell в UNIX-подобной ОС.

Эмулятор должен запускаться из реальной командной строки, а файл с виртуальной файловой системой не нужно распаковывать у пользователя.

Эмулятор принимает образ виртуальной файловой системы в виде файла формата tar. Эмулятор должен работать в режиме GUI.

Ключами командной строки задаются:

      • Имя пользователя для показа в приглашении к вводу.
      
      • Путь к архиву виртуальной файловой системы.
      
      • Путь к log файлу.

Необходимо поддержать в эмуляторе команды ls, cd и exit, а также следующие команды:

1. clear.
2. cp.
   
Все функции эмулятора должны быть покрыты тестами, а для каждой из поддерживаемых команд необходимо написать 3 теста.

### Описание

Этот код реализует простой виртуальный эмулятор файловой системы с использованием архива tar, с графическим интерфейсом оболочки (GUI), построенным на Python с использованием библиотеки TKinter.
Программа создает эмулятор командной оболочки с графическим интерфейсом, который позволяет пользователю выполнять основные команды управления файлами и навигации в файловой системе, извлеченной из tar-архива. 
Пользователь может взаимодействовать с эмулятором через интерфейс, и все команды обрабатываются в фоновом режиме, предоставляя результаты в удобночитаемом формате.
![image](https://github.com/user-attachments/assets/7b974799-fd02-454b-8808-d957389850c6)
## Возможности 
**Список содержимого каталога** (`ls`) с поддержкой флагов: 
- `-l`: Формат длинного списка (права доступа, владелец, размер, дата последнего изменения).
- `-h`: Удобочитаемые размеры файлов.
  
**Изменение каталогов** (`cd`) в виртуальной файловой системе.
  
**Очистка консоли** (`clear`).

**Копирование файла или репозитория** (`cp`).

**Выход** (`exit`).

## Как запустить
1. Приложение можно запустить из командной строки, и для него требуются два обязательных аргумента:
  - `--user`: имя пользователя для отображения в приглашении оболочки.
  - `--vfs`: путь к файлу `.tar`, который служит виртуальной файловой системой.
2. При желании можно указать аргумент `--log`, чтобы указать путь к скрипту запуска (текстовый файл с командами оболочки), который будет выполняться при запуске оболочки.
##### Пример: ```bash python shell_emulator.py --user your_username --vfs path/to/vfs.tar --log path/to/log.csv ```
![image](https://github.com/user-attachments/assets/fc673734-46f0-4cec-b57e-28e67d0fbed0)


## Классы и функции 
### 1. `VirtualFileSystem` 
Этот класс имитирует файловую систему на основе архива `.tar`. 

**Конструктор (`__init__(self, tar_path)`)** 

- `tar_path`: путь к файлу `.tar`, который действует как виртуальная файловая система.
- Инициализирует виртуальную файловую систему и устанавливает текущий каталог в `/bs`.
  ![image](https://github.com/user-attachments/assets/400dbdf5-8a70-406a-9e18-aa30ef5c2eb3)


**`build_file_tree(self)`**

- Строит древовидную структуру из архива `.tar`, представляющую каталоги и файлы.
- Возвращает: словарь, представляющий дерево файлов.
  
**`list_dir(self, path)`** 

- Выводит список каталогов и файлов по указанному `path`. 
- `path`: Каталог для вывода списка.
- Возвращает: Два списка, один для каталогов и один для файлов.
  
**`change_dir(self, path)`**

 - Изменяет текущий каталог на указанный `path`. 
 - `path`: Каталог для перехода.
- Вызывает: `FileNotFoundError`, если каталог не существует.
  
**`copy(self, source, destination)`** 

- Копирует файл или каталог из виртуальной файловой системы.
 - `source`: Что копируем.
 - `destination`: Куда копируем.
   
**`get_node(self, path)`** 

- Извлекает узел (файл или каталог) для указанного `path`.
- `path`: Путь к узлу.
- Возвращает: Узел или `None`, если не найден.

### 2. `ShellEmulator` 
Этот класс реализует интерфейс оболочки с помощью `tkinter`.
![image](https://github.com/user-attachments/assets/fcc2ba94-659f-4285-b12f-d27fe0dce017)


**Конструктор (`__init__(self, root, username, vfs)`)**
 - `root`: Корневое окно `tkinter`. 
 - `username`: Имя пользователя для отображения в приглашении оболочки.
 - `vfs`: Экземпляр `VirtualFileSystem` для взаимодействия.

**`run_command(self, event)`**
 - Обрабатывает выполнение команды, когда пользователь нажимает Enter.
   
**`execute_command(self,command)`**
- Анализирует и выполняет команду оболочки, введенную пользователем.
  
**`ls(self, flags=[])`** 
- Выводит список содержимого текущего каталога.
- `flags`: Необязательные флаги (`-l`, `-h`) для вывода списка.
  
**`format_entry(self, entry, is_dir, flags)`** 
- Форматирует файл или каталог для отображения при использовании `ls -l`. 
- `entry`: Имя файла или каталога. 
- `is_dir`: Логическое значение, указывающее, является ли запись каталогом. 
- `flags`: Список флагов, переданных `ls`.
- Возвращает: Отформатированную строку.
  
**`human_readable_size(self, size)`** 
- Преобразует размер файла в удобочитаемый формат.
- `size`: Размер файла.
- Возвращает: Строку с размером в соответствующих единицах (Б, КБ, МБ и т. д.).
  
**`cd(self, path)`** 
- Изменяет текущий каталог на указанный путь.
- `path`: Каталог, в который необходимо перейти.
  
**`clear(self)`** 
- Очищает содержимое командной строки. 
  
**`cp(self, source, destination)`**
- Копирует указанный `source` в `destination`.
  
**`write_output(self, text)`** 
- Записывает `text` в окно вывода оболочки.
  
  ### 3. `main()` Основная точка входа программы.
  
  **`parser = argparse.ArgumentParser(...)`** 
  - Анализирует аргументы командной строки для имени пользователя, пути к виртуальной файловой системе и необязательного сценария запуска.
    
  **`vfs = VirtualFileSystem(args.vfs)`** 
  - Инициализирует виртуальную файловую систему из предоставленного архива `.tar`.
    
  **`root = tk.Tk()`**
   - Инициализирует корневое окно `tkinter` для интерфейса оболочки.
     
  **`shell = ShellEmulator(root, args.user, vfs)`**
   - Инициализирует эмулятор оболочки с виртуальной файловой системой и именем пользователя.
     
   **`if args.log:`** 
   - Если указан сценарий запуска, он будет выполнен путем вызова `execute_log()`.

  ### 4. `execute_log(log_path, shell)` Выполняет серию команд оболочки из файла сценария.
  
  - **`slog_path`:** Путь к файлу сценария.
    
  - **`shell`:** Экземпляр `ShellEmulator`, в котором будут выполнены команды.
## Результаты тестирования
![image](https://github.com/user-attachments/assets/f017eb96-25f3-4bfc-9ac6-dd6ed44646bb)
![image](https://github.com/user-attachments/assets/08419318-8f1c-4265-b417-c7f8fe8e2101)
![image](https://github.com/user-attachments/assets/6bc091c3-df6c-480e-be6b-f2ab43696df0)
![image](https://github.com/user-attachments/assets/7b974799-fd02-454b-8808-d957389850c6)
