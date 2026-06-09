const socket = new WebSocket(`ws://${window.location.host}/ws/socket-server/`);
let myUserId = null;

socket.onopen = function (e) {
    console.log("WebSocket connection established.");
};

socket.onclose = function (e) {
    console.log("WebSocket connection closed.");
};

// handle incoming files
socket.onmessage = function (e) {
    let data = JSON.parse(e.data);

    if (data.type === 'user_id') {
        myUserId = data.user_id;
        document.getElementById('myUserId').innerHTML = myUserId;
    }

    if (data.type === 'file') {
        let agree = confirm(`User ${data.sender_id} is sending a file: ${data.filename}. Do you want to download it?`);
        if (agree) {
            downloadFile(data.filename, data.file);
        }
    }
};

let form = document.getElementById('form');
form.addEventListener('submit', (e) => {
    e.preventDefault();

    let fileInput = document.getElementById('fileInput');
    let file = fileInput.files[0];
    let targetUserId = document.getElementById('userInput').value;

    let reader = new FileReader();
    reader.onload = function (event) {
        let fileData = event.target.result.split(',')[1];  // extract base64 part

        // FOR DEVELOPMENT ONLY !!!
        // console.log("Encoded: " + fileData.substring(0, 10));

        socket.send(JSON.stringify({
            'filename': file.name,
            'file': fileData,
            'target_user_id': targetUserId
        }));
    };
    reader.readAsDataURL(file);  // convert to base64
    form.reset();
});

function downloadFile(fileName, fileData) {
    // 1. creates an invisible link
    // 2. sets its href to the base64 encoded file data
    // 3. triggers download with the specified filename.

    let link = document.createElement('a');
    link.href = 'data:application/octet-stream;base64,' + fileData;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // FOR DEVELOPMENT ONLY !!!
    // console.log("Decoded: " + link.download.substring(0, 10));
}
