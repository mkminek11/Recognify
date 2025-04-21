
const image      = document.getElementById("image");
const text_input = document.getElementById("text_input");
const options    = document.querySelector(".options");

const uuid = location.pathname.split("/").slice(-2)[0];
const images_count = parseInt(document.getElementById("images_count").value);

let index = 0;

const edit = document.getElementById("previews") != null;

let data = {};
let images = {};


function get_image_data(image) {
    if (image in images) return images[image];

    const xhr = new XMLHttpRequest();

    xhr.open("GET", `/set/${uuid}/image/${image}`, false);
    xhr.send();

    img_data = JSON.parse(xhr.responseText);
    images[image] = img_data;

    return img_data;
}



function move(amount) {
    if (index + amount < 0) {
        index = 0;
        return;
    } else if (index + amount >= images_count ) {
        index = images_count - 1;
        return;
    } else {
        index += amount;
    }
}



function set_index(new_index) {
    if (0 <= new_index < images_count) {
        index = new_index;
        update_cards();
    }
}


