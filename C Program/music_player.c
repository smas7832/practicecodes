#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h>

int main(int argc, char* argv[]) {
    SDL_AudioSpec desired;
    SDL_AudioSpec wavSpec;
    Uint8* wavBuffer = NULL;
    Uint32 wavLength = 0;
    SDL_AudioDeviceID deviceId = 0;

    // Check against 0, as SDL_Init returns 0 on success
    if (SDL_Init(SDL_INIT_AUDIO) != 0) {
        return 1;
    }

    SDL_zero(desired);
    desired.freq = 44100;
    desired.format = SDL_AUDIO_F32;
    desired.channels = 2;
    
    // Pass 0 (which is a valid SDL_AudioDeviceID) instead of NULL (void*)
    // NULL is only for the first argument, which is the device name string (not the device ID).
    deviceId = SDL_OpenAudioDevice(NULL, &desired);

    if (deviceId == 0) {
        SDL_Quit();
        return 1;
    }

    // SDL_LoadWAV returns NULL on failure, so the comparison is fine, but
    // the warning suggests using SDL_LoadWAV_RW and reading the result, or checking the pointer.
    // The current comparison is technically correct for the function signature.
    if (SDL_LoadWAV("my_audio_file.wav", &wavSpec, &wavBuffer, &wavLength) == NULL) {
        SDL_CloseAudioDevice(deviceId);
        SDL_Quit();
        return 1;
    }

    if (SDL_QueueAudio(deviceId, wavBuffer, wavLength) < 0) {
        // Use SDL_FreeWAV to clean up on error
        SDL_FreeWAV(wavBuffer);
        SDL_CloseAudioDevice(deviceId);
        SDL_Quit();
        return 1;
    }

    // SDL_PauseAudioDevice in SDL3 takes only one argument (the device ID)
    // It *toggles* the pause state if called without a second argument.
    // To explicitly *unpause* (play), you now use SDL_PlayAudioDevice.
    SDL_PlayAudioDevice(deviceId);

    while (SDL_GetQueuedAudioSize(deviceId) > 0) {
        SDL_Delay(100);
    }

    SDL_FreeWAV(wavBuffer);
    SDL_CloseAudioDevice(deviceId);
    SDL_Quit();

    return 0;
}