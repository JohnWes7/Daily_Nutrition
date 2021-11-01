import os
import random
import cv2
import numpy
from config import config


def copy_random_img(pool_path: str, drec_dir_path: str):
    if os.path.exists(pool_path):
        filelist = os.listdir(pool_path)
        img_list = filename_filtrate(filelist, '.png', '.jpg')

        index = random.randint(0,img_list.__len__()-1)
        file_name = f'{pool_path}{img_list[index]}'
        print(file_name)
        img_data = cv2.imdecode(numpy.fromfile(file=file_name,dtype=numpy.uint8), cv2.IMREAD_COLOR)

        # cv2.imshow('tutu',img_data)
        # cv2.waitKey(0)
        cv2.imwrite(drec_dir_path, img_data)
        print(f'{file_name} to {drec_dir_path}')

        
        
    else:
        print(f'文件夹不存在：{pool_path}')


def filename_filtrate(filenamelist: list, *suffix):
    ans_list = []

    for name in filenamelist:
        temp = os.path.splitext(name)
        suf = temp[temp.__len__() - 1]
        suf = str(suf)

        for item in suffix:
            if suf.__eq__(str(item)):
                ans_list.append(name)
                break

    return ans_list


if __name__ == '__main__':

    copy_random_img(config.backgroun_pool_path, config.background_dir_path + 'background.png')
    print('done')
    