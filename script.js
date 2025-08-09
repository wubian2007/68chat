// 68tt.co 原版JavaScript功能重建

document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有功能
    initMobileMenu();
    initLanguageSwitch();
    initScrollEffects();
    initDownloadLinks();
});

// 移动端菜单功能 - 完全按照原网站
function initMobileMenu() {
    const openBtn = document.getElementById('openBtn');
    const modal = document.getElementById('modal');
    const navModal = document.querySelector('.nav-modal');
    const body = document.body;
    
    if (openBtn && modal) {
        openBtn.addEventListener('click', function() {
            if (body.classList.contains('openMenu')) {
                // 关闭菜单
                body.classList.remove('openMenu');
                const closeBtn = document.querySelector('#openBtn .close');
                if (closeBtn) {
                    closeBtn.style.opacity = '0';
                    setTimeout(() => {
                        closeBtn.style.opacity = '1';
                    }, 600);
                }
            } else {
                // 打开菜单
                body.classList.add('openMenu');
                const closeBtn = document.querySelector('#openBtn .close');
                if (closeBtn) {
                    closeBtn.style.opacity = '0';
                    setTimeout(() => {
                        closeBtn.style.opacity = '1';
                    }, 1000);
                }
            }
        });
        
        // 点击遮罩关闭菜单
        if (navModal) {
            navModal.addEventListener('click', function() {
                body.classList.remove('openMenu');
                const closeBtn = document.querySelector('#openBtn .close');
                if (closeBtn) {
                    closeBtn.style.opacity = '0';
                    setTimeout(() => {
                        closeBtn.style.opacity = '1';
                    }, 1000);
                }
            });
        }
        
        // 阻止移动端菜单滚动
        modal.addEventListener('touchmove', function(e) {
            e.preventDefault();
        }, false);
    }
}

// 语言切换功能
function initLanguageSwitch() {
    // 桌面端语言切换
    const languageToggle = document.getElementById('language-toggle');
    const languageOptions = document.getElementById('language-options');
    
    if (languageToggle && languageOptions) {
        // 鼠标悬停显示选项
        const languageContainer = languageToggle.closest('.language');
        if (languageContainer) {
            languageContainer.addEventListener('mouseenter', function() {
                languageOptions.style.display = 'block';
            });
            
            languageContainer.addEventListener('mouseleave', function() {
                languageOptions.style.display = 'none';
            });
        }
        
        // 语言选择
        const langItems = languageOptions.querySelectorAll('.lang-item');
        langItems.forEach(function(item) {
            item.addEventListener('click', function() {
                const lang = this.dataset.lang;
                changeLang(lang, 'index');
                languageOptions.style.display = 'none';
            });
        });
    }
    
    // 移动端语言弹窗
    initMobileLanguagePopup();
}

// 移动端语言弹窗
function initMobileLanguagePopup() {
    const showPopup = document.getElementById('showPopup');
    const popupContainer = document.getElementById('popupContainer');
    const closePopup = document.getElementById('closePopup');
    
    if (showPopup && popupContainer) {
        // 默认隐藏弹窗
        popupContainer.style.display = 'none';
        
        showPopup.addEventListener('click', function(e) {
            e.preventDefault();
            popupContainer.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        });
        
        if (closePopup) {
            closePopup.addEventListener('click', function() {
                closeLanguagePopup();
            });
        }
        
        // 点击背景关闭
        popupContainer.addEventListener('click', function(e) {
            if (e.target === popupContainer) {
                closeLanguagePopup();
            }
        });
        
        // 语言选择
        const popupLangItems = popupContainer.querySelectorAll('.lang-item');
        popupLangItems.forEach(function(item) {
            item.addEventListener('click', function() {
                const lang = this.dataset.lang;
                changeLang(lang, 'index');
                closeLanguagePopup();
            });
        });
        
        function closeLanguagePopup() {
            popupContainer.style.display = 'none';
            document.body.style.overflow = '';
        }
    }
}

// 语言切换函数 - 模拟原网站功能
function changeLang(lang, page) {
    // 更新所有语言显示
    const allLangItems = document.querySelectorAll('.lang-item');
    allLangItems.forEach(function(item) {
        item.classList.remove('active');
        if (item.dataset.lang === lang) {
            item.classList.add('active');
        }
    });
    
    // 语言名称映射
    const languageNames = {
        'cn': '繁體中文',
        'en': 'English',
        'vi': 'Tiếng Việt',
        'pt': 'Português'
    };
    
    const selectedName = languageNames[lang] || '繁體中文';
    
    // 更新桌面端显示
    const desktopToggle = document.getElementById('language-toggle');
    if (desktopToggle) {
        desktopToggle.innerHTML = selectedName + ' <img src="68tt_static/images/language.png" alt="">';
    }
    
    // 更新移动端显示
    const mobileToggle = document.querySelector('.phone-language span');
    if (mobileToggle) {
        mobileToggle.innerHTML = selectedName + ' &nbsp;<img src="68tt_static/images/language.png" alt="">';
    }
    
    console.log('Language changed to:', lang, 'on page:', page);
}

