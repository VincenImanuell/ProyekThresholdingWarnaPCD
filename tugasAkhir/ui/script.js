// Select necessary elements
let pickedColors = [];  // Array to hold picked colors
const dropArea = document.querySelector(".drag-area"),
      input = dropArea.querySelector("input"),
      pickColorBtn = document.getElementById("pick-color"),
      result = document.getElementById("result"),
      pickedColorsContainer = document.getElementById("picked-colors-container"),
      error = document.getElementById("error");

let file;

// File drag & drop and file input events
dropArea.addEventListener("click", () => {
    input.click();  // Trigger file input click
});

input.addEventListener("change", () => {
    file = input.files[0];
    dropArea.classList.add("active");
    showFile();
});

dropArea.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropArea.classList.add("active");
});

dropArea.addEventListener("dragleave", () => {
    dropArea.classList.remove("active");
});

dropArea.addEventListener("drop", (event) => {
    event.preventDefault();
    file = event.dataTransfer.files[0];
    showFile();
});

// Function to display the image file
function showFile() {
    const fileType = file.type;
    const validExtensions = ["image/jpeg", "image/jpg", "image/png"];
    if (validExtensions.includes(fileType)) {
        const fileReader = new FileReader();
        fileReader.onload = () => {
            const imgTag = `<img src="${fileReader.result}" alt="image">`;
            dropArea.innerHTML = imgTag;
        };
        fileReader.readAsDataURL(file);
    } else {
        alert("This is not an image file!");
        dropArea.classList.remove("active");
    }
    console.log(file);
}

// Check if EyeDropper API is supported
window.onload = () => {
    if ("EyeDropper" in window) {
        pickColorBtn.classList.remove("hide");
        eyeDropper = new EyeDropper();
    } else {
        error.classList.remove("hide");
        error.innerText = "Your Browser Doesn't Support EyeDropper API";
        pickColorBtn.classList.add("hide");
        return false;
    }
};

// Function to select color from the image using EyeDropper API
const colorSelector = async () => {
    try {
        const colorValue = await eyeDropper.open();
        const hexvalue = colorValue.sRGBHex;

        // Add the new color to the pickedColors array
        pickedColors.push(hexvalue);

        // Update the picked color cards
        updatePickedColors();

        // Change the button text after first color pick
        pickColorBtn.innerHTML = "Pick More Color";

        // Show result section
        result.style.display = "flex";
    } catch (err) {
        error.classList.remove("hide");
    }
};

// Update picked color cards
const updatePickedColors = () => {
    // Clear previous cards
    pickedColorsContainer.innerHTML = "";

    // Loop through each picked color and create a new card for it
    pickedColors.forEach((color, index) => {
        const card = document.createElement("div");
        card.classList.add("picked-color-card");

        // Create a color box for each picked color
        const colorBox = document.createElement("div");
        colorBox.classList.add("color-box");
        colorBox.style.backgroundColor = color;

        // Create color info
        const colorInfo = document.createElement("div");
        colorInfo.classList.add("color-info");

        const hexInput = document.createElement("input");
        hexInput.type = "text";
        hexInput.value = color;
        hexInput.readOnly = true;

        const rgbArr = [];
        for (let i = 1; i < color.length; i += 2) {
            rgbArr.push(parseInt(color[i] + color[i + 1], 16));
        }
        const rgbValue = `rgb(${rgbArr.join(", ")})`;

        const rgbInput = document.createElement("input");
        rgbInput.type = "text";
        rgbInput.value = rgbValue;
        rgbInput.readOnly = true;


        const deleteBtn = document.createElement("button");
        deleteBtn.textContent = "Delete";
        deleteBtn.classList.add("delete-btn");
        deleteBtn.addEventListener("click", () => {
            deleteColor(index);
        });

        colorInfo.appendChild(hexInput);
        colorInfo.appendChild(rgbInput);
        colorInfo.appendChild(deleteBtn);

        // Append color box and info to card
        card.appendChild(colorBox);
        card.appendChild(colorInfo);

        // Append the card to the picked colors container
        pickedColorsContainer.appendChild(card);

        console.log(pickedColors);
    });
};

// Function to delete color from picked colors
const deleteColor = (index) => {
    pickedColors.splice(index, 1);  // Remove the color at the given index
    updatePickedColors();  // Re-render the updated list of colors
};

// Event listeners
pickColorBtn.addEventListener("click", colorSelector);
