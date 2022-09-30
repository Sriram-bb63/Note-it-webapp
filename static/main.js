function deleteNote(i) {
    var xhr_delete = new XMLHttpRequest();
    xhr_delete.open("POST", "/delete-note", true);
    xhr_delete.setRequestHeader('Content-Type', 'application/json');
    xhr_delete.send(JSON.stringify({
        "id": i
    }));
    console.log("Delete request sent");
    location.reload();
}

function openModal(i) {
    modal = document.getElementById("myModal");
    modal.style.display = "block";
    var editTitle = document.getElementById("note-id");
    editTitle.textContent = "Note ID: ".concat(i);
    list = document.getElementById("note-".concat(i));
    listElements = list.childNodes;
    title = listElements[1].textContent;
    content = listElements[3].textContent;
    titleField = document.getElementById("title-field");
    contentField = document.getElementById("content-field");
    titleField.value = title;
    contentField.value = content;
}
function closeModal() {
    modal = document.getElementById("myModal");
    modal.style.display = "none";
}

// function editNote(i) {
//     var xhr_edit = new XMLHttpRequest();
//     xhr_edit.open("POST", "/edit-post", true);
//     xhr_edit.setRequestHeader("Content-Type", "application/json");
//     xhr_edit.send(JSON.stringify({
//         "id": i
//     }));
//     console.log("Edit request sent");
//     location.reload();
// }