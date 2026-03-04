#!/usr/bin/env python3
"""
生成数据库变更 DDL 脚本（Brownfield 模式）

使用方法:
    python3 generate_database_ddl.py \
        --base-version "v1.5" \
        --new-version "v2.0" \
        --changes '{"alter_tables": [...], "new_tables": [...]}' \
        --output Documentation/Basic/Database/5_数据库变更DDL_v2.0.sql
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def generate_alter_table_sql(alter: Dict) -> str:
    """生成 ALTER TABLE 语句"""
    sqls = []
    table = alter["table"]
    
    for col in alter.get("add_columns", []):
        sql_parts = [f'ALTER TABLE "{table}"']
        sql_parts.append(f'ADD COLUMN "{col["name"]}" {col["type"]}')
        
        if col.get("default"):
            sql_parts.append(f"DEFAULT {col['default']}")
        if col.get("not_null"):
            sql_parts.append("NOT NULL")
        
        sqls.append(" ".join(sql_parts) + ";")
        
        # 添加注释
        if col.get("comment"):
            sqls.append(f'COMMENT ON COLUMN "{table}"."{col["name"]}" IS \'{col["comment"]}\';')
    
    return "\n".join(sqls)


def generate_create_table_sql(table: Dict) -> str:
    """生成 CREATE TABLE 语句"""
    table_name = table["name"]
    columns = table.get("columns", [])
    
    sql_parts = [f'CREATE TABLE "{table_name}" (']
    
    # 列定义
    col_definitions = []
    for col in columns:
        col_def = f'    "{col["name"]}" {col["type"]}'
        if col.get("primary_key"):
            col_def += " PRIMARY KEY"
        if col.get("not_null"):
            col_def += " NOT NULL"
        if col.get("default"):
            col_def += f" DEFAULT {col['default']}"
        col_definitions.append(col_def)
    
    sql_parts.append(",\n".join(col_definitions))
    sql_parts.append(');')
    
    # 表注释
    if table.get("comment"):
        sql_parts.append(f'\nCOMMENT ON TABLE "{table_name}" IS \'{table["comment"]}\';')
    
    return "\n".join(sql_parts)


def generate_create_index_sql(index: Dict) -> str:
    """生成 CREATE INDEX 语句"""
    index_name = index["name"]
    table = index["table"]
    columns = index["columns"]
    
    columns_str = ", ".join(f'"{col}"' for col in columns)
    sql = f'CREATE INDEX "{index_name}" ON "{table}"({columns_str});'
    
    return sql


def generate_rollback_sql(changes: Dict) -> str:
    """生成回滚脚本"""
    rollback_sqls = []
    
    # 删除新增字段
    for alter in changes.get("alter_tables", []):
        table = alter["table"]
        for col in alter.get("add_columns", []):
            rollback_sqls.append(f'-- ALTER TABLE "{table}" DROP COLUMN "{col["name"]}";')
    
    # 删除新增表
    for table in changes.get("new_tables", []):
        rollback_sqls.append(f'-- DROP TABLE "{table["name"]}";')
    
    # 删除新增索引（会随表删除自动清理）
    
    return "\n".join(rollback_sqls)


def generate_database_ddl(
    base_version: str,
    new_version: str,
    changes: Dict,
    output_path: str
) -> str:
    """
    生成数据库变更 DDL
    
    参数:
        base_version: 基于版本
        new_version: 新版本
        changes: 变更内容
        output_path: 输出文件路径
    
    返回:
        DDL 文件路径
    """
    ddl = []
    
    # 头部注释
    ddl.append("-- ==============================")
    ddl.append(f"-- 数据库变更 DDL ({new_version})")
    ddl.append(f"-- 基于版本: {base_version}")
    ddl.append(f"-- 变更日期: {datetime.now().strftime('%Y-%m-%d')}")
    ddl.append(f"-- 生成方式: AI Agent")
    ddl.append("-- ==============================\n")
    
    # 1. ALTER TABLE 语句
    if changes.get("alter_tables"):
        ddl.append("-- 1. 修改现有表结构\n")
        for alter in changes["alter_tables"]:
            ddl.append(generate_alter_table_sql(alter))
            ddl.append("\n")
    
    # 2. CREATE TABLE 语句
    if changes.get("new_tables"):
        ddl.append("-- 2. 新增数据表\n")
        for table in changes["new_tables"]:
            ddl.append(generate_create_table_sql(table))
            ddl.append("\n")
    
    # 3. 索引变更
    if changes.get("new_indexes"):
        ddl.append("-- 3. 新增索引\n")
        for idx in changes["new_indexes"]:
            ddl.append(generate_create_index_sql(idx))
            ddl.append("\n")
    
    # 4. 回滚脚本
    ddl.append("-- ==============================")
    ddl.append("-- 回滚脚本 (Rollback)")
    ddl.append("-- ==============================\n")
    ddl.append(generate_rollback_sql(changes))
    
    # 保存文件
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(ddl), encoding="utf-8")
    
    return str(output_file)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="生成数据库变更 DDL")
    parser.add_argument("--base-version", required=True, help="基于版本")
    parser.add_argument("--new-version", required=True, help="新版本")
    parser.add_argument("--changes", required=True, help="变更内容（JSON 字符串）")
    parser.add_argument("--output", required=True, help="输出文件路径")
    
    args = parser.parse_args()
    
    # 解析变更数据
    try:
        changes = json.loads(args.changes)
    except json.JSONDecodeError as e:
        print(f"❌ 变更数据格式错误：{e}", file=sys.stderr)
        sys.exit(1)
    
    # 生成 DDL
    output_path = generate_database_ddl(
        base_version=args.base_version,
        new_version=args.new_version,
        changes=changes,
        output_path=args.output
    )
    
    print(f"✅ DDL 已生成：{output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
