document.addEventListener('DOMContentLoaded', async () => {
    const audioPlayer = document.getElementById('audioPlayer');
    const fileInput = document.getElementById('fileInput');
    const playlistTableBody = document.querySelector('#playlist tbody');
    const playPauseBtn = document.getElementById('playPauseBtn');
    const stopBtn = document.getElementById('stopBtn');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const volumeSlider = document.getElementById('volumeSlider');
    const progressBar = document.getElementById('progressBar');
    const currentTimeDisplay = document.getElementById('currentTime');
    const totalDurationDisplay = document.getElementById('totalDuration');
    const currentAlbumArt = document.getElementById('currentAlbumArt');
    const currentTitle = document.getElementById('currentTitle');
    const currentArtist = document.getElementById('currentArtist');
    const currentAlbum = document.getElementById('currentAlbum');
    const currentYear = document.getElementById('currentYear');
    const sortPlaylistSelect = document.getElementById('sortPlaylist');
    const lyricsPanel = document.getElementById('lyricsPanel');
    const lyricsContent = document.getElementById('lyricsContent');
    const lyricsSourceIndicator = document.getElementById('lyricsSourceIndicator');
    const toggleLyricsBtn = document.getElementById('toggleLyricsPanel');
    const lyricsModeToggleBtn = document.getElementById('lyricsModeToggleBtn');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingStatus = document.getElementById('loadingStatus');
    const loadMusicBtn = document.getElementById('loadMusicBtn');
    const clearPersistedFolderBtn = document.getElementById('clearPersistedFolderBtn');
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');

    const DB_NAME = 'WebMusicPlayerDB';
    const DB_VERSION = 1;
    const STORE_HANDLES = 'persistedFolderHandles';
    const STORE_TRACKS = 'persistedTracks';
    let db;

    async function openDB() {
        return new Promise((resolve, reject) => {
            if (db) { resolve(db); return; }
            const request = indexedDB.open(DB_NAME, DB_VERSION);
            request.onerror = (event) => reject("DB Error: " + event.target.errorCode);
            request.onsuccess = (event) => { db = event.target.result; resolve(db); };
            request.onupgradeneeded = (event) => {
                const storeDb = event.target.result;
                if (!storeDb.objectStoreNames.contains(STORE_HANDLES)) storeDb.createObjectStore(STORE_HANDLES, { keyPath: 'id' });
                if (!storeDb.objectStoreNames.contains(STORE_TRACKS)) {
                    const trackStore = storeDb.createObjectStore(STORE_TRACKS, { keyPath: 'relativePath' });
                    trackStore.createIndex('title', 'title', { unique: false });
                }
            };
        });
    }
    async function saveDirectoryHandle(id, handle) { 
        if (!db) await openDB();
        return new Promise((resolve, reject) => {
            const transaction = db.transaction([STORE_HANDLES], 'readwrite');
            const request = transaction.objectStore(STORE_HANDLES).put({ id, handle });
            request.onsuccess = () => resolve();
            request.onerror = (event) => reject("Save Handle Error: " + event.target.error);
        });
    }
    async function getDirectoryHandle(id) { 
        if (!db) await openDB();
        return new Promise((resolve, reject) => {
            const request = db.transaction([STORE_HANDLES], 'readonly').objectStore(STORE_HANDLES).get(id);
            request.onsuccess = (e) => resolve(e.target.result ? e.target.result.handle : null);
            request.onerror = (e) => reject("Get Handle Error: " + e.target.error);
        });
    }
    async function clearDirectoryHandle(id) {
        if (!db) await openDB();
        return new Promise((resolve, reject) => {
            const transaction = db.transaction([STORE_HANDLES, STORE_TRACKS], 'readwrite');
            transaction.objectStore(STORE_HANDLES).delete(id);
            transaction.objectStore(STORE_TRACKS).clear(); 
            transaction.oncomplete = () => resolve();
            transaction.onerror = (event) => reject("Clear Error: " + event.target.error);
        });
    }
    async function saveTrackMetadata(trackData) {
        if (!db) await openDB();
        return new Promise((resolve, reject) => {
            const request = db.transaction([STORE_TRACKS], 'readwrite').objectStore(STORE_TRACKS).put(trackData);
            request.onsuccess = () => resolve();
            request.onerror = (e) => reject("Save Track Error: " + e.target.error);
        });
    }
    async function getAllPersistedTracksMetadata() {
        if (!db) await openDB();
        return new Promise((resolve, reject) => {
            const request = db.transaction([STORE_TRACKS], 'readonly').objectStore(STORE_TRACKS).getAll();
            request.onsuccess = (e) => resolve(e.target.result || []);
            request.onerror = (e) => reject("Get Tracks Error: " + e.target.error);
        });
    }

    let allTracks = []; 
    let playlist = [];
    let currentTrackIndex = -1;
    let lrcFiles = {}; 
    let currentLrc = null; 
    let lyricsDisplayMode = 'synced';
    const defaultAlbumArt = 'placeholder.png';
    let persistedDirectoryHandle = null;
    const PERSISTED_FOLDER_ID = 'mainMusicFolder';
    let currentSearchTerm = '';
    let currentSortCriteria = 'added';

    async function processInBatches(items, batchSize, processItemFn, updateStatusFn) {
        for (let i = 0; i < items.length; i += batchSize) {
            const batch = items.slice(i, i + Math.min(batchSize, items.length - i));
            await Promise.all(batch.map(item => processItemFn(item))); // Ensure item is passed
            if (updateStatusFn) updateStatusFn(i + batch.length, items.length);
            await new Promise(resolve => setTimeout(resolve, 0));
        }
    }

    fileInput.addEventListener('change', (e) => handleFileSelection(e.target.files));
    if (loadMusicBtn) {
        loadMusicBtn.addEventListener('click', async () => {
            if (window.showDirectoryPicker) {
                try {
                    console.log("Attempting to load persistent folder via Load Music button...");
                    await handleLoadFolderPersistent(); 
                } catch (error) {
                    if (error.name === 'AbortError') {
                        console.log("Folder selection aborted. Falling back to file input.");
                        fileInput.value = null; fileInput.click(); 
                    } else {
                        showLoading(false); console.error("Error during Load Music (folder attempt):", error);
                        if (error.message !== "File System Access API not available.") {
                             alert("Error loading folder: " + error.message + "\nFalling back to file selection.");
                             fileInput.value = null; fileInput.click();
                        } else { // FS API truly not available
                            alert("Browser doesn't support persistent folders. Load individual files.");
                            fileInput.value = null; fileInput.click();
                        }
                    }
                }
            } else {
                console.log("FS API not available. Using standard file input.");
                alert("Browser doesn't support persistent folders. Load individual files.");
                fileInput.value = null; fileInput.click();
            }
        });
    }
    if (clearPersistedFolderBtn) {
        clearPersistedFolderBtn.addEventListener('click', async () => {
            if (!confirm("Clear persisted library?")) return;
            showLoading(true, "Clearing library...");
            try {
                await openDB(); await clearDirectoryHandle(PERSISTED_FOLDER_ID);
                persistedDirectoryHandle = null; allTracks = []; 
                currentSearchTerm = ''; searchInput.value = ''; clearSearchBtn.style.display = 'none';
                await updateAndRenderPlaylistView(); updateCurrentSongDisplay(-1);
                lyricsContent.innerHTML = '<p>Library cleared.</p>';
            } catch (error) { console.error("Error clearing library:", error); alert("Could not clear: " + error.message); }
            showLoading(false);
        });
    }
    searchInput.addEventListener('input', () => {
        currentSearchTerm = searchInput.value.trim().toLowerCase();
        clearSearchBtn.style.display = currentSearchTerm ? 'block' : 'none';
        updateAndRenderPlaylistView();
    });
    clearSearchBtn.addEventListener('click', () => {
        searchInput.value = ''; currentSearchTerm = ''; clearSearchBtn.style.display = 'none';
        updateAndRenderPlaylistView(); searchInput.focus();
    });
    sortPlaylistSelect.addEventListener('change', (e) => {
        currentSortCriteria = e.target.value; updateAndRenderPlaylistView();
    });

    async function updateAndRenderPlaylistView() {
        const previouslyPlayingFile = currentTrackIndex !== -1 && playlist[currentTrackIndex] ? playlist[currentTrackIndex].file : null;
        let processedList = [...allTracks];
        if (currentSearchTerm) {
            processedList = processedList.filter(track => 
                track.title.toLowerCase().includes(currentSearchTerm) ||
                track.artist.toLowerCase().includes(currentSearchTerm) ||
                track.album.toLowerCase().includes(currentSearchTerm)
            );
        }
        switch (currentSortCriteria) {
            case 'title': processedList.sort((a, b) => a.title.localeCompare(b.title)); break;
            case 'artist': processedList.sort((a, b) => a.artist.localeCompare(b.artist)); break;
            case 'album': processedList.sort((a, b) => a.album.localeCompare(b.album)); break;
            case 'year': processedList.sort((a, b) => (a.year || '0').localeCompare(b.year || '0')); break;
            case 'duration': processedList.sort((a, b) => (a.duration || 0) - (b.duration || 0)); break;
            case 'added': default: 
                processedList.sort((a,b) => (allTracks.findIndex(t => t.file === a.file)) - (allTracks.findIndex(t => t.file === b.file)));
                break;
        }
        playlist = processedList;
        if (previouslyPlayingFile) {
            const newIndexOfPlayingTrack = playlist.findIndex(track => track.file === previouslyPlayingFile);
            currentTrackIndex = (newIndexOfPlayingTrack !== -1) ? newIndexOfPlayingTrack : -1;
            if (currentTrackIndex === -1 && audioPlayer && !audioPlayer.paused) stopPlayback();
        } else { currentTrackIndex = -1; }
        await renderPlaylist(); 
        updatePlayingClassInPlaylist();
    }

    async function handleLoadFolderPersistent() {
        if (!window.showDirectoryPicker) throw new Error("File System Access API not available.");
        const dirHandle = await window.showDirectoryPicker(); // This line throws AbortError if cancelled

        showLoading(true, "Scanning folder...");
        persistedDirectoryHandle = dirHandle; await openDB(); await saveDirectoryHandle(PERSISTED_FOLDER_ID, dirHandle);
        const trackStoreTransaction = db.transaction([STORE_TRACKS], 'readwrite');
        await new Promise((resolve, reject) => { trackStoreTransaction.objectStore(STORE_TRACKS).clear().onsuccess = resolve; trackStoreTransaction.onerror = (e) => reject(e.target.error); });
        allTracks = []; currentSearchTerm = ''; searchInput.value = ''; clearSearchBtn.style.display = 'none'; lrcFiles = {};
        const audioFileEntries = [];
        async function collectFileEntries(currentDirHandle, currentPath = '') {
            let entryCounter = 0;
            for await (const entry of currentDirHandle.values()) {
                entryCounter++; if (entryCounter % 100 === 0) { updateLoadingStatus(`Discovering in ${currentPath||'root'}...`); await new Promise(r => setTimeout(r,0)); }
                const entryPath = currentPath ? `${currentPath}/${entry.name}` : entry.name;
                if (entry.kind === 'file' && ['.mp3','.m4a','.aac','.ogg','.wav','.flac'].some(ext => entry.name.toLowerCase().endsWith(ext))) audioFileEntries.push({ entryHandle: entry, relativePath: entryPath });
                else if (entry.kind === 'directory') await collectFileEntries(entry, entryPath);
            }
        }
        await collectFileEntries(dirHandle);
        showLoading(true, `Found ${audioFileEntries.length} files. Processing...`);
        const BATCH_SIZE_PROCESSING = 10;
        await processInBatches(audioFileEntries, BATCH_SIZE_PROCESSING,
            async (audioEntryInfo) => {
                const { entryHandle, relativePath } = audioEntryInfo;
                try {
                    const file = await entryHandle.getFile(); const metadata = await parseMetadata(file);
                    const duration = await getAudioDuration(file); const durationFormatted = formatTime(duration);
                    const trackData = { ...metadata, file, relativePath, originalIndex: allTracks.length, duration, durationFormatted };
                    allTracks.push(trackData); 
                    const { file: _, ...metadataToSave } = trackData; await saveTrackMetadata(metadataToSave);
                } catch (err) { console.warn(`Skipping ${relativePath}: ${err.message}`); }
            }, (p, t) => { showLoading(true, `Processing metadata ${p}/${t}...`); }
        );
        await updateAndRenderPlaylistView();
        if (allTracks.length > 0 && currentTrackIndex === -1) updateCurrentSongDisplay(0);
        else if (allTracks.length === 0) { updateCurrentSongDisplay(-1); lyricsContent.innerHTML = '<p>No audio files.</p>'; }
        console.log("Folder loaded."); showLoading(false);
    }

    async function loadPersistedDataOnStartup() {
        try {
            await openDB(); const dirHandle = await getDirectoryHandle(PERSISTED_FOLDER_ID); // Use non-corrected version
            if (dirHandle) {
                showLoading(true, "Verifying access...");
                if (await dirHandle.queryPermission({ mode: 'read' }) !== 'granted' && await dirHandle.requestPermission({ mode: 'read' }) !== 'granted') {
                    console.warn("Permission denied."); showLoading(false); lyricsContent.innerHTML = '<p>Permission needed. Click "Load Music".</p>'; return;
                }
                showLoading(true, "Restoring library..."); persistedDirectoryHandle = dirHandle;
                const persistedTracksMetadata = await getAllPersistedTracksMetadata();
                if (persistedTracksMetadata.length > 0) {
                    const BATCH_SIZE_RESTORING = 20; allTracks = [];
                    await processInBatches(persistedTracksMetadata, BATCH_SIZE_RESTORING,
                        async (trackMeta) => {
                            try {
                                let currentHandle = persistedDirectoryHandle; const pathParts = trackMeta.relativePath.split('/');
                                const fileName = pathParts.pop();
                                for (const part of pathParts) currentHandle = await currentHandle.getDirectoryHandle(part, { create: false });
                                const fileHandle = await currentHandle.getFileHandle(fileName, { create: false });
                                const file = await fileHandle.getFile();
                                allTracks.push({ ...trackMeta, file, originalIndex: allTracks.length });
                            } catch (err) { console.warn(`Could not restore ${trackMeta.relativePath}: ${err.message}.`); }
                        }, (p, t) => { showLoading(true, `Restoring files ${p}/${t}...`); }
                    );
                    await updateAndRenderPlaylistView();
                    if (allTracks.length > 0 && currentTrackIndex === -1) updateCurrentSongDisplay(0);
                    else if (allTracks.length === 0) updateCurrentSongDisplay(-1);
                    console.log("Persisted library restored.");
                } else { lyricsContent.innerHTML = '<p>No tracks in persisted library.</p>'; }
            } else { console.log("No persisted folder."); updateCurrentSongDisplay(-1); }
        } catch (error) { console.error("Error loading persisted data:", error); lyricsContent.innerHTML = '<p>Could not load library: ' + error.message + '</p>'; }
        finally { showLoading(false); }
    }

    async function handleFileSelection(files) {
        showLoading(true, "Adding files...");
        const allSelectedFiles = Array.from(files); const newLrcFilesTemp = {}; const audioFileObjects = [];
        for (const file of allSelectedFiles) {
            if (file.name.toLowerCase().endsWith('.lrc')) newLrcFilesTemp[file.name.substring(0, file.name.lastIndexOf('.')).toLowerCase()] = file;
            else if (file.type.startsWith('audio/')) audioFileObjects.push(file);
        }
        lrcFiles = {...lrcFiles, ...newLrcFilesTemp}; 
        const BATCH_SIZE_ADHOC = 10; const newAudioTracksTemp = [];
        await processInBatches(audioFileObjects, BATCH_SIZE_ADHOC,
            async (file) => {
                try {
                    const metadata = await parseMetadata(file);
                    newAudioTracksTemp.push({ ...metadata, file, originalIndex: allTracks.length + newAudioTracksTemp.length, duration: 0, durationFormatted: "0:00" });
                } catch (error) { 
                    console.warn(`Metadata error for ${file.name}:`, error); 
                    newAudioTracksTemp.push({ title: file.name.replace(/\.[^/.]+$/, ""), artist:'Unknown', album:'Unknown', year:'N/A', lyrics:null, thumbnail:defaultAlbumArt, file, originalIndex: allTracks.length + newAudioTracksTemp.length, duration:0, durationFormatted:"0:00"});
                }
            }, (p, t) => { showLoading(true, `Processing files ${p}/${t}...`); }
        );
        const previousAllTracksLength = allTracks.length; allTracks = [...allTracks, ...newAudioTracksTemp];
        await updateAndRenderPlaylistView();
        if (newAudioTracksTemp.length > 0 && (currentTrackIndex === -1 || previousAllTracksLength === 0)) {
            const firstNew = newAudioTracksTemp[0].file; const idx = playlist.findIndex(t => t.file === firstNew); if (idx !== -1) playTrack(idx); 
        } else if (newAudioTracksTemp.length > 0 && currentTrackIndex === -1) {
            const firstNew = newAudioTracksTemp[0].file; const idx = playlist.findIndex(t => t.file === firstNew); if (idx !== -1) updateCurrentSongDisplay(idx);
        }
        showLoading(false);
    }

    async function parseMetadata(file) {
        return new Promise((resolve, reject) => {
            jsmediatags.read(file, {
                onSuccess: (tag) => {
                    const d = tag.tags; let thumb = defaultAlbumArt;
                    if (d.picture) { let s=""; for(let i=0;i<d.picture.data.length;i++)s+=String.fromCharCode(d.picture.data[i]); thumb=`data:${d.picture.format};base64,${btoa(s)}`; }
                    let lRaw=d.lyrics||(d.USLT&&d.USLT.length>0?d.USLT[0]:null)||(d.TXXX&&Array.isArray(d.TXXX)?d.TXXX.find(t=>t.description&&t.description.toUpperCase()==="LYRICS"):null);
                    let lTxt=null; if(lRaw){if(typeof lRaw==='string')lTxt=lRaw;else if(typeof lRaw==='object')lTxt=lRaw.text||lRaw.lyrics||(typeof lRaw.data==='string'?lRaw.data:null);}
                    resolve({title:d.title||file.name.replace(/\.[^/.]+$/, ""),artist:d.artist||'Unknown Artist',album:d.album||'Unknown Album',year:d.year||'N/A',lyrics:lTxt,thumbnail:thumb,duration:0,durationFormatted:"0:00"});
                }, onError: (e) => { console.error(`Metadata error for ${file.name}: ${e.type} - ${e.info}`,e); resolve({title:file.name.replace(/\.[^/.]+$/, ""),artist:'Unknown Artist',album:'Unknown Album',year:'N/A',lyrics:null,thumbnail:defaultAlbumArt,duration:0,durationFormatted:"0:00"}); /* Resolve with defaults on error */ }
            });
        });
    }
    async function getAudioDuration(file) {
        return new Promise(r => { let a=document.createElement('audio');a.preload='metadata';a.onloadedmetadata=()=>{URL.revokeObjectURL(a.src);r(a.duration)};a.onerror=()=>{URL.revokeObjectURL(a.src);r(0)};a.src=URL.createObjectURL(file)});
    }

    async function renderPlaylist() {
        showLoading(true, "Rendering playlist..."); const oldScroll = playlistTableBody.parentElement.scrollTop; playlistTableBody.innerHTML = '';
        const BATCH_RENDER = 50; let frag = document.createDocumentFragment();
        for (let i=0; i<playlist.length; i++) {
            const track = playlist[i];
            if((track.duration === undefined || track.duration === 0) && track.file){ // Check undefined too
                try{track.duration=await getAudioDuration(track.file);track.durationFormatted=formatTime(track.duration)}
                catch(e){console.warn("Duration error for", track.title); track.duration=0;track.durationFormatted="0:00"}
            } else if((track.durationFormatted === undefined || track.durationFormatted === "0:00") && track.duration){ // Check undefined
                track.durationFormatted=formatTime(track.duration);
            }
            const row = document.createElement('tr'); row.dataset.index = i;
            const originalIdx = allTracks.findIndex(t => t.file === track.file); // Use file for robust original index
            row.innerHTML = `<td>${i+1}</td><td><img src="${track.thumbnail||defaultAlbumArt}" alt="art" class="playlist-thumb"></td><td>${track.title}</td><td>${track.artist}</td><td>${track.album}</td><td>${track.durationFormatted||'0:00'}<button class="edit-track-btn" data-track-alltracks-index="${originalIdx}" title="Edit Tags"><i class="fas fa-edit"></i></button></td>`;
            row.querySelectorAll('td:not(:last-child)').forEach(td => td.addEventListener('dblclick', () => playTrack(i)));
            const editBtn = row.querySelector('.edit-track-btn');
            if(editBtn) editBtn.addEventListener('click', (e)=>{e.stopPropagation();const idxToEdit=parseInt(e.currentTarget.dataset.trackAlltracksIndex);if(!isNaN(idxToEdit)&&allTracks[idxToEdit])TagEditor.show(allTracks[idxToEdit],idxToEdit); else console.error("Cannot edit, track not found in allTracks. Index:", idxToEdit)});
            frag.appendChild(row);
            if((i+1)%BATCH_RENDER===0||i===playlist.length-1){playlistTableBody.appendChild(frag);frag=document.createDocumentFragment();updateLoadingStatus(`Rendering ${i+1}/${playlist.length}`);await new Promise(rA=>requestAnimationFrame(rA));}
        }
        playlistTableBody.parentElement.scrollTop = oldScroll; showLoading(false); updatePlayingClassInPlaylist();
    }
    
    playPauseBtn.addEventListener('click', togglePlayPause); stopBtn.addEventListener('click', stopPlayback);
    nextBtn.addEventListener('click', playNext); prevBtn.addEventListener('click', playPrevious);
    volumeSlider.addEventListener('input',(e)=>audioPlayer.volume=e.target.value);
    progressBar.addEventListener('input',(e)=>{if(audioPlayer.duration)audioPlayer.currentTime=(e.target.value/100)*audioPlayer.duration});
    audioPlayer.addEventListener('loadedmetadata',()=>{totalDurationDisplay.textContent=formatTime(audioPlayer.duration);progressBar.max=100;if(currentTrackIndex!==-1&&playlist[currentTrackIndex]&&(!playlist[currentTrackIndex].duration||playlist[currentTrackIndex].duration===0)){playlist[currentTrackIndex].duration=audioPlayer.duration;playlist[currentTrackIndex].durationFormatted=formatTime(audioPlayer.duration);const r=playlistTableBody.querySelector(`tr[data-index="${currentTrackIndex}"]`);if(r&&r.cells[5])r.cells[5].getElementsByTagName('span')[0].textContent = playlist[currentTrackIndex].durationFormatted;}}); // Updated to target span if duration is separate
    audioPlayer.addEventListener('timeupdate',()=>{if(audioPlayer.duration){progressBar.value=(audioPlayer.currentTime/audioPlayer.duration)*100;currentTimeDisplay.textContent=formatTime(audioPlayer.currentTime);if(currentLrc&&lyricsDisplayMode==='synced')updateActiveLyricLine(audioPlayer.currentTime)}});
    audioPlayer.addEventListener('ended',playNext); audioPlayer.addEventListener('play',()=>playPauseBtn.innerHTML='<i class="fas fa-pause"></i>'); audioPlayer.addEventListener('pause',()=>playPauseBtn.innerHTML='<i class="fas fa-play"></i>');

    function playTrack(idx){if(idx<0||idx>=playlist.length||!playlist[idx]||!playlist[idx].file)return;currentTrackIndex=idx;const t=playlist[currentTrackIndex];if(audioPlayer.src&&audioPlayer.src.startsWith('blob:'))URL.revokeObjectURL(audioPlayer.src);audioPlayer.src=URL.createObjectURL(t.file);audioPlayer.play().catch(e=>console.error("Play error:",t.title,e));updateCurrentSongDisplay(idx);updatePlayingClassInPlaylist();loadLyricsForCurrentTrack()}
    function togglePlayPause(){if(playlist.length===0)return;if(currentTrackIndex===-1&&playlist.length>0)playTrack(0);else if(audioPlayer.paused||audioPlayer.ended)audioPlayer.play().catch(e=>console.error("Play error:",e));else audioPlayer.pause()}
    function stopPlayback(){audioPlayer.pause();audioPlayer.currentTime=0}
    function playNext(){if(playlist.length===0)return;playTrack((currentTrackIndex+1)%playlist.length)}
    function playPrevious(){if(playlist.length===0)return;playTrack((currentTrackIndex-1+playlist.length)%playlist.length)}

    function updateCurrentSongDisplay(idx){if(idx<0||idx>=playlist.length||!playlist[idx]){currentAlbumArt.src=defaultAlbumArt;currentTitle.textContent='No Song';currentArtist.textContent='---';currentAlbum.textContent='---';currentYear.textContent='---';document.title="Player";currentAlbumArt.classList.remove('art-pulsing');return}const t=playlist[idx];if(currentAlbumArt.src!==(t.thumbnail||defaultAlbumArt)){currentAlbumArt.classList.remove('art-pulsing');void currentAlbumArt.offsetWidth;currentAlbumArt.classList.add('art-pulsing');currentAlbumArt.addEventListener('animationend',()=>currentAlbumArt.classList.remove('art-pulsing'),{once:true})}currentAlbumArt.src=t.thumbnail||defaultAlbumArt;currentTitle.textContent=t.title;currentArtist.textContent=t.artist;currentAlbum.textContent=t.album;currentYear.textContent=t.year!=='N/A'?t.year:'---';document.title=`${t.title} - ${t.artist}`}
    function updatePlayingClassInPlaylist(){playlistTableBody.querySelectorAll('tr').forEach(r=>{r.classList.remove('playing');if(parseInt(r.dataset.index)===currentTrackIndex)r.classList.add('playing')})}
    function formatTime(s){if(isNaN(s)||s<0)return"0:00";const m=Math.floor(s/60),c=Math.floor(s%60);return`${m}:${c<10?'0':''}${c}`}

    toggleLyricsBtn.addEventListener('click',()=>{lyricsPanel.classList.toggle('visible');if(lyricsPanel.classList.contains('visible')&¤tLrc&&audioPlayer.currentTime>0&&lyricsDisplayMode==='synced')updateActiveLyricLine(audioPlayer.currentTime,true)});
    lyricsModeToggleBtn.addEventListener('click',()=>{lyricsDisplayMode=lyricsDisplayMode==='synced'?'plain':'synced';updateLyricsModeButton();if(currentTrackIndex!==-1)loadLyricsForCurrentTrack()});
    function updateLyricsModeButton(){if(lyricsDisplayMode==='synced'){lyricsModeToggleBtn.innerHTML='<i class="fas fa-stream"></i> Synced';lyricsModeToggleBtn.title="To Plain"}else{lyricsModeToggleBtn.innerHTML='<i class="fas fa-paragraph"></i> Plain';lyricsModeToggleBtn.title="To Synced"}}

    async function handleTagChanges(trackIndexInAllTracks, updatedTags, newFileObject) {
        console.log("Saving tags for allTracks index:", trackIndexInAllTracks, updatedTags);
        if (trackIndexInAllTracks < 0 || trackIndexInAllTracks >= allTracks.length) return;
        const trackToUpdate = allTracks[trackIndexInAllTracks];
        Object.assign(trackToUpdate, updatedTags);
        if (newFileObject) trackToUpdate.file = newFileObject; 
        if (trackToUpdate.relativePath && persistedDirectoryHandle) {
            try { const { file: _, ...metadataToSave } = trackToUpdate; await saveTrackMetadata(metadataToSave); console.log("Persisted metadata updated."); }
            catch (dbError) { console.error("Error updating persisted metadata:", dbError); }
        }
        await updateAndRenderPlaylistView();
        if (currentTrackIndex !== -1 && playlist[currentTrackIndex] && playlist[currentTrackIndex].file === trackToUpdate.file) {
            updateCurrentSongDisplay(currentTrackIndex);
            if (updatedTags.lyrics !== undefined) loadLyricsForCurrentTrack();
        }
    }
    
    async function loadLyricsForCurrentTrack() {
        currentLrc=null;lyricsContent.innerHTML='<p>Loading...</p>';lyricsContent.classList.remove('plain-text-mode');lyricsSourceIndicator.textContent='';
        if(currentTrackIndex===-1||!playlist[currentTrackIndex]){lyricsContent.innerHTML='<p>No song.</p>';return}
        const t=playlist[currentTrackIndex];let lrcTxt=null,srcType="",plainFb=null;
        const baseName=t.file?t.file.name.substring(0,t.file.name.lastIndexOf('.')).toLowerCase():t.title.toLowerCase();
        if(lrcFiles[baseName]){const f=lrcFiles[baseName];try{const x=await f.text();if(x&&/\[\d{2}:\d{2}(?:\.\d{1,3})?\]/.test(x)){lrcTxt=x;srcType="(Loaded)"}else if(x){plainFb=x;srcType="(Loaded Plain)"}}catch(e){console.error("LRC load error:",e)}}
        if(!lrcTxt&&persistedDirectoryHandle&&t.relativePath){const lrcPath=t.relativePath.substring(0,t.relativePath.lastIndexOf('.'))+'.lrc';try{let cH=persistedDirectoryHandle;const pP=lrcPath.split('/');const lFN=pP.pop();for(const p of pP)cH=await cH.getDirectoryHandle(p,{create:false});const lFH=await cH.getFileHandle(lFN,{create:false});const lFO=await lFH.getFile();const x=await lFO.text();if(x&&/\[\d{2}:\d{2}(?:\.\d{1,3})?\]/.test(x)){lrcTxt=x;srcType="(Folder)"}else if(x){if(!plainFb)plainFb=x;srcType=srcType||"(Folder Plain)"}}catch(e){/* Suppress if path part not found */}}
        if(!lrcTxt&&t.lyrics){const embed=t.lyrics;if(embed){if(/\[\d{2}:\d{2}(?:\.\d{1,3})?\]/.test(embed)){lrcTxt=embed;srcType="(Embedded)"}else{if(!plainFb)plainFb=embed;srcType=srcType||"(Embedded Plain)"}}}
        if(lrcTxt){const pL=parseLRC(lrcTxt);if(pL&&pL.length>0){if(lyricsDisplayMode==='synced'){currentLrc=pL;renderLRCSynced(currentLrc);lyricsSourceIndicator.textContent=srcType;updateActiveLyricLine(audioPlayer.currentTime,true)}else{renderPlainLyrics(pL.map(l=>l.text).join('\n'));lyricsSourceIndicator.textContent=srcType+" (Plain)"}}else{if(plainFb){renderPlainLyrics(plainFb);lyricsSourceIndicator.textContent=srcType}else lyricsContent.innerHTML='<p>Parse error.</p>'}}
        else if(plainFb){renderPlainLyrics(plainFb);lyricsSourceIndicator.textContent=srcType}else lyricsContent.innerHTML='<p>No lyrics.</p>'
    }
    function parseLRC(txt){const d=[];const l=txt.split('\n');const r=/\[(\d{2}):(\d{2}(?:\.\d{1,3})?)\]/g;for(const i of l){let c=i,ts=[];r.lastIndex=0;let m,lME=0;while((m=r.exec(i))!==null){if(m.index===lME){ts.push(parseInt(m[1])*60+parseFloat(m[2]));lME=r.lastIndex}else break}if(ts.length>0){c=i.substring(lME).trim();for(const t of ts)d.push({time:t,text:c})}}d.sort((a,b)=>a.time-b.time);return d}
    function renderLRCSynced(d){lyricsContent.innerHTML='';lyricsContent.classList.remove('plain-text-mode');d.forEach((l,i)=>{const p=document.createElement('p');p.textContent=l.text||"♪";p.classList.add('lyric-line');p.dataset.time=l.time;p.dataset.index=i;p.addEventListener('click',()=>{const tS=parseFloat(p.dataset.time);if(!isNaN(tS)&&audioPlayer.readyState>0){audioPlayer.currentTime=tS;if(audioPlayer.paused)audioPlayer.play().catch(e=>console.error("Seek play error:",e))}});lyricsContent.appendChild(p)})}
    function renderPlainLyrics(t){lyricsContent.innerHTML='';lyricsContent.classList.add('plain-text-mode');const p=document.createElement('p');p.textContent=t;lyricsContent.appendChild(p);currentLrc=null}
    function updateActiveLyricLine(cT,fS=false){const lE=lyricsContent.querySelectorAll('.lyric-line');if(lyricsDisplayMode!=='synced'||!currentLrc||currentLrc.length===0){lE.forEach(e=>e.classList.remove('active'));return}let aLI=-1;for(let i=0;i<currentLrc.length;i++){if(cT>=currentLrc[i].time){if(i+1<currentLrc.length&&cT<currentLrc[i+1].time){aLI=i;break}else if(i+1===currentLrc.length){aLI=i;break}}else if(cT<currentLrc[i].time)break}lE.forEach(e=>e.classList.remove('active'));if(aLI!==-1&&lE[aLI]){const aE=lE[aLI];aE.classList.add('active');if(lyricsPanel.classList.contains('visible')){const pR=lyricsPanel.getBoundingClientRect(),lR=aE.getBoundingClientRect();if(fS||lR.top<pR.top||lR.bottom>pR.bottom||(Math.abs(lR.top-pR.top-(pR.height/2)+(lR.height/2))>50))aE.scrollIntoView({behavior:'smooth',block:'center'})}}}
    
    function showLoading(s,m="Loading..."){loadingStatus.textContent=m;loadingOverlay.classList.toggle('visible',s)}
    function updateLoadingStatus(m){if(loadingOverlay.classList.contains('visible'))loadingStatus.textContent=m}

    audioPlayer.volume=volumeSlider.value; updateLyricsModeButton(); lyricsPanel.classList.remove('visible'); clearSearchBtn.style.display='none';
    if (typeof TagEditor !== 'undefined' && TagEditor.init(handleTagChanges)) console.log("Tag Editor initialized.");
    else console.warn("Tag Editor failed to initialize. Check HTML for modal elements and ensure tagEditor.js is loaded before script.js.");
    await loadPersistedDataOnStartup(); 
    if (allTracks.length === 0) { await updateAndRenderPlaylistView(); updateCurrentSongDisplay(-1); }
    sortPlaylistSelect.value = currentSortCriteria;
});



