/**
 * CourseGen - Client-Side Interactive JavaScript
 */

document.addEventListener("DOMContentLoaded", function () {
    // 1. Password confirmation check on registration
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", function (e) {
            const password = document.getElementById("password").value;
            const confirmPassword = document.getElementById("confirm_password").value;

            if (password !== confirmPassword) {
                e.preventDefault();
                alert("Passwords do not match. Please verify and try again.");
            }
        });
    }

    // 2. Interactive question tracking on quiz form
    const quizForm = document.getElementById("quizForm");
    if (quizForm) {
        const questionCards = document.querySelectorAll(".question-card");
        const submitBtn = document.getElementById("submitQuizBtn");

        function updateAnsweredCount() {
            let answeredCount = 0;
            questionCards.forEach(function (card) {
                const radios = card.querySelectorAll("input[type='radio']:checked");
                const textInput = card.querySelector("input[type='text']");

                if (radios.length > 0 || (textInput && textInput.value.trim().length > 0)) {
                    answeredCount++;
                }
            });

            if (submitBtn) {
                submitBtn.innerHTML = `<i class="bi bi-check2-circle me-2"></i> Submit Quiz (${answeredCount}/${questionCards.length} Answered)`;
            }
        }

        // Attach change listeners to all inputs in quiz
        quizForm.querySelectorAll("input").forEach(function (input) {
            input.addEventListener("change", updateAnsweredCount);
            input.addEventListener("input", updateAnsweredCount);
        });

        // Initialize count on page load
        updateAnsweredCount();
    }

    // 3. Course generation loading spinner
    const courseForm = document.getElementById("courseForm");
    if (courseForm) {
        courseForm.addEventListener("submit", function () {
            const btn = document.getElementById("generateBtn");
            if (btn) {
                btn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Generating 15-Q Modules & Curricula...`;
                btn.classList.add("disabled");
            }
        });
    }
});
