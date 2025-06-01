// music_player.c

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h> // For directory listing (POSIX)

// SDL Includes
#include <SDL3/SDL.h>
#include <SDL3/SDL_mixer.h>

#define MUSIC_DIRECTORY "./music/" // IMPORTANT: Create this directory and put music files in it!
#define MAX_SONGS 100
#define MAX_FILENAME_LEN 256

typedef struct {
    char filename[MAX_FILENAME_LEN];
    // You could add metadata here later (e.g., title, artist)
} Song;

Song playlist[MAX_SONGS];
int num_songs = 0;
Mix_Music *current_music = NULL;
int current_song_index = -1;
int is_paused = 0;

// --- Function Prototypes ---
void initialize_sdl_mixer();
void cleanup_sdl_mixer();
void load_songs_from_directory(const char *dir_path);
void display_playlist();
void play_song(int song_index);
void stop_music();
void pause_resume_music();
void next_song();
void prev_song();

// --- Main Function ---
int main(int argc, char *argv[]) {
    initialize_sdl_mixer();
    load_songs_from_directory(MUSIC_DIRECTORY);

    if (num_songs == 0) {
        printf("No music files found in '%s'. Exiting.\n", MUSIC_DIRECTORY);
        printf("Please create a 'music' subdirectory in the same location as the executable,\n");
        printf("and place some .mp3, .wav, or .ogg files in it.\n");
        cleanup_sdl_mixer();
        return 1;
    }

    int choice;
    while (1) {
        printf("\n--- C Music Player ---\n");
        if (current_song_index != -1) {
            printf("Now Playing: %s %s\n", playlist[current_song_index].filename, is_paused ? "(Paused)" : "");
        }
        display_playlist();
        printf("----------------------\n");
        printf("1. Play Song (by number)\n");
        printf("2. Stop\n");
        printf("3. Pause/Resume\n");
        printf("4. Next Song\n");
        printf("5. Previous Song\n");
        printf("0. Exit\n");
        printf("Enter your choice: ");

        if (scanf("%d", &choice) != 1) {
            // Clear invalid input
            while (getchar() != '\n');
            printf("Invalid input. Please enter a number.\n");
            continue;
        }

        switch (choice) {
            case 1: {
                int song_num;
                printf("Enter song number to play: ");
                if (scanf("%d", &song_num) != 1) {
                     while (getchar() != '\n');
                     printf("Invalid song number.\n");
                     continue;
                }
                if (song_num >= 1 && song_num <= num_songs) {
                    play_song(song_num - 1); // Adjust to 0-based index
                } else {
                    printf("Invalid song number.\n");
                }
                break;
            }
            case 2:
                stop_music();
                break;
            case 3:
                pause_resume_music();
                break;
            case 4:
                next_song();
                break;
            case 5:
                prev_song();
                break;
            case 0:
                printf("Exiting...\n");
                stop_music(); // Ensure music is stopped and freed
                cleanup_sdl_mixer();
                return 0;
            default:
                printf("Invalid choice. Try again.\n");
        }
    }

    return 0; // Should not be reached
}

// --- Function Implementations ---

void initialize_sdl_mixer() {
    if (SDL_Init(SDL_INIT_AUDIO) < 0) {
        printf("Failed to initialize SDL: %s\n", SDL_GetError());
        exit(1);
    }

    // Initialize SDL_mixer
    // Frequency, format, channels, chunksize
    if (Mix_OpenAudio(44100, MIX_DEFAULT_FORMAT, 2, 2048) < 0) {
        printf("Failed to initialize SDL_mixer: %s\n", Mix_GetError());
        SDL_Quit();
        exit(1);
    }
    // Load support for MP3, OGG, etc.
    int flags = MIX_INIT_MP3 | MIX_INIT_OGG | MIX_INIT_FLAC; // Add more if needed
    int initted = Mix_Init(flags);
    if((initted & flags) != flags) {
        printf("Mix_Init: Failed to init required ogg and mp3 support!\n");
        printf("Mix_Init: %s\n", Mix_GetError());
        // Handle error, exit, etc.
    }


    printf("SDL and SDL_mixer initialized successfully.\n");
}

