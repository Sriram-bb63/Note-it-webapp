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

function openEditModal(i) {
    modal = document.getElementById("editModal");
    modal.style.display = "block";
    var editTitle = document.getElementById("note-id");
    editTitle.textContent = "Note ID: ".concat(i);
    list = document.getElementById("note-".concat(i));
    listElements = list.childNodes;
    title = listElements[1].textContent;
    content = listElements[3].textContent;
    idField = document.getElementById("id-field");
    titleField = document.getElementById("title-field");
    contentField = document.getElementById("content-field");
    idField.value = i;
    titleField.value = title;
    contentField.value = content;
}
function closeModal() {
    modal = document.getElementById("editModal");
    modal.style.display = "none";
}

// function editNote(i) {
//     console.log("Function called");
//     titleField = document.getElementById("title-field");
//     contentField = document.getElementById("content-field");
//     newTitle = titleField.value;
//     newContent = contentField.value;
//     console.log("Form read");
//     const xhr_edit = new XMLHttpRequest();
//     console.log("XHR created");
//     xhr_edit.open("POST", "/edit-note", true);
//     console.log("XHR opened");
//     xhr_edit.setRequestHeader("Content-Type", "application/json");
//     console.log("XHR header");
//     xhr_edit.send(JSON.stringify({
//         "id": i,
//         "title": newTitle,
//         "content": newContent
//     }))
//     console.log("Edit req sent");
//     // location.reload();
// }