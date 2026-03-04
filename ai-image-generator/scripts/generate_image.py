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

CACHE_FILE = os.path.join(os.path.dirname(__file__), ".task_cache.json")
SUPPORTED_ASPECT_RATIOS = [
    "1:1", "3:2", "2:3", "4:3", "3:4",
    "16:9", "9:16", "5:4", "4:5", "21:9",
    "1:4", "4:1", "1:8", "8:1"
]
SUPPORTED_RESOLUTIONS = ["0.5K", "1K", "2K", "4K"]
IMAGE_MODELS = {
    "fast": "gemini-3.1-flash-image-preview",
    "quality": "gemini-3-pro-image-preview",
}
DEFAULT_APIMART_URL = "https://api.apimart.ai/v1/images/generations"
DEFAULT_APIMART_TASK_URL = "https://api.apimart.ai/v1/tasks"
DEFAULT_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_OPENROUTER_MODEL = "google/gemini-3.1-flash-image-preview"


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def get_task_for_output(output_path):
    cache = load_cache()
    abs_path = os.path.abspath(output_path)
    task_info = cache.get(abs_path)
    if task_info and task_info.get("status") in ["pending", "submitted", "processing"]:
        return task_info.get("task_id")
    return None


def set_task_for_output(output_path, task_id, status="pending"):
    cache = load_cache()
    abs_path = os.path.abspath(output_path)
    cache[abs_path] = {"task_id": task_id, "status": status, "timestamp": time.time()}
    save_cache(cache)


def clear_task_for_output(output_path):
    cache = load_cache()
    abs_path = os.path.abspath(output_path)
    if abs_path in cache:
        del cache[abs_path]
        save_cache(cache)


def get_secret(namespace: str, key: str = None):
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
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    print(f"Downloading image to {save_path} ...")
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    with open(save_path, "wb") as f:
        f.write(response.content)
    print(f"✅ Image successfully saved to {save_path}")


def save_data_url(data_url, save_path):
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    _, encoded = data_url.split(",", 1)
    with open(save_path, "wb") as f:
        f.write(base64.b64decode(encoded))
    print(f"✅ Image successfully saved to {save_path}")


def save_image_payload(image_payload, save_path):
    if image_payload.startswith("data:image/"):
        save_data_url(image_payload, save_path)
    else:
        download_image(image_payload, save_path)


def encode_image_to_base64(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Reference image not found: {image_path}")

    ext = os.path.splitext(image_path)[1].lower()
    mime_type = "image/jpeg"
    if ext == ".png":
        mime_type = "image/png"
    elif ext == ".webp":
        mime_type = "image/webp"

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded_string}"


def resolve_output_path(output_path, index, total):
    if total <= 1:
        return output_path
    base, ext = os.path.splitext(output_path)
    return f"{base}_{index + 1}{ext}"


def extract_openrouter_images(response_json):
    choices = response_json.get("choices") or []
    if not choices:
        return []

    message = choices[0].get("message", {})
    images = message.get("images") or []
    resolved = []
    for image in images:
        if not isinstance(image, dict):
            continue
        image_url = image.get("image_url") or image.get("imageUrl") or {}
        if isinstance(image_url, dict) and image_url.get("url"):
            resolved.append(image_url["url"])
    return resolved


def build_openrouter_messages(prompt, reference_image=None):
    if not reference_image:
        return [{"role": "user", "content": prompt}]

    if reference_image.startswith("http://") or reference_image.startswith("https://"):
        image_source = reference_image
    else:
        image_source = encode_image_to_base64(reference_image)

    return [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_source}},
        ],
    }]


