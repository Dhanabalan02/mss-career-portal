// main.js - Common JS functions and UI initializations

$(document).ready(function() {
    // Load reusable components
    if ($("#candidate-navbar").length) {
        $("#candidate-navbar").load("/projects/mss-career-portal/components/candidate-navbar.html", function() {
            // Set active class based on current page path
            let currentPath = window.location.pathname;
            $('.nav-link').each(function() {
                if ($(this).attr('href') === currentPath) {
                    $(this).addClass('active');
                }
            });
        });
    }

    if ($("#hr-sidebar").length) {
        $("#hr-sidebar").load("/projects/mss-career-portal/components/hr-sidebar.html", function() {
            let currentPath = window.location.pathname;
            $('.nav-link').each(function() {
                if ($(this).attr('href') === currentPath) {
                    $(this).addClass('active');
                }
            });
        });
    }
    
    if ($("#school-sidebar").length) {
        $("#school-sidebar").load("/projects/mss-career-portal/components/school-sidebar.html", function() {
             let currentPath = window.location.pathname;
            $('.nav-link').each(function() {
                if ($(this).attr('href') === currentPath) {
                    $(this).addClass('active');
                }
            });
        });
    }

    // Bootstrap Tooltips & Popovers
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Form Validations reusable function
    window.validateForm = function(formId) {
        let isValid = true;
        let form = $(formId);
        
        // Reset errors
        form.find('.is-invalid').removeClass('is-invalid');
        form.find('.invalid-feedback').remove();

        // Check required fields
        form.find('[required]').each(function() {
            if (!$(this).val()) {
                isValid = false;
                showError($(this), 'This field is required');
            }
        });

        // Email validation
        form.find('input[type="email"]').each(function() {
            let email = $(this).val();
            let regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (email && !regex.test(email)) {
                isValid = false;
                showError($(this), 'Please enter a valid email address');
            }
        });

        // Phone validation (10 digits)
        form.find('input[type="tel"]').each(function() {
            let phone = $(this).val();
            let regex = /^\d{10}$/;
            if (phone && !regex.test(phone)) {
                isValid = false;
                showError($(this), 'Please enter a valid 10-digit phone number');
            }
        });

        // File validation (pdf docx max 5MB)
        form.find('input[type="file"]').each(function() {
            let fileInput = $(this)[0];
            if (fileInput.files.length > 0) {
                let file = fileInput.files[0];
                let ext = file.name.split('.').pop().toLowerCase();
                if (ext !== 'pdf' && ext !== 'docx') {
                    isValid = false;
                    showError($(this), 'Only PDF and DOCX files are allowed');
                }
                if (file.size > 5 * 1024 * 1024) { // 5MB
                    isValid = false;
                    showError($(this), 'File size must be less than 5MB');
                }
            }
        });

        return isValid;
    };

    function showError(element, message) {
        element.addClass('is-invalid');
        if (element.next('.invalid-feedback').length === 0) {
            element.after(`<div class="invalid-feedback">${message}</div>`);
        } else {
             element.next('.invalid-feedback').text(message);
        }
    }

    // Global Toast Notification wrapper
    window.showToast = function(title, message, type='success') {
        var msg = message;
        var t = type;
        if (!message) {
            msg = title;
            t = 'success';
        } else if (message === 'success' || message === 'error' || message === 'danger' || message === 'warning' || message === 'info') {
            msg = title;
            t = message;
        } else {
            msg = title + ': ' + message;
        }
        
        var mappedType = t;
        if (t === 'danger') mappedType = 'error';
        
        if (window.showMssToast) {
            window.showMssToast(msg, mappedType);
        } else {
            console.log(msg);
        }
    }
});
