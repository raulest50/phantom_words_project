/**
 * Audio processor for Phantom Words effect
 * This file contains the client-side JavaScript code for processing audio
 * with a delay effect to create the phantom words illusion.
 * It supports both single and dual track modes with speed control and random channel assignment.
 */

// Global variables to store audio sources and context
let audioSources = [];
let currentAudioContext = null;
let isPlaying = false;

// Function to stop all audio playback
function stopAudioPlayback() {
    if (audioSources.length > 0) {
        audioSources.forEach(source => {
            try {
                source.stop();
            } catch (e) {
                // Source might already be stopped
            }
        });
        audioSources = [];
    }

    if (currentAudioContext) {
        currentAudioContext.close().catch(err => console.error('Error closing audio context:', err));
        currentAudioContext = null;
    }

    isPlaying = false;

    return "Reproducción de audio detenida.";
}

// Function to process audio with delay effect
function processAudioWithDelay(n_clicks, delayStr, loopsStr, audioData1Str, audioData2Str, trackMode, speed1Str, speed2Str) {
    // Add debugging logs
    console.log('processAudioWithDelay called with n_clicks:', n_clicks);
    console.log('Parameters:', {
        delayStr, loopsStr, audioData1Str: audioData1Str ? 'data present' : null,
        audioData2Str: audioData2Str ? 'data present' : null, trackMode, speed1Str, speed2Str
    });

    if (!n_clicks) {
        console.log('Returning early: n_clicks is falsy');
        return "Listo para reproducir audio.";
    }

    // Check if we have the necessary data to play audio
    if (!delayStr || !loopsStr || !audioData1Str || !trackMode || !speed1Str) {
        console.log('Returning early: missing required parameters');
        return "Error: Faltan parámetros requeridos. Por favor asegúrese de que todas las configuraciones estén completas.";
    }
    if (trackMode === 'dual' && (!audioData2Str || !speed2Str)) {
        console.log('Returning early: dual track mode but missing track 2 data');
        return "Error: Modo de pistas duales seleccionado pero falta la Pista 2. Por favor suba un segundo archivo de audio.";
    }

    // Stop any currently playing audio
    stopAudioPlayback();

    // Reset audio sources array
    audioSources = [];

    const delay = parseInt(delayStr);
    const loops = parseInt(loopsStr);
    const speed1 = parseFloat(speed1Str);
    const speed2 = parseFloat(speed2Str || "1.0");
    const audioData1 = JSON.parse(audioData1Str);
    let audioData2 = null;

    if (trackMode === 'dual' && audioData2Str) {
        audioData2 = JSON.parse(audioData2Str);
    }

    // Create audio context
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    const audioContext = new AudioContext();
    currentAudioContext = audioContext;

    // Set playing state to true
    isPlaying = true;

    // Force a new random channel assignment each time
    // true = track1 on left, track2 on right; false = track1 on right, track2 on left
    const randomizeChannels = Math.random() >= 0.5;

    if (trackMode === 'single') {
        // Single track mode
        fetch(audioData1.content)
            .then(response => response.arrayBuffer())
            .then(arrayBuffer => audioContext.decodeAudioData(arrayBuffer))
            .then(audioBuffer => {
                // Create two audio sources (left and right)
                const sourceLeft = audioContext.createBufferSource();
                const sourceRight = audioContext.createBufferSource();

                // Add sources to global array for stop functionality
                audioSources.push(sourceLeft, sourceRight);

                sourceLeft.buffer = audioBuffer;
                sourceRight.buffer = audioBuffer;

                // Set playback speed
                sourceLeft.playbackRate.value = speed1;
                sourceRight.playbackRate.value = speed1;

                // Set loop count
                sourceLeft.loop = loops > 1;
                sourceRight.loop = loops > 1;

                if (loops > 1) {
                    sourceLeft.loopEnd = audioBuffer.duration;
                    sourceRight.loopEnd = audioBuffer.duration;

                    // Stop after specified number of loops
                    setTimeout(() => {
                        try {
                            sourceLeft.stop();
                            sourceRight.stop();
                        } catch (e) {
                            // Sources might already be stopped
                        }

                        // Set playing state to false
                        isPlaying = false;
                    }, (audioBuffer.duration / speed1) * loops * 1000);
                } else {
                    // For single play, set timeout based on audio duration
                    setTimeout(() => {
                        isPlaying = false;
                    }, (audioBuffer.duration / speed1) * 1000);
                }

                // Create channel merger for stereo output
                const merger = audioContext.createChannelMerger(2);

                // Create delay node
                const delayNode = audioContext.createDelay();
                delayNode.delayTime.value = delay / 1000; // Convert ms to seconds

                // Connect nodes for left channel (no delay)
                sourceLeft.connect(merger, 0, 0); // Connect to left channel

                // Connect nodes for right channel (with delay)
                sourceRight.connect(delayNode);
                delayNode.connect(merger, 0, 1); // Connect to right channel

                // Connect merger to output
                merger.connect(audioContext.destination);

                // Start playback
                sourceLeft.start();
                sourceRight.start();
            })
            .catch(error => {
                console.error('Error processing audio:', error);
                isPlaying = false;
                return "Error al procesar el audio. Por favor verifique su archivo de audio e intente nuevamente.";
            });
    } else {
        // Dual track mode
        console.log(`Channel assignment: Track 1 on ${randomizeChannels ? 'left' : 'right'}, Track 2 on ${randomizeChannels ? 'right' : 'left'}`);

        Promise.all([
            // Fetch and decode the first audio file
            fetch(audioData1.content)
                .then(response => response.arrayBuffer())
                .then(arrayBuffer => audioContext.decodeAudioData(arrayBuffer)),

            // Fetch and decode the second audio file
            fetch(audioData2.content)
                .then(response => response.arrayBuffer())
                .then(arrayBuffer => audioContext.decodeAudioData(arrayBuffer))
        ])
        .then(([audioBuffer1, audioBuffer2]) => {
            // Create audio sources for both tracks
            const source1 = audioContext.createBufferSource();
            const source2 = audioContext.createBufferSource();

            // Add sources to global array for stop functionality
            audioSources.push(source1, source2);

            source1.buffer = audioBuffer1;
            source2.buffer = audioBuffer2;

            // Set playback speed
            source1.playbackRate.value = speed1;
            source2.playbackRate.value = speed2;

            // Set loop count
            source1.loop = loops > 1;
            source2.loop = loops > 1;

            // Find the duration for timeout
            const duration1 = audioBuffer1.duration / speed1;
            const duration2 = audioBuffer2.duration / speed2;
            const maxDuration = Math.max(duration1, duration2);

            if (loops > 1) {
                source1.loopEnd = audioBuffer1.duration;
                source2.loopEnd = audioBuffer2.duration;

                // Stop after specified number of loops
                setTimeout(() => {
                    try {
                        source1.stop();
                        source2.stop();
                    } catch (e) {
                        // Sources might already be stopped
                    }

                    // Set playing state to false
                    isPlaying = false;
                }, maxDuration * loops * 1000);
            } else {
                // For single play, set timeout based on audio duration
                setTimeout(() => {
                    isPlaying = false;
                }, maxDuration * 1000);
            }

            // Create channel merger for stereo output
            const merger = audioContext.createChannelMerger(2);

            // Create delay nodes for both tracks
            const delayNode1 = audioContext.createDelay();
            const delayNode2 = audioContext.createDelay();
            delayNode1.delayTime.value = delay / 1000; // Convert ms to seconds
            delayNode2.delayTime.value = delay / 1000; // Convert ms to seconds

            // Connect nodes based on random channel assignment
            if (randomizeChannels) {
                // Track 1 to left channel (with delay)
                source1.connect(delayNode1);
                delayNode1.connect(merger, 0, 0); // Connect to left channel

                // Track 2 to right channel (with delay)
                source2.connect(delayNode2);
                delayNode2.connect(merger, 0, 1); // Connect to right channel
            } else {
                // Track 2 to left channel (with delay)
                source2.connect(delayNode1);
                delayNode1.connect(merger, 0, 0); // Connect to left channel

                // Track 1 to right channel (with delay)
                source1.connect(delayNode2);
                delayNode2.connect(merger, 0, 1); // Connect to right channel
            }

            // Connect merger to output
            merger.connect(audioContext.destination);

            // Start playback
            source1.start();
            source2.start();
        })
        .catch(error => {
            console.error('Error processing audio:', error);
            isPlaying = false;
            return "Error al procesar el audio. Por favor verifique sus archivos de audio e intente nuevamente.";
        });
    }

    return trackMode === 'single' 
        ? "Reproduciendo pista única con efecto de palabras fantasma..." 
        : "Reproduciendo pistas duales con efecto de palabras fantasma...";
}


// Export the functions for use in Dash clientside callbacks
window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.audio_processor = {
    processAudioWithDelay: processAudioWithDelay,
    stopAudioPlayback: stopAudioPlayback,
    isAudioPlaying: function() {
        return isPlaying;
    }
};
