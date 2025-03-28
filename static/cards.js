
const image      = document.getElementById("image");
const text_input = document.getElementById("text_input");
const options    = document.querySelector(".options");

const uuid = location.pathname.split("/").slice(-2)[0];
const images_count = parseInt(document.getElementById("images_count").value);

let index = 0;

const edit = document.getElementById("previews") != null;

if (edit) {
    var ignore_numbers   = document.getElementById("ignore_numbers"  ).checked;
    var ignore_symbols   = document.getElementById("ignore_symbols"  ).checked;
    var strip_whitespace = document.getElementById("strip_whitespace").checked;
    var skip_links       = document.getElementById("skip_links"      ).checked;
    var split_brackets   = document.getElementById("split_brackets"  ).checked;
    var capitalize       = document.getElementById("capitalize"      ).checked;
    
    document.getElementById("ignore_numbers")  .onchange = () => { ignore_numbers   = document.getElementById("ignore_numbers"  ).checked; };
    document.getElementById("ignore_symbols")  .onchange = () => { ignore_symbols   = document.getElementById("ignore_symbols"  ).checked; };
    document.getElementById("strip_whitespace").onchange = () => { strip_whitespace = document.getElementById("strip_whitespace").checked; };
    document.getElementById("skip_links")      .onchange = () => { skip_links       = document.getElementById("skip_links"      ).checked; };
    document.getElementById("split_brackets")  .onchange = () => { split_brackets   = document.getElementById("split_brackets"  ).checked; };
    document.getElementById("capitalize")      .onchange = () => { capitalize       = document.getElementById("capitalize"      ).checked; };
}



let data = {};
let images = {};


/**
 * Makes a GET request to /set/${uuid}/image/${image} and returns the parsed response.
 * The response should be a JSON object with two properties: "image", which is a base64 encoded string
 * of the image data, and "options", which is an array of strings, each of which is a label
 * for the image.
 *
 * @param {number} image The index of the image to retrieve.
 * @returns {object} The response object with "image" and "options" properties.
 */
function get_image_data(image) {
    if (image in images) return images[image];

    const xhr = new XMLHttpRequest();

    xhr.open("GET", `/set/${uuid}/image/${image}`, false);
    xhr.send();

    img_data = JSON.parse(xhr.responseText);

    images[image] = img_data;

    if (edit) {
        const img = document.getElementById("previews").children[image].querySelector("img");
        document.getElementById("previews").scrollTo(0, 40 * index - 100);

        img.src = `data:image/png;base64,${img_data["image"]}`;
    }

    return img_data;
}



/**
 * Changes the index of the image displayed by moving the index by the given amount.
 * If the new index would be out of bounds, it is set to either 0 or the last valid index.
 *
 * @param {number} amount The amount to move the index by.
 */
function move(amount) {
    if (edit) save_image_title();

    if (index + amount < 0) {
        index = 0;
        return;
    } else if (index + amount >= images_count ) {
        index = images_count - 1;
        return;
    } else {
        index += amount;
    }

    update_cards();
}



/**
 * Sets the current image index to the specified new index if it is within the valid range.
 * Calls the update_cards function to refresh the displayed image and options.
 *
 * @param {number} new_index The new index to set, must be between 0 and images_count - 1.
 */
function set_index(new_index) {
    if (0 <= new_index < images_count) {
        index = new_index;
        update_cards();
    }
}



/**
 * Updates the cards section of the UI by retrieving the image and options data at the
 * current index and updating the image and options section of the UI accordingly.
 * Also resets the text input to an empty string.
 */
function update_cards() {
    const image_data = get_image_data(index);

    image.src = `data:image/png;base64,${image_data["image"]}`;
    if (edit) text_input.value = index in data ? data[index] : "";

    document.getElementById("btn_l").disabled = index == 0;
    document.getElementById("btn_r").disabled = index == images_count - 1;

    if (edit) update_options(image_data);
}



/**
 * Updates the options section of the UI by parsing and formatting the options provided in the image_data.
 * If the `split_symbols` flag is set, the options are split on symbols like commas, semicolons, etc.
 * Each option is further processed based on flags such as `ignore_numbers`, `strip_whitespace`, and `skip_links`.
 * The processed options are then set as the inner HTML of the options container, with each option displayed
 * as a clickable div that triggers the `save` function when clicked.
 *
 * @param {object} image_data The data object containing the image options to display. 
 *                            Expected to have an `options` property which is an array of strings.
 */
function update_options(image_data) {
    options.innerHTML = image_data["options"].map((option) => {

        if (split_symbols) {
            option = option.split(/\s*[,;:–><-=]+\s*/g).join("\n");
        }

        return option.split("\n").map(o => {
            if (ignore_numbers)   {o = o.replace(/\d/g, "");}
            if (strip_whitespace) {o = o.trim();}
            if (skip_links)       {o = o.replace(/https?:\/\/[^\s]+/g, "");}

            if (o.match(/^[\s.:;,–><=]*$/g)) return "";
            if (capitalize) o = o[0].toUpperCase() + o.slice(1).toLowerCase();
            return `<div class="option" title="${o}" onclick="save(this)">${o}</div>`;
        }).join("\n");
    }).join("\n");
}



function save_image_title(element = null) {
    if (element) text_input.value = element.title;

    data[index] = text_input.value;

    const label = document.getElementById("previews").children[index].querySelector("label");
    if (text_input.value) {
        label.innerText = text_input.value;
    } else {
        label.innerHTML = "<i class='fa-solid fa-xmark'></i>";
    }

    document.getElementById("previews").scrollTo(0, 40 * index - 100);

    text_input.blur();
}



function skip_image() {
    text_input.value = "";
    save_image_title();
}



function submit() {
    const xhr = new XMLHttpRequest();

    xhr.open("POST", `/set/${uuid}/save`, false);
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    xhr.onload = () => {
        if (xhr.status == 200) {
            window.location.href = "/";
        } else {
            alert(`Error saving presentation: ${xhr.status} ${xhr.statusText}`);
        }
    };

    xhr.send("data=" + encodeURIComponent(JSON.stringify(data)));
}



document.addEventListener("keydown", (event) => {
    if (document.activeElement === text_input) {
        if (event.key === "Enter") {text_input.blur();}
        if (event.key === "Escape") {text_input.blur();}
    } else {
        if (event.key === "ArrowRight") {move(+1);}
        if (event.key === "ArrowLeft" ) {move(-1);}
        if (event.key === ",") {skip_image();}

        if (!isNaN(+event.key) && parseInt(event.key) == parseFloat(event.key)) {
            if (+event.key < document.querySelector(".options").children.length) {
                save_image_title(document.querySelector(".options").children[+event.key]);
            }
        }

        if (event.key === "Enter") {text_input.focus();}
    }
});