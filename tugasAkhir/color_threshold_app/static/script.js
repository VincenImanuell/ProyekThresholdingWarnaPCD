// Select necessary elements
let pickedColors = []; // Array to hold picked colors
const dragArea = document.querySelector(".drag-area");
// const input = dropArea.querySelector("input"); // Original, might conflict if input removed from dragArea
const fileUploadInput = document.getElementById("fileUploadInput"); // Use the dedicated input
const uploadButtonTrigger = document.getElementById("uploadButtonTrigger"); // Button to click the hidden file input

const pickColorBtn = document.getElementById("pick-color");
const pickedColorsContainer = document.getElementById("picked-colors-container");
const error = document.getElementById("error");

// New elements for processing and display
const processImageBtn = document.getElementById("processImageBtn");
const processedImageDisplay = document.getElementById("processedImageDisplay");
const resultHeading = document.getElementById("result-heading");
const processingLoader = document.getElementById("processing-loader");


let uploadedFileObject; // To store the File object
let eyeDropper;

// Trigger file input click when drag area or custom upload button is clicked
dragArea.addEventListener("click", () => {
    fileUploadInput.click();
});
uploadButtonTrigger.addEventListener("click", () => {
    fileUploadInput.click();
});


fileUploadInput.addEventListener("change", function() { // Use `this` for file input
    if (this.files && this.files[0]) {
        uploadedFileObject = this.files[0];
        dragArea.classList.add("active");
        showFilePreview();
        pickColorBtn.style.display = "inline-block"; // Show pick color button
        processImageBtn.style.display = "none"; // Hide process until colors are picked
        processedImageDisplay.style.display = "none"; // Hide previous result
        resultHeading.style.display = "none";
        error.classList.add("hide");
    }
});

dragArea.addEventListener("dragover", (event) => {
    event.preventDefault();
    dragArea.classList.add("active");
    dragArea.querySelector("h1").textContent = "Lepaskan untuk Upload"; // More direct
});

dragArea.addEventListener("dragleave", () => {
    dragArea.classList.remove("active");
    dragArea.querySelector("h1").textContent = "Klik di sini untuk upload gambar";
});

dragArea.addEventListener("drop", (event) => {
    event.preventDefault();
    if (event.dataTransfer.files && event.dataTransfer.files[0]) {
        uploadedFileObject = event.dataTransfer.files[0];
        fileUploadInput.files = event.dataTransfer.files; // Synchronize with the hidden input
        dragArea.classList.add("active");
        showFilePreview();
        pickColorBtn.style.display = "inline-block";
        processImageBtn.style.display = "none";
        processedImageDisplay.style.display = "none";
        resultHeading.style.display = "none";
        error.classList.add("hide");
    }
});

// Function to display the image file preview
function showFilePreview() {
    if (!uploadedFileObject) return;
    const fileType = uploadedFileObject.type;
    const validExtensions = ["image/jpeg", "image/jpg", "image/png"];
    if (validExtensions.includes(fileType)) {
        const fileReader = new FileReader();
        fileReader.onload = () => {
            const imgTag = `<img src="${fileReader.result}" alt="image-preview" style="max-width:100%; max-height:100%; object-fit: contain;">`;
            dragArea.innerHTML = imgTag;
            dragArea.style.border = "2px dashed #ccc"; // Keep some border or style as needed
        };
        fileReader.readAsDataURL(uploadedFileObject);
    } else {
        alert("Ini bukan file gambar (jpeg, jpg, png)!");
        dragArea.classList.remove("active");
        dragArea.innerHTML = `
            <div class="icon"><i class="fas fa-cloud-upload-alt"></i></div>
            <h1 style="margin-bottom: 15px;">Klik di sini untuk upload gambar</h1>
            <h2>Atau drag file gambar ke sini</h2>`;
        uploadedFileObject = null;
        pickColorBtn.style.display = "none";
        processImageBtn.style.display = "none";
    }
}

// Check if EyeDropper API is supported
window.onload = () => {
    error.classList.add("hide");
    pickColorBtn.style.display = "none"; // Hide initially

    if ("EyeDropper" in window) {
        eyeDropper = new EyeDropper();
    } else {
        error.classList.remove("hide");
        error.innerText = "Browser Anda tidak mendukung EyeDropper API";
        pickColorBtn.style.display = "none";
        return false;
    }
};

