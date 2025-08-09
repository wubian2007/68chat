// 68tt.co 网站 JavaScript 功能

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 移动端布局修复
    initMobileLayoutFix();
    
    // 语言切换功能
    initLanguageSwitch();
    
    // 平滑滚动
    initSmoothScroll();
    
    // 下载按钮点击事件
    initDownloadButtons();
    
    // 移动端导航
    initMobileNavigation();
    
    // 响应式导航
    initResponsiveNav();
});

// 移动端布局修复功能
function initMobileLayoutFix() {
    // 检测并修复水平滚动问题
    function fixHorizontalOverflow() {
        if (window.innerWidth <= 768) {
            const body = document.body;
            const html = document.documentElement;
            
            // 确保没有水平滚动
            body.style.overflowX = 'hidden';
            html.style.overflowX = 'hidden';
            
            // 检查所有可能导致溢出的元素
            const allElements = document.querySelectorAll('*');
            allElements.forEach(function(element) {
                const rect = element.getBoundingClientRect();
                if (rect.width > window.innerWidth) {
                    element.style.maxWidth = '100%';
                    element.style.overflowX = 'hidden';
                    element.style.boxSizing = 'border-box';
                }
            });
        }
    }
    
    // 修复图片尺寸
    function fixImageSizes() {
        const images = document.querySelectorAll('img');
        images.forEach(function(img) {
            if (window.innerWidth <= 768) {
                img.style.maxWidth = '100%';
                img.style.height = 'auto';
                img.style.objectFit = 'contain';
            }
        });
    }
    
    // 修复视口设置
    function fixViewport() {
        let viewport = document.querySelector('meta[name="viewport"]');
        if (!viewport) {
            viewport = document.createElement('meta');
            viewport.name = 'viewport';
            document.head.appendChild(viewport);
        }
        viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
    }
    
    // 修复触控区域
    function fixTouchTargets() {
        if (window.innerWidth <= 768) {
            const touchElements = document.querySelectorAll('button, a, input, select, textarea');
            touchElements.forEach(function(element) {
                const rect = element.getBoundingClientRect();
                if (rect.width < 44 || rect.height < 44) {
                    element.style.minWidth = '44px';
                    element.style.minHeight = '44px';
                    element.style.display = 'inline-flex';
                    element.style.alignItems = 'center';
                    element.style.justifyContent = 'center';
                }
            });
        }
    }
    
    // 添加移动端专用样式类
    function addMobileClasses() {
        if (window.innerWidth <= 768) {
            document.body.classList.add('mobile-layout');
        } else {
            document.body.classList.remove('mobile-layout');
        }
        
        if (window.innerWidth <= 480) {
            document.body.classList.add('small-mobile');
        } else {
            document.body.classList.remove('small-mobile');
        }
    }
    
    // 初始修复
    fixViewport();
    fixHorizontalOverflow();
    fixImageSizes();
    fixTouchTargets();
    addMobileClasses();
    
    // 窗口大小改变时重新修复
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            fixHorizontalOverflow();
            fixImageSizes();
            fixTouchTargets();
            addMobileClasses();
        }, 250);
    });
    
    // 监听方向改变
    window.addEventListener('orientationchange', function() {
        setTimeout(function() {
            fixHorizontalOverflow();
            fixImageSizes();
            addMobileClasses();
        }, 500);
    });
}

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

// 移动端导航功能
function initMobileNavigation() {
    const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
    const mobileNavMenu = document.querySelector('.mobile-nav-menu');
    const mobileNavOverlay = document.querySelector('.mobile-nav-overlay');
    const navLinks = document.querySelectorAll('.mobile-nav-menu .nav-link');
    
    if (!mobileNavToggle || !mobileNavMenu || !mobileNavOverlay) return;
    
    // 打开/关闭移动菜单
    mobileNavToggle.addEventListener('click', function() {
        toggleMobileMenu();
    });
    
    // 点击遮罩关闭菜单
    mobileNavOverlay.addEventListener('click', function() {
        closeMobileMenu();
    });
    
    // 点击菜单链接后关闭菜单
    navLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            closeMobileMenu();
        });
    });
    
    // 按ESC键关闭菜单
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeMobileMenu();
        }
    });
    
    function toggleMobileMenu() {
        const isActive = mobileNavMenu.classList.contains('active');
        if (isActive) {
            closeMobileMenu();
        } else {
            openMobileMenu();
        }
    }
    
    function openMobileMenu() {
        mobileNavMenu.classList.add('active');
        mobileNavOverlay.classList.add('active');
        document.body.style.overflow = 'hidden'; // 防止背景滚动
        mobileNavToggle.innerHTML = '✕';
        mobileNavToggle.setAttribute('aria-label', '關閉菜單');
    }
    
    function closeMobileMenu() {
        mobileNavMenu.classList.remove('active');
        mobileNavOverlay.classList.remove('active');
        document.body.style.overflow = '';
        mobileNavToggle.innerHTML = '☰';
        mobileNavToggle.setAttribute('aria-label', '打開菜單');
    }
    
    // 窗口大小改变时处理菜单状态
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeMobileMenu();
        }
    });
}

// 响应式导航
function initResponsiveNav() {
    // 处理窗口大小变化
    window.addEventListener('resize', function() {
        const navContainer = document.querySelector('.nav-container');
        const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
        
        if (window.innerWidth <= 768) {
            // 移动端：隐藏桌面导航，显示移动按钮
            if (navContainer) {
                const desktopLinks = navContainer.querySelectorAll('a');
                desktopLinks.forEach(link => link.style.display = 'none');
            }
            if (mobileNavToggle) {
                mobileNavToggle.style.display = 'block';
            }
        } else {
            // 桌面端：显示桌面导航，隐藏移动按钮
            if (navContainer) {
                const desktopLinks = navContainer.querySelectorAll('a');
                desktopLinks.forEach(link => link.style.display = 'block');
            }
            if (mobileNavToggle) {
                mobileNavToggle.style.display = 'none';
            }
        }
    });
    
    // 初始化时触发一次
    window.dispatchEvent(new Event('resize'));
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
