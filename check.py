from src import tool

module_dict = {
    'lxml' : 'lxml',
    'selenium' : 'selenium',
}


if __name__ == '__main__':
    print('模组检测：')
    tool.check_module(module_dict)
    print()

    print('代码更新')
    input('done')