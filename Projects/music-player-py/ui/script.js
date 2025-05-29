// ui/script.js
document.addEventListener('DOMContentLoaded', () => {
    const playlistElement = document.getElementById('playlist');
    const playPauseBtn = document.getElementById('play-pause-btn');
    const stopBtn = document.getElementById('stop-btn');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const volumeSlider = document.getElementById('volume-slider');
    const progressBar = document.getElementById('progress-bar');
    const currentTimeDisplay = document.getElementById('current-time');
    const totalTimeDisplay = document.getElementById('total-time');
    
    const currentAlbumArt = document.getElementById('current-album-art');
    const currentTitle = document.getElementById('current-title');
    const currentArtist = document.getElementById('current-artist');
    const currentAlbum = document.getElementById('current-album');

    const loadFilesBtn = document.getElementById('load-files-btn');
    const loadFolderBtn = document.getElementById('load-folder-btn');
    const sortPlaylistSelect = document.getElementById('sort-playlist');

    const lyricsPanel = document.getElementById('lyrics-panel');
    const toggleLyricsBtn = document.getElementById('toggle-lyrics-btn');

    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingMessage = document.getElementById('loading-message');

    let playlist = [];
    let currentSort = 'added';
    let isSeeking = false; // Flag to prevent progress updates while user is seeking

    // --- UTILITY FUNCTIONS ---
    function formatTime(seconds) {
        if (isNaN(seconds)) return "0:00";
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
    }

    function showLoading(message = "Loading...") {
        loadingMessage.textContent = message;
        loadingOverlay.style.display = 'flex';
    }

    function hideLoading() {
        loadingOverlay.style.display = 'none';
    }

    // --- PLAYLIST HANDLING ---
    function renderPlaylist() {
        playlistElement.innerHTML = ''; // Clear existing list
        const sortedPlaylist = sortPlaylist(playlist, currentSort);

        sortedPlaylist.forEach((song, index) => {
            const li = document.createElement('li');
            li.dataset.index = song.originalIndex; // Use original index for playback
            
            const thumbnail = document.createElement('img');
            thumbnail.src = song.thumbnail || 'placeholder.png';
            thumbnail.alt = 'Thumb';
            thumbnail.className = 'track-thumbnail';
            li.appendChild(thumbnail);

            const trackInfo = document.createElement('div');
            trackInfo.className = 'track-info';
            
            const title = document.createElement('span');
            title.className = 'track-title';
            title.textContent = song.title || 'Unknown Title';
            trackInfo.appendChild(title);

            const artistAlbum = document.createElement('span');
            artistAlbum.className = 'track-artist-album';
            artistAlbum.textContent = `${song.artist || 'Unknown Artist'} - ${song.album || 'Unknown Album'}`;
            trackInfo.appendChild(artistAlbum);
            
            li.appendChild(trackInfo);

            const duration = document.createElement('span');
            duration.className = 'track-duration';
            duration.textContent = formatTime(song.duration);
            li.appendChild(duration);
            
            if (song.isPlaying) {
                li.classList.add('playing');
            }

            li.addEventListener('dblclick', () => {
                webui.call('play_song_by_index', parseInt(li.dataset.index));
            });
            playlistElement.appendChild(li);
        });
    }

    function sortPlaylist(list, sortBy) {
        const sorted = [...list]; // Create a copy to sort
        sorted.sort((a, b) => {
            let valA = a[sortBy];
            let valB = b[sortBy];

            if (sortBy === 'added') return a.originalIndex - b.originalIndex; // Special case for added order
            if (typeof valA === 'string') valA = valA.toLowerCase();
            if (typeof valB === 'string') valB = valB.toLowerCase();
            
            if (valA === undefined || valA === null) valA = sortBy === 'year' || sortBy === 'duration' ? 0 : '';
            if (valB === undefined || valB === null) valB = sortBy === 'year' || sortBy === 'duration' ? 0 : '';

            if (valA < valB) return -1;
            if (valA > valB) return 1;
            return 0;
        });
        return sorted;
    }

    sortPlaylistSelect.addEventListener('change', (e) => {
        currentSort = e.target.value;
        renderPlaylist();
    });

    // --- UI UPDATES FROM PYTHON ---
    window.update_playlist = function(newPlaylist) {
        console.log("JS: Received playlist update", newPlaylist);
        // Store original index for stable playback control after sorting
        playlist = newPlaylist.map((song, index) => ({ ...song, originalIndex: index }));
        renderPlaylist();
        hideLoading();
    }

    window.update_current_song_info = function(song) {
        console.log("JS: Received current song info", song);
        if (song) {
            currentTitle.textContent = song.title || 'Unknown Title';
            currentArtist.textContent = song.artist || 'Unknown Artist';
            currentAlbum.textContent = song.album || 'Unknown Album';
            currentAlbumArt.src = song.album_art_data || 'placeholder.png';
            totalTimeDisplay.textContent = formatTime(song.duration);
            progressBar.max = song.duration || 100;
            
            // Highlight in playlist
            playlist.forEach(p => p.isPlaying = false);
            const current = playlist.find(p => p.path === song.path);
            if (current) current.isPlaying = true;
            renderPlaylist(); // Re-render to show playing status

            // Request lyrics
            webui.call('get_lyrics_for_current_song');
        } else {
            currentTitle.textContent = 'No Song Loaded';
            currentArtist.textContent = 'Artist';
            currentAlbum.textContent = 'Album';
            currentAlbumArt.src = 'placeholder.png';
            totalTimeDisplay.textContent = formatTime(0);
            progressBar.value = 0;
            progressBar.max = 100;
            currentTimeDisplay.textContent = formatTime(0);
            lyricsPanel.innerHTML = '<p>Lyrics will appear here...</p>';
        }
    }

    window.update_playback_state = function(isPlaying, isPaused) {
        console.log("JS: Playback state:", isPlaying, isPaused);
        if (isPlaying && !isPaused) {
            playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
        } else {
            playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
        }
    }

    window.update_progress = function(position, duration) {
        if (!isSeeking) { // Only update if user is not actively dragging slider
            currentTimeDisplay.textContent = formatTime(position);
            totalTimeDisplay.textContent = formatTime(duration); // Ensure duration is up-to-date
            progressBar.value = position;
            progressBar.max = duration; // Ensure max is correct
        }
    }
    
    window.update_volume = function(volume) {
        volumeSlider.value = volume * 100;
    }

    window.display_lyrics = function(lyricsText) {
        console.log("JS: Displaying lyrics");
        if (lyricsText) {
            lyricsPanel.textContent = lyricsText;
        } else {
            lyricsPanel.innerHTML = '<p>No lyrics found for this song.</p>';
        }
    }

    window.show_loading_feedback = function(message, progress) {
        let fullMessage = message;
        if (progress !== undefined && progress !== null) {
            fullMessage += ` (${Math.round(progress * 100)}%)`;
        }
        showLoading(fullMessage);
    }
    window.hide_loading_feedback = hideLoading;


    // --- CONTROLS ---
    playPauseBtn.addEventListener('click', () => webui.call('toggle_play_pause'));
    stopBtn.addEventListener('click', () => webui.call('stop_music'));
    nextBtn.addEventListener('click', () => webui.call('next_song'));
    prevBtn.addEventListener('click', () => webui.call('prev_song'));

    volumeSlider.addEventListener('input', (e) => {
        webui.call('set_volume', parseFloat(e.target.value) / 100);
    });

    progressBar.addEventListener('mousedown', () => {
        isSeeking = true; // User starts dragging
    });
    progressBar.addEventListener('input', (e) => { // 'input' for live update while dragging
        if(isSeeking) { // Only update current time display if seeking, Python handles actual seek on 'change'
            currentTimeDisplay.textContent = formatTime(parseFloat(e.target.value));
        }
    });
    progressBar.addEventListener('change', (e) => { // 'change' fires when dragging stops
        isSeeking = false;
        webui.call('seek_music', parseFloat(e.target.value));
    });


    loadFilesBtn.addEventListener('click', () => {
        showLoading("Select audio files...");
        webui.call('load_files').then(hideLoading).catch(hideLoading);
    });
    loadFolderBtn.addEventListener('click', () => {
        showLoading("Select a folder...");
        webui.call('load_folder').then(hideLoading).catch(hideLoading);
    });

    toggleLyricsBtn.addEventListener('click', () => {
        lyricsPanel.classList.toggle('hidden');
        // Optional: Adjust layout if needed
        // For example, if lyrics panel takes space from right-panel's main content
        // You might need to resize elements or let flexbox handle it.
    });

    // Initial setup
    webui.call('get_initial_data'); // Ask for playlist and volume on load
    // Ensure lyrics panel is hidden by default if it's set up that way in CSS
    if (lyricsPanel.classList.contains('hidden')) {
        // It's already hidden, fine
    } else {
        // lyricsPanel.classList.add('hidden'); // Or ensure CSS handles it.
    }
});