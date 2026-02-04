#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公司名称预处理脚本

功能：
1. 去除数字编号前缀
2. 去除地点前缀
3. 去除公司法律后缀
4. 清理特殊字符和多余空格

输入：标准输入或文件，格式为 "数字 公司名称" 每行一个
输出：
  - 第一次输出：数字|处理后|原始（方便核对）
  - 第二次输出：数字|处理后（供后续处理）
"""

import sys
import re
import os
from typing import List, Tuple

# 地点前缀列表（常见中国城市和地区）
LOCATION_PREFIXES = [
    'Shanghai', 'Shenzhen', 'Beijing', 'Chongqing', 'Guangzhou', 'Hangzhou',
    'Nanjing', 'Chengdu', 'Wuhan', 'Xian', 'Tianjin', 'Suzhou', 'Zhengzhou',
    'Changsha', 'Dongguan', 'Qingdao', 'Shenyang', 'Ningbo', 'Kunming',
    'Hefei', 'Fuzhou', 'Xiamen', 'Wuxi', 'Jinan', 'Dalian', 'Harbin',
    'Taipei', 'Taiwan', 'Hong Kong', 'Macau',
    'Foshan', 'Nantong', 'Changchun', 'Shijiazhuang', 'Guiyang', 'Nanning',
    'Nanchang', 'Taiyuan', 'Changzhou', 'Ningbo', 'Wenzhou', 'Jiaxing',
    'Zhuhai', 'Huizhou', 'Zhongshan', 'Kunshan', 'Nantong', 'Yantai',
    'Weifang', 'Linyi', 'Zibo', 'Jining', "Tai'an", 'Weihai',
    'Xianyang', 'Luoyang', 'Nanyang', 'Anyang', 'Xinxiang', 'Jiaozuo',
    'Qingdao', 'Yantai', 'Weihai', 'Rizhao',
]

# 公司法律后缀（按频率排序）- 增强版本
LEGAL_SUFFIXES = [
    # ========== 简短后缀（优先匹配）==========
    r'\bLLC\.?\b',                           # Limited Liability Company
    r'\bInc\.?\b',                           # Incorporated
    r'\blimited\b',                          # 小写
    r'\bLimited\b',                          # 首字母大写
    r'\bLIMITED\b',                          # 全大写
    r'\bLTD\b',                              # Limited (无点)
    r'\bLtd\.?\b',                           # Limited (有点或无点)
    r'\bCO\.?\s+LTD\.?\b',                   # Company Limited
    r'\bCo\.?\s+Ltd\.?\b',                   # Company Limited (混合)
    r'\bCO\.?\s+INC\.?\b',                   # Company Incorporated
    r'\bCo\.?\s+Inc\.?\b',                   # Company Incorporated (混合)
    r'\bCo\.?\b',                            # Company
    r'\bCorp\.?\b',                          # Corporation
    r'\bGmbH\b',                             # 德国
    r'\bAG\b',                               # 德国/瑞士
    r'\bSE\b',                               # 欧盟公司
    r'\bSA\b',                               # 法国/西班牙
    r'\bSP\.?\b',                            # Sociedad Pública
    r'\bKft\.?\b',                           # 匈牙利
    r'\bb\.?v\.?\b',                         # 荷兰
    r'\bUG\b',                               # 德国
    r'\bUG\s+\(haftungsbeschränkt\)',        # 德国
    r'\bOy\b',                               # 芬兰
    r'\bAB\b',                               # 瑞典
    r'\bS\.?L\.?\b',                         # 西班牙
    r'\bSLU\b',                              # 西班牙
    r'\bSpA\b',                              # 意大利
    r'\bd\.?o\.?o\.?\b',                     # 克罗地亚/塞尔维亚
    r'\bSp\.?\s*z\s+o\.?o\.?\b',             # 波兰
    r'\bPte\.?\s+Ltd\.?\b',                  # 新加坡
    r'\bPty\s+Ltd\.?\b',                     # 澳大利亚
    r'\bLtd\.?\s+and\s+Co\.?\b',             # 英国
    r'\bLtd\.?\s*&\s+Co\.?\b',               # 英国

    # ========== 国际/地区扩展后缀 ==========
    r'\bS\.?A\.?R\.?L\.?\b',                 # 法国
    r'\bS\.?r\.?l\.?\b',                     # 罗马尼亚
    r'\bSro\.?\b',                           # 斯洛伐克
    r'\bs\.?r\.?o\.?\b',                     # 斯洛文尼亚
    r'\bd\.?\s*d\.?\b',                      # 波斯尼亚
    r'\bEIRL\b',                             # 智利
    r'\bS\.?A\.?S\.?\b',                     # 秘鲁
    r'\bLTDA\b',                             # 巴西
    r'\bS\.?de\s+R\.?L\.?\b',                # 墨西哥
    r'\bRL\b',                               # 墨西哥
    r'\bS\.?A\.?\b',                         # 罗马尼亚/波兰
    r'\bZ\.?o\.?o\.?\b',                     # 波兰

    # ========== 较长后缀 ==========
    r'\bCompany\b',
    r'\bCorporation\b',
    r'\bIncorporated\b',
    r'\bEnterprises\b',
    r'\bEnterprise\b',
    r'\bGroup\b',
    r'\bAssociates?\b',                      # 专业公司
    r'\bPartners?\b',                        # 合伙公司
    r'\bPartnership\b',                      # 合伙企业
    r'\bFoundation\b',                       # 基金会
    r'\bInstitute\b',                        # 研究所
    r'\bLaboratories?\b',                    # 实验室
    r'\bHoldings?\b',                        # 控股

    # ========== 复合后缀（重要！）==========
    r'\bCorp\.?\s+Ltd\.?\b',
    r'\bGmbH\s+&\s+Co\.?\s+KG\b',
    r'\b&\s+Co\.?\s+KG\b',
    r'\b&\s+Affiliates\b',
    r'\b&\s+Co\.?\b',
    r'\b&\s+Company\b',
    r'\b&\s+KG\b',                           # 德国：去除 Gmbh 后残留
    r'\bKG\b',                               # 德国 Kommanditgesellschaft
    r'\(with\s+limited\s+liability\)',
    r'\(with\s+Ltd\s+liability\)',
    r'\bwith\s+limited\s+liability\b',       # 无括号版本
    r'\bwith\s+Ltd\s+liability\b',
    r'\bLimited\s+Liability\b',              # 直接组合（必须在整个词之前）
    r'\bLIMITED\s+LIABILITY\b',              # 全大写
    r'\blimited\s+liability\b',              # 全小写
    r'\bLiability\s+(Company|Corporation)\b',  # Liability Company/Corporation
    r'\s+Liability$',                        # 结尾的单独 Liability
    r'\(Shanghai\)',
    r'\(ShenZhen\)',
    r'\(Xiamen\)',
    r'\(Jiangsu\)',
    r'\bPrivate\s+Limited\b',
    r'\bPte\s+Ltd\b',
    r'\bSociedad\s+Limitada\b',
    r'\bb\.?v\.?b\.?a\.?\b',

    # ========== 后缀残留清理 ==========
    r'\s+and\s+Company$',                    # "and Company" 结尾
    r'\s+&\s+Company$',                      # "& Company" 结尾
    r'\s+and\s+Sons$',                       # "and Sons" 结尾
    r'\s+&\s+Sons$',                         # "& Sons" 结尾
]

# 冗余描述词（去除这些行业通用词）
REDUNDANT_WORDS = [
    r'\bTechnology\b',
    r'\bTechnologies\b',
    r'\bElectronics?\b',
    r'\bEngineering\b',
    r'\bSystems?\b',
    r'\bSolutions?\b',
    r'\bDevices?\b',
    r'\bProducts?\b',
    r'\bIndustries?\b',
    r'\bHoldings?\b',
    r'\bBusiness\b',
    r'\bNetworks?\b',
    r'\bCommunications?\b',
    r'\bTelecommunications?\b',
    r'\bInnovative\b',
    r'\bAdvanced\b',
    r'\bDigital\b',
    r'\bSmart\b',
    r'\bGlobal\b',
    r'\bInternational\b',
    r'\bWorldwide\b',
    r'\bUniversal\b',
    r'\bIntegrated\b',
    r'\bSolutions\b',
]


def extract_number_and_name(line: str) -> Tuple[str, str]:
    """
    提取数字编号和公司名称

    Args:
        line: 输入行，格式为 "数字 公司名称" 或仅 "公司名称"

    Returns:
        (数字, 公司名称) 元组
    """
    # 尝试匹配开头的数字
    match = re.match(r'^(\d+)\s+(.+)$', line.strip())
    if match:
        return match.group(1), match.group(2)
    # 如果没有数字，返回空作为编号
    return '', line.strip()


def remove_location_prefix(name: str) -> str:
    """
    去除地点前缀和中间的地点词

    Args:
        name: 公司名称

    Returns:
        去除地点后的名称
    """
    # 按长度降序排序，优先匹配长的地点名
    sorted_locations = sorted(LOCATION_PREFIXES, key=len, reverse=True)

    # 先去除开头的地点
    for location in sorted_locations:
        pattern = rf'^{re.escape(location)}[\s,]+'
        if re.match(pattern, name, re.IGNORECASE):
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)
            break

    # 再去除中间的地点（前后都有其他词的情况）
    for location in sorted_locations:
        # 匹配 "地点名 " 或 " 地点名 " 模式
        pattern = rf'\s{re.escape(location)}\s'
        if re.search(pattern, name, re.IGNORECASE):
            name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)

    return name.strip()


def remove_legal_suffixes(name: str) -> str:
    """
    去除公司法律后缀（多次迭代确保清理干净）

    Args:
        name: 公司名称

    Returns:
        去除法律后缀后的名称
    """
    original = name
    # 多次迭代确保所有后缀都被去除
    for _ in range(3):
        for suffix in LEGAL_SUFFIXES:
            name = re.sub(suffix, '', name, flags=re.IGNORECASE)
            name = name.strip()
        if name == original:
            break
        original = name

    return name


def remove_redundant_words(name: str) -> str:
    """
    去除冗余描述词

    注意：这个函数比较保守，优先去除明确的行业词，
    避免把短名称的完整名称错误处理。

    Args:
        name: 公司名称

    Returns:
        去除冗余词后的名称
    """
    words = name.split()
    word_count = len(words)

    # 对于2个词的情况，只去除明确的冗余后缀词
    if word_count <= 2:
        # 只去除作为最后一个词的冗余词
        for word_pattern in REDUNDANT_WORDS:
            # 检查是否以冗余词结尾
            pattern = rf'\s+{word_pattern}$'
            if re.search(pattern, name, re.IGNORECASE):
                name = re.sub(pattern, '', name, flags=re.IGNORECASE)
                name = name.strip()
                break
    else:
        # 3个词以上，去除所有冗余词
        for word_pattern in REDUNDANT_WORDS:
            name = re.sub(word_pattern, '', name, flags=re.IGNORECASE)
            name = name.strip()

    return name


def clean_special_chars(name: str) -> str:
    """
    清理特殊字符和多余空格

    Args:
        name: 公司名称

    Returns:
        清理后的名称
    """
    # 去除括号及其内容
    name = re.sub(r'\([^)]*\)', '', name)
    # 去除引号
    name = name.replace('"', '').replace("'", '').replace('`', '')
    # 去除多余的点号（单独的点或无意义的点号）
    name = re.sub(r'\s+\.\s*$', '', name)  # 去除结尾的点
    name = re.sub(r'\s+\.\s+', ' ', name)   # 去除中间单独的点

    # 去除 & 符号及其周围空格
    name = re.sub(r'\s*&\s*$', '', name)   # 去除结尾的 &
    name = re.sub(r'\s*&\s*', ' ', name)    # 去除中间的 &，替换为空格

    # 去除多余空格
    name = ' '.join(name.split())
    # 去除首尾的特殊字符（但保留开头的 -，如 -Q）
    while name and name[0] in '.,;:_+|/\\':
        name = name[1:]
    while name and name[-1] in '.,;:-_+|/\\':
        name = name[:-1]

    return name.strip()


# 后缀残留检测词（用于发现可能未被正确清理的名称）
SUFFIX_RESIDUE_PATTERNS = [
    r'\bLLC\b',
    r'\bInc\b',
    r'\bLtd\b',
    r'\bLTD\b',
    r'\bCo\b',
    r'\bCorp\b',
    r'\bGmbH\b',
    r'\blimited\b',
    r'\bCompany\b',
    r'\bCorporation\b',
    r'\bIncorporated\b',
    r'\bSA\b',
    r'\bAG\b',
    r'\bSE\b',
    r'\bSP\b',
]


def check_suffix_residue(name: str) -> list:
    """
    检查名称中是否可能残留后缀

    Args:
        name: 处理后的公司名称

    Returns:
        匹配到的残留模式列表
    """
    residues = []
    for pattern in SUFFIX_RESIDUE_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            residues.append(pattern)
    return residues


def process_line(line: str) -> Tuple[str, str, str]:
    """
    处理一行公司名称

    Args:
        line: 输入行

    Returns:
        (编号, 处理后的名称, 原始名称) 元组
    """
    number, original_name = extract_number_and_name(line)

    if not original_name:
        return number, '', original_name

    # 按顺序处理
    name = remove_location_prefix(original_name)
    name = remove_legal_suffixes(name)
    name = remove_redundant_words(name)
    name = clean_special_chars(name)

    return number, name, original_name


def main():
    """主函数"""
    input_lines = []

    # 从标准输入读取
    for line in sys.stdin:
        line = line.strip()
        if line:
            input_lines.append(line)

    # 如果没有输入，打印使用说明
    if not input_lines:
        print(__doc__)
        print("\n使用方法:")
        print('  echo "2208 Aclara Technologies LLC" | python3 preprocess.py')
        print('  cat input.txt | python3 preprocess.py')
        print('  python3 preprocess.py < input.txt')
        return

    # 处理每一行
    results = []
    residue_warnings = []  # 后缀残留警告

    for line in input_lines:
        number, name, original = process_line(line)
        if name:  # 只输出非空名称
            # 检查后缀残留
            residues = check_suffix_residue(name)
            if residues:
                residue_warnings.append({
                    'number': number,
                    'name': name,
                    'original': original,
                    'residues': residues
                })
            results.append((number, name, original))

    # 输出格式1：包含原始内容（方便核对）
    print("=== 第一次输出（含原始内容，方便核对）===")
    print("格式：数字|处理后|原始")
    print("---")
    for number, name, original in results:
        print(f"{number}|{name}|{original}")

    print("\n=== 第二次输出（处理后）===")
    print("格式：数字|处理后")
    print("---")
    for number, name, _ in results:
        print(f"{number}|{name}")

    # 输出后缀残留警告（如果有）
    if residue_warnings:
        print("\n=== 后缀残留警告（可能需要手动检查）===")
        print(f"发现 {len(residue_warnings)} 条可能残留后缀的记录:")
        print("---")
        for w in residue_warnings:
            residue_str = ", ".join(w['residues'])
            print(f"[{w['number']}] {w['name']}")
            print(f"        原始: {w['original']}")
            print(f"        检测到: {residue_str}")
            print()


if __name__ == "__main__":
    main()
