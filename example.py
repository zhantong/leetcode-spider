from Extractor import Extractor

extractor = Extractor()

# 获取问题列表（保存在数据库leetcode.db中，若希望获取问题状态（是否ac），需首先登录）
# extractor.login('foo@bar.com', '123456')
extractor.update_problem_list()

# 导出问题列表为中文CSV文件
extractor.save_problem_list('problems.csv')

# 导出问题列表为英文Excel文件
extractor.save_problem_list('problems.xlsx', 'excel', 'English')

# 获取问题描述HTML文件（保存在descriptions文件夹下，需要先获取问题列表）
extractor.update_descriptions()

# 获取提交的代码（保存在submissions文件夹下，需要先获取问题列，并登录）
extractor.login('foo@bar.com', '123456')
extractor.update_submissions()

# 导出提交的代码（保存在out_submissions文件夹下，需先获取提交的代码）
extractor.output_submissions()
