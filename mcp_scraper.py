#!/usr/bin/env python3
"""
MCP (Model Context Protocol) 风格的网站抓取工具
专门为 68tt.co 网站设计的轻量级抓取器
"""

import asyncio
import aiohttp
import json
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time

class MCPScraper:
    def __init__(self):
        self.base_url = "https://68tt.co/cn/"
        self.output_dir = Path("mcp_scraped")
        self.session = None
        self.scraped_content = {}
        
    async def initialize(self):
        """初始化异步会话"""
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'MCP-Scraper/1.0 (68tt.co content extraction)'
            }
        )
        self.output_dir.mkdir(exist_ok=True)
        
    async def close(self):
        """关闭会话"""
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url):
        """异步获取页面内容"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    return {
                        'url': url,
                        'status': response.status,
                        'content': content,
                        'headers': dict(response.headers)
                    }
                else:
                    return {
                        'url': url,
                        'status': response.status,
                        'error': f'HTTP {response.status}'
                    }
        except Exception as e:
            return {
                'url': url,
                'status': 0,
                'error': str(e)
            }
    
    async def fetch_asset(self, url):
        """异步获取静态资源"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    return {
                        'url': url,
                        'status': response.status,
                        'content': content,
                        'content_type': response.headers.get('content-type', '')
                    }
                else:
                    return {'url': url, 'status': response.status, 'error': f'HTTP {response.status}'}
        except Exception as e:
            return {'url': url, 'status': 0, 'error': str(e)}
    
    def extract_content(self, html_content):
        """提取页面结构化内容"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 提取主要内容
        content_data = {
            'title': soup.title.string if soup.title else '',
            'meta_description': '',
            'headings': [],
            'paragraphs': [],
            'links': [],
            'images': [],
            'scripts': [],
            'stylesheets': []
        }
        
        # Meta描述
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            content_data['meta_description'] = meta_desc.get('content', '')
        
        # 标题
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            for h in headings:
                content_data['headings'].append({
                    'level': i,
                    'text': h.get_text().strip(),
                    'id': h.get('id', '')
                })
        
        # 段落
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().strip()
            if text:
                content_data['paragraphs'].append(text)
        
        # 链接
        links = soup.find_all('a', href=True)
        for link in links:
            content_data['links'].append({
                'href': link['href'],
                'text': link.get_text().strip(),
                'title': link.get('title', '')
            })
        
        # 图片
        images = soup.find_all('img', src=True)
        for img in images:
            content_data['images'].append({
                'src': img['src'],
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
        
        # 样式表
        stylesheets = soup.find_all('link', rel='stylesheet')
        for css in stylesheets:
            if css.get('href'):
                content_data['stylesheets'].append(css['href'])
        
        # JavaScript
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            content_data['scripts'].append(script['src'])
        
        return content_data
    
    async def scrape_main_pages(self):
        """抓取主要页面"""
        pages_to_scrape = [
            self.base_url,
            urljoin(self.base_url, '/about'),
            urljoin(self.base_url, '/privacy'),
            urljoin(self.base_url, '/contact'),
        ]
        
        print("🚀 开始抓取主要页面...")
        
        tasks = [self.fetch_page(url) for url in pages_to_scrape]
        results = await asyncio.gather(*tasks)
        
        scraped_pages = {}
        
        for result in results:
            if 'content' in result:
                print(f"✅ 成功抓取: {result['url']}")
                
                # 提取结构化内容
                extracted = self.extract_content(result['content'])
                
                scraped_pages[result['url']] = {
                    'raw_html': result['content'],
                    'extracted_content': extracted,
                    'status': result['status'],
                    'headers': result.get('headers', {})
                }
                
                # 保存原始HTML
                filename = self.url_to_filename(result['url'])
                html_path = self.output_dir / f"{filename}.html"
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(result['content'])
                
                # 保存结构化数据
                json_path = self.output_dir / f"{filename}.json"
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(extracted, f, ensure_ascii=False, indent=2)
                    
            else:
                print(f"❌ 抓取失败: {result['url']} - {result.get('error', 'Unknown error')}")
        
        return scraped_pages
    
    async def download_assets(self, pages_data):
        """下载静态资源"""
        assets_to_download = set()
        
        # 收集所有资源URL
        for url, page_data in pages_data.items():
            extracted = page_data['extracted_content']
            
            # 图片
            for img in extracted['images']:
                img_url = urljoin(url, img['src'])
                assets_to_download.add(img_url)
            
            # 样式表
            for css in extracted['stylesheets']:
                css_url = urljoin(url, css)
                assets_to_download.add(css_url)
            
            # JavaScript
            for js in extracted['scripts']:
                js_url = urljoin(url, js)
                assets_to_download.add(js_url)
        
        print(f"📦 发现 {len(assets_to_download)} 个静态资源")
        
        # 创建资源目录
        assets_dir = self.output_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # 下载资源
        downloaded_assets = {}
        
        for asset_url in assets_to_download:
            if self.is_same_domain(asset_url):
                result = await self.fetch_asset(asset_url)
                
                if 'content' in result:
                    filename = self.url_to_filename(asset_url, keep_extension=True)
                    asset_path = assets_dir / filename
                    
                    with open(asset_path, 'wb') as f:
                        f.write(result['content'])
                    
                    downloaded_assets[asset_url] = {
                        'local_path': str(asset_path),
                        'content_type': result['content_type'],
                        'size': len(result['content'])
                    }
                    
                    print(f"📥 下载资源: {filename}")
                else:
                    print(f"❌ 资源下载失败: {asset_url}")
        
        return downloaded_assets
    
    def is_same_domain(self, url):
        """检查是否同域名"""
        return urlparse(url).netloc == urlparse(self.base_url).netloc
    
    def url_to_filename(self, url, keep_extension=False):
        """URL转文件名"""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        if not path:
            return 'index'
        
        # 清理文件名
        filename = path.replace('/', '_').replace('?', '_').replace('&', '_')
        
        if keep_extension:
            return filename
        else:
            return os.path.splitext(filename)[0] or 'index'
    
    async def generate_mcp_report(self, pages_data, assets_data):
        """生成MCP格式的报告"""
        report = {
            'scraping_info': {
                'target_url': self.base_url,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_pages': len(pages_data),
                'total_assets': len(assets_data),
                'output_directory': str(self.output_dir)
            },
            'pages': {},
            'assets': assets_data,
            'summary': {
                'successful_pages': len([p for p in pages_data.values() if p['status'] == 200]),
                'failed_pages': len([p for p in pages_data.values() if p['status'] != 200]),
                'total_content_size': sum(len(p['raw_html']) for p in pages_data.values()),
                'unique_images': len(set(img['src'] for page in pages_data.values() 
                                      for img in page['extracted_content']['images'])),
                'unique_links': len(set(link['href'] for page in pages_data.values() 
                                     for link in page['extracted_content']['links']))
            }
        }
        
        # 简化页面数据用于报告
        for url, page_data in pages_data.items():
            report['pages'][url] = {
                'title': page_data['extracted_content']['title'],
                'status': page_data['status'],
                'content_length': len(page_data['raw_html']),
                'headings_count': len(page_data['extracted_content']['headings']),
                'paragraphs_count': len(page_data['extracted_content']['paragraphs']),
                'images_count': len(page_data['extracted_content']['images']),
                'links_count': len(page_data['extracted_content']['links'])
            }
        
        # 保存报告
        report_path = self.output_dir / 'mcp_scraping_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
    
    async def run(self):
        """运行MCP抓取器"""
        await self.initialize()
        
        try:
            print("🔧 MCP 68tt.co 网站内容抓取器")
            print("=" * 50)
            
            # 抓取页面
            pages_data = await self.scrape_main_pages()
            
            # 下载资源
            assets_data = await self.download_assets(pages_data)
            
            # 生成报告
            report = await self.generate_mcp_report(pages_data, assets_data)
            
            print("\n✅ MCP 抓取完成!")
            print(f"📊 页面: {report['summary']['successful_pages']} 成功, {report['summary']['failed_pages']} 失败")
            print(f"📦 资源: {len(assets_data)} 个文件")
            print(f"💾 总大小: {report['summary']['total_content_size']:,} 字节")
            print(f"📁 输出目录: {self.output_dir}")
            
        finally:
            await self.close()

async def main():
    """主函数"""
    scraper = MCPScraper()
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())
