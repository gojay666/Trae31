// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化表单提交事件
    initFormSubmission();
    
    // 初始化导航菜单
    initNavigation();
    
    // 初始化数据表格
    initDataTables();
});

// 表单提交事件处理
function initFormSubmission() {
    // 获取所有表单
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // 表单验证
            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }
            
            // 显示提交中状态
            showLoadingState(this);
        });
    });
}

// 表单验证
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            showFieldError(field, '此字段为必填项');
        } else {
            hideFieldError(field);
        }
    });
    
    return isValid;
}

// 显示字段错误信息
function showFieldError(field, message) {
    // 移除已存在的错误信息
    const existingError = field.nextElementSibling;
    if (existingError && existingError.classList.contains('error-message')) {
        existingError.remove();
    }
    
    // 创建新的错误信息元素
    const errorElement = document.createElement('div');
    errorElement.classList.add('error-message');
    errorElement.style.color = 'red';
    errorElement.style.fontSize = '14px';
    errorElement.style.marginTop = '5px';
    errorElement.textContent = message;
    
    // 添加到字段后面
    field.parentNode.appendChild(errorElement);
    
    // 高亮字段
    field.style.borderColor = 'red';
}

// 隐藏字段错误信息
function hideFieldError(field) {
    const existingError = field.nextElementSibling;
    if (existingError && existingError.classList.contains('error-message')) {
        existingError.remove();
    }
    
    // 恢复字段样式
    field.style.borderColor = '#ddd';
}

// 显示加载状态
function showLoadingState(form) {
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="loading">处理中...</span>';
    }
}

// 导航菜单初始化
function initNavigation() {
    const navLinks = document.querySelectorAll('nav a');
    const currentPath = window.location.pathname;
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// 数据表格初始化
function initDataTables() {
    // 这里可以添加表格排序、过滤等功能
    const tables = document.querySelectorAll('table');
    
    tables.forEach(table => {
        // 添加表格行悬停效果
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = '#f5f5f5';
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '#fff';
            });
        });
    });
}

// 工具函数：显示通知
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.classList.add('notification', type);
    notification.textContent = message;
    
    // 设置样式
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.padding = '10px 15px';
    notification.style.borderRadius = '3px';
    notification.style.color = '#fff';
    notification.style.fontSize = '14px';
    notification.style.zIndex = '9999';
    
    // 根据类型设置背景颜色
    switch(type) {
        case 'success':
            notification.style.backgroundColor = '#4CAF50';
            break;
        case 'error':
            notification.style.backgroundColor = '#f44336';
            break;
        case 'warning':
            notification.style.backgroundColor = '#ff9800';
            break;
        default:
            notification.style.backgroundColor = '#2196F3';
    }
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
        notification.remove();
    }, 3000);
}
