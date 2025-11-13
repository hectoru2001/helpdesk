document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileToggle = document.querySelector('.mobile-toggle');
    
    sidebarToggle.addEventListener('click', function() {
        const wasCollapsed = sidebar.classList.contains('collapsed');
        sidebar.classList.toggle('collapsed');
        
        if (!wasCollapsed) {
            closeAllSubmenus();
        }
    });
    
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.toggle('mobile-open');
        });
    }
    
    if (window.innerWidth < 768) {
        const navLinks = document.querySelectorAll('.nav-link, .submenu-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                sidebar.classList.remove('mobile-open');
            });
        });
    }
    
    const navItemsWithSubmenu = document.querySelectorAll('.nav-item');
    navItemsWithSubmenu.forEach(item => {
        const navLink = item.querySelector('.nav-link[data-bs-toggle="collapse"]');
        const submenu = item.querySelector('.submenu');
        
        if (navLink && submenu) {
            navLink.addEventListener('click', function(e) {
                if (sidebar.classList.contains('collapsed')) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    document.querySelectorAll('.submenu.show').forEach(openSubmenu => {
                        if (openSubmenu !== submenu) {
                            openSubmenu.classList.remove('show');
                        }
                    });
                    
                    submenu.classList.toggle('show');
                }
            });
        }
    });
    
    function closeAllSubmenus() {
        document.querySelectorAll('.submenu.show').forEach(submenu => {
            submenu.classList.remove('show');
        });
        
        document.querySelectorAll('.submenu.collapse.show').forEach(collapse => {
            const bsCollapse = bootstrap.Collapse.getInstance(collapse);
            if (bsCollapse) {
                bsCollapse.hide();
            }
        });
    }
    
    document.addEventListener('click', function(e) {
        if (!sidebar.contains(e.target) && !e.target.classList.contains('mobile-toggle')) {
            closeAllSubmenus();
        }
    });
});