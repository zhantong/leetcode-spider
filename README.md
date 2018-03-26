# LeetCode-Spider

Python实现的LeetCode爬虫。爬取LeetCode题目描述和提交的代码。

## 特点

- 支持爬取题目列表，保存为本地CSV/Excel文件。
- 支持爬取题目描述，保存为本地HTML文件。
- 支持爬取用户提交的代码，保存为如_.py、_.java、\*.cpp等源码。
- 高速并发下载题目描述和提交的代码。
- 支持增量更新，当本地有缺损或LeetCode有新内容（题目/提交的代码）时，以增量形式更新。

## 使用

参考example.py。

### 克隆或下载本仓库

使用`git clone`或直接下载本仓库代码，并切换工作目录到本项目根目录

### 安装依赖

本项目需要用到第三方库`lxml`和`openpyxl`（如果需要保存为Excel），可通过如下`pip`命令安装：

```bash
pip3 install lxml
pip3 install openpyxl
```

### 获取问题列表（必须）

```python
from Extractor import Extractor

extractor = Extractor()

# 获取问题列表（保存在数据库leetcode.db中，若希望获取问题状态（是否ac），需首先登录）
# extractor.login('foo@bar.com', '123456')
extractor.update_problem_list()
```

获取得到的数据保存在leetcode.db数据库中。

### 导出问题列表

可将问题列表导出为CSV/Excel格式文件，参考下面的截图。

```python
# 导出问题列表为中文CSV文件
extractor.save_problem_list('problems.csv')

# 导出问题列表为英文Excel文件
extractor.save_problem_list('problems.xlsx', 'excel', 'English')
```

![CSV][csv]

![Excel][excel]

### 获取问题描述HTML文件

**需先获取问题列表**

```python
# 获取问题描述HTML文件（保存在descriptions文件夹下，需要先获取问题列表）
extractor.update_descriptions()
```

根据问题列表增量多线程并发下载新的问题描述，并将HTML文件保存到descriptions文件夹下。文件夹结构为：

```
descriptions
    001. Two Sum.html
    002. Add Two Numbers.html
    003. Longest Substring Without Repeating Characters.html
    ...
```

### 获取提交的代码

**需先获取问题列表**

```python
# 获取提交的代码（保存在submissions文件夹下，需要先获取问题列，并登录）
extractor.login('foo@bar.com', '123456')
extractor.update_submissions()
```

这里需要先输入用户名和密码登录，然后才能获取到此用户提交的代码。

根据问题列表增量多线程并发下载新的提交代码，并将其保存到submissions文件夹下。文件夹结构为：

```
submissions
    24152714
    24153189
    24165875
    ...
```

### 导出提交的代码

**需先获取提交的代码**

```python
# 导出提交的代码（保存在out_submissions文件夹下，需先获取提交的代码）
extractor.output_submissions()
```

导出之前保存的文件为格式化文件结构（默认仅导出每种语言的最新提交版本），保存到out_submissions文件夹下。文件夹结构为：

```
out_submissions
    001. Two Sum
        C++
            Solution.cpp
        Java
            Solution.java
        Python
            Solution
    002. Add Two Numbers
        C++
            Solution.cpp
        Java
            Solution.java
        Python
            Solution
    ...
```

[csv]: screenshot/csv.png

[excel]: screenshot/excel.png
