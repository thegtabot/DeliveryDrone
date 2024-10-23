function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(msg => {
        msg.classList.toggle('dark-mode');
    });
    const pElements = document.querySelectorAll('p');
    pElements.forEach(p => {
        p.classList.toggle('dark-mode');
    });
    const inputFields = document.querySelectorAll('.input-group input');
    inputFields.forEach(input => {
        input.classList.toggle('dark-mode'); // Added for input fields
    });
}
