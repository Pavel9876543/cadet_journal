/*
Главный JS файл проекта

Функции:
- навигация по ячейкам (Enter)
- фильтрация журнала
- AJAX сохранение оценок
- мобильное меню
*/

document.addEventListener("DOMContentLoaded", () => {

    /* ========================= */
    /* НАВИГАЦИЯ ПО ЯЧЕЙКАМ */
    /* ========================= */

    const inputs = document.querySelectorAll(".grade-input");

    inputs.forEach((input, index) => {

        input.addEventListener("keydown", e => {

            if (e.key === "Enter") {

                e.preventDefault();

                let next = inputs[index + 1];

                if (next) {
                    next.focus();
                }

            }

        });

    });


    /* ========================= */
    /* ФИЛЬТРЫ ЖУРНАЛА */
    /* ========================= */

    const form = document.getElementById("filterForm");
    const groupSelect = document.getElementById("groupSelect");
    const subjectSelect = document.getElementById("subjectSelect");

    if (form && groupSelect && subjectSelect && window.subjectGroups) {

        function updateGroups() {

            const subjectId = subjectSelect.value;
            const allowedGroups = window.subjectGroups[subjectId] || [];

            let hasSelected = false;

            [...groupSelect.options].forEach(option => {

                if (allowedGroups.includes(Number(option.value))) {

                    option.style.display = "block";

                    if (option.value === groupSelect.value) {
                        hasSelected = true;
                    }

                } else {
                    option.style.display = "none";
                }

            });

            // если выбранная группа недоступна
            if (!hasSelected) {

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
    /* AJAX СОХРАНЕНИЕ ОЦЕНОК */
    /* ========================= */

    document.querySelectorAll(".grade-input").forEach(input => {

        input.addEventListener("change", function () {

            const cadetId = this.dataset.cadet;
            const lessonId = this.dataset.lesson;
            const value = this.value;

            fetch("/save-grade/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({
                    cadet_id: cadetId,
                    lesson_id: lessonId,
                    value: value
                })
            })
            .then(res => res.json())
            .then(() => {
                this.style.background = "#dcfce7";
            });

        });

    });


    /* ========================= */
    /* МОБИЛЬНОЕ МЕНЮ */
    /* ========================= */

    const toggle = document.querySelector(".menu-toggle");
    const menu = document.querySelector(".nav-links");

    if (toggle && menu) {

        toggle.addEventListener("click", () => {
            menu.classList.toggle("active");
        });

    }

});


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