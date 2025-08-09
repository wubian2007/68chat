#!/usr/bin/env python3
"""
68tt.co 网站内容抓取工具
使用 requests, BeautifulSoup 和 urllib 实现完整网站克隆
"""

import os
import sys
import requests
from urllib.parse import urljoin, urlparse, unquote
from bs4 import BeautifulSoup
import time
import json
from pathlib import Path
import mimetypes
import re

class WebsiteScraper:
    def __init__(self, base_url, output_dir="scraped_site"):
        self.base_url = base_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        self.downloaded_urls = set()
        self.failed_urls = set()
        self.site_map = {}
        
    def clean_filename(self, url):
        """清理URL生成安全的文件名"""
        parsed = urlparse(url)
        path = unquote(parsed.path)
        
        if path == '/' or path == '':
            return 'index.html'
        
        # 移除开头的斜杠
        path = path.lstrip('/')
        
        # 如果没有扩展名，添加.html
        if not os.path.splitext(path)[1]:
            if not path.endswith('/'):
                path += '.html'
            else:
                path += 'index.html'
        
        # 替换不安全的字符
        path = re.sub(r'[<>:"|?*]', '_', path)
        return path
    
    def download_file(self, url, local_path):
        """下载文件到本地路径"""
        try:
            print(f"下载: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 确保目录存在
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            self.downloaded_urls.add(url)
            return True
            
        except Exception as e:
            print(f"下载失败 {url}: {e}")
            self.failed_urls.add(url)
            return False
    
    def process_html(self, html_content, base_url):
        """处理HTML内容，下载资源并更新链接"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 处理图片
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                img_url = urljoin(base_url, src)
                if self.is_same_domain(img_url):
                    local_path = self.url_to_local_path(img_url)
                    if self.download_file(img_url, local_path):
                        img['src'] = self.local_path_to_relative(local_path)
        
        # 处理CSS链接
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                css_url = urljoin(base_url, href)
                if self.is_same_domain(css_url):
                    local_path = self.url_to_local_path(css_url)
                    if self.download_file(css_url, local_path):
                        link['href'] = self.local_path_to_relative(local_path)
        
        # 处理JavaScript
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                js_url = urljoin(base_url, src)
                if self.is_same_domain(js_url):
                    local_path = self.url_to_local_path(js_url)
                    if self.download_file(js_url, local_path):
                        script['src'] = self.local_path_to_relative(local_path)
        
        # 处理页面链接
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            if href and not href.startswith('#') and not href.startswith('mailto:'):
                page_url = urljoin(base_url, href)
                if self.is_same_domain(page_url):
                    local_path = self.url_to_local_path(page_url)
                    a['href'] = self.local_path_to_relative(local_path)
        
        return str(soup)
    
    def is_same_domain(self, url):
        """检查URL是否属于同一域名"""
        return urlparse(url).netloc == urlparse(self.base_url).netloc
    
    def url_to_local_path(self, url):
        """将URL转换为本地文件路径"""
        filename = self.clean_filename(url)
        return self.output_dir / filename
    
    def local_path_to_relative(self, local_path):
        """将本地路径转换为相对路径"""
        return os.path.relpath(local_path, self.output_dir)
    
    def scrape_page(self, url):
        """抓取单个页面"""
        if url in self.downloaded_urls:
            return
        
        try:
            print(f"抓取页面: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 处理HTML内容
            processed_html = self.process_html(response.text, url)
            
            # 保存页面
            local_path = self.url_to_local_path(url)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(processed_html)
            
            self.downloaded_urls.add(url)
            self.site_map[url] = str(local_path)
            
            print(f"✅ 成功保存: {local_path}")
            
        except Exception as e:
            print(f"❌ 页面抓取失败 {url}: {e}")
            self.failed_urls.add(url)
    
    def discover_pages(self, start_url):
        """发现网站中的所有页面"""
        pages_to_scrape = []
        
        try:
            response = self.session.get(start_url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有内部链接
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                if href and not href.startswith('#') and not href.startswith('mailto:'):
                    page_url = urljoin(start_url, href)
                    if self.is_same_domain(page_url) and page_url not in pages_to_scrape:
                        pages_to_scrape.append(page_url)
            
        except Exception as e:
            print(f"页面发现失败: {e}")
        
        return pages_to_scrape
    
    def scrape_website(self):
        """抓取整个网站"""
        print(f"🚀 开始抓取网站: {self.base_url}")
        print(f"📁 输出目录: {self.output_dir}")
        
        # 发现所有页面
        pages = [self.base_url]
        discovered_pages = self.discover_pages(self.base_url)
        pages.extend(discovered_pages)
        
        # 添加常见页面
        common_pages = ['/about', '/privacy', '/contact', '/help']
        for page in common_pages:
            full_url = self.base_url + page
            if full_url not in pages:
                pages.append(full_url)
        
        print(f"📄 发现 {len(pages)} 个页面")
        
        # 抓取所有页面
        for i, page_url in enumerate(pages, 1):
            print(f"\n[{i}/{len(pages)}] 处理页面...")
            self.scrape_page(page_url)
            time.sleep(1)  # 避免过于频繁的请求
        
        # 生成报告
        self.generate_report()
        
        print(f"\n✅ 抓取完成!")
        print(f"📊 成功: {len(self.downloaded_urls)} 个文件")
        print(f"❌ 失败: {len(self.failed_urls)} 个文件")
        print(f"📁 文件保存在: {self.output_dir}")
    
    def generate_report(self):
        """生成抓取报告"""
        report = {
            'base_url': self.base_url,
            'total_downloaded': len(self.downloaded_urls),
            'total_failed': len(self.failed_urls),
            'downloaded_urls': list(self.downloaded_urls),
            'failed_urls': list(self.failed_urls),
            'site_map': self.site_map,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        report_path = self.output_dir / 'scrape_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 生成简单的HTML报告
        html_report = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>网站抓取报告</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .success {{ color: green; }}
                .error {{ color: red; }}
                .info {{ color: blue; }}
                ul {{ list-style-type: none; }}
                li {{ margin: 5px 0; }}
            </style>
        </head>
        <body>
            <h1>网站抓取报告</h1>
            <p class="info">目标网站: {self.base_url}</p>
            <p class="info">抓取时间: {report['timestamp']}</p>
            
            <h2 class="success">成功下载 ({len(self.downloaded_urls)} 个文件)</h2>
            <ul>
                {''.join([f'<li>✅ {url}</li>' for url in sorted(self.downloaded_urls)])}
            </ul>
            
            <h2 class="error">下载失败 ({len(self.failed_urls)} 个文件)</h2>
            <ul>
                {''.join([f'<li>❌ {url}</li>' for url in sorted(self.failed_urls)])}
            </ul>
        </body>
        </html>
        """
        
        html_report_path = self.output_dir / 'scrape_report.html'
        with open(html_report_path, 'w', encoding='utf-8') as f:
            f.write(html_report)

def main():
    """主函数"""
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = "https://68tt.co/cn/"
    
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = "scraped_68tt"
    
    print("🔧 68tt.co 网站内容抓取工具")
    print("=" * 50)
    
    scraper = WebsiteScraper(target_url, output_dir)
    scraper.scrape_website()

if __name__ == "__main__":
    main()
