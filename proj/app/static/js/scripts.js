document.addEventListener("DOMContentLoaded", function () {
  // Get the submit button element
  var submitButton = document.getElementById("submit-button");

  // Add click event listener to the submit button
  if (submitButton) {
    submitButton.addEventListener("click", function () {
      simulateUpload();
    });
  }

  // Define the handleFiles function
  window.handleFiles = function (files) {
    const fileList = document.getElementById("file-display");
    fileList.innerHTML = "";
    for (let i = 0; i < files.length; i++) {
      const li = document.createElement("li");
      li.textContent = files[i].name;
      fileList.appendChild(li);
    }
  };

  // Define the simulateUpload function
  window.simulateUpload = function () {
    const fileList = document.getElementById("file-display");
    if (fileList.innerHTML === "No files selected") {
      alert("Please select a file to upload.");
      return;
    }
    // Redirect to the success view
    window.location.href = "/api/success/";
  };

  // Define the cancelUpload function
  window.cancelUpload = function () {
    document.getElementById("fileElem").value = "";
    document.getElementById("file-display").innerHTML = "No files selected";
  };
});

function check(){
        const emailField = document.getElementById("email");
        const proofField = document.getElementById("proof");

        // Check if fields are empty
        if (emailField == "" || proofField == "") {
            // Display an alert message
            alert("Please fill in both the email and proof fields.");
        }
        else{
            alert("Feedback Received")
            emailField.innerHTML = "";
            proofField.innerHTML = "";
        }
    }