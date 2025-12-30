document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileToggle = document.querySelector('.mobile-toggle');
    const mainContent = document.querySelector('.main-content');
    
    // Estado inicial
    let sidebarState = localStorage.getItem('sidebarState') || 'expanded';
    
    // Aplicar estado guardado
    if (sidebarState === 'collapsed') {
        sidebar.classList.add('collapsed');
        mainContent.style.marginLeft = 'var(--sidebar-collapsed)';
    }
    
    // Toggle del botón sidebar
    sidebarToggle.addEventListener('click', function() {
        const wasCollapsed = sidebar.classList.contains('collapsed');
        
        sidebar.classList.toggle('collapsed');
        
        if (sidebar.classList.contains('collapsed')) {
            mainContent.style.marginLeft = 'var(--sidebar-collapsed)';
            localStorage.setItem('sidebarState', 'collapsed');
        } else {
            mainContent.style.marginLeft = 'var(--sidebar-expanded)';
            localStorage.setItem('sidebarState', 'expanded');
            
            // Cerrar todos los submenús al expandir
            closeAllSubmenus();
        }
        
        // Animación del ícono
        const icon = sidebarToggle.querySelector('i');
        icon.style.transform = sidebar.classList.contains('collapsed') 
            ? 'rotate(180deg)' 
            : 'rotate(0deg)';
        
        // Efecto de transición suave
        mainContent.style.transition = 'margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    });
    
    // Toggle móvil
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
            
            // Efecto de overlay para móvil
            if (sidebar.classList.contains('show')) {
                createMobileOverlay();
            } else {
                removeMobileOverlay();
            }
            
            // Animación del ícono del botón móvil
            const icon = mobileToggle.querySelector('i');
            if (sidebar.classList.contains('show')) {
                icon.classList.remove('bi-list');
                icon.classList.add('bi-x');
                icon.style.transform = 'rotate(90deg)';
            } else {
                icon.classList.remove('bi-x');
                icon.classList.add('bi-list');
                icon.style.transform = 'rotate(0deg)';
            }
        });
    }
    
    // Función para crear overlay móvil
    function createMobileOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'mobile-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1040;
            backdrop-filter: blur(3px);
            animation: fadeIn 0.3s ease;
        `;
        
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('show');
            removeMobileOverlay();
            const icon = mobileToggle.querySelector('i');
            icon.classList.remove('bi-x');
            icon.classList.add('bi-list');
            icon.style.transform = 'rotate(0deg)';
        });
        
        document.body.appendChild(overlay);
        document.body.style.overflow = 'hidden';
    }
    
    // Función para remover overlay móvil
    function removeMobileOverlay() {
        const overlay = document.querySelector('.mobile-overlay');
        if (overlay) {
            overlay.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                if (overlay.parentNode) {
                    overlay.parentNode.removeChild(overlay);
                }
            }, 300);
        }
        document.body.style.overflow = '';
    }
    
    // Cerrar sidebar móvil al hacer clic en enlaces
    if (window.innerWidth < 768) {
        const navLinks = document.querySelectorAll('.nav-link, .submenu-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                // Solo cerrar si es un enlace real (no un toggle de submenú)
                if (!this.hasAttribute('data-bs-toggle') || this.getAttribute('data-bs-toggle') !== 'collapse') {
                    sidebar.classList.remove('show');
                    removeMobileOverlay();
                    const icon = mobileToggle.querySelector('i');
                    icon.classList.remove('bi-x');
                    icon.classList.add('bi-list');
                    icon.style.transform = 'rotate(0deg)';
                }
            });
        });
    }
    
    // Manejo especial de submenús cuando sidebar está colapsado
    const navItemsWithSubmenu = document.querySelectorAll('.nav-item');
    navItemsWithSubmenu.forEach(item => {
        const navLink = item.querySelector('.nav-link[data-bs-toggle="collapse"]');
        const submenu = item.querySelector('.submenu');
        
        if (navLink && submenu) {
            navLink.addEventListener('click', function(e) {
                if (sidebar.classList.contains('collapsed')) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Cerrar otros submenús abiertos
                    document.querySelectorAll('.submenu.show').forEach(openSubmenu => {
                        if (openSubmenu !== submenu) {
                            openSubmenu.classList.remove('show');
                            openSubmenu.style.maxHeight = '0';
                            openSubmenu.style.opacity = '0';
                        }
                    });
                    
                    // Alternar el submenú actual
                    const isShowing = submenu.classList.contains('show');
                    
                    if (isShowing) {
                        submenu.classList.remove('show');
                        submenu.style.maxHeight = '0';
                        submenu.style.opacity = '0';
                    } else {
                        submenu.classList.add('show');
                        submenu.style.maxHeight = submenu.scrollHeight + 'px';
                        submenu.style.opacity = '1';
                        submenu.style.transition = 'all 0.3s ease';
                    }
                }
            });
        }
    });
    
    // Cerrar todos los submenús
    function closeAllSubmenus() {
        document.querySelectorAll('.submenu.show').forEach(submenu => {
            submenu.classList.remove('show');
            submenu.style.maxHeight = '0';
            submenu.style.opacity = '0';
        });
        
        // También cerrar los submenús de Bootstrap
        document.querySelectorAll('.submenu.collapse.show').forEach(collapse => {
            const bsCollapse = bootstrap.Collapse.getInstance(collapse);
            if (bsCollapse) {
                bsCollapse.hide();
            }
        });
    }
    
    // Cerrar submenús al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (!sidebar.contains(e.target) && !e.target.classList.contains('mobile-toggle')) {
            closeAllSubmenus();
        }
    });
    
    // Manejo responsive
    function handleResize() {
        if (window.innerWidth >= 768) {
            // En desktop, asegurar que sidebar no tenga clase móvil
            sidebar.classList.remove('show');
            removeMobileOverlay();
            if (mobileToggle) {
                const icon = mobileToggle.querySelector('i');
                icon.classList.remove('bi-x');
                icon.classList.add('bi-list');
                icon.style.transform = 'rotate(0deg)';
            }
        } else {
            // En móvil, si sidebar está colapsado, expandirlo
            if (sidebar.classList.contains('collapsed')) {
                sidebar.classList.remove('collapsed');
                mainContent.style.marginLeft = '0';
            }
        }
    }
    
    // Escuchar cambios de tamaño
    window.addEventListener('resize', handleResize);
    handleResize(); // Ejecutar al cargar
    
    // Efectos de hover para items del menú (solo desktop)
    if (window.innerWidth >= 768) {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('mouseenter', function() {
                if (sidebar.classList.contains('collapsed')) {
                    const tooltip = this.querySelector('.nav-text');
                    if (tooltip) {
                        createTooltip(this, tooltip.textContent);
                    }
                }
            });
            
            link.addEventListener('mouseleave', function() {
                removeTooltip();
            });
        });
    }
    
    // Función para tooltips en sidebar colapsado
    function createTooltip(element, text) {
        removeTooltip();
        
        const tooltip = document.createElement('div');
        tooltip.className = 'sidebar-tooltip';
        tooltip.textContent = text;
        tooltip.style.cssText = `
            position: absolute;
            left: 100%;
            top: 50%;
            transform: translateY(-50%);
            background: var(--color-guinda);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 0.875rem;
            white-space: nowrap;
            z-index: 1060;
            margin-left: 10px;
            box-shadow: var(--shadow-md);
            animation: slideIn 0.2s ease;
        `;
        
        element.style.position = 'relative';
        element.appendChild(tooltip);
    }
    
    function removeTooltip() {
        const tooltip = document.querySelector('.sidebar-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }
    
    // Añadir animaciones CSS necesarias
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-50%) translateX(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(-50%) translateX(0);
            }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
        
        .submenu {

            overflow: hidden;
            transition: max-height 0.3s ease, opacity 0.2s ease;
        }
        

        
        .sidebar {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .sidebar.collapsed {
            width: var(--sidebar-collapsed);
        }
        
        .sidebar.collapsed .nav-text,
        .sidebar.collapsed .brand-text,
        .sidebar.collapsed .nav-chevron {
            opacity: 0;
            width: 0;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .sidebar.collapsed .logo-container {
            justify-content: center;
            padding: 10px;
        }
        
        .sidebar.collapsed .logo {
            transform: scale(0.8);
        }
        
        .sidebar.collapsed .nav-link {
            justify-content: center;
            padding: 15px !important;
        }
        
        .sidebar.collapsed .nav-icon {
            margin-right: 0;
            font-size: 1.4rem;
        }
        
        @media (max-width: 767px) {
            .sidebar {
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }
            
            .sidebar.show {
                transform: translateX(0);
                box-shadow: var(--shadow-lg);
            }
            
            .sidebar.collapsed {
                width: var(--sidebar-expanded);
            }
        }
    `;
    document.head.appendChild(style);
});