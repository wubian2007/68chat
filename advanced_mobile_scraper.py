#!/usr/bin/env python3
"""
高级移动端抓取器 - 检查JavaScript动态内容和CSS媒体查询
"""

import requests
from pathlib import Path
from bs4 import BeautifulSoup
import json
import re

def analyze_mobile_specific_content():
    """分析移动端特有的内容和样式"""
    
    output_dir = Path("advanced_mobile_analysis")
    output_dir.mkdir(exist_ok=True)
    
    # 移动端User-Agent
    mobile_headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    }
    
    url = "https://68tt.co/cn/"
    
    print("🔍 高级移动端内容分析...")
    
    try:
        # 获取HTML内容
        response = requests.get(url, headers=mobile_headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("✅ 页面获取成功")
        
        analysis = {
            'mobile_content_areas': [],
            'hidden_elements': [],
            'css_links': [],
            'javascript_files': [],
            'media_queries': [],
            'mobile_specific_classes': []
        }
        
        # 1. 分析所有可能包含移动端内容的区域
        mobile_areas = soup.find_all(['div', 'section', 'article'], class_=lambda x: x and any(
            keyword in ' '.join(x).lower() for keyword in ['phone', 'mobile', 'h5', 'inner', 'content', 'feature', 'intro']
        ))
        
        print(f"\n📱 找到 {len(mobile_areas)} 个潜在的移动端内容区域:")
        
        for area in mobile_areas:
            area_info = {
                'tag': area.name,
                'classes': area.get('class', []),
                'id': area.get('id', ''),
                'text_content': area.get_text(strip=True)[:200],
                'has_images': len(area.find_all('img')) > 0,
                'image_count': len(area.find_all('img')),
                'child_elements': len(area.find_all()),
                'style': area.get('style', ''),
                'display_style': 'none' if 'display:none' in area.get('style', '').replace(' ', '') else 'visible'
            }
            
            # 检查是否有详细的文本内容
            if len(area.get_text(strip=True)) > 50:
                area_info['detailed_text'] = area.get_text(strip=True)
            
            # 检查图片
            images = area.find_all('img')
            area_info['images'] = []
            for img in images:
                area_info['images'].append({
                    'src': img.get('src', ''),
                    'alt': img.get('alt', ''),
                    'class': img.get('class', [])
                })
            
            analysis['mobile_content_areas'].append(area_info)
            print(f"  📍 {area_info['tag']}.{'.'.join(area_info['classes'])} - {area_info['text_content'][:50]}...")
            if area_info['image_count'] > 0:
                print(f"    🖼️ 包含 {area_info['image_count']} 个图片")
        
        # 2. 检查CSS文件链接
        css_links = soup.find_all('link', rel='stylesheet')
        for link in css_links:
            href = link.get('href', '')
            if href:
                analysis['css_links'].append(href)
                print(f"🎨 CSS文件: {href}")
        
        # 3. 检查JavaScript文件
        js_scripts = soup.find_all('script', src=True)
        for script in js_scripts:
            src = script.get('src', '')
            if src:
                analysis['javascript_files'].append(src)
                print(f"⚡ JS文件: {src}")
        
        # 4. 尝试获取CSS内容分析媒体查询
        try:
            for css_link in analysis['css_links']:
                if css_link.startswith('../'):
                    css_url = f"https://68tt.co/css/{css_link.replace('../css/', '')}"
                    print(f"\n🔍 分析CSS文件: {css_url}")
                    
                    css_response = requests.get(css_url, timeout=15)
                    if css_response.status_code == 200:
                        css_content = css_response.text
                        
                        # 查找媒体查询
                        media_queries = re.findall(r'@media[^{]+\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', css_content, re.DOTALL)
                        analysis['media_queries'].extend(media_queries)
                        
                        # 查找移动端特有的类
                        mobile_classes = re.findall(r'\.phone-[^,\s{]+|\.mobile-[^,\s{]+|\.h5-[^,\s{]+', css_content)
                        analysis['mobile_specific_classes'].extend(mobile_classes)
                        
                        print(f"  📱 找到 {len(media_queries)} 个媒体查询")
                        print(f"  📱 找到 {len(mobile_classes)} 个移动端类")
                        
        except Exception as e:
            print(f"⚠️ CSS分析失败: {e}")
        
        # 5. 查找隐藏元素（可能在移动端显示）
        hidden_elements = soup.find_all(style=lambda x: x and 'display:none' in x.replace(' ', ''))
        for elem in hidden_elements:
            hidden_info = {
                'tag': elem.name,
                'classes': elem.get('class', []),
                'id': elem.get('id', ''),
                'content': elem.get_text(strip=True)[:100],
                'has_images': len(elem.find_all('img')) > 0
            }
            analysis['hidden_elements'].append(hidden_info)
            print(f"👻 隐藏元素: {hidden_info['tag']}.{'.'.join(hidden_info['classes'])} - {hidden_info['content'][:30]}...")
        
        # 保存分析结果
        with open(output_dir / "advanced_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        # 生成详细报告
        generate_advanced_report(analysis, output_dir)
        
        print(f"\n📊 高级分析完成!")
        print(f"📁 输出目录: {output_dir}")
        print(f"📋 分析结果: advanced_analysis.json")
        print(f"📝 详细报告: advanced_mobile_report.md")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")

def generate_advanced_report(analysis, output_dir):
    """生成高级分析报告"""
    
    report = f"""# 68tt.co 高级移动端内容分析报告

## 📱 移动端内容区域分析

共发现 {len(analysis['mobile_content_areas'])} 个潜在的移动端内容区域：

"""
    
    for i, area in enumerate(analysis['mobile_content_areas'], 1):
        report += f"""### 区域 {i}: {area['tag']}.{'.'.join(area['classes'])}
- **ID**: {area['id']}
- **显示状态**: {area['display_style']}
- **图片数量**: {area['image_count']}
- **子元素数量**: {area['child_elements']}
- **样式**: `{area['style']}`

**文本内容**:
```
{area['text_content']}
```

"""
        
        if area['images']:
            report += "**图片资源**:\n"
            for img in area['images']:
                report += f"- `{img['src']}` - Alt: `{img['alt']}`\n"
            report += "\n"
        
        if 'detailed_text' in area and len(area['detailed_text']) > 200:
            report += f"**详细文本内容**:\n```\n{area['detailed_text'][:500]}...\n```\n\n"
    
    report += f"""## 🎨 CSS和JavaScript资源

### CSS文件 ({len(analysis['css_links'])} 个):
"""
    for css in analysis['css_links']:
        report += f"- `{css}`\n"
    
    report += f"""
### JavaScript文件 ({len(analysis['javascript_files'])} 个):
"""
    for js in analysis['javascript_files']:
        report += f"- `{js}`\n"
    
    if analysis['media_queries']:
        report += f"""
## 📱 媒体查询分析 ({len(analysis['media_queries'])} 个)

"""
        for i, mq in enumerate(analysis['media_queries'][:5], 1):  # 只显示前5个
            report += f"### 媒体查询 {i}:\n```css\n{mq[:300]}...\n```\n\n"
    
    if analysis['mobile_specific_classes']:
        report += f"""
## 📱 移动端特有CSS类 ({len(analysis['mobile_specific_classes'])} 个)

"""
        for cls in set(analysis['mobile_specific_classes'])[:10]:  # 去重并只显示前10个
            report += f"- `{cls}`\n"
    
    if analysis['hidden_elements']:
        report += f"""
## 👻 隐藏元素分析 ({len(analysis['hidden_elements'])} 个)

可能在移动端显示的隐藏元素：

"""
        for elem in analysis['hidden_elements']:
            report += f"- `{elem['tag']}.{'.'.join(elem['classes'])}` - {elem['content'][:50]}...\n"
    
    with open(output_dir / "advanced_mobile_report.md", 'w', encoding='utf-8') as f:
        f.write(report)

if __name__ == "__main__":
    analyze_mobile_specific_content()