def submit_apimart_task(prompt, model, aspect_ratio, resolution, n, output_path, reference_image, api_url, headers):
    data = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "size": aspect_ratio,
        "resolution": resolution,
    }

    if reference_image:
        try:
            if reference_image.startswith("http://") or reference_image.startswith("https://"):
                data["image_urls"] = [reference_image]
            else:
                data["image_urls"] = [encode_image_to_base64(reference_image)]
            print(f"Using reference image for {output_path}")
        except Exception as e:
            return {"success": False, "error": f"Failed to process reference image: {e}", "task_id": None}

    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=120)
    except Exception as e:
        return {"success": False, "error": f"Network error during APIMart request: {e}", "task_id": None}

    if response.status_code != 200:
        return {"success": False, "error": f"APIMart error {response.status_code}: {response.text}", "task_id": None}

    res_json = response.json()
    task_id = None
    if "data" in res_json and res_json["data"]:
        task_id = res_json["data"][0].get("task_id")

    if not task_id:
        return {"success": False, "error": f"Failed to get APIMart task_id. Response: {res_json}", "task_id": None}

    return {"success": True, "task_id": task_id}


def poll_apimart_task(task_id, output_path, n, task_status_url, headers, max_retries=60):
    status_url = f"{task_status_url.rstrip('/')}/{task_id}"
    for i in range(max_retries):
        time.sleep(3)
        try:
            status_res = requests.get(status_url, headers=headers, timeout=10)
            if status_res.status_code == 200:
                status_data = status_res.json().get("data", {})
                status = status_data.get("status")

                if status in ["succeeded", "completed"]:
                    images = status_data.get("result", {}).get("images", [])
                    if images:
                        saved_files = []
                        for idx, img in enumerate(images):
                            urls = img.get("url") or []
                            if urls:
                                current_output = resolve_output_path(output_path, idx, n)
                                save_image_payload(urls[0], current_output)
                                saved_files.append(current_output)

                        clear_task_for_output(output_path)
                        if saved_files:
                            return {"success": True, "files": saved_files, "output": output_path, "task_id": task_id, "provider": "apimart"}
                        return {"success": False, "error": "APIMart task completed but no valid image URLs found.", "output": output_path, "task_id": task_id}

                    clear_task_for_output(output_path)
                    return {"success": False, "error": "APIMart task completed but no images returned.", "output": output_path, "task_id": task_id}

                if status == "failed":
                    clear_task_for_output(output_path)
                    error_msg = status_data.get("error", {}).get("message", "Unknown error")
                    return {"success": False, "error": f"APIMart task failed: {error_msg}", "output": output_path, "task_id": task_id}

                print(f"Status check {i + 1}/{max_retries} for {task_id}: {status} ...")
            else:
                print(f"Status request failed with code {status_res.status_code} for {task_id}")
        except Exception as e:
            print(f"Exception during status check for {task_id}: {e}")

    return {
        "success": False,
        "error": f"Timeout waiting for APIMart image generation. Task ID: {task_id}. Please run the command again to resume polling.",
        "output": output_path,
        "task_id": task_id,
        "timeout": True,
    }


def submit_openrouter_generation(prompt, model, aspect_ratio, resolution, n, output_path, reference_image, api_url, headers):
    saved_files = []
    for idx in range(n):
        payload = {
            "model": model,
            "messages": build_openrouter_messages(prompt, reference_image),
            "modalities": ["image", "text"],
            "image_config": {
                "aspect_ratio": aspect_ratio,
                "image_size": resolution,
            },
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=180)
        except Exception as e:
            return {"success": False, "error": f"Network error during OpenRouter request: {e}", "output": output_path, "task_id": None}

        if response.status_code != 200:
            return {"success": False, "error": f"OpenRouter error {response.status_code}: {response.text}", "output": output_path, "task_id": None}

        res_json = response.json()
        image_payloads = extract_openrouter_images(res_json)
        if not image_payloads:
            return {"success": False, "error": f"OpenRouter returned no images. Response: {res_json}", "output": output_path, "task_id": None}

        current_output = resolve_output_path(output_path, idx, n)
        try:
            save_image_payload(image_payloads[0], current_output)
        except Exception as e:
            return {"success": False, "error": f"Failed to save OpenRouter image: {e}", "output": output_path, "task_id": None}
        saved_files.append(current_output)

    return {"success": True, "files": saved_files, "output": output_path, "task_id": None, "provider": "openrouter"}


