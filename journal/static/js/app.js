/*
Главный JS файл проекта

Функции:
- навигация по ячейкам (Enter)
- фильтрация журнала
- пакетное сохранение оценок
- валидация + подсветка
- мобильное меню
*/

document.addEventListener("DOMContentLoaded", () => {

    /* ========================= */
    /* НАВИГАЦИЯ (ENTER) */
    /* ========================= */

    const inputs = Array.from(document.querySelectorAll(".grade-input"));

    inputs.forEach((input, index) => {

        input.addEventListener("keydown", e => {

            if (e.key === "Enter") {

                e.preventDefault();

                const next = inputs[index + 1];
                if (next) next.focus();

            }

        });

    });


    /* ========================= */
    /* ФИЛЬТРЫ */
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
    /* СОХРАНЕНИЕ */
/* ========================= */

let changedGrades = {};

// отслеживание изменений
document.querySelectorAll(".grade-input").forEach(input => {

    const handler = function () {

        const cadetId = this.dataset.cadet;
        const lessonId = this.dataset.lesson;
        const key = cadetId + "_" + lessonId;

        changedGrades[key] = {
            cadet_id: cadetId,
            lesson_id: lessonId,
            value: this.value
        };

        this.classList.remove("saved", "error");
        this.classList.add("changed");
    };

    input.addEventListener("input", handler);
    input.addEventListener("change", handler); // 🔥 для select

});


const saveBtn = document.getElementById("saveBtn");

if (saveBtn) {

    saveBtn.addEventListener("click", async () => {

        if (Object.keys(changedGrades).length === 0) {
            alert("Нет изменений");
            return;
        }

        let hasError = false;

        // 🧪 ВАЛИДАЦИЯ
        for (let key in changedGrades) {

            let item = changedGrades[key];
            let val = item.value;

            const input = document.querySelector(
                `.grade-input[data-cadet="${item.cadet_id}"][data-lesson="${item.lesson_id}"]`
            );

            input.classList.remove("error");

            if (val === "") continue;

            const validValues = [
            "2", "3", "4", "5",
            "2-", "3-", "4-", "5+",
            "зачет", "незачет", "_",
            ];

            if (!validValues.includes(val) && val !== "") {
                input.classList.add("error");
                hasError = true;
            }

        }

        if (hasError) {
            alert("Исправьте ошибки (оценки 2–5)");
            return;
        }

        // 💾 СОХРАНЕНИЕ
        for (let key in changedGrades) {

            const item = changedGrades[key];

            try {

                await fetch("/save-grade/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken")
                    },
                    body: JSON.stringify(item)
                });

                const input = document.querySelector(
                    `.grade-input[data-cadet="${item.cadet_id}"][data-lesson="${item.lesson_id}"]`
                );

                input.classList.remove("changed");
                input.classList.add("saved");

            } catch (e) {
                alert("Ошибка сети");
                return;
            }

        }

        alert("Сохранено ✅");
        changedGrades = {};
    });

}


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