// Audio Logic using global Howl object (loaded in index.html)

// Hardcoded Scancode Map (QWERTY Standard)
const KEY_MAP = {
    // Row 1
    16: 'Q', 17: 'W', 18: 'E', 19: 'R', 20: 'T', 21: 'Y', 22: 'U', 23: 'I', 24: 'O', 25: 'P',
    // Row 2
    30: 'A', 31: 'S', 32: 'D', 33: 'F', 34: 'G', 35: 'H', 36: 'J', 37: 'K', 38: 'L',
    // Row 3
    44: 'Z', 45: 'X', 46: 'C', 47: 'V', 48: 'B', 49: 'N', 50: 'M',
    // Control
    57: 'Space',
    28: 'Enter',
    14: 'Backspace'
};

const noteFiles = [
    'sounds/felt_piano_1_C4.wav',
    'sounds/felt_piano_2_Eb4.wav',
    'sounds/felt_piano_3_F4.wav',
    'sounds/felt_piano_4_G4.wav',
    'sounds/felt_piano_5_Bb4.wav'
];

const notes = noteFiles.map(src => new Howl({
    src: [src],
    volume: 0.8
}));


const drums = {
    kick: new Howl({ src: ['sounds/kick.wav'], volume: 1.0 }),
    snare: new Howl({ src: ['sounds/snare.wav'], volume: 1.0 }),
    hat: new Howl({ src: ['sounds/hat.wav'], volume: 0.5 })
};

// Controls
const muteBtn = document.getElementById('mute-btn');
const volumeSlider = document.getElementById('volume-slider');
let isMuted = false;

// Initialize
Howler.volume(1.0);

muteBtn.addEventListener('click', () => {
    isMuted = !isMuted;
    Howler.mute(isMuted);
    muteBtn.innerText = isMuted ? 'Unmute' : 'Mute';
    muteBtn.classList.toggle('muted', isMuted);
});

volumeSlider.addEventListener('input', (e) => {
    Howler.volume(parseFloat(e.target.value));
});

const keyDisplay = document.getElementById('key-display');
const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD', '#D4A5A5', '#9B59B6', '#3498DB'];

// Handle Global Key Events
window.electronAPI.onGlobalKeyDown((e) => {
    const code = e.keycode;

    // 1. Audio Logic
    // Rhythm Section
    if (code === 57) { // Space
        drums.kick.play();
    } else if (code === 28) { // Enter
        drums.snare.play();
    } else if (code === 14) { // Backspace
        drums.hat.play();
    } else {
        // Melody (Map any other key to a note deterministically)
        const noteIndex = code % notes.length;
        if (notes[noteIndex]) {
            notes[noteIndex].play();
        }
    }

    // 2. Visual Logic (Using Manual Map)
    const mappedChar = KEY_MAP[code];
    const displayText = mappedChar ? mappedChar : `UNKNOWN: ${code}`;

    animateUI(displayText);
});

function animateUI(text) {
    keyDisplay.innerText = text;
    // Pick random color
    keyDisplay.style.color = colors[Math.floor(Math.random() * colors.length)];

    // Simple "thump" animation
    keyDisplay.style.transform = 'scale(1.2)';
    setTimeout(() => {
        keyDisplay.style.transform = 'scale(1.0)';
    }, 50);
}
