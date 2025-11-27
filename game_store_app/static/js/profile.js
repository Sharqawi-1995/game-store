// profile.js
function toggleEdit(editMode) {
    const info = document.getElementById('profile-info');
    const form = document.getElementById('edit-form');
    const editBtn = document.getElementById('edit-btn');

    if (!info || !form || !editBtn) return;

    if (editMode) {
        info.style.display = 'none';
        form.style.display = 'block';
        editBtn.style.display = 'none';
    } else {
        info.style.display = 'block';
        form.style.display = 'none';
        editBtn.style.display = 'inline-block';
    }
}