// Function to select color from the image using EyeDropper API
const colorSelector = async () => {
    if (!uploadedFileObject) {
        alert("Silakan upload gambar terlebih dahulu!");
        return;
    }
    if (!eyeDropper) {
        error.classList.remove("hide");
        error.innerText = "EyeDropper API tidak tersedia.";
        return;
    }
    try {
        error.classList.add("hide"); // Hide previous errors
        const colorValue = await eyeDropper.open();
        const hexvalue = colorValue.sRGBHex;

        pickedColors.push(hexvalue);
        updatePickedColorsDisplay();

        pickColorBtn.innerHTML = "Pilih Warna Lain";
        if (pickedColors.length > 0) {
            processImageBtn.style.display = "inline-block"; // Show process button
        }
    } catch (err) {
        console.error("Error menggunakan EyeDropper:", err);
        // User might cancel the eyedropper, which is normal
        if (err.name !== "AbortError") {
             error.classList.remove("hide");
             error.innerText = "Tidak bisa memilih warna. Pastikan klik pada gambar.";
        }
    }
};

// Update picked color cards display
const updatePickedColorsDisplay = () => {
    pickedColorsContainer.innerHTML = ""; // Clear previous cards
    pickedColors.forEach((color, index) => {
        const card = document.createElement("div");
        card.classList.add("picked-color-card");

        const colorBox = document.createElement("div");
        colorBox.classList.add("color-box");
        colorBox.style.backgroundColor = color;

        const colorInfo = document.createElement("div");
        colorInfo.classList.add("color-info");

        const hexInput = document.createElement("input");
        hexInput.type = "text";
        hexInput.value = color;
        hexInput.readOnly = true;

        // Convert HEX to RGB for display
        let tempHex = color.startsWith('#') ? color.substring(1) : color;
        if (tempHex.length === 3) { // Handle shorthand hex
            tempHex = tempHex.split('').map(char => char + char).join('');
        }
        const r = parseInt(tempHex.substring(0, 2), 16);
        const g = parseInt(tempHex.substring(2, 4), 16);
        const b = parseInt(tempHex.substring(4, 6), 16);
        const rgbValue = `rgb(${r}, ${g}, ${b})`;

        const rgbInput = document.createElement("input");
        rgbInput.type = "text";
        rgbInput.value = rgbValue;
        rgbInput.readOnly = true;

        const deleteBtn = document.createElement("button");
        deleteBtn.textContent = "Hapus";
        deleteBtn.classList.add("delete-btn"); // Make sure this class exists in style.css for styling
        deleteBtn.addEventListener("click", () => {
            deleteColor(index);
        });

        colorInfo.appendChild(hexInput);
        colorInfo.appendChild(rgbInput);
        colorInfo.appendChild(deleteBtn);

        card.appendChild(colorBox);
        card.appendChild(colorInfo);
        pickedColorsContainer.appendChild(card);
    });

    if (pickedColors.length === 0) {
        pickColorBtn.innerHTML = "Pilih warna";
        processImageBtn.style.display = "none"; // Hide if no colors are picked
    }

    console.log(pickedColors);
};

// Function to delete color from picked colors
const deleteColor = (index) => {
    pickedColors.splice(index, 1);
    updatePickedColorsDisplay();
};

// Event listeners
pickColorBtn.addEventListener("click", colorSelector);

// Process Image Button Logic
processImageBtn.addEventListener("click", async () => {
    if (!uploadedFileObject) {
        alert("Silakan upload gambar terlebih dahulu.");
        return;
    }
    if (pickedColors.length === 0) {
        alert("Silakan pilih minimal satu warna.");
        return;
    }

    processingLoader.classList.remove("hide");
    processedImageDisplay.style.display = "none";
    resultHeading.style.display = "none";
    error.classList.add("hide");

    const formData = new FormData();
    formData.append("image", uploadedFileObject);
    // Send colors as an array. Flask can get this with request.form.getlist('colors[]')
    pickedColors.forEach(color => {
        formData.append("colors[]", color);
    });
    // Fallback for some server configurations if colors[] doesn't work:
    // formData.append("colors", pickedColors.join(','));


    try {
        const response = await fetch("/process_image", {
            method: "POST",
            body: formData, // FormData handles headers for multipart/form-data
        });

        processingLoader.classList.add("hide");

        if (response.ok) {
            const data = await response.json();
            if (data.processed_image) {
                processedImageDisplay.src = data.processed_image;
                processedImageDisplay.style.display = "block";
                resultHeading.style.display = "block";
            } else if (data.error) {
                error.innerText = `Error dari server: ${data.error}`;
                error.classList.remove("hide");
            }
        } else {
            // Try to get error message from server if response is not OK
            const errData = await response.json().catch(() => ({ error: "Respons tidak valid dari server." }));
            error.innerText = `Error server: ${response.status} - ${errData.error || 'Terjadi kesalahan tidak diketahui.'}`;
            error.classList.remove("hide");
        }
    } catch (err) {
        processingLoader.classList.add("hide");
        error.innerText = `Error JavaScript: ${err.message}`;
        error.classList.remove("hide");
        console.error("Error mengirim data:", err);
    }
});