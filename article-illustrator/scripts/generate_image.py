#!/usr/bin/env python3
import os
import sys
import json
import time
import argparse
import requests
import subprocess
import urllib.request

def get_secret(namespace: str, key: str = None):
    """从 secrets-vault 获取凭证"""
    script = os.path.expanduser("~/.cursor/skills/secrets-vault/scripts/get_secret.py")
    if not os.path.exists(script):
        print(f"Error: secrets-vault script not found at {script}")
        sys.exit(1)
        
    cmd = ["python3", script, namespace]
    if key:
        cmd.append(key)
        
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to get secret: {result.stderr}")
    return json.loads(result.stdout) if not key else result.stdout.strip()

def download_image(url, save_path):
    """下载图片并保存到指定路径"""
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    print(f"Downloading image to {save_path} ...")
    urllib.request.urlretrieve(url, save_path)
    print(f"✅ Image successfully saved to {save_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate image using APIMart API")
    parser.add_argument("--prompt", type=str, required=True, help="英文生图提示词")
    parser.add_argument("--style", type=str, required=True, help="风格模板ID (对应 styles.yaml 中的 key)")
    parser.add_argument("--output", type=str, required=True, help="图片的本地保存路径")
    parser.add_argument("--size", type=str, default="16:9", help="图片比例, 如 16:9, 1:1, 4:3 等")
    parser.add_argument("--resolution", type=str, default="1K", help="图片分辨率, 如 1K, 2K")
    
    args = parser.parse_args()

    style_suffix = ""
    styles_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "styles.yaml")
    
    # 手动解析 yaml 的简化版本，避免缺少 yaml 模块的问题
    if os.path.exists(styles_file):
        try:
            import yaml
            with open(styles_file, "r", encoding="utf-8") as f:
                styles_data = yaml.safe_load(f)
                if args.style in styles_data.get("styles", {}):
                    template_str = styles_data["styles"][args.style].get("template", "")
                    if "{prompt}," in template_str:
                        style_suffix = template_str.replace("{prompt},", "").strip()
                    elif "{prompt}" in template_str:
                        style_suffix = template_str.replace("{prompt}", "").strip()
        except ImportError:
            # Fallback
            with open(styles_file, "r", encoding="utf-8") as f:
                in_style = False
                for line in f:
                    if line.strip().startswith(f"{args.style}:"):
                        in_style = True
                    elif in_style and line.strip().startswith("template:"):
                        template_str = line.split("template:", 1)[1].strip().strip('"').strip("'")
                        if "{prompt}," in template_str:
                            style_suffix = template_str.replace("{prompt},", "").strip()
                        elif "{prompt}" in template_str:
                            style_suffix = template_str.replace("{prompt}", "").strip()
                        break
                    elif in_style and not line.startswith(" ") and not line.startswith("\t"):
                        if line.strip() and not line.strip().startswith("#"):
                            in_style = False

    final_prompt = args.prompt
    if style_suffix:
        final_prompt = f"{args.prompt}, {style_suffix}"
        
    print(f"Final Prompt: {final_prompt}")

    try:
        api_token = get_secret("apimart_image", "api_token")
    except Exception as e:
        print(f"Error fetching API token from secrets-vault: {e}")
        sys.exit(1)

    url = "https://api.apimart.ai/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gemini-3-pro-image-preview",
        "prompt": final_prompt,
        "n": 1,
        "size": args.size,
        "resolution": args.resolution
    }

    print("Sending generation request to APIMart API...")
    try:
        response = requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"Network error during API request: {e}")
        sys.exit(1)
        
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        sys.exit(1)
        
    res_json = response.json()
    task_id = None
    if "data" in res_json and len(res_json["data"]) > 0:
        task_id = res_json["data"][0].get("task_id")
        
    if not task_id:
        print(f"Failed to get task_id. Response: {res_json}")
        sys.exit(1)
        
    print(f"Task ID {task_id} submitted successfully. Polling status...")
    status_url = f"https://api.apimart.ai/v1/tasks/{task_id}"
    
    max_retries = 30
    for i in range(max_retries):
        time.sleep(3)
        try:
            status_res = requests.get(status_url, headers=headers)
            if status_res.status_code == 200:
                status_data = status_res.json().get("data", {})
                status = status_data.get("status")
                
                if status in ["succeeded", "completed"]:
                    images = status_data.get("result", {}).get("images", [])
                    if images and len(images) > 0 and images[0].get("url") and len(images[0]["url"]) > 0:
                        image_url = images[0]["url"][0]
                        download_image(image_url, args.output)
                        sys.exit(0)
                    else:
                        print("Task completed but no image URL found.")
                        sys.exit(1)
                elif status == "failed":
                    error_msg = status_data.get("error", {}).get("message", "Unknown error")
                    print(f"Task failed: {error_msg}")
                    sys.exit(1)
                else:
                    print(f"Status check {i+1}/{max_retries}: {status} ...")
            else:
                print(f"Status request failed with code {status_res.status_code}")
        except Exception as e:
            print(f"Exception during status check: {e}")
            
    print("Timeout waiting for image generation.")
    sys.exit(1)

if __name__ == "__main__":
    main()
