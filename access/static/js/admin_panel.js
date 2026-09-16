document.addEventListener('DOMContentLoaded', () => {

    // =========================================================
    // ЭЛЕМЕНТЫ
    // =========================================================

    const applicationModal = document.getElementById('application-modal');
    const testModal = document.getElementById('test-modal');

    const applicationModalBody = document.getElementById(
        'application-modal-body'
    );

    const closeButtons = document.querySelectorAll('.ap-close-btn');


    // =========================================================
    // ПЕРЕКЛЮЧЕНИЕ ТАБОВ
    // =========================================================

    const tabButtons = document.querySelectorAll('.ap-tab-button');
    const sections = document.querySelectorAll('.ap-section');

    tabButtons.forEach((button) => {

        button.addEventListener('click', () => {

            tabButtons.forEach((btn) => {
                btn.classList.remove('active');
            });

            button.classList.add('active');

            const tabId = button.getAttribute('data-tab');

            sections.forEach((section) => {
                section.classList.remove('active');
            });

            const targetSection = document.getElementById(tabId);

            if (targetSection) {
                targetSection.classList.add('active');
            }
        });

    });


    // =========================================================
    // ЗАКРЫТИЕ МОДАЛЬНЫХ ОКОН
    // =========================================================

    function closeModals() {

        if (applicationModal) {
            applicationModal.classList.remove('active');
        }

        if (testModal) {
            testModal.classList.remove('active');
        }

    }


    closeButtons.forEach((button) => {

        button.addEventListener('click', () => {
            closeModals();
        });

    });


    window.addEventListener('click', (event) => {

        if (event.target === applicationModal) {
            applicationModal.classList.remove('active');
        }

        if (event.target === testModal) {
            testModal.classList.remove('active');
        }

    });


    document.addEventListener('keydown', (event) => {

        if (event.key === 'Escape') {
            closeModals();
        }

    });


    // =========================================================
    // CSRF
    // =========================================================

    function getCookie(name) {

        let cookieValue = null;

        if (document.cookie && document.cookie !== '') {

            const cookies = document.cookie.split(';');

            for (let cookie of cookies) {

                cookie = cookie.trim();

                if (cookie.startsWith(name + '=')) {

                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );

                    break;
                }
            }
        }

        return cookieValue;
    }
// =========================================================
// ПРЕДПРОСМОТР ФАЙЛА
// =========================================================

    function renderFilePreview(container, fileUrl, fileName = '') {

        container.innerHTML = '';

        // Файла нет
        if (!fileUrl) {

            const placeholder = document.createElement('div');

            placeholder.className = 'ap-document-placeholder';

            placeholder.textContent = '❌ Файл отсутствует';

            container.appendChild(placeholder);

            return;
        }


        // ---------------------------------------------------------
        // Сначала пробуем открыть файл как изображение
        // ---------------------------------------------------------

        const img = document.createElement('img');

        img.src = fileUrl;
        img.alt = fileName || 'Документ';

        img.onload = () => {

            container.innerHTML = '';

            img.style.display = 'block';
            img.style.maxWidth = '100%';
            img.style.maxHeight = '500px';
            img.style.width = 'auto';
            img.style.height = 'auto';
            img.style.objectFit = 'contain';
            img.style.margin = '0 auto';

            container.appendChild(img);
        };


        img.onerror = () => {

            // Изображением не является.
            // Проверяем, не PDF ли это.

            if (fileUrl.toLowerCase().split('?')[0].endsWith('.pdf')) {

                const iframe = document.createElement('iframe');

                iframe.src = fileUrl;

                iframe.style.width = '100%';
                iframe.style.height = '500px';
                iframe.style.border = 'none';

                container.innerHTML = '';

                container.appendChild(iframe);

                return;
            }


            // -----------------------------------------------------
            // Другие типы файлов
            // -----------------------------------------------------

            const placeholder = document.createElement('div');

            placeholder.className = 'ap-document-placeholder';

            placeholder.innerHTML =
                '📄 Предпросмотр недоступен для этого файла.<br>' +
                'Откройте оригинал для просмотра.';

            container.innerHTML = '';

            container.appendChild(placeholder);
        };


        // Добавляем изображение сразу, чтобы браузер начал загрузку
        container.appendChild(img);
    }



    // =========================================================
    // ОТПРАВКА РЕШЕНИЯ ПО ЗАЯВКЕ
    // =========================================================

    function submitApplicationDecision(
        applicationId,
        action
    ) {

        const form = document.createElement('form');

        form.method = 'POST';
        form.action = '/learn/applications/decision/';


        const csrfInput = document.createElement('input');

        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = getCookie('csrftoken');


        const idInput = document.createElement('input');

        idInput.type = 'hidden';
        idInput.name = 'application_id';
        idInput.value = applicationId;


        const actionInput = document.createElement('input');

        actionInput.type = 'hidden';
        actionInput.name = 'action';
        actionInput.value = action;


        form.appendChild(csrfInput);
        form.appendChild(idInput);
        form.appendChild(actionInput);

        document.body.appendChild(form);

        form.submit();
    }


    // =========================================================
    // ОТПРАВКА РЕШЕНИЯ ПО ТЕСТУ
    // =========================================================

    function submitTestDecision(
        testId,
        action,
        comment
    ) {

        const form = document.createElement('form');

        form.method = 'POST';
        form.action = `/learn/tests/decision/`;


        const csrfInput = document.createElement('input');

        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = getCookie('csrftoken');


        const idInput = document.createElement('input');

        idInput.type = 'hidden';
        idInput.name = 'test_id';
        idInput.value = testId;


        const actionInput = document.createElement('input');

        actionInput.type = 'hidden';
        actionInput.name = 'action';
        actionInput.value = action;


        const commentInput = document.createElement('input');

        commentInput.type = 'hidden';
        commentInput.name = 'comment';
        commentInput.value = comment || '';


        form.appendChild(csrfInput);
        form.appendChild(idInput);
        form.appendChild(actionInput);
        form.appendChild(commentInput);

        document.body.appendChild(form);

        form.submit();
    }


    // =========================================================
    // ЗАЯВКИ
    // =========================================================

    const applicationButtons = document.querySelectorAll(
        '.ap-view-application-btn'
    );

    applicationButtons.forEach((button) => {

        button.addEventListener('click', () => {

            const userName = button.getAttribute(
                'data-user-name'
            );

            const userEmail = button.getAttribute(
                'data-user-email'
            );

            const applicationId = button.getAttribute(
                'data-id'
            );


            // -------------------------------------------------
            // Информация о пользователе
            // -------------------------------------------------

            document.getElementById(
                'modal-user-info'
            ).textContent = `${userName} • ${userEmail}`;


            // -------------------------------------------------
            // Документы
            // -------------------------------------------------

            const documents = [

                {
                    title: 'Диплом об образовании',
                    url: button.getAttribute('data-diploma'),
                    fileName: button.getAttribute('data-diploma-name')
                },

                {
                    title: 'Паспорт (фото)',
                    url: button.getAttribute('data-passport-main'),
                    fileName: button.getAttribute('data-passport-main-name')
                },

                {
                    title: 'Паспорт (прописка)',
                    url: button.getAttribute('data-passport-registration'),
                    fileName: button.getAttribute('data-passport-registration-name')
                },

                {
                    title: 'СНИЛС',
                    url: button.getAttribute('data-snils'),
                    fileName: button.getAttribute('data-snils-name')
                }

            ];


            applicationModalBody.innerHTML = '';


        documents.forEach((doc, index) => {

            const docSection =
                document.createElement('div');

            docSection.className =
                'ap-document-section';


            docSection.innerHTML = `

                <div class="ap-document-title">
                    ${doc.title}
                </div>

                <div class="ap-document-preview">

                    <div class="ap-document-placeholder">
                        ⏳ Загрузка файла...
                    </div>

                </div>

                <div class="ap-document-actions">

                    <a
                        href="${doc.url || '#'}"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="ap-view-original-btn"
                        data-doc-index="${index}"
                    >
                        🔍 Открыть оригинал
                    </a>

                </div>

            `;


            applicationModalBody.appendChild(
                docSection
            );


            // -------------------------------------------------
            // ПРЕДПРОСМОТР
            // -------------------------------------------------

            const previewDiv =
                docSection.querySelector(
                    '.ap-document-preview'
                );

            renderFilePreview(
                previewDiv,
                doc.url,
                doc.fileName
            );

        });

            // =====================================================
            // КНОПКА ОТКЛОНЕНИЯ
            // =====================================================

            document.getElementById(
                'reject-application'
            ).onclick = () => {

                const confirmed = confirm(
                    `Вы уверены, что хотите отклонить заявку пользователя ${userName}?`
                );

                if (confirmed) {

                    submitApplicationDecision(
                        applicationId,
                        'reject'
                    );

                }

            };


            // =====================================================
            // КНОПКА ПРИНЯТИЯ
            // =====================================================

            document.getElementById(
                'accept-application'
            ).onclick = () => {

                const confirmed = confirm(
                    `Принять заявку пользователя ${userName}?`
                );

                if (confirmed) {

                    submitApplicationDecision(
                        applicationId,
                        'accept'
                    );

                }

            };


            // =====================================================
            // ОТКРЫТИЕ МОДАЛКИ
            // =====================================================

            applicationModal.classList.add('active');

            applicationModalBody.scrollTop = 0;

        });

    });


    // =========================================================
    // ТЕСТЫ
    // =========================================================

    const testButtons = document.querySelectorAll(
        '.ap-view-test-btn'
    );


    testButtons.forEach((button) => {

        button.addEventListener('click', () => {

            const testId =
                button.getAttribute('data-id');
            console.log(testId)

            const userName =
                button.getAttribute('data-user-name');

            const userEmail =
                button.getAttribute('data-user-email');

            const fileUrl =
                button.getAttribute('data-file-url');

            const fileName =
                button.getAttribute('data-file-name');

            const fileSize =
                button.getAttribute('data-file-size');


            // -------------------------------------------------
            // Заполняем данные
            // -------------------------------------------------

            document.getElementById(
                'test-user-name'
            ).textContent = userName || '';


            document.getElementById(
                'test-user-email'
            ).textContent = userEmail || '';


            document.getElementById(
                'test-file-name'
            ).textContent = fileName || '';


            document.getElementById(
                'test-file-size'
            ).textContent = fileSize || '';


            document.getElementById(
                'test-id-display'
            ).textContent = testId || '';


            // -------------------------------------------------
            // Инициалы
            // -------------------------------------------------

            const initials =
                (userName || '')
                    .split(' ')
                    .filter(Boolean)
                    .map((part) => part[0])
                    .join('')
                    .toUpperCase();


            document.getElementById(
                'test-user-avatar'
            ).textContent = initials;


            // -------------------------------------------------
            // Ссылка на скачивание
            // -------------------------------------------------

            const downloadLink =
                document.getElementById(
                    'test-download-link'
                );


            downloadLink.href = fileUrl || '#';

            if (fileName) {
                downloadLink.download = fileName;
            } else {
                downloadLink.removeAttribute('download');
            }


            // -------------------------------------------------
            // Предпросмотр
            // -------------------------------------------------


           const previewContainer =
                document.getElementById(
                    'test-file-preview'
                );

            renderFilePreview(
                previewContainer,
                fileUrl,
                fileName
            );


            


            // =====================================================
            // ОТКЛОНИТЬ ТЕСТ
            // =====================================================

            document.getElementById(
                'reject-test'
            ).onclick = () => {

                const comment =
                    document.getElementById(
                        'test-comment'
                    ).value;


                const confirmed = confirm(
                    `Отклонить тест пользователя ${userName}?`
                );


                if (confirmed) {

                    submitTestDecision(
                        testId,
                        'reject',
                        comment
                    );

                }

            };


            // =====================================================
            // ПРИНЯТЬ ТЕСТ
            // =====================================================

            document.getElementById(
                'accept-test'
            ).onclick = () => {

                const comment =
                    document.getElementById(
                        'test-comment'
                    ).value;


                const confirmed = confirm(
                    `Принять тест пользователя ${userName}?`
                );


                if (confirmed) {

                    submitTestDecision(
                        testId,
                        'accept',
                        comment
                    );

                }

            };


            // =====================================================
            // ОТКРЫВАЕМ МОДАЛКУ
            // =====================================================

            testModal.classList.add('active');

        });

    });


    // =========================================================
    // СЧЁТЧИКИ
    // =========================================================

    const applicationCount =
        document.querySelector(
            '[data-tab="applications"] .ap-tab-count'
        );

    const testCount =
        document.querySelector(
            '[data-tab="tests"] .ap-tab-count'
        );


    if (applicationCount && testCount) {

        console.log(
            `Заявок: ${applicationCount.textContent}, ` +
            `Тестов: ${testCount.textContent}`
        );

    }

});