#!/usr/bin/env python3
"""
Firecrawl MCP 客户端 - 68tt.co 网站抓取
使用 Firecrawl MCP 服务进行专业网站内容提取
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
import time
import requests
from urllib.parse import urljoin, urlparse
import shutil

class FirecrawlMCPClient:
    def __init__(self, config_file="firecrawl_simple_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.output_dir = Path(self.config['scraping_config']['output']['directory'])
        self.output_dir.mkdir(exist_ok=True)
        self.api_key = None
        
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 配置文件 {self.config_file} 不存在")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件格式错误: {e}")
            sys.exit(1)
    
    def setup_api_key(self):
        """设置Firecrawl API密钥"""
        # 检查环境变量
        api_key = os.getenv('FIRECRAWL_API_KEY')
        
        if not api_key:
            print("🔑 Firecrawl API 密钥设置")
            print("=" * 40)
            print("请访问 https://firecrawl.dev 获取免费API密钥")
            print("或者使用演示模式（功能受限）")
            print()
            
            choice = input("1) 输入API密钥\n2) 使用演示模式\n请选择 (1-2): ").strip()
            
            if choice == "1":
                api_key = input("请输入您的Firecrawl API密钥: ").strip()
                if not api_key:
                    print("❌ 未输入API密钥")
                    return False
                    
                # 保存到环境变量
                os.environ['FIRECRAWL_API_KEY'] = api_key
                
                # 询问是否保存到配置文件
                save_choice = input("是否保存到配置文件? (y/n): ").strip().lower()
                if save_choice == 'y':
                    self.config['mcpServers']['firecrawl']['env']['FIRECRAWL_API_KEY'] = api_key
                    with open(self.config_file, 'w', encoding='utf-8') as f:
                        json.dump(self.config, f, indent=2, ensure_ascii=False)
                    print("✅ API密钥已保存到配置文件")
                    
            elif choice == "2":
                print("⚠️  使用演示模式，功能受限")
                api_key = "demo-key"
                os.environ['FIRECRAWL_API_KEY'] = api_key
            else:
                print("❌ 无效选择")
                return False
        
        self.api_key = api_key
        return True
    
    def install_firecrawl_mcp(self):
        """安装Firecrawl MCP服务器"""
        print("📦 检查Firecrawl MCP服务器...")
        
        try:
            # 检查是否已安装
            result = subprocess.run(['npx', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ NPX 未安装，请先安装 Node.js")
                return False
            
            print("✅ NPX 可用")
            
            # 测试Firecrawl MCP服务器
            print("🔧 准备Firecrawl MCP服务器...")
            return True
            
        except FileNotFoundError:
            print("❌ Node.js/NPM 未安装")
            print("请访问 https://nodejs.org 安装 Node.js")
            return False
    
    def scrape_with_firecrawl_api(self):
        """使用Firecrawl API直接抓取"""
        if not self.api_key or self.api_key == "demo-key":
            print("⚠️  使用免费抓取模式（无需API密钥）")
            return self.scrape_without_api()
        
        print("🔥 使用Firecrawl API抓取网站...")
        
        base_url = "https://api.firecrawl.dev/v0"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        target_url = self.config['scraping_config']['target_url']
        crawl_options = self.config['scraping_config']['crawl_options']
        
        # 启动爬取任务
        crawl_data = {
            "url": target_url,
            "crawlerOptions": {
                "generateImgAltText": crawl_options.get("generateImgAltText", True),
                "returnOnlyUrls": False,
                "maxDepth": crawl_options.get("maxDepth", 2),
                "limit": crawl_options.get("limit", 5)
            },
            "pageOptions": {
                "onlyMainContent": True,
                "includeHtml": True,
                "screenshot": False
            }
        }
        
        try:
            print(f"🚀 开始爬取: {target_url}")
            response = requests.post(f"{base_url}/crawl", json=crawl_data, headers=headers)
            
            if response.status_code == 200:
                job_data = response.json()
                job_id = job_data.get("jobId")
                
                if job_id:
                    print(f"📋 爬取任务ID: {job_id}")
                    return self.wait_for_crawl_completion(job_id, headers, base_url)
                else:
                    print("❌ 未获取到任务ID")
                    return False
            else:
                print(f"❌ API请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求错误: {e}")
            return False
    
    def wait_for_crawl_completion(self, job_id, headers, base_url):
        """等待爬取任务完成"""
        print("⏳ 等待爬取任务完成...")
        
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            try:
                response = requests.get(f"{base_url}/crawl/status/{job_id}", headers=headers)
                
                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data.get("status")
                    
                    if status == "completed":
                        print("✅ 爬取任务完成!")
                        return self.process_crawl_results(status_data)
                    elif status == "failed":
                        print("❌ 爬取任务失败")
                        print(f"错误信息: {status_data.get('error', 'Unknown error')}")
                        return False
                    else:
                        completed = status_data.get("completed", 0)
                        total = status_data.get("total", 0)
                        print(f"🔄 进度: {completed}/{total} ({status})")
                        
                else:
                    print(f"⚠️  状态检查失败: {response.status_code}")
                
            except requests.exceptions.RequestException as e:
                print(f"⚠️  状态检查错误: {e}")
            
            attempt += 1
            time.sleep(5)  # 等待5秒后重试
        
        print("⏰ 等待超时")
        return False
    
    def process_crawl_results(self, results_data):
        """处理爬取结果"""
        print("📊 处理爬取结果...")
        
        data = results_data.get("data", [])
        if not data:
            print("❌ 没有获取到数据")
            return False
        
        print(f"📄 获取到 {len(data)} 个页面")
        
        # 保存原始结果
        raw_results_path = self.output_dir / "firecrawl_raw_results.json"
        with open(raw_results_path, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        # 处理每个页面
        processed_pages = []
        
        for i, page_data in enumerate(data, 1):
            url = page_data.get("metadata", {}).get("sourceURL", f"page_{i}")
            title = page_data.get("metadata", {}).get("title", "Untitled")
            
            print(f"📝 处理页面 {i}: {title}")
            
            # 保存HTML
            if page_data.get("html"):
                html_filename = self.url_to_filename(url) + ".html"
                html_path = self.output_dir / html_filename
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(page_data["html"])
            
            # 保存Markdown
            if page_data.get("markdown"):
                md_filename = self.url_to_filename(url) + ".md"
                md_path = self.output_dir / md_filename
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(page_data["markdown"])
            
            # 保存结构化数据
            page_info = {
                "url": url,
                "title": title,
                "metadata": page_data.get("metadata", {}),
                "content_length": len(page_data.get("markdown", "")),
                "html_length": len(page_data.get("html", "")),
                "extracted_at": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            processed_pages.append(page_info)
        
        # 生成总结报告
        self.generate_firecrawl_report(processed_pages, results_data)
        
        print(f"✅ 所有页面处理完成，保存在: {self.output_dir}")
        return True
    
    def scrape_without_api(self):
        """无API密钥的备用抓取方法"""
        print("🔧 使用备用抓取方法...")
        
        # 使用requests直接抓取主要页面
        target_url = self.config['scraping_config']['target_url']
        pages_to_scrape = [
            target_url,
            urljoin(target_url, '/about'),
            urljoin(target_url, '/privacy')
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        processed_pages = []
        
        for url in pages_to_scrape:
            try:
                print(f"📥 抓取: {url}")
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    # 保存HTML
                    html_filename = self.url_to_filename(url) + ".html"
                    html_path = self.output_dir / html_filename
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    # 提取基本信息
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.title.string if soup.title else "Untitled"
                    
                    page_info = {
                        "url": url,
                        "title": title.strip(),
                        "status_code": response.status_code,
                        "content_length": len(response.text),
                        "extracted_at": time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    processed_pages.append(page_info)
                    print(f"✅ 成功: {title.strip()}")
                    
                else:
                    print(f"❌ 失败 {url}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 错误 {url}: {e}")
        
        # 生成报告
        self.generate_simple_report(processed_pages)
        return len(processed_pages) > 0
    
    def url_to_filename(self, url):
        """URL转文件名"""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        if not path:
            return 'index'
        
        # 清理文件名
        filename = path.replace('/', '_').replace('?', '_').replace('&', '_')
        return filename or 'index'
    
    def generate_firecrawl_report(self, processed_pages, raw_data):
        """生成Firecrawl报告"""
        report = {
            "scraping_info": {
                "tool": "Firecrawl MCP",
                "target_url": self.config['scraping_config']['target_url'],
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "total_pages": len(processed_pages),
                "api_key_used": bool(self.api_key and self.api_key != "demo-key")
            },
            "pages": processed_pages,
            "raw_data_summary": {
                "total_data_points": len(raw_data.get("data", [])),
                "job_status": raw_data.get("status", "unknown"),
                "completed": raw_data.get("completed", 0),
                "total": raw_data.get("total", 0)
            }
        }
        
        report_path = self.output_dir / "firecrawl_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 报告已生成: {report_path}")
    
    def generate_simple_report(self, processed_pages):
        """生成简单报告"""
        report = {
            "scraping_info": {
                "tool": "Backup Scraper",
                "target_url": self.config['scraping_config']['target_url'],
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "total_pages": len(processed_pages)
            },
            "pages": processed_pages
        }
        
        report_path = self.output_dir / "scraping_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 报告已生成: {report_path}")
    
    def run(self):
        """运行Firecrawl MCP客户端"""
        print("🔥 Firecrawl MCP 68tt.co 网站抓取器")
        print("=" * 50)
        
        # 检查Node.js环境
        if not self.install_firecrawl_mcp():
            return False
        
        # 设置API密钥
        if not self.setup_api_key():
            return False
        
        # 开始抓取
        success = self.scrape_with_firecrawl_api()
        
        if success:
            print("\n🎉 Firecrawl 抓取完成!")
            print(f"📁 结果保存在: {self.output_dir}")
            
            # 显示输出文件
            if self.output_dir.exists():
                files = list(self.output_dir.glob("*"))
                print(f"\n📄 生成的文件 ({len(files)} 个):")
                for file in sorted(files):
                    print(f"   - {file.name}")
        else:
            print("\n❌ 抓取失败")
        
        return success

def main():
    """主函数"""
    client = FirecrawlMCPClient()
    client.run()

if __name__ == "__main__":
    main()
