// Add a special class for the current day if we are in December.
window.addEventListener("DOMContentLoaded", function() {
    let date = new Date();
    if (date.getMonth() == 11) {
        let jours = document.querySelectorAll(".jours a");
        for(let jour of jours) {
            if (jour.textContent == date.getDate()) {
                jour.classList.add("ajd");  // for backwards compatibility
                jour.classList.add("today");
            }
        }
    }
});
