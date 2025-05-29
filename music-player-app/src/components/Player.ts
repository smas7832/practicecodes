class Player {
    private audio: HTMLAudioElement;
    private volume: number;

    constructor() {
        this.audio = new Audio();
        this.volume = 1; // Default volume is 100%
        this.audio.volume = this.volume;
    }

    play(trackUrl: string) {
        this.audio.src = trackUrl;
        this.audio.play();
    }

    pause() {
        this.audio.pause();
    }

    stop() {
        this.audio.pause();
        this.audio.currentTime = 0;
    }

    setVolume(volume: number) {
        this.volume = Math.min(Math.max(volume, 0), 1); // Clamp volume between 0 and 1
        this.audio.volume = this.volume;
    }
}

export default Player;