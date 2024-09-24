const socket = new WebSocket(`ws://${window.location.host}/ws/socket-server/`);
let myUserId = null;

socket.onopen = function (e) {
    console.log("WebSocket connection established.");
};

socket.onclose = function (e) {
    console.log("WebSocket connection closed.");
};

// Handle incoming files
socket.onmessage = function (e) {
    let data = JSON.parse(e.data);

    // Display the user's unique ID on the page
    if (data.type === 'user_id') {
        myUserId = data.user_id;
        document.getElementById('myUserId').innerHTML = myUserId;
    }

    // Handle form submission (sending files)
    if (data.type === 'file_offer') {
        let agree = confirm(`User ${data.sender_id} is sending a file: ${data.file_name}. Do you want to download it?`);
        if (agree) {
            downloadFile(data.file_name, data.file);
        }
    }
};

let form = document.getElementById('form');
form.addEventListener('submit', (e) => {
    e.preventDefault();  // Prevent it from doing a normal submission

    let fileInput = document.getElementById('fileInput');
    let file = fileInput.files[0];
    let targetUserId = document.getElementById('userInput').value;

    let reader = new FileReader();
    reader.onload = function (event) {
        let fileData = event.target.result.split(',')[1];  // Extract base64 part

        // FOR DEVELOPMENT ONLY !!!
        // console.log("Encoded: " + fileData.substring(0, 10));

        // Send the file data to the selected user via WebSocket
        socket.send(JSON.stringify({
            'file_name': file.name,
            'file': fileData,
            'target_user_id': targetUserId
        }));
    };
    reader.readAsDataURL(file);  // Convert to base64
    form.reset();
});

function downloadFile(fileName, fileData) {
    // Creates an invisible link, sets its href to the base64-encoded file data,
    // and triggers a download with the specified filename. The browser automatically
    // decodes the base64 string back into the original binary file upon download.
    let link = document.createElement('a');
    link.href = 'data:application/octet-stream;base64,' + fileData;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // FOR DEVELOPMENT ONLY !!!
    // console.log("Decoded: " + link.download.substring(0, 10));
}
