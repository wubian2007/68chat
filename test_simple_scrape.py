#!/usr/bin/env python3
"""
简单的68tt.co抓取测试 - 包含图片下载
"""

import requests
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time

def download_with_assets():
    """使用requests直接抓取并下载资源"""
    
    # 创建输出目录
    output_dir = Path("simple_scrape_output")
    output_dir.mkdir(exist_ok=True)
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # 要抓取的页面
    pages = [
        "https://68tt.co/cn/",
        "https://68tt.co/cn/about.html", 
        "https://68tt.co/cn/privacy.html"
    ]
    
    downloaded_images = []
    
    print("🚀 开始简单抓取...")
    
    for i, url in enumerate(pages, 1):
        print(f"\n[{i}/{len(pages)}] 处理页面: {url}")
        
        try:
            # 获取页面内容
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code != 200:
                print(f"❌ 页面获取失败: HTTP {response.status_code}")
                continue
                
            print(f"✅ 页面获取成功: {len(response.text)} 字符")
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "Untitled"
            
            # 保存HTML
            filename = f"page_{i}_{urlparse(url).path.strip('/').replace('/', '_') or 'index'}.html"
            html_path = output_dir / filename
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"📄 HTML保存: {filename}")
            
            # 查找并下载图片
            images = soup.find_all('img', src=True)
            print(f"🖼️  发现 {len(images)} 个图片")
            
            for j, img in enumerate(images):
                img_src = img['src']
                
                # 处理相对URL
                if img_src.startswith('//'):
                    img_url = 'https:' + img_src
                elif img_src.startswith('/'):
                    img_url = 'https://68tt.co' + img_src
                elif not img_src.startswith('http'):
                    img_url = urljoin(url, img_src)
                else:
                    img_url = img_src
                
                # 跳过base64图片
                if img_url.startswith('data:'):
                    continue
                    
                # 跳过已下载的图片
                if img_url in downloaded_images:
                    continue
                
                try:
                    print(f"  📥 下载图片 {j+1}: {img_url}")
                    img_response = requests.get(img_url, headers=headers, timeout=30)
                    
                    if img_response.status_code == 200:
                        # 生成文件名
                        img_filename = os.path.basename(urlparse(img_url).path)
                        if not img_filename or '.' not in img_filename:
                            # 根据内容类型生成扩展名
                            content_type = img_response.headers.get('content-type', '')
                            if 'png' in content_type:
                                ext = '.png'
                            elif 'jpeg' in content_type or 'jpg' in content_type:
                                ext = '.jpg'
                            elif 'gif' in content_type:
                                ext = '.gif'
                            elif 'svg' in content_type:
                                ext = '.svg'
                            else:
                                ext = '.jpg'
                            img_filename = f"image_{hash(img_url) % 10000}{ext}"
                        
                        # 确保文件名唯一
                        counter = 1
                        original_filename = img_filename
                        while (assets_dir / img_filename).exists():
                            name, ext = os.path.splitext(original_filename)
                            img_filename = f"{name}_{counter}{ext}"
                            counter += 1
                        
                        img_path = assets_dir / img_filename
                        with open(img_path, 'wb') as f:
                            f.write(img_response.content)
                        
                        downloaded_images.append(img_url)
                        print(f"    ✅ 保存: {img_filename} ({len(img_response.content)} 字节)")
                    else:
                        print(f"    ❌ 下载失败: HTTP {img_response.status_code}")
                        
                except Exception as e:
                    print(f"    ❌ 图片下载错误: {e}")
                
                # 避免过于频繁的请求
                time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ 页面处理错误: {e}")
        
        # 页面间稍作停顿
        time.sleep(1)
    
    # 生成报告
    print(f"\n📊 抓取完成统计:")
    
    all_files = list(output_dir.rglob("*"))
    files = [f for f in all_files if f.is_file()]
    
    html_files = [f for f in files if f.suffix == '.html']
    img_files = [f for f in files if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']]
    
    print(f"📄 HTML 文件: {len(html_files)} 个")
    print(f"🖼️  图片文件: {len(img_files)} 个")
    print(f"📁 总文件: {len(files)} 个")
    print(f"💾 输出目录: {output_dir}")
    
    # 显示文件列表
    print(f"\n📋 文件列表:")
    for file in sorted(files):
        size = file.stat().st_size
        if size > 1024:
            size_str = f"{size/1024:.1f}KB"
        else:
            size_str = f"{size}B"
        print(f"  - {file.name} ({size_str})")

if __name__ == "__main__":
    download_with_assets()
