#!/usr/bin/env python3
"""
关于页面和隐私页面内容抓取器
"""

import requests
from pathlib import Path
from bs4 import BeautifulSoup
import json
import time

def scrape_pages():
    """抓取关于页面和隐私页面的完整内容"""
    
    pages = {
        'about': 'https://68tt.co/cn/about.html',
        'privacy': 'https://68tt.co/cn/privacy.html'
    }
    
    # 桌面端和移动端User-Agent
    user_agents = {
        'desktop': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'mobile': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    }
    
    # 创建输出目录
    output_dir = Path("pages_analysis")
    output_dir.mkdir(exist_ok=True)
    
    results = {}
    
    for page_name, url in pages.items():
        print(f"\n🔍 抓取 {page_name} 页面: {url}")
        results[page_name] = {}
        
        for device, ua in user_agents.items():
            print(f"  📱 {device} 版本...")
            
            try:
                headers = {'User-Agent': ua}
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code != 200:
                    print(f"    ❌ HTTP {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 保存原始HTML
                with open(output_dir / f"{page_name}_{device}_raw.html", 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                # 分析页面结构
                page_data = {
                    'title': soup.title.string if soup.title else '',
                    'body_class': soup.body.get('class', []) if soup.body else [],
                    'main_content': [],
                    'images': [],
                    'text_sections': [],
                    'special_elements': []
                }
                
                # 查找主要内容区域
                main_wrapper = soup.find('div', class_='main-wrapper')
                if main_wrapper:
                    # 查找内容区域
                    content_areas = main_wrapper.find_all(['div', 'section', 'article'], 
                                                        class_=lambda x: x and any(
                                                            keyword in ' '.join(x).lower() 
                                                            for keyword in ['content', 'inner', 'main', 'about', 'privacy']
                                                        ))
                    
                    for area in content_areas:
                        area_info = {
                            'tag': area.name,
                            'classes': area.get('class', []),
                            'id': area.get('id', ''),
                            'text_content': area.get_text(strip=True)[:500],
                            'html_snippet': str(area)[:1000],
                            'child_count': len(area.find_all()),
                            'images': []
                        }
                        
                        # 查找图片
                        images = area.find_all('img')
                        for img in images:
                            img_info = {
                                'src': img.get('src', ''),
                                'alt': img.get('alt', ''),
                                'class': img.get('class', [])
                            }
                            area_info['images'].append(img_info)
                            page_data['images'].append(img_info)
                        
                        page_data['main_content'].append(area_info)
                
                # 查找所有文本段落
                text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div'], 
                                            string=lambda text: text and len(text.strip()) > 20)
                
                for elem in text_elements[:10]:  # 限制前10个
                    text_info = {
                        'tag': elem.name,
                        'class': elem.get('class', []),
                        'text': elem.get_text(strip=True)[:200],
                        'parent_class': elem.parent.get('class', []) if elem.parent else []
                    }
                    page_data['text_sections'].append(text_info)
                
                # 查找特殊元素
                special_selectors = [
                    'div[class*="about"]',
                    'div[class*="privacy"]', 
                    'div[class*="policy"]',
                    'div[class*="content"]',
                    'div[class*="text"]',
                    'div[class*="info"]'
                ]
                
                for selector in special_selectors:
                    elements = soup.select(selector)
                    for elem in elements:
                        special_info = {
                            'selector': selector,
                            'tag': elem.name,
                            'classes': elem.get('class', []),
                            'id': elem.get('id', ''),
                            'text_preview': elem.get_text(strip=True)[:100]
                        }
                        page_data['special_elements'].append(special_info)
                
                results[page_name][device] = page_data
                
                print(f"    ✅ 成功: {len(page_data['main_content'])} 个内容区域")
                print(f"       图片: {len(page_data['images'])} 个")
                print(f"       文本段落: {len(page_data['text_sections'])} 个")
                
            except Exception as e:
                print(f"    ❌ 失败: {e}")
                results[page_name][device] = {'error': str(e)}
    
    # 保存分析结果
    with open(output_dir / "pages_analysis.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # 生成报告
    generate_pages_report(results, output_dir)
    
    print(f"\n📊 页面分析完成!")
    print(f"📁 输出目录: {output_dir}")
    print(f"📋 分析结果: pages_analysis.json")
    print(f"📝 页面报告: pages_report.md")

def generate_pages_report(results, output_dir):
    """生成页面分析报告"""
    
    report = """# 关于页面和隐私页面分析报告

## 📋 页面概览

"""
    
    for page_name, page_data in results.items():
        report += f"""## 📄 {page_name.title()} 页面

"""
        
        for device, data in page_data.items():
            if 'error' in data:
                report += f"""### {device.title()} 版本
❌ 抓取失败: {data['error']}

"""
                continue
            
            report += f"""### {device.title()} 版本
- **页面标题**: {data['title']}
- **Body类**: {', '.join(data['body_class'])}
- **主要内容区域**: {len(data['main_content'])} 个
- **图片数量**: {len(data['images'])} 个
- **文本段落**: {len(data['text_sections'])} 个

#### 主要内容区域:
"""
            
            for i, area in enumerate(data['main_content'], 1):
                report += f"""
**区域 {i}**: `{area['tag']}.{'.'.join(area['classes'])}`
- ID: `{area['id']}`
- 子元素: {area['child_count']} 个
- 图片: {len(area['images'])} 个
- 内容预览: {area['text_content'][:100]}...

"""
                
                if area['images']:
                    report += "**图片资源**:\n"
                    for img in area['images']:
                        report += f"- `{img['src']}` - Alt: `{img['alt']}`\n"
                    report += "\n"
            
            if data['text_sections']:
                report += "#### 主要文本内容:\n"
                for text in data['text_sections'][:5]:  # 只显示前5个
                    report += f"- **{text['tag']}.{'.'.join(text['class'])}**: {text['text'][:80]}...\n"
                report += "\n"
            
            if data['special_elements']:
                report += "#### 特殊元素:\n"
                unique_elements = {}
                for elem in data['special_elements']:
                    key = f"{elem['tag']}.{'.'.join(elem['classes'])}"
                    if key not in unique_elements:
                        unique_elements[key] = elem
                
                for elem in list(unique_elements.values())[:5]:
                    report += f"- `{elem['tag']}.{'.'.join(elem['classes'])}` - {elem['text_preview'][:50]}...\n"
                report += "\n"
    
    report += """## 🔧 修复建议

### 1. 页面结构对比
- 比较当前页面与源站点的HTML结构
- 识别缺失或多余的内容区域
- 确保CSS类名和ID一致

### 2. 内容同步
- 更新页面标题和meta信息
- 同步所有文本内容
- 下载并替换图片资源

### 3. 样式一致性
- 确保CSS样式与源站点匹配
- 检查响应式设计在移动端的表现
- 验证字体、颜色、间距等视觉元素

### 4. 功能完整性
- 确保所有链接和交互功能正常
- 验证表单和按钮的行为
- 测试在不同设备上的兼容性
"""
    
    with open(output_dir / "pages_report.md", 'w', encoding='utf-8') as f:
        f.write(report)

if __name__ == "__main__":
    scrape_pages()
