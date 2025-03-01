// static/js/scripts.js

console.log("Library Management System: JS loaded!");

// Confirms borrowing a specific book
function confirmBorrow(bookName) {
    return confirm(`Are you sure you want to borrow "${bookName}"?`);
}

// Confirms returning a specific book
function confirmReturn(bookName) {
    return confirm(`Are you sure you want to return "${bookName}"?`);
}

// Confirms removing a specific book from the system
function confirmRemove(bookName) {
    return confirm(`Are you sure you want to remove "${bookName}"?`);
}