// 滚动效果 - 完全按照原网站
function initScrollEffects() {
    let lastScrollTop = 0;
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const windowHeight = window.innerHeight;
        const windowWidth = window.innerWidth;
        
        // 返回顶部按钮显示/隐藏
        const toTop = document.querySelector('.toTop');
        if (toTop) {
            if (windowHeight < scrollTop) {
                toTop.classList.remove('hide');
                toTop.style.display = 'block';
                
                // 桌面端头部高度调整
                if (windowWidth > 768) {
                    const headerInner = document.querySelector('.header .inner');
                    if (headerInner) {
                        headerInner.classList.add('rHeight');
                    }
                }
            } else {
                toTop.classList.add('hide');
                toTop.style.display = 'none';
                
                const headerInner = document.querySelector('.header .inner');
                if (headerInner) {
                    headerInner.classList.remove('rHeight');
                }
            }
        }
        
        // 移动端up-arrow处理
        const upArrow = document.querySelector('.up-arrow');
        if (upArrow && isMobile()) {
            if (scrollTop > 50) {
                upArrow.style.display = 'none';
            } else {
                upArrow.style.display = 'block';
            }
        }
        
        lastScrollTop = scrollTop;
    });
    
    // 返回顶部功能
    const toTopLinks = document.querySelectorAll('.toTop a, .up-arrow');
    toTopLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    });
}

// 下载链接初始化
function initDownloadLinks() {
    // 设置下载URL (模拟原网站的app对象)
    const app = {
        windows_url: 'https://a1.888317.xyz/68-new-1.6.4-win-x64-setup.exe',
        mac_url: 'https://a1.888317.xyz/68chat_prod_release_6_0_2_20250805134622_1d7848f46_2565_protected.apk',
        android_url: 'https://a1.888317.xyz/68chat_prod_release_6_0_2_20250805134622_1d7848f46_2565_protected.apk',
        android_google_link: 'https://play.google.com/store/apps/details?id=com.chat68.app'
    };
    
    // Windows下载
    const windowsUrl = document.getElementById('windows_url');
    if (windowsUrl) {
        windowsUrl.href = app.windows_url;
    }
    
    // Mac下载
    const macUrl = document.getElementById('mac_url');
    if (macUrl) {
        macUrl.href = app.mac_url;
    }
    
    // Android下载
    const androidUrl = document.getElementById('android_url');
    if (androidUrl) {
        androidUrl.href = app.android_url;
        androidUrl.addEventListener('click', function() {
            window.location.href = app.android_url;
        });
    }
    
    // Google Play下载
    const googleDown = document.getElementById('goole-down');
    if (googleDown) {
        googleDown.addEventListener('click', function() {
            window.location.href = app.android_google_link;
        });
    }
    
    // 显示隐藏的下载框
    const boxes = document.querySelectorAll('.box.hide');
    boxes.forEach(function(box) {
        box.classList.remove('hide');
    });
    
    const blocks = document.querySelectorAll('.block.block-hide');
    blocks.forEach(function(block) {
        block.classList.remove('block-hide');
    });
}

// 工具函数
function isMobile() {
    return /mobile/i.test(navigator.userAgent) || window.innerWidth <= 768;
}

// 窗口大小改变处理
window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
        // 桌面端 - 关闭移动端菜单和弹窗
        document.body.classList.remove('openMenu');
        
        const popupContainer = document.getElementById('popupContainer');
        if (popupContainer) {
            popupContainer.style.display = 'none';
        }
        
        document.body.style.overflow = '';
    }
});

// QR码悬停效果
document.addEventListener('DOMContentLoaded', function() {
    const qrcode = document.querySelector('.fiexd-block .qrcode');
    const detail = document.querySelector('.qrcode .detail');
    
    if (qrcode && detail) {
        qrcode.addEventListener('mouseenter', function() {
            detail.style.display = 'block';
        });
        
        qrcode.addEventListener('mouseleave', function() {
            detail.style.display = 'none';
        });
    }
});

// 错误处理
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
});

// 导出全局函数供外部调用
window.changeLang = changeLang;