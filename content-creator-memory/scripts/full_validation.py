#!/usr/bin/env python3
"""
完整验证测试脚本
验证 content-creator-memory 的所有核心功能
"""

import subprocess
import json
import time
from pathlib import Path

def run_command(cmd):
    """执行命令并返回结果"""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr

def test_search_content():
    """测试自有内容搜索"""
    print("\n📝 测试 1: 搜索自有内容")
    print("-" * 50)
    
    cmd = "python3 ~/.cursor/skills/content-creator-memory/scripts/search_content.py --query 'AI编程' --top-k 2"
    code, stdout, stderr = run_command(cmd)
    
    if code == 0:
        data = json.loads(stdout)
        print(f"✅ 搜索成功")
        print(f"   - 返回结果: {len(data['results'])} 条")
        print(f"   - 总计发现: {data['total_found']} 篇")
        print(f"   - 响应时间: {data['search_time_ms']}ms")
        if data['results']:
            print(f"   - 首条标题: {data['results'][0]['title'][:50]}...")
        return True
    else:
        print(f"❌ 搜索失败: {stderr}")
        return False

def test_search_reference():
    """测试标杆案例搜索"""
    print("\n📚 测试 2: 搜索标杆案例")
    print("-" * 50)
    
    cmd = "python3 ~/.cursor/skills/content-creator-memory/scripts/search_reference.py --query '产品' --top-k 2"
    code, stdout, stderr = run_command(cmd)
    
    if code == 0:
        data = json.loads(stdout)
        print(f"✅ 搜索成功")
        print(f"   - 返回结果: {len(data['results'])} 条")
        print(f"   - 总计发现: {data['total_found']} 篇")
        print(f"   - 响应时间: {data['search_time_ms']}ms")
        if data['results']:
            print(f"   - 首条作者: {data['results'][0]['author']}")
        return True
    else:
        print(f"❌ 搜索失败: {stderr}")
        return False

def test_index_files():
    """测试索引文件完整性"""
    print("\n📦 测试 3: 索引文件完整性")
    print("-" * 50)
    
    data_dir = Path.home() / ".cursor/skills/content-creator-memory/data"
    required_files = [
        "own_works.json",
        "reference_examples.json",
        "search_index.json",
        "metadata.json"
    ]
    
    all_exist = True
    for filename in required_files:
        file_path = data_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {filename}: {size:,} bytes")
        else:
            print(f"❌ {filename}: 不存在")
            all_exist = False
    
    return all_exist

def test_metadata():
    """测试元数据"""
    print("\n📊 测试 4: 元数据验证")
    print("-" * 50)
    
    metadata_file = Path.home() / ".cursor/skills/content-creator-memory/data/metadata.json"
    
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"✅ 元数据加载成功")
        print(f"   - 版本: {metadata.get('version')}")
        print(f"   - 创建时间: {metadata.get('created_at')}")
        print(f"   - 自有内容: {metadata.get('total_own_works')} 篇")
        print(f"   - 标杆案例: {metadata.get('total_reference_examples')} 篇")
        print(f"   - 关键词数: {metadata.get('total_keywords')} 个")
        
        # 验证数量合理性
        if metadata.get('total_own_works', 0) > 0 and metadata.get('total_reference_examples', 0) > 0:
            return True
        else:
            print(f"⚠️  警告: 内容数量异常")
            return False
            
    except Exception as e:
        print(f"❌ 元数据加载失败: {e}")
        return False

def test_content_source():
    """测试原始内容源"""
    print("\n📁 测试 5: 原始内容源")
    print("-" * 50)
    
    contents_dir = Path.home() / ".cursor/skills/content-creator/memories/contents"
    examples_dir = Path.home() / ".cursor/skills/content-creator/memories/examples"
    
    contents_exist = contents_dir.exists()
    examples_exist = examples_dir.exists()
    
    if contents_exist:
        md_files = list(contents_dir.rglob("*.md"))
        print(f"✅ contents/ 目录存在: {len(md_files)} 个 .md 文件")
    else:
        print(f"❌ contents/ 目录不存在")
    
    if examples_exist:
        md_files = list(examples_dir.rglob("*.md"))
        print(f"✅ examples/ 目录存在: {len(md_files)} 个 .md 文件")
    else:
        print(f"❌ examples/ 目录不存在")
    
    return contents_exist and examples_exist

def test_performance():
    """测试性能"""
    print("\n⚡ 测试 6: 性能测试")
    print("-" * 50)
    
    queries = ["AI", "编程", "产品", "设计", "技术"]
    times = []
    
    for query in queries:
        cmd = f"python3 ~/.cursor/skills/content-creator-memory/scripts/search_content.py --query '{query}' --top-k 1"
        start = time.time()
        code, stdout, stderr = run_command(cmd)
        elapsed = (time.time() - start) * 1000  # 转为毫秒
        
        if code == 0:
            times.append(elapsed)
    
    if times:
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        print(f"✅ 性能测试完成 ({len(times)} 次查询)")
        print(f"   - 平均响应: {avg_time:.1f}ms")
        print(f"   - 最快响应: {min_time:.1f}ms")
        print(f"   - 最慢响应: {max_time:.1f}ms")
        
        # 性能要求: 平均响应 < 100ms
        return avg_time < 100
    else:
        print(f"❌ 性能测试失败")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🔍 content-creator-memory 完整验证测试")
    print("=" * 50)
    
    tests = [
        ("搜索自有内容", test_search_content),
        ("搜索标杆案例", test_search_reference),
        ("索引文件完整性", test_index_files),
        ("元数据验证", test_metadata),
        ("原始内容源", test_content_source),
        ("性能测试", test_performance),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ 测试异常: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status}: {name}")
    
    print("\n" + "-" * 50)
    print(f"总计: {passed_count}/{total_count} 通过")
    
    if passed_count == total_count:
        print("\n🎉 所有测试通过！content-creator-memory 运行正常。")
        return 0
    else:
        print(f"\n⚠️  有 {total_count - passed_count} 个测试失败，请检查。")
        return 1

if __name__ == "__main__":
    exit(main())
