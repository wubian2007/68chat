#!/usr/bin/env python3
"""
68tt.co 综合网站抓取工具
整合 Firecrawl MCP、简单抓取和资源下载功能
"""

import asyncio
import requests
import json
import os
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import base64

class ComprehensiveScraper:
    def __init__(self, output_dir="comprehensive_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 创建子目录
        self.assets_dir = self.output_dir / "assets"
        self.screenshots_dir = self.output_dir / "screenshots"
        self.html_dir = self.output_dir / "html"
        self.markdown_dir = self.output_dir / "markdown"
        
        for dir_path in [self.assets_dir, self.screenshots_dir, self.html_dir, self.markdown_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        self.downloaded_images = set()
        self.scraped_pages = []
        
    def scrape_page(self, url):
        """抓取单个页面"""
        print(f"🔍 抓取页面: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code != 200:
                print(f"❌ 页面获取失败: HTTP {response.status_code}")
                return None
            
            print(f"✅ 页面获取成功: {len(response.text)} 字符")
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "Untitled"
            
            # 生成文件名
            parsed_url = urlparse(url)
            filename_base = parsed_url.path.strip('/').replace('/', '_') or 'index'
            if parsed_url.query:
                filename_base += '_' + parsed_url.query.replace('&', '_').replace('=', '_')
            
            page_data = {
                'url': url,
                'title': title.strip(),
                'filename_base': filename_base,
                'html_content': response.text,
                'soup': soup,
                'content_length': len(response.text)
            }
            
            return page_data
            
        except Exception as e:
            print(f"❌ 页面抓取错误: {e}")
            return None
    
    def save_html(self, page_data):
        """保存HTML文件"""
        filename = f"{page_data['filename_base']}.html"
        html_path = self.html_dir / filename
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(page_data['html_content'])
        
        print(f"📄 HTML保存: {filename}")
        return html_path
    
    def extract_and_save_markdown(self, page_data):
        """提取并保存Markdown格式内容"""
        soup = page_data['soup']
        
        # 提取主要内容
        markdown_content = []
        
        # 标题
        if soup.title:
            markdown_content.append(f"# {soup.title.string}\n")
        
        # 主要文本内容
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div']):
            text = element.get_text().strip()
            if text and len(text) > 10:  # 过滤太短的内容
                if element.name.startswith('h'):
                    level = int(element.name[1])
                    markdown_content.append(f"{'#' * level} {text}\n")
                else:
                    markdown_content.append(f"{text}\n")
        
        # 链接
        links = soup.find_all('a', href=True)
        if links:
            markdown_content.append("\n## 链接\n")
            for link in links:
                href = link['href']
                text = link.get_text().strip()
                if text and href:
                    markdown_content.append(f"- [{text}]({href})")
        
        # 图片
        images = soup.find_all('img', src=True)
        if images:
            markdown_content.append("\n## 图片\n")
            for img in images:
                src = img['src']
                alt = img.get('alt', '')
                markdown_content.append(f"![{alt}]({src})")
        
        # 保存Markdown
        markdown_text = '\n'.join(markdown_content)
        filename = f"{page_data['filename_base']}.md"
        md_path = self.markdown_dir / filename
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
        
        print(f"📝 Markdown保存: {filename}")
        return md_path
    
    def download_images(self, page_data):
        """下载页面中的图片"""
        soup = page_data['soup']
        images = soup.find_all('img', src=True)
        
        print(f"🖼️  发现 {len(images)} 个图片")
        downloaded_count = 0
        
        for i, img in enumerate(images):
            img_src = img['src']
            
            # 处理相对URL
            if img_src.startswith('//'):
                img_url = 'https:' + img_src
            elif img_src.startswith('/'):
                img_url = 'https://68tt.co' + img_src
            elif not img_src.startswith('http'):
                img_url = urljoin(page_data['url'], img_src)
            else:
                img_url = img_src
            
            # 跳过base64和已下载的图片
            if img_url.startswith('data:') or img_url in self.downloaded_images:
                continue
            
            try:
                print(f"  📥 下载图片 {i+1}: {os.path.basename(urlparse(img_url).path)}")
                img_response = requests.get(img_url, headers=self.headers, timeout=30)
                
                if img_response.status_code == 200:
                    # 生成文件名
                    img_filename = os.path.basename(urlparse(img_url).path)
                    if not img_filename or '.' not in img_filename:
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
                    while (self.assets_dir / img_filename).exists():
                        name, ext = os.path.splitext(original_filename)
                        img_filename = f"{name}_{counter}{ext}"
                        counter += 1
                    
                    img_path = self.assets_dir / img_filename
                    with open(img_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    self.downloaded_images.add(img_url)
                    downloaded_count += 1
                    print(f"    ✅ 保存: {img_filename} ({len(img_response.content)} 字节)")
                else:
                    print(f"    ❌ 下载失败: HTTP {img_response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ 图片下载错误: {e}")
            
            # 避免过于频繁的请求
            time.sleep(0.2)
        
        print(f"📥 成功下载 {downloaded_count} 个图片")
        return downloaded_count
    
    def take_screenshot_simulation(self, page_data):
        """模拟截图功能（创建页面预览）"""
        # 由于我们无法真正截图，创建一个HTML预览文件
        preview_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>页面预览: {page_data['title']}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .preview {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 20px; }}
                .url {{ color: #666; font-size: 14px; }}
                .title {{ color: #333; font-size: 18px; font-weight: bold; margin: 10px 0; }}
                .content {{ line-height: 1.6; }}
                .stats {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="preview">
                <div class="header">
                    <div class="url">{page_data['url']}</div>
                    <div class="title">{page_data['title']}</div>
                </div>
                <div class="content">
                    <p>页面内容长度: {page_data['content_length']} 字符</p>
                    <p>抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div class="stats">
                    <strong>页面统计:</strong><br>
                    - 图片数量: {len(page_data['soup'].find_all('img'))} 个<br>
                    - 链接数量: {len(page_data['soup'].find_all('a', href=True))} 个<br>
                    - 段落数量: {len(page_data['soup'].find_all('p'))} 个
                </div>
            </div>
        </body>
        </html>
        """
        
        filename = f"{page_data['filename_base']}_preview.html"
        preview_path = self.screenshots_dir / filename
        
        with open(preview_path, 'w', encoding='utf-8') as f:
            f.write(preview_html)
        
        print(f"📸 页面预览保存: {filename}")
        return preview_path
    
    def scrape_website(self):
        """抓取整个网站"""
        print("🚀 开始综合网站抓取...")
        print(f"📁 输出目录: {self.output_dir}")
        
        # 要抓取的页面
        pages = [
            "https://68tt.co/cn/",
            "https://68tt.co/cn/about.html",
            "https://68tt.co/cn/privacy.html",
            "https://68tt.co/cn/enterprise.html"
        ]
        
        total_images = 0
        
        for i, url in enumerate(pages, 1):
            print(f"\n{'='*60}")
            print(f"[{i}/{len(pages)}] 处理页面")
            
            # 抓取页面
            page_data = self.scrape_page(url)
            if not page_data:
                continue
            
            # 保存HTML
            self.save_html(page_data)
            
            # 保存Markdown
            self.extract_and_save_markdown(page_data)
            
            # 下载图片
            img_count = self.download_images(page_data)
            total_images += img_count
            
            # 创建页面预览
            self.take_screenshot_simulation(page_data)
            
            # 记录页面信息
            self.scraped_pages.append({
                'url': page_data['url'],
                'title': page_data['title'],
                'content_length': page_data['content_length'],
                'images_downloaded': img_count
            })
            
            # 页面间停顿
            if i < len(pages):
                time.sleep(2)
        
        # 生成最终报告
        self.generate_final_report(total_images)
    
    def generate_final_report(self, total_images):
        """生成最终报告"""
        print(f"\n{'='*60}")
        print("📊 综合抓取完成统计")
        
        # 文件统计
        all_files = list(self.output_dir.rglob("*"))
        files = [f for f in all_files if f.is_file()]
        
        html_files = [f for f in files if f.suffix == '.html']
        md_files = [f for f in files if f.suffix == '.md']
        img_files = [f for f in files if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']]
        
        # 计算总大小
        total_size = sum(f.stat().st_size for f in files)
        
        print(f"📄 HTML 文件: {len(html_files)} 个")
        print(f"📝 Markdown 文件: {len(md_files)} 个")
        print(f"🖼️  图片文件: {len(img_files)} 个")
        print(f"📁 总文件数: {len(files)} 个")
        print(f"💾 总大小: {total_size/1024:.1f} KB")
        
        # 页面统计
        print(f"\n📋 页面详情:")
        for page in self.scraped_pages:
            print(f"  - {page['title']}")
            print(f"    URL: {page['url']}")
            print(f"    内容: {page['content_length']} 字符")
            print(f"    图片: {page['images_downloaded']} 个")
        
        # 生成JSON报告
        report = {
            'scraping_info': {
                'tool': 'Comprehensive Scraper',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_pages': len(self.scraped_pages),
                'total_images': len(img_files),
                'total_files': len(files),
                'total_size_bytes': total_size
            },
            'pages': self.scraped_pages,
            'file_counts': {
                'html': len(html_files),
                'markdown': len(md_files),
                'images': len(img_files),
                'total': len(files)
            },
            'directory_structure': {
                'html': str(self.html_dir),
                'markdown': str(self.markdown_dir),
                'assets': str(self.assets_dir),
                'screenshots': str(self.screenshots_dir)
            }
        }
        
        report_path = self.output_dir / 'comprehensive_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 详细报告: {report_path}")
        print(f"🎉 所有内容已保存到: {self.output_dir}")

def main():
    """主函数"""
    scraper = ComprehensiveScraper()
    scraper.scrape_website()

if __name__ == "__main__":
    main()
