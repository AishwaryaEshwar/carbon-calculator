document.getElementById("uploadForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const pdfFile = document.getElementById("pdfFile").files[0];
    const co2File = document.getElementById("co2File").files[0];
    const status = document.getElementById("status");
    const downloadBtn = document.getElementById("downloadBtn");

    if (!pdfFile || !co2File) {
        status.innerText = "Please select both files.";
        return;
    }

    const formData = new FormData();
    formData.append("pdf_file", pdfFile);
    formData.append("co2_file", co2File);

    status.innerText = "Processing... Please wait.";
    downloadBtn.style.display = "none";

    try {
        const response = await fetch("http://127.0.0.1:8000/upload", {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Processing failed");

        const data = await response.json();
        const filename = data.filename;

        status.innerText = "Processing complete! Click below to download.";

        downloadBtn.style.display = "inline-block";

        downloadBtn.onclick = function() {
            window.location.href = `http://127.0.0.1:8000/download/${filename}`;
        };

    } catch (error) {
        status.innerText = "Error processing files.";
        console.error(error);
    }
});