def submit_task_and_wait(
    prompt,
    style_suffix,
    provider,
    apimart_model,
    openrouter_model,
    aspect_ratio,
    resolution,
    n,
    output_path,
    reference_image,
    apimart_url,
    apimart_task_url,
    apimart_headers,
    openrouter_url,
    openrouter_headers,
    force=False,
):
    final_prompt = f"{prompt}, {style_suffix}" if style_suffix else prompt
    print(f"Final Prompt for {output_path}: {final_prompt}")

    task_id = None
    if provider in ["apimart", "auto"] and not force:
        task_id = get_task_for_output(output_path)

    if task_id:
        print(f"Found existing APIMart task {task_id} for {output_path} in cache. Resuming polling...")
        return poll_apimart_task(task_id, output_path, n, apimart_task_url, apimart_headers)

    if provider == "openrouter":
        return submit_openrouter_generation(
            final_prompt,
            openrouter_model,
            aspect_ratio,
            resolution,
            n,
            output_path,
            reference_image,
            openrouter_url,
            openrouter_headers,
        )

    submit_result = submit_apimart_task(
        final_prompt,
        apimart_model,
        aspect_ratio,
        resolution,
        n,
        output_path,
        reference_image,
        apimart_url,
        apimart_headers,
    )
    if submit_result["success"]:
        task_id = submit_result["task_id"]
        print(f"APIMart task {task_id} submitted successfully for {output_path}. Caching and polling...")
        set_task_for_output(output_path, task_id, "submitted")
        return poll_apimart_task(task_id, output_path, n, apimart_task_url, apimart_headers)

    if provider == "apimart":
        return {"success": False, "error": submit_result["error"], "output": output_path, "task_id": None}

    print(f"APIMart submission failed before task creation for {output_path}. Falling back to OpenRouter...")
    return submit_openrouter_generation(
        final_prompt,
        openrouter_model,
        aspect_ratio,
        resolution,
        n,
        output_path,
        reference_image,
        openrouter_url,
        openrouter_headers,
    )


