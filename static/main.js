function deleteNote(i) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/delete-note", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        id: i
    }));
    console.log("Request sent");
    location.reload();
}