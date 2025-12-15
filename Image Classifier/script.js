
// More API functions here:
// https://github.com/googlecreativelab/teachablemachine-community/tree/master/libraries/image

// the link to your model provided by Teachable Machine export panel
const URL = "./model/";

let model, webcam, labelContainer, maxPredictions;

// Load the image model and setup the webcam
async function init() {
    const startButton = document.querySelector('.btn-primary');
    const loader = document.getElementById('loader');
    const overlay = document.getElementById('overlay-message');

    // Disable button to prevent multiple clicks
    startButton.disabled = true;
    loader.classList.remove('hidden');
    overlay.classList.add('hidden'); // Hide the "Click Start" text

    const modelURL = URL + "model.json";
    const metadataURL = URL + "metadata.json";

    try {
        // load the model and metadata
        // Note: the pose library adds "tmImage" object to your window (window.tmImage)
        model = await tmImage.load(modelURL, metadataURL);
        maxPredictions = model.getTotalClasses();

        // Convenience function to setup a webcam
        const flip = true; // whether to flip the webcam
        webcam = new tmImage.Webcam(400, 400, flip); // width, height, flip
        await webcam.setup(); // request access to the webcam
        await webcam.play();
        window.requestAnimationFrame(loop);

        // append elements to the DOM
        const canvas = document.getElementById("canvas");
        // We use the existing canvas element instead of appending a new one
        // The tmImage.Webcam class creates its own canvas, but we can draw it to ours
        // or just replace the element. Let's sync with the requestAnimationFrame loop.

        // Actually tmImage.webcam.canvas is the canvas element.
        // Let's replace our placeholder canvas or draw into it.
        // Simplest is to replace the ID or just append to container if we didn't have one.
        // Since I put a <canvas id="canvas"> in HTML, let's use the context to draw.
        // But tmImage provides a nice webcam object.

        labelContainer = document.getElementById("label-container");
        labelContainer.innerHTML = ''; // Clear previous labels if any

        for (let i = 0; i < maxPredictions; i++) { // and class labels
            // Create the label bar structure
            const barContainer = document.createElement("div");
            barContainer.classList.add("label-bar");

            const nameSpan = document.createElement("div");
            nameSpan.classList.add("label-name");

            const trackDiv = document.createElement("div");
            trackDiv.classList.add("progress-track");

            const fillDiv = document.createElement("div");
            fillDiv.classList.add("progress-fill");

            const probSpan = document.createElement("div");
            probSpan.classList.add("prob-text");

            trackDiv.appendChild(fillDiv);
            barContainer.appendChild(nameSpan);
            barContainer.appendChild(trackDiv);
            barContainer.appendChild(probSpan);

            labelContainer.appendChild(barContainer);
        }

        loader.classList.add('hidden');
    } catch (error) {
        console.error(error);
        alert("Error details: " + error.message + "\n\nMake sure the 'model' folder exists with model.json, metadata.json AND weights.bin, and that you are using 'Live Server'.");
        startButton.disabled = false;
        loader.classList.add('hidden');
        overlay.classList.remove('hidden');
        overlay.innerHTML = "<p>Error loading model.</p>";
    }
}

async function loop() {
    webcam.update(); // update the webcam frame
    await predict();

    // Draw the webcam frame to our canvas
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    if (webcam.canvas) {
        ctx.drawImage(webcam.canvas, 0, 0, canvas.width, canvas.height);
    }

    window.requestAnimationFrame(loop);
}

// run the webcam image through the image model
async function predict() {
    // predict can take in an image, video or canvas html element
    const prediction = await model.predict(webcam.canvas);

    const labelBars = document.getElementsByClassName("label-bar");

    for (let i = 0; i < maxPredictions; i++) {
        const classPrediction = prediction[i].className;
        const probability = prediction[i].probability;

        // Update DOM
        const bar = labelBars[i];
        const nameEl = bar.querySelector(".label-name");
        const fillEl = bar.querySelector(".progress-fill");
        const probEl = bar.querySelector(".prob-text");

        nameEl.innerText = classPrediction;
        fillEl.style.width = (probability * 100) + "%";
        probEl.innerText = probability.toFixed(2);

        // Highlight logic (optional)
        if (probability > 0.8) {
            fillEl.style.backgroundColor = "var(--primary-color)";
        } else {
            fillEl.style.backgroundColor = "var(--secondary-color)";
        }
    }
}
