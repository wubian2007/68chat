// 68tt.co 网站 JavaScript 功能

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 语言切换功能
    initLanguageSwitch();
    
    // 平滑滚动
    initSmoothScroll();
    
    // 下载按钮点击事件
    initDownloadButtons();
    
    // 响应式导航
    initResponsiveNav();
});

// 语言切换功能
function initLanguageSwitch() {
    const languageCurrent = document.querySelector('.language-current');
    const languageDropdown = document.querySelector('.language-dropdown');
    
    if (languageCurrent && languageDropdown) {
        // 点击当前语言显示/隐藏下拉菜单
        languageCurrent.addEventListener('click', function(e) {
            e.stopPropagation();
            const isVisible = languageDropdown.style.display === 'block';
            languageDropdown.style.display = isVisible ? 'none' : 'block';
        });
        
        // 点击语言选项
        const languageOptions = languageDropdown.querySelectorAll('p');
        languageOptions.forEach(function(option) {
            option.addEventListener('click', function() {
                const selectedLang = this.textContent;
                languageCurrent.querySelector('span').textContent = selectedLang;
                languageDropdown.style.display = 'none';
                
                // 这里可以添加实际的语言切换逻辑
                console.log('切换到语言:', selectedLang);
            });
        });
        
        // 点击页面其他地方关闭下拉菜单
        document.addEventListener('click', function(event) {
            if (!event.target.closest('.language-switch')) {
                languageDropdown.style.display = 'none';
            }
        });
    }
}

// 平滑滚动功能
function initSmoothScroll() {
    // 为页面内链接添加平滑滚动
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// 下载按钮功能
function initDownloadButtons() {
    const downloadButtons = document.querySelectorAll('.download-link');
    
    downloadButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // 获取下载类型
            const downloadType = this.textContent.trim();
            
            // 显示下载提示
            showDownloadModal(downloadType);
        });
    });
    
    // QR码下载链接
    const qrLinks = document.querySelectorAll('.qr-section a');
    qrLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const platform = this.textContent.trim();
            showDownloadModal(platform);
        });
    });
}

// 显示下载模态框
function showDownloadModal(downloadType) {
    // 创建模态框
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    `;
    
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white;
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        max-width: 400px;
        width: 90%;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    `;
    
    modalContent.innerHTML = `
        <h3 style="margin-bottom: 20px; color: #333;">下載 ${downloadType}</h3>
        <p style="margin-bottom: 30px; color: #666;">感謝您選擇 68！您的下載即將開始...</p>
        <div style="margin-bottom: 20px;">
            <div style="width: 60px; height: 60px; margin: 0 auto; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem;">📱</div>
        </div>
        <button onclick="closeModal()" style="background: #007bff; color: white; border: none; padding: 12px 25px; border-radius: 25px; cursor: pointer; font-size: 16px;">確定</button>
    `;
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // 添加关闭功能
    window.closeModal = function() {
        document.body.removeChild(modal);
        delete window.closeModal;
    };
    
    // 点击背景关闭
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            window.closeModal();
        }
    });
    
    // 3秒后自动关闭
    setTimeout(function() {
        if (document.body.contains(modal)) {
            window.closeModal();
        }
    }, 3000);
}

// 响应式导航
function initResponsiveNav() {
    // 在小屏幕上添加移动端菜单功能
    const nav = document.querySelector('.nav');
    const navContainer = document.querySelector('.nav-container');
    
    if (window.innerWidth <= 768) {
        // 创建移动端菜单按钮
        const mobileMenuBtn = document.createElement('button');
        mobileMenuBtn.innerHTML = '☰';
        mobileMenuBtn.style.cssText = `
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            display: none;
        `;
        
        // 监听窗口大小变化
        window.addEventListener('resize', function() {
            if (window.innerWidth <= 768) {
                mobileMenuBtn.style.display = 'block';
                navContainer.style.display = 'none';
            } else {
                mobileMenuBtn.style.display = 'none';
                navContainer.style.display = 'flex';
            }
        });
    }
}

// 添加页面滚动效果
window.addEventListener('scroll', function() {
    const header = document.querySelector('.header');
    if (header) {
        if (window.scrollY > 100) {
            header.style.background = 'rgba(255,255,255,0.95)';
            header.style.backdropFilter = 'blur(10px)';
        } else {
            header.style.background = '#fff';
            header.style.backdropFilter = 'none';
        }
    }
});

// 添加特色动画效果
function initAnimations() {
    // 观察者API用于滚动动画
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });
    
    // 为特色卡片添加动画
    const featureItems = document.querySelectorAll('.feature-item');
    featureItems.forEach(function(item) {
        item.style.opacity = '0';
        item.style.transform = 'translateY(30px)';
        item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(item);
    });
    
    // 为下载按钮添加动画
    const downloadBtns = document.querySelectorAll('.download-btn');
    downloadBtns.forEach(function(btn, index) {
        btn.style.opacity = '0';
        btn.style.transform = 'translateY(30px)';
        btn.style.transition = `opacity 0.6s ease ${index * 0.2}s, transform 0.6s ease ${index * 0.2}s`;
        observer.observe(btn);
    });
}

// 页面加载完成后添加动画
window.addEventListener('load', function() {
    initAnimations();
});

// 导出功能供其他页面使用
window.WebsiteUtils = {
    initLanguageSwitch: initLanguageSwitch,
    showDownloadModal: showDownloadModal
};
