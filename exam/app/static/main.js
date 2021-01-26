

function imagePreviewHandler(event) {
    if (event.target.files && event.target.files[0]) {
        let reader = new FileReader();
        reader.onload = function (e) {
            let img = document.querySelector('.background-preview > img');
            img.src = e.target.result;
            if (img.classList.contains('d-none')) {
                let label = document.querySelector('.background-preview > label');
                label.classList.add('d-none');
                img.classList.remove('d-none');
            }
        }
        reader.readAsDataURL(event.target.files[0]);
    }
}


const TOOLBAR_ITEMS = [
    "bold", "italic", "heading", "|", 
    "quote", "ordered-list", "unordered-list", "|",
    "link", "upload-image", "|",  
    "preview", "side-by-side", "fullscreen", "|",
    "guide"
]


window.onload = function() {
    let poster = document.getElementById('poster');
    if (poster) {
        poster.onchange = imagePreviewHandler;
    }
    
    if (document.getElementById('description')) {
        let easyMDE = new EasyMDE({
            element: document.getElementById('description'),
            toolbar: TOOLBAR_ITEMS,
            uploadImage: true,
            imageUploadEndpoint: '/api/images/upload',
            imageUploadFunction: imageUploadFunction
        });
    }
}