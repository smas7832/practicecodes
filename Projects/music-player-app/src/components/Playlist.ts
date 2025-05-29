class Track {
    constructor(public id: string, public title: string, public artist: string) {}
}

export class Playlist {
    private tracks: Track[] = [];

    addTrack(track: Track) {
        this.tracks.push(track);
    }

    removeTrack(trackId: string) {
        this.tracks = this.tracks.filter(track => track.id !== trackId);
    }

    getTracks() {
        return this.tracks;
    }
}