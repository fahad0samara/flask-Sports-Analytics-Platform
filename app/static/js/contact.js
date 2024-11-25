document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    const successModal = document.getElementById('successModal');
    const closeModal = document.querySelector('.close');
    const closeButton = successModal.querySelector('.btn');

    // Form submission handler
    contactForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Show loading state
        const submitButton = contactForm.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

        try {
            const formData = new FormData(contactForm);
            const response = await fetch('/contact', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                // Show success modal
                successModal.style.display = 'block';
                // Reset form
                contactForm.reset();
            } else {
                throw new Error('Failed to send message');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to send message. Please try again later.');
        } finally {
            // Reset button state
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    });

    // Form validation
    const inputs = contactForm.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateInput(this);
        });

        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateInput(this);
            }
        });
    });

    function validateInput(input) {
        const value = input.value.trim();
        
        // Remove existing error messages
        const existingError = input.parentElement.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        // Reset validation classes
        input.classList.remove('is-invalid', 'is-valid');

        if (!value) {
            showError(input, 'This field is required');
            return false;
        }

        if (input.type === 'email') {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                showError(input, 'Please enter a valid email address');
                return false;
            }
        }

        input.classList.add('is-valid');
        return true;
    }

    function showError(input, message) {
        input.classList.add('is-invalid');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        input.parentElement.appendChild(errorDiv);
    }

    // Modal close handlers
    function closeSuccessModal() {
        successModal.style.display = 'none';
    }

    closeModal.addEventListener('click', closeSuccessModal);
    closeButton.addEventListener('click', closeSuccessModal);

    window.addEventListener('click', function(e) {
        if (e.target === successModal) {
            closeSuccessModal();
        }
    });

    // Smooth scroll for FAQ links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add animation on scroll for info cards
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.info-card').forEach(card => {
        observer.observe(card);
    });
});
