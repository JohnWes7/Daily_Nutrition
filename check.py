from src import tool

module_dict = {
    'lxml' : 'lxml',
    'selenium' : 'selenium'
}


if __name__ == '__main__':
    tool.check_module(module_dict)