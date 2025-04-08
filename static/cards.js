
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

    if (edit) {
        const img = document.getElementById("previews").children[image].querySelector("img");
        document.getElementById("previews").scrollTo(0, 40 * index - 100);

        img.src = `data:image/png;base64,${img_data["image"]}`;
    }

    return img_data;
}



function move(amount) {
    if (edit) {save_image_title()};

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



function set_index(new_index) {
    if (0 <= new_index < images_count) {
        index = new_index;
        update_cards();
    }
}



function update_cards() {
    const image_data = get_image_data(index);

    image.src = `data:image/png;base64,${image_data["image"]}`;
    if (edit) text_input.value = index in data ? data[index] : "";

    document.getElementById("btn_l").disabled = index == 0;
    document.getElementById("btn_r").disabled = index == images_count - 1;

    if (edit) update_options(image_data);
}

