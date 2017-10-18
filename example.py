from Extractor import Extractor

extractor = Extractor()

# 获取问题列表（保存在数据库leetcode.db中）
extractor.update_problem_list()

# 获取问题描述HTML文件（保存在descriptions文件夹下，需要先获取问题列表）
extractor.update_descriptions()

# 获取提交的代码（保存在submissions文件夹下，需要先获取问题列，并登录）
extractor.login('foo@bar.com', '123456')
extractor.update_submissions()

# 导出提交的代码（保存在out_submissions文件夹下，需先获取提交的代码）
extractor.output_submissions()
