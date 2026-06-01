"""
测试脚本：验证Ollama API是否能正常返回结果
AI生成部分：本脚本由AI辅助生成，主要用于测试Ollama服务连接和模型可用性
"""

import requests
import json
import sys


def test_ollama_service():
    """测试Ollama服务是否运行"""
    print("=" * 60)
    print("开始测试Ollama服务...")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✓ Ollama服务运行正常")
            print(f"  已安装的模型: {[m['name'] for m in data.get('models', [])]}")
            return True
        else:
            print(f"✗ Ollama服务响应异常，状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到Ollama服务")
        print("  请确保Ollama已启动，或运行: ollama serve")
        return False
    except Exception as e:
        print(f"✗ 测试Ollama服务时出错: {e}")
        return False


def test_model_inference(model_name="deepseek-r1:7b"):
    """测试模型推理能力"""
    print("\n" + "=" * 60)
    print(f"开始测试模型 {model_name} 推理能力...")
    print("=" * 60)
    
    test_prompt = "请用一句话介绍自然语言处理（NLP）技术。"
    print(f"测试问题: {test_prompt}")
    print("-" * 60)
    
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": model_name,
            "prompt": test_prompt,
            "stream": False
        }
        
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "").strip()
            print(f"模型回答: {answer}")
            print("-" * 60)
            print("✓ 模型推理测试通过")
            return True
        else:
            print(f"✗ 模型推理失败，状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到Ollama服务")
        return False
    except Exception as e:
        print(f"✗ 测试模型推理时出错: {e}")
        return False


def test_embedding_model(model_name="nomic-embed-text"):
    """测试嵌入模型"""
    print("\n" + "=" * 60)
    print(f"开始测试嵌入模型 {model_name}...")
    print("=" * 60)
    
    test_text = "自然语言处理是人工智能的一个重要分支。"
    print(f"测试文本: {test_text}")
    
    try:
        url = "http://localhost:11434/api/embeddings"
        payload = {
            "model": model_name,
            "prompt": test_text
        }
        
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            embedding = data.get("embedding", [])
            print(f"嵌入向量维度: {len(embedding)}")
            print(f"前5个值: {embedding[:5]}")
            print("-" * 60)
            print("✓ 嵌入模型测试通过")
            return True
        else:
            print(f"✗ 嵌入模型测试失败，状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到Ollama服务")
        return False
    except Exception as e:
        print(f"✗ 测试嵌入模型时出错: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("Ollama环境测试脚本")
    print("=" * 60)
    
    results = []
    
    # 测试1: Ollama服务
    results.append(("Ollama服务", test_ollama_service()))
    
    # 测试2: 大模型推理
    results.append(("模型推理", test_model_inference()))
    
    # 测试3: 嵌入模型
    results.append(("嵌入模型", test_embedding_model()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(r for _, r in results)
    print("-" * 60)
    if all_passed:
        print("✓ 所有测试通过，环境配置正确！")
        sys.exit(0)
    else:
        print("✗ 部分测试失败，请检查环境配置。")
        sys.exit(1)


if __name__ == "__main__":
    main()