def main():
    parser = argparse.ArgumentParser(description="Generate image using APIMart or OpenRouter API")
    parser.add_argument("--prompt", type=str, nargs="+", required=True, help="英文生图提示词 (支持传入多个实现并发生成)")
    parser.add_argument("--style", type=str, required=True, help="风格模板ID (对应 styles.yaml 中的 key)")
    parser.add_argument("--output", type=str, nargs="+", required=True, help="图片的本地保存路径 (需与 prompt 数量一致)")
    parser.add_argument(
        "--aspect_ratio", "--size",
        dest="aspect_ratio",
        type=str,
        default="16:9",
        choices=SUPPORTED_ASPECT_RATIOS,
        help="图片横纵比。推荐使用 --aspect_ratio；--size 为兼容旧命令的别名。"
    )
    parser.add_argument("--mode", choices=["fast", "quality"], default="fast", help="生图模式：fast 为默认快速模式，quality 为高质量模式。")
    parser.add_argument("--provider", choices=["auto", "apimart", "openrouter"], default="auto", help="图片生成通道。auto 会优先 APIMart，提交前失败时切 OpenRouter。")
    parser.add_argument(
        "--resolution",
        type=str,
        default="1K",
        choices=SUPPORTED_RESOLUTIONS,
        help="图片分辨率, 默认 1K。除非用户明确要求，否则应保持 1K。可选 0.5K / 1K / 2K / 4K"
    )
    parser.add_argument("--reference_image", type=str, nargs="*", help="参考图路径或URL (可选，用于图生图)。如果提供，数量必须为 1 或与 prompt 数量一致")
    parser.add_argument("--n", type=int, default=1, help="每个提示词生成图像的数量，默认为 1")
    parser.add_argument("--force", action="store_true", help="强制重新生成，忽略本地缓存的任务凭证")

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
    if os.path.exists(styles_file):
        try:
            import yaml
            with open(styles_file, "r", encoding="utf-8") as f:
                styles_data = yaml.safe_load(f)
            if args.style in styles_data.get("styles", {}):
                template_str = styles_data["styles"][args.style].get("template", "")
                template_str = template_str.replace("{brand_guidelines},", "").replace("{brand_guidelines}", "").strip()
                if "{prompt}," in template_str:
                    style_suffix = template_str.replace("{prompt},", "").strip()
                elif "{prompt}" in template_str:
                    style_suffix = template_str.replace("{prompt}", "").strip()
        except ImportError:
            with open(styles_file, "r", encoding="utf-8") as f:
                in_style = False
                for line in f:
                    if line.strip().startswith(f"{args.style}:"):
                        in_style = True
                    elif in_style and line.strip().startswith("template:"):
                        template_str = line.split("template:", 1)[1].strip().strip('"').strip("'")
                        template_str = template_str.replace("{brand_guidelines},", "").replace("{brand_guidelines}", "").strip()
                        if "{prompt}," in template_str:
                            style_suffix = template_str.replace("{prompt},", "").strip()
                        elif "{prompt}" in template_str:
                            style_suffix = template_str.replace("{prompt}", "").strip()
                        break
                    elif in_style and not line.startswith(" ") and not line.startswith("\t") and line.strip() and not line.strip().startswith("#"):
                        in_style = False

    try:
        apimart_creds = get_secret("apimart_image")
        openrouter_creds = get_secret("openrouter_image")
    except Exception as e:
        print(f"Error fetching API credentials from secrets-vault: {e}")
        sys.exit(1)

    apimart_headers = {
        "Authorization": f"Bearer {apimart_creds['api_token']}",
        "Content-Type": "application/json",
    }
    openrouter_headers = {
        "Authorization": f"Bearer {openrouter_creds['api_key']}",
        "Content-Type": "application/json",
    }

    apimart_model = IMAGE_MODELS[args.mode]
    openrouter_model = openrouter_creds.get("model") or DEFAULT_OPENROUTER_MODEL
    apimart_url = apimart_creds.get("api_url") or DEFAULT_APIMART_URL
    apimart_task_url = apimart_creds.get("task_status_url") or DEFAULT_APIMART_TASK_URL
    openrouter_url = openrouter_creds.get("api_url") or DEFAULT_OPENROUTER_URL

    print(
        f"Starting {len(args.prompt)} concurrent image generation tasks... "
        f"(provider={args.provider}, mode={args.mode}, apimart_model={apimart_model}, "
        f"openrouter_model={openrouter_model}, aspect_ratio={args.aspect_ratio}, resolution={args.resolution})"
    )

    all_success = True
    total_saved = 0
    with ThreadPoolExecutor(max_workers=min(5, len(args.prompt))) as executor:
        future_to_task = {
            executor.submit(
                submit_task_and_wait,
                prompt,
                style_suffix,
                args.provider,
                apimart_model,
                openrouter_model,
                args.aspect_ratio,
                args.resolution,
                args.n,
                output_path,
                ref_img,
                apimart_url,
                apimart_task_url,
                apimart_headers,
                openrouter_url,
                openrouter_headers,
                args.force,
            ): (prompt, output_path)
            for prompt, output_path, ref_img in zip(args.prompt, args.output, ref_images)
        }

        for future in as_completed(future_to_task):
            _, output_path = future_to_task[future]
            try:
                result = future.result()
                if result["success"]:
                    print(f"✅ Success for {output_path}: provider={result.get('provider', args.provider)}, saved {len(result['files'])} images.")
                    total_saved += len(result["files"])
                else:
                    print(f"❌ Failed for {output_path}: {result['error']}")
                    all_success = False
            except Exception as exc:
                print(f"❌ Exception for {output_path}: {exc}")
                all_success = False

    if not all_success:
        print(f"⚠️ Process finished with errors or timeouts. Saved {total_saved} images total.")
        sys.exit(1)

    print(f"🎉 All tasks completed successfully! Saved {total_saved} images total.")
    sys.exit(0)


if __name__ == "__main__":
    main()
