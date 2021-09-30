$('#delete-film-modal').on('show.bs.modal', function (event) {
    let url = event.relatedTarget.dataset.url;
    let form = this.querySelector('form');
    form.action = url;
    let filmName = event.relatedTarget.closest('tr').querySelector('.film-name').textContent;
    this.querySelector('#film-name').textContent = filmName;
    })

$('select').selectpicker();

const TOOLBAR_ITEMS = [
    "bold", "italic", "heading", "|", 
    "quote", "ordered-list", "unordered-list", "|",
    "guide"
]

window.onload = function() {
    if (document.getElementById('description')) {
        let easyMDE = new EasyMDE({
            element: document.getElementById('description'),
            toolbar: TOOLBAR_ITEMS
        });}
    if (document.getElementById('text_field')) {
        let easyMDE2 = new EasyMDE({
            element: document.getElementById('text_field'),
            toolbar: TOOLBAR_ITEMS
        });}
}

