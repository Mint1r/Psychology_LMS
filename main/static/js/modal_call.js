        // Мобильное меню
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        const navMenu = document.getElementById('navMenu');
        
        mobileMenuBtn.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            mobileMenuBtn.innerHTML = navMenu.classList.contains('active') 
                ? '<i class="fas fa-times"></i>' 
                : '<i class="fas fa-bars"></i>';
        });
        
        // Закрытие меню при клике на ссылку
        const navLinks = document.querySelectorAll('.nav-menu a');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
            });
        });
        
        // Модальное окно
        const callbackModal = document.getElementById('callbackModal');
        const callbackBtnHeader = document.getElementById('callbackBtnHeader');
        const callbackBtnHero = document.getElementById('callbackBtnHero');
        const callbackBtnFooter = document.getElementById('callbackBtnFooter');
        const modalClose = document.getElementById('modalClose');
        const callbackForm = document.getElementById('callbackForm');
        
        // Открытие модального окна
        function openModal() {
            callbackModal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
        
        // Закрытие модального окна
        function closeModal() {
            callbackModal.classList.remove('active');
            document.body.style.overflow = 'auto';
        }
        
        // Обработчики открытия
        callbackBtnHeader.addEventListener('click', openModal);
        callbackBtnHero.addEventListener('click', openModal);
        callbackBtnFooter.addEventListener('click', openModal);
        
        // Обработчики закрытия
        modalClose.addEventListener('click', closeModal);
        
        // Закрытие при клике вне окна
        callbackModal.addEventListener('click', (e) => {
            if (e.target === callbackModal) {
                closeModal();
            }
        });
        
        // Закрытие на Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && callbackModal.classList.contains('active')) {
                closeModal();
            }
        });

        
        const phoneInput = document.getElementById('phone');

        phoneInput.addEventListener('input', (e) => {
            let digits = e.target.value.replace(/\D/g, '');

            // Если пользователь вставил номер с +7 или 8
            if (digits.startsWith('7') || digits.startsWith('8')) {
                digits = digits.substring(1);
            }

            // Максимум 10 цифр после +7
            digits = digits.substring(0, 10);

            let formatted = '';

            if (digits.length > 0) {
                formatted = '+7';
            }

            if (digits.length > 0) {
                formatted += ' (' + digits.substring(0, 3);
            }

            if (digits.length >= 3) {
                formatted += ')';
            }

            if (digits.length > 3) {
                formatted += ' ' + digits.substring(3, 6);
            }

            if (digits.length > 6) {
                formatted += '-' + digits.substring(6, 8);
            }

            if (digits.length > 8) {
                formatted += '-' + digits.substring(8, 10);
            }

            e.target.value = formatted;
        });
        
        // Изменение хедера при скролле
        window.addEventListener('scroll', () => {
            const header = document.querySelector('.site-header');
            if (window.scrollY > 50) {
                header.style.boxShadow = '0 5px 25px rgba(13, 43, 30, 0.1)';
                header.style.backgroundColor = 'rgba(255, 255, 255, 0.98)';
            } else {
                header.style.boxShadow = '0 2px 20px rgba(13, 43, 30, 0.08)';
                header.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
            }
        });
        
        // Анимация появления элементов при скролле
        const animateOnScroll = () => {
            const elements = document.querySelectorAll('.advantage-card, .teacher-card, .story-card');
            
            elements.forEach(element => {
                const elementTop = element.getBoundingClientRect().top;
                const elementVisible = 150;
                
                if (elementTop < window.innerHeight - elementVisible) {
                    element.style.opacity = "1";
                    element.style.transform = "translateY(0)";
                }
            });
        };
        
        // Устанавливаем начальные стили для анимации
        document.querySelectorAll('.advantage-card, .teacher-card, .story-card').forEach(el => {
            el.style.opacity = "0";
            el.style.transform = "translateY(20px)";
            el.style.transition = "opacity 0.6s ease, transform 0.6s ease";
        });
        
        window.addEventListener('scroll', animateOnScroll);
        // Запускаем сразу на случай, если элементы уже в поле зрения
        animateOnScroll();