#!/usr/bin/env python3
import os
import sys
import json
import time
import base64
import argparse
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    response = requests.get(url)
    response.raise_for_status()
    with open(save_path, 'wb') as f:
        f.write(response.content)
    print(f"✅ Image successfully saved to {save_path}")

def encode_image_to_base64(image_path):
    """将本地图片转换为带有 Data URI 前缀的 base64 字符串"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Reference image not found: {image_path}")
        
    ext = os.path.splitext(image_path)[1].lower()
    mime_type = "image/jpeg"
    if ext == ".png":
        mime_type = "image/png"
    elif ext in [".webp"]:
        mime_type = "image/webp"
        
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
    return f"data:{mime_type};base64,{encoded_string}"

def submit_task_and_wait(prompt, style_suffix, size, resolution, n, output_path, reference_image, headers, max_retries=30):
    final_prompt = prompt
    if style_suffix:
        final_prompt = f"{prompt}, {style_suffix}"
        
    print(f"Final Prompt for {output_path}: {final_prompt}")

    url = "https://api.apimart.ai/v1/images/generations"
    data = {
        "model": "gemini-3-pro-image-preview",
        "prompt": final_prompt,
        "n": n,
        "size": size,
        "resolution": resolution
    }
    
    if reference_image:
        try:
            if reference_image.startswith("http://") or reference_image.startswith("https://"):
                data["image_urls"] = [reference_image]
            else:
                base64_img = encode_image_to_base64(reference_image)
                data["image_urls"] = [base64_img]
            print(f"Using reference image for {output_path}")
        except Exception as e:
            return {"success": False, "error": f"Failed to process reference image: {e}", "output": output_path}

    try:
        response = requests.post(url, headers=headers, json=data)
    except Exception as e:
        return {"success": False, "error": f"Network error during API request: {e}", "output": output_path}
        
    if response.status_code != 200:
        return {"success": False, "error": f"Error {response.status_code}: {response.text}", "output": output_path}
        
    res_json = response.json()
    task_id = None
    if "data" in res_json and len(res_json["data"]) > 0:
        task_id = res_json["data"][0].get("task_id")
        
    if not task_id:
        return {"success": False, "error": f"Failed to get task_id. Response: {res_json}", "output": output_path}
        
    print(f"Task ID {task_id} submitted successfully for {output_path}. Polling status...")
    status_url = f"https://api.apimart.ai/v1/tasks/{task_id}"
    
    for i in range(max_retries):
        time.sleep(3)
        try:
            status_res = requests.get(status_url, headers=headers)
            if status_res.status_code == 200:
                status_data = status_res.json().get("data", {})
                status = status_data.get("status")
                
                if status in ["succeeded", "completed"]:
                    images = status_data.get("result", {}).get("images", [])
                    if images and len(images) > 0:
                        saved_files = []
                        for idx, img in enumerate(images):
                            if img.get("url") and len(img["url"]) > 0:
                                image_url = img["url"][0]
                                
                                # Handle multiple outputs by appending index if n > 1
                                current_output = output_path
                                if n > 1:
                                    base, ext = os.path.splitext(output_path)
                                    current_output = f"{base}_{idx+1}{ext}"
                                    
                                download_image(image_url, current_output)
                                saved_files.append(current_output)
                        
                        if saved_files:
                            return {"success": True, "files": saved_files, "output": output_path}
                        else:
                            return {"success": False, "error": "Task completed but no valid image URLs found.", "output": output_path}
                    else:
                        return {"success": False, "error": "Task completed but no images returned.", "output": output_path}
                elif status == "failed":
                    error_msg = status_data.get("error", {}).get("message", "Unknown error")
                    return {"success": False, "error": f"Task failed: {error_msg}", "output": output_path}
                else:
                    print(f"Status check {i+1}/{max_retries} for {task_id}: {status} ...")
            else:
                print(f"Status request failed with code {status_res.status_code} for {task_id}")
        except Exception as e:
            print(f"Exception during status check for {task_id}: {e}")
            
    return {"success": False, "error": "Timeout waiting for image generation.", "output": output_path}

def main():
    parser = argparse.ArgumentParser(description="Generate image using APIMart API")
    parser.add_argument("--prompt", type=str, nargs="+", required=True, help="英文生图提示词 (支持传入多个实现并发生成)")
    parser.add_argument("--style", type=str, required=True, help="风格模板ID (对应 styles.yaml 中的 key)")
    parser.add_argument("--output", type=str, nargs="+", required=True, help="图片的本地保存路径 (需与 prompt 数量一致)")
    parser.add_argument("--size", type=str, default="16:9", help="图片比例, 如 16:9, 1:1, 4:3 等")
    parser.add_argument("--resolution", type=str, default="1K", help="图片分辨率, 如 1K, 2K")
    parser.add_argument("--reference_image", type=str, nargs="*", help="参考图路径或URL (可选，用于图生图)。如果提供，数量必须为 1 或与 prompt 数量一致")
    
    parser.add_argument("--n", type=int, default=1, help="每个提示词生成图像的数量，默认为 1")
    
    args = parser.parse_args()
    
    if len(args.prompt) != len(args.output):
        print("Error: The number of --prompt arguments must match the number of --output arguments.")
        sys.exit(1)
        
    ref_images = [None] * len(args.prompt)
    if args.reference_image:
        if len(args.reference_image) == 1:
            ref_images = [args.reference_image[0]] * len(args.prompt)
        elif len(args.reference_image) == len(args.prompt):
            ref_images = args.reference_image
        else:
            print("Error: --reference_image must have exactly 1 item or match the number of --prompt arguments.")
            sys.exit(1)

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

    try:
        api_token = get_secret("apimart_image", "api_token")
    except Exception as e:
        print(f"Error fetching API token from secrets-vault: {e}")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # Run tasks concurrently
    print(f"Starting {len(args.prompt)} concurrent image generation tasks...")
    
    all_success = True
    total_saved = 0
    
    with ThreadPoolExecutor(max_workers=min(5, len(args.prompt))) as executor:
        future_to_task = {
            executor.submit(
                submit_task_and_wait, 
                prompt, style_suffix, args.size, args.resolution, args.n, output_path, ref_img, headers
            ): (prompt, output_path)
            for prompt, output_path, ref_img in zip(args.prompt, args.output, ref_images)
        }
        
        for future in as_completed(future_to_task):
            prompt, output_path = future_to_task[future]
            try:
                result = future.result()
                if result["success"]:
                    print(f"✅ Success for {output_path}: Saved {len(result['files'])} images.")
                    total_saved += len(result['files'])
                else:
                    print(f"❌ Failed for {output_path}: {result['error']}")
                    all_success = False
            except Exception as exc:
                print(f"❌ Exception for {output_path}: {exc}")
                all_success = False
                
    if not all_success:
        print(f"⚠️ Process finished with errors. Saved {total_saved} images total.")
        sys.exit(1)
    else:
        print(f"🎉 All tasks completed successfully! Saved {total_saved} images total.")
        sys.exit(0)

if __name__ == "__main__":
    main()
