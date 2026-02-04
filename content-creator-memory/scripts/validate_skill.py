#!/usr/bin/env python3
"""
Skill 验证脚本 - Validate Skill

功能：验证 memory-index skill 是否达到预期目标

Metrics：
1. 索引完整性（Indexing Completeness）
2. 搜索准确度（Search Accuracy）
3. 性能指标（Performance）
4. API 可用性（API Availability）
5. 数据质量（Data Quality）
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Any


class SkillValidator:
    def __init__(self, data_dir: str, scripts_dir: str):
        self.data_dir = Path(data_dir).expanduser()
        self.scripts_dir = Path(scripts_dir).expanduser()
        self.results = {
            "metrics": {},
            "tests": [],
            "overall_score": 0.0,
            "status": "UNKNOWN"
        }
    
    def run_all_tests(self):
        """运行所有验证测试"""
        print("=" * 80)
        print("🔍 memory-index Skill 验证测试")
        print("=" * 80)
        print()
        
        # Metric 1: 索引完整性
        self.test_indexing_completeness()
        
        # Metric 2: 搜索准确度
        self.test_search_accuracy()
        
        # Metric 3: 性能指标
        self.test_performance()
        
        # Metric 4: API 可用性
        self.test_api_availability()
        
        # Metric 5: 数据质量
        self.test_data_quality()
        
        # 计算总分
        self.calculate_overall_score()
        
        # 输出总结报告
        self.print_summary()
    
    def test_indexing_completeness(self):
        """Metric 1: 索引完整性"""
        print("📊 Metric 1: 索引完整性（Indexing Completeness）")
        print("-" * 80)
        
        score = 0.0
        max_score = 20.0
        
        tests = [
            ("own_works.json 存在", self.data_dir / "own_works.json"),
            ("reference_examples.json 存在", self.data_dir / "reference_examples.json"),
            ("search_index.json 存在", self.data_dir / "search_index.json"),
            ("metadata.json 存在", self.data_dir / "metadata.json")
        ]
        
        for test_name, file_path in tests:
            if file_path.exists():
                print(f"  ✓ {test_name}")
                score += max_score / len(tests)
            else:
                print(f"  ✗ {test_name}")
        
        # 检查索引内容
        try:
            with open(self.data_dir / "metadata.json", 'r') as f:
                metadata = json.load(f)
            
            own_works_count = metadata.get("total_own_works", 0)
            reference_count = metadata.get("total_reference_examples", 0)
            keywords_count = metadata.get("total_keywords", 0)
            
            print(f"\n  索引统计:")
            print(f"    - 自有内容: {own_works_count} 篇")
            print(f"    - 标杆案例: {reference_count} 篇")
            print(f"    - 关键词数: {keywords_count} 个")
            
            if own_works_count >= 30:
                print(f"  ✓ 自有内容数量达标（≥30）")
            else:
                print(f"  ⚠️  自有内容数量不足（{own_works_count} < 30）")
                score -= 2
            
            if reference_count >= 40:
                print(f"  ✓ 标杆案例数量达标（≥40）")
            else:
                print(f"  ⚠️  标杆案例数量不足（{reference_count} < 40）")
                score -= 2
        
        except Exception as e:
            print(f"  ✗ 读取元数据失败: {e}")
            score -= 5
        
        self.results["metrics"]["indexing_completeness"] = {
            "score": max(0, score),
            "max_score": max_score,
            "percentage": max(0, score) / max_score * 100
        }
        
        print(f"\n  得分: {max(0, score):.1f}/{max_score} ({max(0, score)/max_score*100:.1f}%)")
        print()
    
    def test_search_accuracy(self):
        """Metric 2: 搜索准确度"""
        print("🎯 Metric 2: 搜索准确度（Search Accuracy）")
        print("-" * 80)
        
        score = 0.0
        max_score = 30.0
        
        test_cases = [
            {
                "name": "测试1: 查询'AI编程'",
                "query": "AI编程",
                "expected_min_results": 3,
                "expected_relevance_threshold": 0.1
            },
            {
                "name": "测试2: 查询'Cursor'",
                "query": "Cursor",
                "expected_min_results": 2,
                "expected_relevance_threshold": 0.1
            },
            {
                "name": "测试3: 查询'独立开发'",
                "query": "独立开发",
                "expected_min_results": 2,
                "expected_relevance_threshold": 0.1
            }
        ]
        
        points_per_test = max_score / len(test_cases)
        
        for test in test_cases:
            print(f"\n  {test['name']}")
            try:
                result = subprocess.run([
                    "python3", str(self.scripts_dir / "search_content.py"),
                    "--query", test["query"],
                    "--top-k", "5",
                    "--min-quality", "6.0"
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    results_count = len(data.get("results", []))
                    
                    if results_count >= test["expected_min_results"]:
                        print(f"    ✓ 返回结果数量: {results_count} (≥{test['expected_min_results']})")
                        score += points_per_test / 2
                    else:
                        print(f"    ✗ 返回结果数量不足: {results_count} < {test['expected_min_results']}")
                    
                    # 检查相关度分数
                    if results_count > 0:
                        avg_relevance = sum(r.get("relevance_score", 0) for r in data["results"]) / results_count
                        if avg_relevance >= test["expected_relevance_threshold"]:
                            print(f"    ✓ 平均相关度: {avg_relevance:.3f} (≥{test['expected_relevance_threshold']})")
                            score += points_per_test / 2
                        else:
                            print(f"    ✗ 平均相关度不足: {avg_relevance:.3f}")
                else:
                    print(f"    ✗ 搜索失败: {result.stderr}")
            
            except Exception as e:
                print(f"    ✗ 测试异常: {e}")
        
        self.results["metrics"]["search_accuracy"] = {
            "score": score,
            "max_score": max_score,
            "percentage": score / max_score * 100
        }
        
        print(f"\n  得分: {score:.1f}/{max_score} ({score/max_score*100:.1f}%)")
        print()
    
    def test_performance(self):
        """Metric 3: 性能指标"""
        print("⚡ Metric 3: 性能指标（Performance）")
        print("-" * 80)
        
        score = 0.0
        max_score = 20.0
        
        # 测试搜索性能
        print("\n  测试搜索性能:")
        try:
            start_time = time.time()
            result = subprocess.run([
                "python3", str(self.scripts_dir / "search_content.py"),
                "--query", "AI编程",
                "--top-k", "5"
            ], capture_output=True, text=True, timeout=5)
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                search_time_ms = data.get("search_time_ms", elapsed_ms)
                
                print(f"    - 搜索耗时: {search_time_ms:.1f}ms")
                
                if search_time_ms < 100:
                    print(f"    ✓ 性能优秀 (<100ms)")
                    score += max_score / 2
                elif search_time_ms < 200:
                    print(f"    ✓ 性能良好 (<200ms)")
                    score += (max_score / 2) * 0.8
                elif search_time_ms < 500:
                    print(f"    ⚠️  性能一般 (<500ms)")
                    score += (max_score / 2) * 0.5
                else:
                    print(f"    ✗ 性能较差 (≥500ms)")
            
        except Exception as e:
            print(f"    ✗ 性能测试失败: {e}")
        
        # 测试索引大小
        print("\n  测试索引大小:")
        try:
            total_size = 0
            for file in ["own_works.json", "reference_examples.json", "search_index.json", "metadata.json"]:
                file_path = self.data_dir / file
                if file_path.exists():
                    size = file_path.stat().st_size
                    total_size += size
                    print(f"    - {file}: {size/1024:.1f}KB")
            
            print(f"    总大小: {total_size/1024:.1f}KB")
            
            if total_size < 1024 * 1024:  # <1MB
                print(f"    ✓ 索引大小合理 (<1MB)")
                score += max_score / 2
            elif total_size < 5 * 1024 * 1024:  # <5MB
                print(f"    ✓ 索引大小可接受 (<5MB)")
                score += (max_score / 2) * 0.7
            else:
                print(f"    ⚠️  索引大小较大 (≥5MB)")
                score += (max_score / 2) * 0.5
        
        except Exception as e:
            print(f"    ✗ 索引大小检查失败: {e}")
        
        self.results["metrics"]["performance"] = {
            "score": score,
            "max_score": max_score,
            "percentage": score / max_score * 100
        }
        
        print(f"\n  得分: {score:.1f}/{max_score} ({score/max_score*100:.1f}%)")
        print()
    
    def test_api_availability(self):
        """Metric 4: API 可用性"""
        print("🔌 Metric 4: API 可用性（API Availability）")
        print("-" * 80)
        
        score = 0.0
        max_score = 15.0
        
        apis = [
            ("search_content.py", ["--query", "测试", "--top-k", "1"]),
            ("search_reference.py", ["--query", "测试", "--top-k", "1"]),
        ]
        
        points_per_api = max_score / len(apis)
        
        for api_name, args in apis:
            print(f"\n  测试 {api_name}:")
            try:
                result = subprocess.run([
                    "python3", str(self.scripts_dir / api_name),
                    *args
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    if "results" in data:
                        print(f"    ✓ API 可用")
                        score += points_per_api
                    else:
                        print(f"    ✗ 返回格式异常")
                else:
                    print(f"    ✗ API 调用失败: {result.stderr}")
            
            except Exception as e:
                print(f"    ✗ 测试异常: {e}")
        
        self.results["metrics"]["api_availability"] = {
            "score": score,
            "max_score": max_score,
            "percentage": score / max_score * 100
        }
        
        print(f"\n  得分: {score:.1f}/{max_score} ({score/max_score*100:.1f}%)")
        print()
    
    def test_data_quality(self):
        """Metric 5: 数据质量"""
        print("✨ Metric 5: 数据质量（Data Quality）")
        print("-" * 80)
        
        score = 0.0
        max_score = 15.0
        
        try:
            # 检查自有内容数据质量
            with open(self.data_dir / "own_works.json", 'r') as f:
                own_works = json.load(f)
            
            print(f"\n  检查自有内容数据质量:")
            
            # 检查必需字段
            required_fields = ["id", "file_path", "title", "summary", "word_count", "quality_score", "keywords"]
            valid_count = 0
            
            for doc in own_works:
                if all(field in doc for field in required_fields):
                    valid_count += 1
            
            validity_ratio = valid_count / len(own_works) if own_works else 0
            print(f"    - 有效记录比例: {validity_ratio*100:.1f}% ({valid_count}/{len(own_works)})")
            
            if validity_ratio >= 0.95:
                print(f"    ✓ 数据质量优秀 (≥95%)")
                score += max_score / 2
            elif validity_ratio >= 0.80:
                print(f"    ✓ 数据质量良好 (≥80%)")
                score += (max_score / 2) * 0.7
            else:
                print(f"    ⚠️  数据质量需改进 (<80%)")
                score += (max_score / 2) * 0.5
            
            # 检查标杆案例数据质量
            with open(self.data_dir / "reference_examples.json", 'r') as f:
                references = json.load(f)
            
            print(f"\n  检查标杆案例数据质量:")
            ref_required_fields = ["id", "file_path", "title", "author", "platform", "keywords"]
            ref_valid_count = 0
            
            for doc in references:
                if all(field in doc for field in ref_required_fields):
                    ref_valid_count += 1
            
            ref_validity_ratio = ref_valid_count / len(references) if references else 0
            print(f"    - 有效记录比例: {ref_validity_ratio*100:.1f}% ({ref_valid_count}/{len(references)})")
            
            if ref_validity_ratio >= 0.95:
                print(f"    ✓ 数据质量优秀 (≥95%)")
                score += max_score / 2
            elif ref_validity_ratio >= 0.80:
                print(f"    ✓ 数据质量良好 (≥80%)")
                score += (max_score / 2) * 0.7
            else:
                print(f"    ⚠️  数据质量需改进 (<80%)")
                score += (max_score / 2) * 0.5
        
        except Exception as e:
            print(f"    ✗ 数据质量检查失败: {e}")
        
        self.results["metrics"]["data_quality"] = {
            "score": score,
            "max_score": max_score,
            "percentage": score / max_score * 100
        }
        
        print(f"\n  得分: {score:.1f}/{max_score} ({score/max_score*100:.1f}%)")
        print()
    
    def calculate_overall_score(self):
        """计算总分"""
        total_score = sum(m["score"] for m in self.results["metrics"].values())
        max_total_score = sum(m["max_score"] for m in self.results["metrics"].values())
        
        self.results["overall_score"] = total_score / max_total_score * 100
        
        if self.results["overall_score"] >= 90:
            self.results["status"] = "EXCELLENT"
        elif self.results["overall_score"] >= 80:
            self.results["status"] = "GOOD"
        elif self.results["overall_score"] >= 70:
            self.results["status"] = "ACCEPTABLE"
        else:
            self.results["status"] = "NEEDS_IMPROVEMENT"
    
    def print_summary(self):
        """输出总结报告"""
        print("=" * 80)
        print("📋 验证总结报告")
        print("=" * 80)
        print()
        
        print("Metrics 得分:")
        for metric_name, metric_data in self.results["metrics"].items():
            print(f"  - {metric_name.replace('_', ' ').title()}: "
                  f"{metric_data['score']:.1f}/{metric_data['max_score']} "
                  f"({metric_data['percentage']:.1f}%)")
        
        print()
        print(f"总分: {self.results['overall_score']:.1f}/100")
        print(f"状态: {self.results['status']}")
        
        print()
        if self.results["status"] == "EXCELLENT":
            print("✅ 验证通过！memory-index skill 完全达到预期目标。")
        elif self.results["status"] == "GOOD":
            print("✅ 验证通过！memory-index skill 达到预期目标，有小幅改进空间。")
        elif self.results["status"] == "ACCEPTABLE":
            print("⚠️  验证基本通过，但存在一些需要改进的地方。")
        else:
            print("❌ 验证未通过，需要修复以下问题后再次验证。")
        
        print()


def main():
    data_dir = "~/.cursor/skills/content-creator-memory/data"
    scripts_dir = "~/.cursor/skills/content-creator-memory/scripts"
    
    validator = SkillValidator(data_dir, scripts_dir)
    validator.run_all_tests()


if __name__ == "__main__":
    main()
