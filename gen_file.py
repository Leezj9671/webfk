#!/usr/bin/env python
# encoding: utf-8

import os

# 在当前目录下创建
root_path = os.getcwd()

# 目录列表
directory_list = [
    'dbconnector',
    'exceptions',
    'helper',
    'route',
    'session',
    'template_engine',
    'view',
    'wsgi_adapter'
]

# 子文件
children = {'name': '__init__.py', 'children': None, 'type': 'file'}

# 目录结构
dir_map = [{
    # name 为框架的名字，记得修改好名字，不然脚本运行会报错，建议使用与后续实验匹配的“sylfk”来命名
    'name': "sylfk",
    'children': [{
        'name': directory,
        'type': 'dir',
        'children': [children]
    } for directory in directory_list] + [children],
    'type': 'dir'
}]


# 创建文件夹或者文件
def create(path, kind):
    if kind == 'dir':
        os.mkdir(path)
    else:
        open(path, 'w').close()


# 递归创建目录
def gen_project(parent_path, map_obj):
    for line in map_obj:
        path = os.path.join(parent_path, line['name'])
        create(path, line['type'])
        if line['children']:
            gen_project(path, line['children'])


# 脚本入口
def main():
    gen_project(root_path, dir_map)


if __name__ == '__main__':
    main()