/*
Главный JS файл проекта
Функции:
- фильтры журнала
- AJAX сохранение оценок
- экзамен / итог
- цвета оценок
- toast уведомления
*/

document.addEventListener("DOMContentLoaded", () => {

    /* ========================= */
    /* TOAST */
    /* ========================= */

    function showToast(message, type="success") {

        const container = document.getElementById("toastContainer");

        if (!container) return;

        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        toast.innerText = message;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = "0";
            setTimeout(() => toast.remove(), 300);
        }, 2500);
    }


    /* ========================= */
    /* CSRF */
    /* ========================= */

    function getCookie(name) {
        let cookieValue = null;

        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');

            for (let cookie of cookies) {
                cookie = cookie.trim();

                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }

        return cookieValue;
    }


    /* ========================= */
    /* ЦВЕТА ОЦЕНОК */
    /* ========================= */

    function applyGradeColor(input) {

        const val = (input.value || "").toLowerCase();

        input.classList.remove(
            "grade-5","grade-4","grade-3","grade-2",
            "grade-n","grade-empty","grade-pass","grade-fail"
        );

        if (!val || val === "_") input.classList.add("grade-empty");
        else if (val === "н") input.classList.add("grade-n");
        else if (val === "зачет") input.classList.add("grade-pass");
        else if (val === "незачет") input.classList.add("grade-fail");
        else if (val.startsWith("5")) input.classList.add("grade-5");
        else if (val.startsWith("4")) input.classList.add("grade-4");
        else if (val.startsWith("3")) input.classList.add("grade-3");
        else if (val.startsWith("2")) input.classList.add("grade-2");
    }


    /* ========================= */
    /* ФИЛЬТРЫ */
    /* ========================= */

    const form = document.getElementById("filterForm");
    const groupSelect = document.getElementById("groupSelect");
    const subjectSelect = document.getElementById("subjectSelect");

    // 🔧 фикс: безопасный fallback
    const subjectGroups = window.subjectGroups || {};

    if (form && groupSelect && subjectSelect) {

        function updateGroups() {

            const subjectId = subjectSelect.value;
            const allowed = subjectGroups[subjectId] || [];

            let hasValid = false;

            [...groupSelect.options].forEach(option => {

                if (allowed.includes(Number(option.value))) {
                    option.style.display = "block";

                    if (option.value === groupSelect.value) {
                        hasValid = true;
                    }

                } else {
                    option.style.display = "none";
                }

            });

            if (!hasValid) {
                for (let option of groupSelect.options) {
                    if (option.style.display !== "none") {
                        groupSelect.value = option.value;
                        break;
                    }
                }
            }
        }

        subjectSelect.addEventListener("change", () => {
            updateGroups();
            form.submit();
        });

        groupSelect.addEventListener("change", () => {
            form.submit();
        });

        updateGroups();
    }


    /* ========================= */
    /* ОЦЕНКИ */
    /* ========================= */

    document.querySelectorAll(".grade-input").forEach(input => {

        applyGradeColor(input);

        input.addEventListener("input", function () {
            applyGradeColor(this);
        });

        input.addEventListener("change", function () {

            // 🔧 фиксы
            if (!this.dataset.cadet || !this.dataset.lesson) return;

            let value = this.value.trim();
            value = value === "" ? null : value;

            fetch("/save_grade/", {  // 🔧 фикс URL
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({
                    cadet_id: this.dataset.cadet,
                    lesson_id: this.dataset.lesson,
                    value: value
                })
            })
            .then(res => res.json().catch(() => null)) // 🔧 фикс
            .then(data => {

                if (!data) {
                    showToast("Ошибка сервера", "error");
                    return;
                }

                if (data.error) {
                    showToast(data.error, "error");
                    return;
                }

                this.style.background = "#dcfce7";
                showToast("Сохранено");
            })
            .catch(() => {
                showToast("Ошибка", "error");
            });

        });

    });


    /* ========================= */
    /* ЭКЗАМЕН / ИТОГ */
    /* ========================= */

    document.querySelectorAll(".exam-input, .final-input").forEach(input => {

        input.addEventListener("change", function () {

            // 🔧 фиксы
            if (!this.dataset.cadet || !this.dataset.subject) return;

            let value = this.value.trim();
            value = value === "" ? null : value;

            fetch("/set_result/", {  // 🔧 фикс URL
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({
                    cadet_id: this.dataset.cadet,
                    subject_id: this.dataset.subject,
                    type: this.classList.contains("exam-input") ? "exam" : "final",
                    value: value
                })
            })
            .then(res => res.json().catch(() => null)) // 🔧 фикс
            .then(data => {

                if (!data) {
                    showToast("Ошибка сервера", "error");
                    return;
                }

                if (data.error) {
                    showToast(data.error, "error");
                    return;
                }

                showToast("Сохранено");
            })
            .catch(() => {
                showToast("Ошибка", "error");
            });

        });

    });


    /* ========================= */
    /* MOBILE ЦВЕТА */
    /* ========================= */

    document.querySelectorAll(".mobile-grade").forEach(el => {

        const val = (el.dataset.value || "").toLowerCase();

        if (!val || val === "_") el.classList.add("grade-empty");
        else if (val === "н") el.classList.add("grade-n");
        else if (val === "зачет") el.classList.add("grade-pass");
        else if (val === "незачет") el.classList.add("grade-fail");
        else if (val.startsWith("5")) el.classList.add("grade-5");
        else if (val.startsWith("4")) el.classList.add("grade-4");
        else if (val.startsWith("3")) el.classList.add("grade-3");
        else if (val.startsWith("2")) el.classList.add("grade-2");

    });

});