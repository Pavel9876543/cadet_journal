/*
Скрипт улучшает ввод оценок
и позволяет перемещаться по ячейкам
как в Excel
*/

document.addEventListener("DOMContentLoaded", () => {

const inputs = document.querySelectorAll(".grade-input");

inputs.forEach((input, index) => {

input.addEventListener("keydown", e => {

if(e.key === "Enter"){

e.preventDefault();

let next = inputs[index + 1];

if(next){
next.focus();
}

}

});

});

});

/*
Мобильное меню
*/

const toggle = document.querySelector(".menu-toggle");
const menu = document.querySelector(".nav-links");

if(toggle){

toggle.addEventListener("click", () => {

menu.classList.toggle("active");

});

}