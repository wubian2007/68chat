#!/usr/bin/env python3
"""
移动端专用抓取器 - 获取手机版完整内容
"""

import requests
from pathlib import Path
from bs4 import BeautifulSoup
import json
import time

def scrape_mobile_version():
    """抓取移动端版本的完整内容"""
    
    # 移动端User-Agent
    mobile_headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    }
    
    # 创建输出目录
    output_dir = Path("mobile_scrape_output")
    output_dir.mkdir(exist_ok=True)
    
    url = "https://68tt.co/cn/"
    
    print("🔍 开始抓取移动端版本...")
    print(f"📱 User-Agent: iPhone")
    print(f"🌐 目标URL: {url}")
    
    try:
        response = requests.get(url, headers=mobile_headers, timeout=30)
        if response.status_code != 200:
            print(f"❌ 请求失败: HTTP {response.status_code}")
            return
        
        print(f"✅ 页面获取成功: {len(response.text)} 字符")
        
        # 保存原始HTML
        with open(output_dir / "mobile_raw.html", 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 分析移动端特有的内容结构
        print("\n📋 分析移动端内容结构:")
        
        # 查找phone-inner区域
        phone_inner_sections = soup.find_all('div', class_='phone-inner')
        print(f"📱 找到 {len(phone_inner_sections)} 个 phone-inner 区域")
        
        mobile_content = {
            'title': soup.title.string if soup.title else '',
            'phone_inner_sections': [],
            'mobile_specific_content': [],
            'images': [],
            'text_content': []
        }
        
        for i, section in enumerate(phone_inner_sections):
            print(f"\n📱 Phone-inner 区域 {i+1}:")
            
            section_data = {
                'index': i+1,
                'classes': section.get('class', []),
                'html': str(section),
                'text_content': section.get_text(strip=True),
                'images': [],
                'buttons': [],
                'structure': []
            }
            
            # 查找图片
            images = section.find_all('img')
            for img in images:
                img_data = {
                    'src': img.get('src', ''),
                    'alt': img.get('alt', ''),
                    'class': img.get('class', [])
                }
                section_data['images'].append(img_data)
                print(f"  🖼️ 图片: {img_data['src']}")
            
            # 查找按钮和链接
            buttons = section.find_all(['a', 'button', 'div'], class_=lambda x: x and ('btn' in ' '.join(x) or 'download' in ' '.join(x)))
            for btn in buttons:
                btn_data = {
                    'tag': btn.name,
                    'class': btn.get('class', []),
                    'text': btn.get_text(strip=True),
                    'href': btn.get('href', ''),
                    'id': btn.get('id', '')
                }
                section_data['buttons'].append(btn_data)
                print(f"  🔘 按钮: {btn_data['text']} ({btn_data['class']})")
            
            # 查找文本内容
            text_elements = section.find_all(['p', 'div', 'span'], string=True)
            for elem in text_elements:
                text = elem.get_text(strip=True)
                if text and len(text) > 5:  # 过滤短文本
                    section_data['text_content'] = text
                    print(f"  📝 文本: {text[:50]}...")
            
            mobile_content['phone_inner_sections'].append(section_data)
        
        # 查找其他移动端特有内容
        mobile_specific = soup.find_all(['div', 'section'], class_=lambda x: x and any(keyword in ' '.join(x) for keyword in ['mobile', 'phone', 'h5']))
        print(f"\n📱 找到 {len(mobile_specific)} 个移动端特有元素")
        
        for elem in mobile_specific:
            if elem not in phone_inner_sections:  # 避免重复
                elem_data = {
                    'tag': elem.name,
                    'classes': elem.get('class', []),
                    'text': elem.get_text(strip=True)[:200],
                    'html': str(elem)[:500]
                }
                mobile_content['mobile_specific_content'].append(elem_data)
                print(f"  📱 移动端元素: {elem_data['classes']} - {elem_data['text'][:50]}...")
        
        # 查找所有图片
        all_images = soup.find_all('img')
        for img in all_images:
            img_data = {
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'class': img.get('class', []),
                'parent_class': img.parent.get('class', []) if img.parent else []
            }
            mobile_content['images'].append(img_data)
        
        print(f"\n🖼️ 总共找到 {len(all_images)} 个图片")
        
        # 保存分析结果
        with open(output_dir / "mobile_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(mobile_content, f, indent=2, ensure_ascii=False)
        
        # 生成移动端内容报告
        generate_mobile_report(mobile_content, output_dir)
        
        print(f"\n📊 移动端抓取完成!")
        print(f"📁 输出目录: {output_dir}")
        print(f"📄 原始HTML: mobile_raw.html")
        print(f"📋 分析结果: mobile_analysis.json")
        print(f"📝 内容报告: mobile_content_report.md")
        
    except Exception as e:
        print(f"❌ 抓取失败: {e}")

def generate_mobile_report(content, output_dir):
    """生成移动端内容报告"""
    
    report = f"""# 68tt.co 移动端内容分析报告

## 📱 页面基本信息
- **标题**: {content['title']}
- **Phone-inner区域数量**: {len(content['phone_inner_sections'])}
- **移动端特有元素**: {len(content['mobile_specific_content'])}
- **图片总数**: {len(content['images'])}

## 📋 Phone-inner区域详细分析

"""
    
    for section in content['phone_inner_sections']:
        report += f"""### 区域 {section['index']}
- **CSS类**: {', '.join(section['classes'])}
- **图片数量**: {len(section['images'])}
- **按钮数量**: {len(section['buttons'])}

#### 图片资源:
"""
        for img in section['images']:
            report += f"- `{img['src']}` - {img['alt']}\n"
        
        report += "\n#### 按钮元素:\n"
        for btn in section['buttons']:
            report += f"- **{btn['text']}** ({btn['tag']}) - 类: {', '.join(btn['class'])}\n"
        
        report += f"\n#### 文本内容:\n```\n{section['text_content'][:200]}...\n```\n\n"
    
    report += "## 🖼️ 所有图片资源\n\n"
    for img in content['images']:
        report += f"- `{img['src']}` - Alt: `{img['alt']}` - 父级类: {', '.join(img['parent_class'])}\n"
    
    with open(output_dir / "mobile_content_report.md", 'w', encoding='utf-8') as f:
        f.write(report)

if __name__ == "__main__":
    scrape_mobile_version()
