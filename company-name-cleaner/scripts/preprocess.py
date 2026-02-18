#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公司名称预处理脚本 — 确定性规则清理

功能：
1. 解析编号（decimal + hex）
2. 合并多行条目
3. 提取括号内缩写（全大写且 <= 8 字符）
4. 去除 (formerly ...) 等括号内容
5. 去除地点前缀
6. 去除法律后缀（保护品牌中的 &）
7. 去除冗余描述词（有最小长度保护）
8. 清理特殊字符

输入：标准输入或文件，格式为 "编号 公司名称" 每行一个
输出：TSV 格式 → ID\t清理后\t提取缩写\t原名
"""

import sys
import re
from typing import List, Tuple, Optional


# ============================================================
# 配置：地点前缀
# ============================================================
LOCATION_PREFIXES = [
    'Shanghai', 'Shenzhen', 'Beijing', 'Chongqing', 'Guangzhou', 'Hangzhou',
    'Nanjing', 'Chengdu', 'Wuhan', 'Xian', 'Tianjin', 'Suzhou', 'Zhengzhou',
    'Changsha', 'Dongguan', 'Qingdao', 'Shenyang', 'Ningbo', 'Kunming',
    'Hefei', 'Fuzhou', 'Xiamen', 'Wuxi', 'Jinan', 'Dalian', 'Harbin',
    'Taipei', 'Taiwan', 'Hong Kong', 'Macau',
    'Foshan', 'Nantong', 'Changchun', 'Shijiazhuang', 'Guiyang', 'Nanning',
    'Nanchang', 'Taiyuan', 'Changzhou', 'Wenzhou', 'Jiaxing',
    'Zhuhai', 'Huizhou', 'Zhongshan', 'Kunshan', 'Yantai',
    'Weifang', 'Linyi', 'Zibo', 'Jining', 'Weihai',
    'Xianyang', 'Luoyang', 'Nanyang', 'Anyang', 'Xinxiang', 'Jiaozuo',
    'Rizhao', 'Wuhu', 'Zhuhai', 'Tangshan', 'Guilin', 'Jiangsu',
    'Guangdong', 'Heilongjiang', 'Anhui', 'Sichuan', 'Fujian', 'Hubei',
    'Hunan', 'Hebei', 'Henan', 'Zhejiang',
    # 拼音形式的 SZ/GD 等
    'SZ', 'GD',
]

# ============================================================
# 配置：法律后缀（按匹配优先级排序）
# ============================================================
# 复合后缀必须排在简单后缀之前
LEGAL_SUFFIXES_ORDERED = [
    # === 超长复合后缀（最先匹配）===
    r'GmbH\s*&\s*Co\.?\s*KGaA',
    r'GmbH\s*&\s*Co\.?\s*KG',
    r'GmbH\s*&\s*Co\.?\s*OHG',
    r'SE\s*&\s*Co\.?\s*KGaA',
    r'SE\s*&\s*Co\.?\s*KG',
    r'AG\s*&\s*Co\.?\s*KG',
    r'AG\s*&\s*Co\.?\s*KGaA',
    r'Corp\.?\s*&\s*Co\.?\s*KG',
    # === 长复合后缀 ===
    r'Sp\.?\s*z\s*o\.?\s*o\.?\s*sp\.?\s*k\.?',  # 波兰 sp. z o.o. sp. k.
    r'Sp\.?\s*z\.?\s*o\.?\s*o\.?',    # 波兰 Sp. z o.o.
    r'Pte\.?\s*Ltd\.?',               # 新加坡
    r'Pty\.?\s*Ltd\.?',               # 澳大利亚
    r'Private\s+Limited',
    r'CO\.?\s*,?\s*LTD\.?',           # Co., Ltd.  CO. LTD
    r'Co\.?\s*,?\s*Ltd\.?',
    r'with\s+limited\s+liability',
    r'Sociedad\s+Limitada',
    r'Limited\s+Liability',
    r'Korlátolt\s+Felelősségű\s+Társaság',
    r'Korlatolt\s+Felelossegu\s+Tarsasag',
    # === 标准后缀 ===
    r'Corporation',
    r'Incorporated',
    r'Company',
    r'Enterprises?',
    r'Laboratories?',
    r'Holdings?',
    r'Foundation',
    r'Institute',
    r'Partners?(?:hip)?',
    r'Associates?',
    r'LLC\.?',
    r'Inc\.?',
    r'LIMITED',
    r'Limited',
    r'limited',
    r'LTD\.?',
    r'Ltd\.?',
    r'Corp\.?',
    r'Co\.?',
    r'GmbH',
    r'KGaA',
    r'KG',
    r'AG',
    r'SE',
    r'SA',
    r'S\.?A\.?S\.?',
    r'S\.?A\.?R\.?L\.?',
    r'S\.?r\.?l\.?',
    r'S\.?L\.?U?',
    r'S\.?p\.?A\.?',
    r'S\.?de\s+R\.?L\.?',
    r'UG',
    r'Kft\.?',
    r'[Bb]\.?[Vv]\.?',
    r'[Oo]y\.?',
    r'AB',
    r'ASA',
    r'A/?S',
    r'ApS',
    r'[Dd]\.?[Oo]\.?[Oo]\.?',
    r'[Ss]\.?[Rr]\.?[Oo]\.?',
    r'LTDA\.?',
    r'OÜ',
    r'Oyj',
    r'N\.?V\.?',
    r'plc',
    r'PLC',
    r'Group',
]

# ============================================================
# 配置：冗余描述词
# ============================================================
REDUNDANT_WORDS = [
    'Technology', 'Technologies', 'TECHNOLOGY', 'TECHNOLOGIES',
    'Electronics?', 'ELECTRONICS?',
    'Semiconductor', 'Semiconductors', 'SEMICONDUCTOR',
    'Microelectronics', 'MICROELECTRONICS',
    'Optoelectronics', 'OPTOELECTRONICS',
    'Engineering', 'ENGINEERING',
    'Systems?', 'SYSTEMS?',
    'Solutions?', 'SOLUTIONS?',
    'Devices?', 'DEVICES?',
    'Products?', 'PRODUCTS?',
    'Industries?', 'INDUSTRIES?',
    'Networks?', 'NETWORKS?',
    'Networking',
    'Communications?', 'COMMUNICATIONS?',
    'Telecommunications?',
    'Innovative', 'Advanced',
    'Digital', 'Smart',
    'Global', 'International', 'Worldwide', 'Universal',
    'Integrated',
    'Manufacturing',
    'Automation',
]


# ============================================================
# 解析
# ============================================================
def parse_lines(raw_lines: List[str]) -> List[Tuple[str, str]]:
    """
    解析输入行，支持 decimal 和 hex ID，自动合并多行条目。

    Returns:
        [(id, company_name), ...]
    """
    id_pattern = re.compile(r'^(0x[0-9a-fA-F]+|\d+)\s+(.+)$')
    entries = []

    for line in raw_lines:
        line = line.strip()
        if not line:
            continue

        match = id_pattern.match(line)
        if match:
            entries.append((match.group(1), match.group(2)))
        else:
            # 无 ID 开头 → 合并到上一条（多行条目）
            if entries:
                prev_id, prev_name = entries[-1]
                entries[-1] = (prev_id, prev_name + ' ' + line)

    return entries


# ============================================================
# 括号处理
# ============================================================
def extract_parenthetical_abbr(name: str) -> Tuple[str, Optional[str]]:
    """
    提取括号内的缩写（全大写/数字混合，<= 8 字符），
    同时去除所有括号内容。

    Returns:
        (去除括号后的名称, 提取到的缩写 or None)
    """
    extracted_abbr = None

    # 查找所有括号内容
    parens = re.findall(r'\(([^)]+)\)', name)
    for content in parens:
        content_stripped = content.strip()
        # 缩写特征：主要大写+少量小写，无空格，2-8字符，含至少1个字母
        # 匹配：CATC, QuIC, ACECAD 等
        # 排除：国家/地区代码、法律术语、年份、地名
        ABBR_EXCLUSIONS = {
            'HK', 'UK', 'US', 'EU', 'NZ', 'AU', 'CN', 'JP', 'KR', 'TW',
            'DE', 'FR', 'IT', 'ES', 'NL', 'SE', 'NO', 'DK', 'FI', 'CH',
            'OPC', 'PTY', 'CJSC', 'JSC', 'LTD', 'LLC', 'INC',
            'Shanghai', 'ShenZhen', 'Xiamen', 'Jiangsu', 'THAILAND',
            'formerly', 'Formerly',
        }
        is_abbr = (
            re.match(r'^[A-Za-z0-9]{2,8}$', content_stripped)
            and sum(1 for c in content_stripped if c.isupper()) >= len(content_stripped) * 0.4
            and any(c.isalpha() for c in content_stripped)
            and not content_stripped.isdigit()  # 排除纯数字（年份如 2003）
            and content_stripped not in ABBR_EXCLUSIONS
            and not content_stripped.lower().startswith('formerly')
        )
        if is_abbr:
            extracted_abbr = content_stripped

    # 去除所有括号及内容
    cleaned = re.sub(r'\s*\([^)]*\)', '', name)
    return cleaned.strip(), extracted_abbr


# ============================================================
# 地点前缀
# ============================================================
def remove_location_prefix(name: str) -> str:
    """去除开头的地点前缀"""
    sorted_locs = sorted(LOCATION_PREFIXES, key=len, reverse=True)
    for loc in sorted_locs:
        pattern = rf'^{re.escape(loc)}[\s,]+'
        if re.match(pattern, name, re.IGNORECASE):
            name = re.sub(pattern, '', name, count=1, flags=re.IGNORECASE).strip()
            break
    return name


# ============================================================
# 法律后缀
# ============================================================
def remove_legal_suffixes(name: str) -> str:
    """
    去除法律后缀，迭代3轮确保清理干净。
    注意：不使用全局 & 替换，仅在法律后缀模式中处理 &。
    """
    for _ in range(3):
        original = name
        for suffix in LEGAL_SUFFIXES_ORDERED:
            # 用 \b 边界匹配，从名称中移除
            pattern = rf'\s*\b{suffix}\b\.?'
            name = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
        # 清理法律后缀残留的 & 和 Co 连接
        name = re.sub(r'\s*&\s*$', '', name).strip()  # 结尾的孤立 &
        name = re.sub(r'\s*,\s*$', '', name).strip()  # 结尾的孤立 ,
        if name == original:
            break
    return name


# ============================================================
# 冗余词
# ============================================================
def remove_redundant_words(name: str) -> str:
    """
    去除冗余描述词。
    保护规则：处理后至少保留 1 个词，否则回退。
    """
    original = name
    words_before = len(name.split())

    for word in REDUNDANT_WORDS:
        pattern = rf'\b{word}\b'
        candidate = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
        candidate = ' '.join(candidate.split())  # 合并多余空格
        # 保护：不能清成空
        if candidate and len(candidate) >= 2:
            name = candidate

    # 最终保护：如果结果为空或太短，回退
    if not name or len(name.strip()) < 2:
        return original

    return name


# ============================================================
# 特殊字符清理
# ============================================================
def clean_special_chars(name: str) -> str:
    """
    清理特殊字符和多余空格。
    注意：保留品牌中的 & 符号（如 Bang & Olufsen）。
    """
    # 去除引号
    name = name.replace('"', '').replace("'", '').replace('`', '')
    # 去除反斜杠
    name = name.replace('\\', '')
    # 去除结尾的孤立标点
    name = re.sub(r'[\s.,;:]+$', '', name)
    # 去除开头的标点（保留 - 和数字开头）
    name = re.sub(r'^[.,;:_+|/\\]+', '', name)
    # 合并多余空格
    name = ' '.join(name.split())
    return name.strip()


# ============================================================
# 主处理
# ============================================================
def process_entry(entry_id: str, original_name: str) -> Tuple[str, str, Optional[str], str]:
    """
    处理单条公司名称。

    Returns:
        (id, cleaned_name, extracted_abbr, original_name)
    """
    if not original_name.strip():
        return entry_id, '', None, original_name

    name = original_name

    # 1. 提取括号缩写 + 去除括号内容
    name, abbr = extract_parenthetical_abbr(name)

    # 2. 去除地点前缀
    name = remove_location_prefix(name)

    # 3. 去除法律后缀
    name = remove_legal_suffixes(name)

    # 4. 去除冗余描述词
    name = remove_redundant_words(name)

    # 5. 清理特殊字符
    name = clean_special_chars(name)

    # 6. 最终保护：如果清空了，回退到原名
    if not name or len(name.strip()) < 1:
        name = original_name.strip()

    return entry_id, name, abbr, original_name


def main():
    """主函数：读取输入，处理，输出 TSV"""
    raw_lines = []

    # 优先检查文件参数，再检查 stdin
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            raw_lines = f.readlines()
    elif not sys.stdin.isatty():
        raw_lines = sys.stdin.readlines()
    else:
        print("用法: python3 preprocess.py input.txt", file=sys.stderr)
        print("  或: python3 preprocess.py < input.txt", file=sys.stderr)
        sys.exit(1)

    entries = parse_lines(raw_lines)

    # 输出 TSV 头
    print("ID\tCleaned\tExtractedAbbr\tOriginal")

    for entry_id, original_name in entries:
        eid, cleaned, abbr, orig = process_entry(entry_id, original_name)
        abbr_str = abbr if abbr else ''
        print(f"{eid}\t{cleaned}\t{abbr_str}\t{orig}")

    # 统计到 stderr
    total = len(entries)
    with_abbr = sum(1 for _, n in entries
                    if extract_parenthetical_abbr(n)[1] is not None)
    print(f"\n处理完成: {total} 条, 其中 {with_abbr} 条提取到括号缩写",
          file=sys.stderr)


if __name__ == "__main__":
    main()
