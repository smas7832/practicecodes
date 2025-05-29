// tagEditor.js

const TagEditor = (() => {
    let modalElement, closeButton, formElement, editTrackIndexInput;
    let titleInput, artistInput, albumInput, yearInput, lyricsInput;
    let onSaveChangesCallback = null;

    function _populateForm(trackData, trackIndexInAllTracks) {
        editTrackIndexInput.value = trackIndexInAllTracks;
        titleInput.value = trackData.title || '';
        artistInput.value = trackData.artist || '';
        albumInput.value = trackData.album || '';
        yearInput.value = trackData.year || '';
        
        let lyricsText = '';
        if (trackData.lyrics) {
            if (typeof trackData.lyrics === 'string') {
                lyricsText = trackData.lyrics;
            } else if (typeof trackData.lyrics === 'object' && (trackData.lyrics.lyrics || trackData.lyrics.text)) {
                lyricsText = trackData.lyrics.lyrics || trackData.lyrics.text;
            }
        }
        lyricsInput.value = lyricsText;
    }

    async function _handleFormSubmit(event) {
        event.preventDefault();
        const trackIndex = parseInt(editTrackIndexInput.value);
        if (isNaN(trackIndex)) {
            console.error("Tag Editor: Invalid track index."); return;
        }
        const updatedTags = {
            title: titleInput.value.trim(),
            artist: artistInput.value.trim(),
            album: albumInput.value.trim(),
            year: yearInput.value.trim(),
            lyrics: lyricsInput.value.trim(), // Stored as plain string
        };
        if (onSaveChangesCallback) {
            // Pass null for newFileObject as client-side file writing is out of scope for this example
            onSaveChangesCallback(trackIndex, updatedTags, null); 
        }
        hide();
    }

    function init(saveCallback) {
        modalElement = document.getElementById('tagEditorModal');
        closeButton = document.getElementById('closeTagEditorBtn');
        formElement = document.getElementById('tagEditorForm');
        editTrackIndexInput = document.getElementById('editTrackIndex');
        titleInput = document.getElementById('editTitle');
        artistInput = document.getElementById('editArtist');
        albumInput = document.getElementById('editAlbum');
        yearInput = document.getElementById('editYear');
        lyricsInput = document.getElementById('editLyrics');

        if (!modalElement || !formElement || !closeButton || !titleInput) {
            console.error("Tag Editor: Critical modal elements not found in DOM. Ensure modal HTML is correct.");
            return false;
        }
        onSaveChangesCallback = saveCallback;
        closeButton.addEventListener('click', hide);
        modalElement.addEventListener('click', (e) => { if (e.target === modalElement) hide(); });
        formElement.addEventListener('submit', _handleFormSubmit);
        console.log("TagEditor initialized with DOM elements.");
        return true;
    }

    function show(trackData, trackIndexInAllTracks) {
        if (!modalElement) { console.error("Tag Editor not initialized."); return; }
        _populateForm(trackData, trackIndexInAllTracks);
        modalElement.classList.add('visible');
        titleInput.focus();
    }

    function hide() {
        if (modalElement) {
            modalElement.classList.remove('visible');
            if(formElement) formElement.reset();
        }
    }
    return { init, show, hide };
})();