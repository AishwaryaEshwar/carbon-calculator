document.getElementById("uploadForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const pdfFile = document.getElementById("pdfFile").files[0];
    const co2File = document.getElementById("co2File").files[0];

    const status = document.getElementById("status");
    const downloadBtn = document.getElementById("downloadBtn");
    const spinner = document.getElementById("spinner");

    if (!pdfFile || !co2File) {
        status.innerText = "Please select both files.";
        return;
    }

    const formData = new FormData();
    formData.append("pdf_file", pdfFile);
    formData.append("co2_file", co2File);

    status.innerText = "";
    downloadBtn.style.display = "none";
    spinner.style.display = "flex";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Processing failed");

        const data = await response.json();
        const filename = data.filename;

        spinner.style.display = "none";
        status.innerText = "Processing complete! Click below to download.";
        downloadBtn.style.display = "inline-block";

        downloadBtn.onclick = function() {
            window.location.href = `/download/${filename}`;
        };
    } catch (error) {
        spinner.style.display = "none";
        status.innerText = "Error processing files.";
        console.error(error);
    }
});