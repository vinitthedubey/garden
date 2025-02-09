document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("camera-feed");
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    const processedImage = document.getElementById("processed-image");
    const captureBtn = document.getElementById("capture-btn");

    // Access user camera
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(err => {
            console.error("Error accessing webcam: ", err);
        });

    // Capture & send frame for detection
    captureBtn.addEventListener("click", () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageData = canvas.toDataURL("image/jpeg"); // Convert frame to base64

        fetch("/detect", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: imageData })
        })
        .then(response => response.json())
        .then(data => {
            processedImage.src = data.image; // Display processed image
        })
        .catch(err => console.error("Error:", err));
    });
});
