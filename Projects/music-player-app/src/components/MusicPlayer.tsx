import * as React from 'react';

interface Song {
  id: number;
  title: string;
  artist: string;
  duration: string;
}

interface MusicPlayerProps {
  songs: Song[];
}

export const MusicPlayer: React.FC<MusicPlayerProps> = ({ songs }) => {
  const [currentSong, setCurrentSong] = React.useState<Song>(songs[0]);
  const [isPlaying, setIsPlaying] = React.useState(false);
  const [progress, setProgress] = React.useState(0);
  const [volume, setVolume] = React.useState(80);

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  const handleProgress = (event: React.ChangeEvent<HTMLInputElement>) => {
    setProgress(parseInt(event.target.value));
  };

  const handleVolume = (event: React.ChangeEvent<HTMLInputElement>) => {
    setVolume(parseInt(event.target.value));
  };

  return (
    <div className="music-player">
      <h1>Music Player</h1>
      <div className="player-container">
        <div className="song-info">
          <h2>{currentSong.title}</h2>
          <p>{currentSong.artist}</p>
        </div>
        <div className="controls">
          <button onClick={togglePlay}>
            {isPlaying ? 'Pause' : 'Play'}
          </button>
          <div className="progress-container">
            <input
              type="range"
              min="0"
              max="100"
              value={progress}
              onChange={handleProgress}
            />
          </div>
          <div className="volume-container">
            <label>Volume: {volume}%</label>
            <input
              type="range"
              min="0"
              max="100"
              value={volume}
              onChange={handleVolume}
            />
          </div>
        </div>
      </div>
    </div>
  );
};