void cleanup_sdl_mixer() {
    if (current_music) {
        Mix_FreeMusic(current_music);
        current_music = NULL;
    }
    Mix_CloseAudio();
    Mix_Quit(); // Uninitialize SDL_mixer subsystems
    SDL_Quit();
    printf("SDL and SDL_mixer cleaned up.\n");
}

void load_songs_from_directory(const char *dir_path) {
    DIR *d;
    struct dirent *dir;
    d = opendir(dir_path);
    if (d) {
        while ((dir = readdir(d)) != NULL && num_songs < MAX_SONGS) {
            // Check for common audio file extensions
            if (strstr(dir->d_name, ".mp3") || strstr(dir->d_name, ".wav") ||
                strstr(dir->d_name, ".ogg") || strstr(dir->d_name, ".flac")) {
                strncpy(playlist[num_songs].filename, dir->d_name, MAX_FILENAME_LEN - 1);
                playlist[num_songs].filename[MAX_FILENAME_LEN - 1] = '\0'; // Ensure null-termination
                num_songs++;
            }
        }
        closedir(d);
    } else {
        perror("Could not open music directory");
        // You might want to create the directory if it doesn't exist, or handle this more gracefully.
    }
}

void display_playlist() {
    if (num_songs == 0) {
        printf("Playlist is empty.\n");
        return;
    }
    printf("Available Songs:\n");
    for (int i = 0; i < num_songs; i++) {
        printf("%d. %s\n", i + 1, playlist[i].filename);
    }
}

void play_song(int song_index) {
    if (song_index < 0 || song_index >= num_songs) {
        printf("Invalid song index.\n");
        return;
    }

    stop_music(); // Stop current music if any and free it

    char full_path[MAX_FILENAME_LEN + strlen(MUSIC_DIRECTORY) + 1];
    snprintf(full_path, sizeof(full_path), "%s%s", MUSIC_DIRECTORY, playlist[song_index].filename);

    current_music = Mix_LoadMUS(full_path);
    if (!current_music) {
        printf("Failed to load music '%s': %s\n", full_path, Mix_GetError());
        return;
    }

    if (Mix_PlayMusic(current_music, 1) == -1) { // Play once
        printf("Failed to play music: %s\n", Mix_GetError());
        Mix_FreeMusic(current_music);
        current_music = NULL;
    } else {
        current_song_index = song_index;
        is_paused = 0;
        printf("Playing: %s\n", playlist[current_song_index].filename);
    }
}

void stop_music() {
    if (Mix_PlayingMusic()) {
        Mix_HaltMusic();
    }
    if (current_music) {
        Mix_FreeMusic(current_music);
        current_music = NULL;
    }
    current_song_index = -1;
    is_paused = 0;
    // printf("Music stopped.\n"); // Can be noisy
}

void pause_resume_music() {
    if (!Mix_PlayingMusic() && !Mix_PausedMusic()) {
        printf("No music is currently playing or paused.\n");
        return;
    }

    if (is_paused) {
        Mix_ResumeMusic();
        is_paused = 0;
        printf("Resumed.\n");
    } else {
        Mix_PauseMusic();
        is_paused = 1;
        printf("Paused.\n");
    }
}

void next_song() {
    if (num_songs == 0) return;
    if (current_song_index == -1 && num_songs > 0) { // If nothing was playing, play first song
        play_song(0);
    } else if (current_song_index < num_songs - 1) {
        play_song(current_song_index + 1);
    } else { // Loop back to the first song
        play_song(0);
    }
}

void prev_song() {
    if (num_songs == 0) return;
     if (current_song_index == -1 && num_songs > 0) { // If nothing was playing, play last song
        play_song(num_songs - 1);
    } else if (current_song_index > 0) {
        play_song(current_song_index - 1);
    } else { // Loop back to the last song
        play_song(num_songs - 1);
    }
}
