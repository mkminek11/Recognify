const title = document.getElementById("title");
const title_edit_btn = document.getElementById("edit_title");
const title_input = document.getElementById("title_input");
const size_callibration = document.getElementById("size_callibration");

title_input.parentElement.style.display = "none";



/**
 * Switches the title into edit mode. Hides the original title, shows the input
 * field with the original title's value, and changes the button to a "save"
 * button.
 */
function edit_title() {
    const old_title = title.innerHTML;
    title.style.display = "none";
    title_input.value = old_title;
    title_input.parentElement.style.display = "inline-block";
    title_edit_btn.classList.replace("fa-pencil", "fa-check");
    title_edit_btn.onclick = save_title;
    update_size();

    title_input.addEventListener("input", update_size);
}



/**
 * Saves the title. Hides the input field, shows the original title, and
 * changes the button back to an edit button.
 */
function save_title() {
    const new_title = document.getElementById("title_input").value;

    if (new_title.match(/^\s*$/)) {new_title = title.innerHTML;}

    title.style.display = "inline-block";
    title.innerHTML = new_title;
    title.title = new_title;
    title_input.parentElement.style.display = "none";

    title_edit_btn.classList.replace("fa-check", "fa-pencil");
    title_edit_btn.onclick = edit_title;

    const xhr = new XMLHttpRequest();
    
    xhr.open("POST", `/edit/${uuid}/title`, false);
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    xhr.send("title=" + encodeURIComponent(new_title));
}



/**
 * Updates the width of the title's input field to be the same width as the
 * title's current text. This is needed because the input field's width is
 * determined by its content, and if the content is too long, the input field
 * will be too wide for the page.
 */
function update_size() {
    size_callibration.innerHTML = title_input.value;
}



title_input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        save_title();
        title_input.blur();
    }

    if (event.key === "Escape") {
        title_input.value = title.innerHTML;
        save_title();
        title_input.blur();
    }
});