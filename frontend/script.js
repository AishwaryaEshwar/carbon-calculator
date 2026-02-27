document.getElementById("uploadForm").addEventListener("submit", function(e) {
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

    if (!pdfFile.name.toLowerCase().endsWith(".pdf")) {
        status.innerText = "Only PDF files are allowed for the first input.";
        return;
    }
    if (!co2File.name.toLowerCase().endsWith(".xlsx")) {
        status.innerText = "Only .xlsx files are allowed for the second input.";
        return;
    }

    const formData = new FormData();
    formData.append("pdf_file", pdfFile);
    formData.append("co2_file", co2File);

    status.innerText = "";
    downloadBtn.style.display = "none";
    spinner.style.display = "flex";

    // Use a simple form submission to backend
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/upload");
    xhr.onload = function() {
        spinner.style.display = "none";
        if (xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            const filename = data.filename;

            status.innerText = "Processing complete! Click below to download.";
            downloadBtn.style.display = "inline-block";

            // Set download URL
            downloadBtn.href = `/download/${filename}`;
            downloadBtn.setAttribute("download", filename);
        } else {
            status.innerText = "Error processing files.";
            console.error(xhr.responseText);
        }
    };
    xhr.send(formData);
});
