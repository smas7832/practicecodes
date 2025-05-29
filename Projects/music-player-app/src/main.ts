import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { MusicPlayer } from './components/MusicPlayer';

const songs: Song[] = [
  { id: 1, title: 'Song 1', artist: 'Artist 1', duration: '3:45' },
  { id: 2, title: 'Song 2', artist: 'Artist 2', duration: '4:20' },
];

ReactDOM.render(
  <React.StrictMode>
    <MusicPlayer songs={songs} />
  </React.StrictMode>,
  document.getElementById('root')
);
