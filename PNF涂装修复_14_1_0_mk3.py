#! /usr/bin/env python3
# coding:utf-8

import os
import sys
import re
import importlib
importlib.reload(sys)
import warnings
warnings.filterwarnings("ignore")

import xml.etree.ElementTree as ET
from xml.dom import minidom

def prettify(elem):
    """
    将节点转换成字符串，并添加缩进。
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

def file_extension(path):
  return os.path.splitext(path)[1]

def listFiles(dirPath):
    fileList=[]
    for root,dirs,files in os.walk(dirPath):
        for fileObj in files:
            fileList.append(os.path.join(root,fileObj))
    return fileList

def main(fileDir):
    print('scaning')
    p1 = r"(PnFMods/[^/]*/[^/]*/)"
    p2 = r"(./[^\\]*\\)"
    p3 = r"(PnFMods/[^/]*/[^/]*/[^/]*/)"
    fileList = listFiles(fileDir)
    for fileObj in fileList:
        if file_extension(fileObj) == '.model':
            # 找到第一个model文件
            if not ('lod' in fileObj):
                fileObj_m = fileObj # 不影响原变量
                flag_model = 1      # 是否有下一级model文件
                flag_visual = 1     # 是否有visual文件
                num_model = 1       # 需要组合的model文件数目(以1开始,第一个不进行计数)
                num_visual = 0      # 需要组合的visual文件数目
                i = 0               # render节点数目记录 用于后续lod节点写入
                name_v = []         # name节点所对应的值
                flag_old = 0             # 是否为新版本model

                FileName_m = re.sub(p2, '', str(fileObj_m))     # 获取需新建model文件的名称
                FileAdderss_m = str(fileObj_m)                       # 获取需新建model文件的地址

                # 提前读取一次model文件内容,以确认是否为新版本model文件
                print(fileObj_m)
                xmlstring = fileObj_m
                tree_m = ET.parse(xmlstring)
                root_m = tree_m.getroot()

                # 检测是否为旧版本model文件
                # 当前检测原理:检测内部是否有 旧版本含有的extent节点
                for elem in root_m.iter('extent'):
                    flag_old = 1

                if flag_old:
                    while(flag_model):
                        # 初始化标识符
                        flag_model = 0  # 是否有下一级model文件
                        flag_visual = 0 # 是否有visual文件

                        # 读取model文件内容
                        # print(fileObj_m)
                        xmlstring = fileObj_m
                        tree_m = ET.parse(xmlstring)
                        root_m = tree_m.getroot()
                        elem = root_m

                        # 开始进行处理
                        print('start')

                        # 建立生成的model文件基础
                        if num_model == 1:
                            print(elem.tag)
                            n_root_m = ET.Element(elem.tag)     # 创建需生成的model文件的根节点
                            n_visual_m = ET.SubElement(n_root_m, 'visual')  # 创建子节点 visual
                            n_animations_m = ET.SubElement(n_root_m, 'animations')  # 创建子节点 animations
                            n_dyes_m = ET.SubElement(n_root_m, 'dyes')              # 创建子节点 dyes        目前留空,不做处理
                            n_metaData_m = ET.SubElement(n_root_m, 'metaData')      # 创建子节点 metaData

                            # 处理model文件的metaData节点
                            for elem in root_m.iter('metaData'):
                                n_metaData_m.text = elem.text

                            # 处理model文件的 animations节点
                            for elem in root_m.iter('animations'):
                                elem_1 = elem.find('animation')
                                n_animations_m.append(elem_1)

                        # 查找下一级model文件路径
                        for elem in root_m.iter('parent'):
                            # 处理掉路径中多余的部分
                            key = elem.text
                            Address_m = re.sub('\t', '', key)
                            Address_m = Address_m + '.model'
                            newline = re.sub(p1,'./', Address_m)
                            flag_model = 1
                            num_model = num_model + 1
                            fileObj_m = newline
                            print('next model:', newline)
                            pass

                        # 查找对应visual文件路径
                        for elem in root_m.iter('nodefullVisual'):
                            # 处理掉多余的路径
                            key = elem.text
                            Address_v = re.sub('\t*', '', key)
                            Address_v = Address_v + '.visual'
                            newline_v = re.sub(p1, './', Address_v)
                            fileObj_v = newline_v
                            flag_visual = 1
                            num_visual = num_visual + 1
                            print('visual:', newline_v)
                            pass

                        # 处理model文件的visual节点
                        if num_visual == 1:         # 为第一个visual文件(由于两者命名相同)
                            n_visual_m.text = Address_v   # 给子节点visual赋值
                            FileName_v = re.sub(p3, '', Address_v)      # 获取需新建visual文件的名称
                            FileAdderss_v = str(fileObj_v)                   # 获取需新建visual文件的地址

                        # 是否存在对应visual文件
                        if flag_visual == 1:
                            # 读取visual文件内容
                            print(fileObj_v)
                            xmlstring = fileObj_v
                            tree_v = ET.parse(xmlstring)
                            root_v = tree_v.getroot()
                            elem = root_v

                            # 建立生成的visual文件基础
                            if num_visual == 1:
                                print(elem.tag)
                                n_root_v = ET.Element(elem.tag)  # 创建需生成的visual文件的根节点
                                n_skeleton_v = ET.SubElement(n_root_v, 'skeleton')  # 创建子节点 skeleton
                                n_properties_v = ET.SubElement(n_root_v, 'properties')  # 创建子节点 properties
                                n_boundingBox_v = ET.SubElement(n_root_v, 'boundingBox')  # 创建子节点 boundingBox
                                n_renderSets_v = ET.SubElement(n_root_v, 'renderSets')  # 创建子节点 renderSets
                                n_lods_v = ET.SubElement(n_root_v, 'lods')  # 创建子节点 lods

                            # 读取第一级visual文件的node数据  后续层级均相同且新文件中无需重复
                            if num_visual == 1:
                                n_node_v = root_v.find('node')
                                n_skeleton_v.append(n_node_v)

                            # 处理新出现的properties节点
                            if num_visual == 1:
                                n_underwater_v = ET.SubElement(n_properties_v, 'underwaterModel')
                                n_abovewater_v = ET.SubElement(n_properties_v, 'abovewaterModel')
                                n_underwater_v.text = 'false'
                                n_abovewater_v.text = 'true'

                            # 处理boundingBox节点
                            if num_visual == 1:
                                min_v = root_v.find('boundingBox').find('min')
                                max_v = root_v.find('boundingBox').find('max')
                                n_boundingBox_v.append(min_v)
                                n_boundingBox_v.append(max_v)

                            # 处理renderSets节点

                            for elem in root_v.iter('renderSet'):
                                n_renderSet_v = ET.SubElement(n_renderSets_v, 'renderSet')  # 在renderSets节点中生成新的renderSet节点
                                # name节点处理
                                name_v.append(elem.find('geometry').find('vertices').text)     # 找到name节点所对应的值
                                name_v[i] = re.sub('\t*', '', name_v[i])        # 删去多余字符
                                name_v[i] = re.sub('.vertices', '', name_v[i])
                                n_name_v = ET.SubElement(n_renderSet_v, 'name')    # 生成name节点
                                n_name_v.text = name_v[i]       # 写入name节点的值
                                i = i + 1
                                # treatAsWorldSpaceObject节点处理
                                n_treatAsWorldSpaceObject_v = elem.find('treatAsWorldSpaceObject')  # 找出原文件中对应节点
                                n_renderSet_v.append(n_treatAsWorldSpaceObject_v)       # 将子节点写入renderSet节点中
                                # nodes节点处理
                                n_r_nodes_v = ET.SubElement(n_renderSet_v, 'nodes')  # 建立子节点nodes
                                for node in elem.iter('node'):
                                    n_r_nodes_v.append(node)       # 写入子节点node
                                # material节点处理
                                r_material_v = elem.find('geometry').find('primitiveGroup').find('material')    # 找出原文件的material节点
                                n_renderSet_v.append(r_material_v)     # 写入renderSet节点

                            # 处理lods节点
                            n_lod_v = ET.SubElement(n_lods_v, 'lod')
                            extent_v = ET.SubElement(n_lod_v, 'extent')
                            castsShadow_v = ET.SubElement(n_lod_v, 'castsShadow')
                            renderSets_v = ET.SubElement(n_lod_v, 'renderSets')
                            # 含_ports文件的单独赋值
                            if ('_ports' in root_v.tag):
                                # <extent>	200.0000	</extent>
                                extent_v.text = '200'
                                # <castsShadow>	true	</castsShadow>
                                castsShadow_v.text = 'true'
                                # <renderSets />
                            else:   # 其他文件处理
                                # extent节点
                                extent_v.text = root_m.find('extent').text
                                # castsShadow节点
                                castsShadow_v.text = root_m.find('castsShadow').text
                                # renderSets节点
                                num_lod = i
                                while(i):
                                    renderSet_v = ET.SubElement(renderSets_v, 'renderSet')
                                    renderSet_v.text = name_v[num_lod-i]
                                    i = i-1

                        print('finish','\n')

                    # 生成新的model文件
                    model_str = prettify(n_root_m)
                    # 去除版本声明
                    model_str = '\n'.join([
                        line for line in model_str.split('\n')
                        if line.strip() != '<?xml version="1.0" ?>'
                    ])
                    # 去除空白行
                    model_str = '\n'.join([
                        line for line in model_str.split('\n')
                        if line.strip() != ''
                    ])
                    f = open(FileAdderss_m, 'w', encoding='utf-8')
                    f.write(model_str)
                    f.close()

                    # 生成新的visual文件
                    visual_str = prettify(n_root_v)
                    # 去除版本声明
                    visual_str = '\n'.join([
                        line for line in visual_str.split('\n')
                        if line.strip() != '<?xml version="1.0" ?>'
                    ])
                    # 去除空白行
                    visual_str = '\n'.join([
                        line for line in visual_str.split('\n')
                        if line.strip() != ''
                    ])
                    f = open(FileAdderss_v, 'w', encoding='utf-8')
                    f.write(visual_str)
                    f.close()
                    print('model:', num_model, '\nvisual:', num_visual,'\n')
                else:
                    print('new model')
    return 0


if __name__ == "__main__":
    main("./")

