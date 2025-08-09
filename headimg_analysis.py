#!/usr/bin/env python3
"""
headImg.png 渲染尺寸和背景色分析工具
"""

import requests
from pathlib import Path
from bs4 import BeautifulSoup
import re
import json

def analyze_headimg_rendering():
    """分析源站点headImg.png的实际渲染情况"""
    
    print("🔍 分析源站点 headImg.png 渲染情况...")
    
    # 桌面端和移动端User-Agent
    user_agents = {
        'desktop': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'mobile': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    }
    
    url = "https://68tt.co/cn/"
    results = {}
    
    for device, ua in user_agents.items():
        print(f"\n📱 分析 {device} 版本...")
        
        try:
            headers = {'User-Agent': ua}
            response = requests.get(url, headers=headers, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找headImg相关元素
            headimg_container = soup.find('div', class_='headImg')
            headimg_element = soup.find('img', src=lambda x: x and 'headImg.png' in x) if not headimg_container else headimg_container.find('img')
            
            device_result = {
                'headimg_found': headimg_element is not None,
                'headimg_src': headimg_element.get('src', '') if headimg_element else '',
                'headimg_alt': headimg_element.get('alt', '') if headimg_element else '',
                'headimg_style': headimg_element.get('style', '') if headimg_element else '',
                'container_class': headimg_container.get('class', []) if headimg_container else [],
                'container_style': headimg_container.get('style', '') if headimg_container else '',
                'parent_elements': []
            }
            
            # 分析父级元素的样式
            if headimg_element:
                current = headimg_element.parent
                level = 0
                while current and level < 5:  # 最多检查5层父级
                    parent_info = {
                        'level': level + 1,
                        'tag': current.name,
                        'class': current.get('class', []),
                        'id': current.get('id', ''),
                        'style': current.get('style', ''),
                        'computed_styles': {}
                    }
                    device_result['parent_elements'].append(parent_info)
                    current = current.parent
                    level += 1
            
            results[device] = device_result
            
            print(f"  ✅ headImg找到: {device_result['headimg_found']}")
            if device_result['headimg_found']:
                print(f"  📍 图片路径: {device_result['headimg_src']}")
                print(f"  🎨 图片样式: {device_result['headimg_style']}")
                print(f"  📦 容器类: {device_result['container_class']}")
                print(f"  🎨 容器样式: {device_result['container_style']}")
        
        except Exception as e:
            print(f"  ❌ {device} 分析失败: {e}")
            results[device] = {'error': str(e)}
    
    # 获取CSS文件分析headImg相关样式
    print(f"\n🎨 分析CSS样式...")
    try:
        css_urls = [
            'https://68tt.co/css/index.css',
            'https://68tt.co/css/lang.css'
        ]
        
        css_styles = {}
        for css_url in css_urls:
            try:
                css_response = requests.get(css_url, timeout=15)
                if css_response.status_code == 200:
                    css_content = css_response.text
                    
                    # 查找headImg相关样式
                    headimg_styles = re.findall(r'\.headImg[^{]*\{[^}]*\}', css_content, re.DOTALL)
                    headimg_img_styles = re.findall(r'\.headImg\s+img[^{]*\{[^}]*\}', css_content, re.DOTALL)
                    banner_styles = re.findall(r'\.banner[^{]*\{[^}]*\}', css_content, re.DOTALL)
                    bg_styles = re.findall(r'\.bg[^{]*\{[^}]*\}', css_content, re.DOTALL)
                    
                    css_styles[css_url] = {
                        'headImg_styles': headimg_styles,
                        'headImg_img_styles': headimg_img_styles,
                        'banner_styles': banner_styles,
                        'bg_styles': bg_styles
                    }
                    
                    print(f"  📄 {css_url}:")
                    print(f"    .headImg 样式: {len(headimg_styles)} 个")
                    print(f"    .headImg img 样式: {len(headimg_img_styles)} 个")
                    print(f"    .banner 样式: {len(banner_styles)} 个")
                    print(f"    .bg 样式: {len(bg_styles)} 个")
                    
                    # 打印具体样式
                    for style in headimg_styles + headimg_img_styles:
                        print(f"    🎨 样式: {style.strip()}")
            
            except Exception as e:
                print(f"  ⚠️ CSS分析失败 {css_url}: {e}")
        
        results['css_analysis'] = css_styles
    
    except Exception as e:
        print(f"❌ CSS分析失败: {e}")
    
    # 保存分析结果
    output_file = Path("headimg_analysis.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # 生成修复建议
    generate_fix_suggestions(results)
    
    print(f"\n📊 分析完成!")
    print(f"📋 结果保存: {output_file}")
    print(f"📝 修复建议: headimg_fix_suggestions.md")

def generate_fix_suggestions(results):
    """生成修复建议"""
    
    report = """# headImg.png 渲染问题修复建议

## 🔍 问题分析

根据对源站点的分析，headImg.png的渲染尺寸问题可能来源于：

1. **CSS样式设置不当**
2. **容器尺寸限制**
3. **背景色设置错误**
4. **响应式设计参数不匹配**

## 📊 源站点分析结果

"""
    
    for device, data in results.items():
        if device in ['desktop', 'mobile'] and 'error' not in data:
            report += f"""### {device.title()} 版本
- **headImg找到**: {data['headimg_found']}
- **图片路径**: `{data['headimg_src']}`
- **图片样式**: `{data['headimg_style']}`
- **容器类**: {data['container_class']}
- **容器样式**: `{data['container_style']}`

"""
    
    if 'css_analysis' in results:
        report += """## 🎨 CSS样式分析

从源站点的CSS文件中提取的相关样式：

"""
        for css_url, styles in results['css_analysis'].items():
            report += f"""### {css_url}

"""
            for style_type, style_list in styles.items():
                if style_list:
                    report += f"""#### {style_type}:
```css
"""
                    for style in style_list:
                        report += f"{style.strip()}\n\n"
                    report += "```\n\n"
    
    report += """## 🔧 修复方案

### 1. 图片尺寸修正
```css
.headImg img {
    /* 根据源站点的实际渲染尺寸设置 */
    width: auto;
    height: auto;
    max-width: 180px; /* 调整为源站点的实际尺寸 */
    display: block;
    margin: 0 auto;
}

/* 移动端特殊设置 */
@media (max-width: 768px) {
    .headImg img {
        max-width: 150px; /* 移动端尺寸 */
    }
}
```

### 2. 背景色调整
```css
.banner .bg {
    /* 确保背景色与源站点一致 */
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    /* 或者使用纯色背景 */
    background-color: #f8f9fa;
}
```

### 3. 容器设置
```css
.headImg {
    /* 确保容器不限制图片大小 */
    width: 100%;
    text-align: center;
    margin: 20px 0;
}
```

## ✅ 实施步骤

1. **备份当前样式**
2. **应用新的CSS规则**
3. **测试桌面端和移动端效果**
4. **微调尺寸直到与源站点一致**
5. **验证在不同屏幕尺寸下的表现**
"""
    
    with open("headimg_fix_suggestions.md", 'w', encoding='utf-8') as f:
        f.write(report)

if __name__ == "__main__":
    analyze_headimg_rendering()
