export function loadTrack(trackId: string): Promise<HTMLAudioElement> {
    return new Promise((resolve, reject) => {
        const audio = new Audio(`path/to/your/audio/files/${trackId}`);
        audio.addEventListener('canplaythrough', () => resolve(audio), false);
        audio.addEventListener('error', () => reject(new Error('Error loading track')), false);
    });
}

export function playTrack(trackId: string): Promise<HTMLAudioElement> {
    return loadTrack(trackId).then(audio => {
        audio.play();
        return audio;
    });
}