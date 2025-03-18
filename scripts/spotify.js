// Spotify API Configuration
const clientId = '408562e3abcb4163bdff3f081a57f7c0'; // Your Spotify Client ID
const redirectUri = 'http://localhost:5000/callback'; // Changed to localhost since that's where Flask is running
const scope = 'user-read-private user-read-email playlist-read-private user-top-read';

// Load Spotify Web Playback SDK
let player = null;

window.onSpotifyWebPlaybackSDKReady = () => {
    player = new Spotify.Player({
        name: 'Spedorio Music Player',
        getOAuthToken: cb => { cb(accessToken); },
        volume: 0.5
    });

    // Error handling
    player.addListener('initialization_error', ({ message }) => { console.error(message); });
    player.addListener('authentication_error', ({ message }) => { console.error(message); });
    player.addListener('account_error', ({ message }) => { console.error(message); });
    player.addListener('playback_error', ({ message }) => { console.error(message); });

    // Playback status updates
    player.addListener('player_state_changed', state => {
        if (state) {
            console.log('Player State:', state);
            currentTrack = state.track_window.current_track;
            isPlaying = !state.paused;
            updatePlayerUI({
                item: currentTrack,
                is_playing: isPlaying,
                progress_ms: state.position
            });
        }
    });

    // Ready
    player.addListener('ready', ({ device_id }) => {
        console.log('Ready with Device ID', device_id);
        localStorage.setItem('spotify_device_id', device_id);
        // Transfer playback to the web player
        transferPlayback(device_id);
    });

    // Connect to the player
    player.connect();
};

// Spotify API endpoints
const SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize';
const SPOTIFY_API_BASE = 'https://api.spotify.com/v1';

// Spotify player state
let accessToken = null;
let currentTrack = null;
let isPlaying = false;
let progressInterval = null;

// DOM Elements
document.addEventListener('DOMContentLoaded', () => {
    const loginButton = document.querySelector('.spotify-auth-btn');
    if (loginButton) {
        loginButton.addEventListener('click', initiateSpotifyLogin);
    }

    // Check if we have a token in localStorage
    const token = localStorage.getItem('spotify_access_token');
    if (token) {
        accessToken = token;
        initializePlayer();
    }

    // Setup player controls
    setupPlayerControls();
});

// Login handling
function initiateSpotifyLogin() {
    const params = new URLSearchParams({
        client_id: clientId,
        response_type: 'token',
        redirect_uri: redirectUri,
        scope: scope,
        show_dialog: true // Added to force login dialog
    });
    
    const authUrl = `${SPOTIFY_AUTH_URL}?${params.toString()}`;
    window.location.href = authUrl;
}

// Handle the OAuth callback
function handleCallback() {
    const hash = window.location.hash.substring(1);
    const params = new URLSearchParams(hash);
    accessToken = params.get('access_token');

    if (accessToken) {
        localStorage.setItem('spotify_access_token', accessToken);
        initializePlayer();
        // Clear the URL hash
        history.pushState("", document.title, window.location.pathname);
    }
}

// Initialize the player
async function initializePlayer() {
    try {
        await loadUserPlaylists();
        await loadTopTracks();
    } catch (error) {
        console.error('Error initializing:', error);
        handleError(error);
    }
}

// API Calls
async function spotifyFetch(endpoint, options = {}) {
    if (!accessToken) throw new Error('No access token');

    const response = await fetch(`${SPOTIFY_API_BASE}${endpoint}`, {
        ...options,
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            ...options.headers
        }
    });

    if (response.status === 401) {
        // Token expired
        localStorage.removeItem('spotify_access_token');
        accessToken = null;
        showLoginPrompt();
        throw new Error('Token expired');
    }

    if (!response.ok) {
        throw new Error(`Spotify API error: ${response.statusText}`);
    }

    return response.json();
}

// Get current playback state
async function getCurrentPlayback() {
    try {
        const data = await spotifyFetch('/me/player');
        if (data) {
            updatePlayerUI(data);
        }
    } catch (error) {
        console.error('Error getting playback state:', error);
        handleError(error);
    }
}

// Load user's playlists
async function loadUserPlaylists() {
    try {
        const data = await spotifyFetch('/me/playlists');
        updatePlaylistsUI(data.items);
    } catch (error) {
        console.error('Error loading playlists:', error);
        handleError(error);
    }
}

// Load user's top tracks
async function loadTopTracks() {
    try {
        const data = await spotifyFetch('/me/top/tracks');
        updateTopTracksUI(data.items);
    } catch (error) {
        console.error('Error loading top tracks:', error);
        handleError(error);
    }
}

// Playback Controls
async function togglePlayback() {
    try {
        if (!player) throw new Error('Player not initialized');
        
        const state = await player.getCurrentState();
        if (!state) {
            // If no track is playing, start with the first available track
            const tracks = document.querySelectorAll('.track-item');
            if (tracks.length > 0) {
                await playTrack(tracks[0].dataset.trackUri);
                return;
            }
        }

        await player.togglePlay();
        isPlaying = !isPlaying;
        updatePlayPauseButton();
    } catch (error) {
        console.error('Error toggling playback:', error);
        handleError(error);
    }
}

async function skipTrack(direction) {
    try {
        if (!player) throw new Error('Player not initialized');
        
        if (direction === 'next') {
            await player.nextTrack();
        } else {
            await player.previousTrack();
        }
        
        // Wait a moment for the state to update
        setTimeout(async () => {
            const state = await player.getCurrentState();
            if (state) {
                updatePlayerUI({
                    item: state.track_window.current_track,
                    is_playing: !state.paused,
                    progress_ms: state.position
                });
            }
        }, 200);
    } catch (error) {
        console.error('Error skipping track:', error);
        handleError(error);
    }
}

// Playlist and Track Controls
async function loadPlaylist(playlistId) {
    try {
        // Get playlist tracks
        const data = await spotifyFetch(`/playlists/${playlistId}/tracks`);
        if (data.items && data.items.length > 0) {
            // Start playing the first track
            const firstTrack = data.items[0].track;
            await playTrack(firstTrack.uri);
            
            // Update the tracks list with playlist tracks
            updatePlaylistTracksUI(data.items);
        }
    } catch (error) {
        console.error('Error loading playlist:', error);
        handleError(error);
    }
}

async function playTrack(trackUri) {
    try {
        if (!player) throw new Error('Player not initialized');
        const deviceId = localStorage.getItem('spotify_device_id');
        
        await spotifyFetch('/me/player/play', {
            method: 'PUT',
            body: JSON.stringify({
                uris: [trackUri],
                device_id: deviceId
            })
        });

        isPlaying = true;
        updatePlayPauseButton();
        startProgressUpdate();
    } catch (error) {
        console.error('Error playing track:', error);
        handleError(error);
    }
}

function updatePlaylistTracksUI(tracks) {
    const tracksList = document.querySelector('.tracks-list');
    if (!tracksList) return;

    tracksList.innerHTML = tracks.map((item, index) => {
        const track = item.track;
        return `
            <div class="track-item">
                <span class="track-number">${index + 1}</span>
                <div class="track-thumbnail">
                    <img src="${track.album.images[track.album.images.length - 1]?.url || '/assets/default-playlist.png'}" 
                         alt="${track.name}"
                         onerror="this.src='/assets/default-playlist.png'">
                </div>
                <div class="track-details">
                    <h4>${track.name}</h4>
                    <p>${track.artists.map(artist => artist.name).join(', ')}</p>
                </div>
                <div class="track-actions">
                    ${track.preview_url ? `
                        <button class="preview-btn" data-preview-url="${track.preview_url}">
                            Preview ▶️
                        </button>
                    ` : ''}
                    <a href="${track.external_urls.spotify}" target="_blank" class="spotify-link">
                        Open in Spotify
                    </a>
                </div>
                <span class="track-duration">${formatDuration(track.duration_ms)}</span>
            </div>
        `;
    }).join('');

    // Add click handlers for preview buttons
    tracksList.querySelectorAll('.preview-btn').forEach(button => {
        button.addEventListener('click', handlePreviewClick);
    });
}

// UI Updates
function updatePlayerUI(data) {
    if (!data) return;

    const albumArt = document.querySelector('.album-art img');
    const trackTitle = document.querySelector('.track-info h4');
    const artistName = document.querySelector('.track-info p');
    const progressBar = document.querySelector('.progress');
    const currentTime = document.querySelector('.current-time');
    const totalTime = document.querySelector('.total-time');

    if (data.item) {
        currentTrack = data.item;
        isPlaying = data.is_playing;

        if (albumArt) {
            albumArt.src = currentTrack.album.images[0]?.url || '/assets/default-playlist.png';
            albumArt.onerror = () => albumArt.src = '/assets/default-playlist.png';
        }
        if (trackTitle) trackTitle.textContent = currentTrack.name;
        if (artistName) artistName.textContent = currentTrack.artists.map(artist => artist.name).join(', ');

        updateProgress(data.progress_ms, currentTrack.duration_ms);
        updatePlayPauseButton();
    }
}

function updatePlaylistsUI(playlists) {
    const playlistsGrid = document.querySelector('.playlists-grid');
    const showMoreBtn = document.querySelector('.show-more-btn');
    if (!playlistsGrid || !showMoreBtn) return;

    playlistsGrid.innerHTML = playlists.map(playlist => `
        <div class="playlist-card" data-playlist-id="${playlist.id}">
            <div class="playlist-art">
                <img src="${playlist.images[0]?.url || '/assets/default-playlist.png'}" 
                     alt="${playlist.name}" 
                     onerror="this.src='/assets/default-playlist.png'">
            </div>
            <div class="playlist-info">
                <h4>${playlist.name}</h4>
                <p>${playlist.tracks.total} tracks</p>
            </div>
            <a href="${playlist.external_urls.spotify}" target="_blank" class="spotify-link">
                Open in Spotify
            </a>
        </div>
    `).join('');

    // Add click handlers for playlists
    playlistsGrid.querySelectorAll('.playlist-card').forEach(card => {
        card.addEventListener('click', async () => {
            playlistsGrid.querySelectorAll('.playlist-card').forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            await loadPlaylist(card.dataset.playlistId);
        });
    });

    // Show/hide show more button based on playlist count
    showMoreBtn.classList.toggle('hidden', playlists.length <= 8);
    showMoreBtn.addEventListener('click', () => {
        playlistsGrid.classList.toggle('show-all');
        showMoreBtn.textContent = playlistsGrid.classList.contains('show-all') ? 'Show Less' : 'Show More Playlists';
    });
}

function updateTopTracksUI(tracks) {
    const tracksList = document.querySelector('.tracks-list');
    if (!tracksList) return;

    tracksList.innerHTML = tracks.map((track, index) => `
        <div class="track-item" data-track-uri="${track.uri}">
            <span class="track-number">${index + 1}</span>
            <div class="track-thumbnail">
                <img src="${track.album.images[track.album.images.length - 1]?.url || '/assets/default-playlist.png'}" 
                     alt="${track.name}"
                     onerror="this.src='/assets/default-playlist.png'">
            </div>
            <div class="track-details">
                <h4>${track.name}</h4>
                <p>${track.artists.map(artist => artist.name).join(', ')}</p>
            </div>
            <span class="track-duration">${formatDuration(track.duration_ms)}</span>
        </div>
    `).join('');

    // Add click handlers
    tracksList.querySelectorAll('.track-item').forEach(item => {
        item.addEventListener('click', () => playTrack(item.dataset.trackUri));
    });
}

// Helper functions
function formatDuration(ms) {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function updateProgress(progress, duration) {
    const progressBar = document.querySelector('.progress');
    const currentTime = document.querySelector('.current-time');
    const totalTime = document.querySelector('.total-time');

    if (progressBar && currentTime && totalTime) {
        const progressPercent = (progress / duration) * 100;
        progressBar.style.width = `${progressPercent}%`;
        currentTime.textContent = formatDuration(progress);
        totalTime.textContent = formatDuration(duration);
    }
}

function startProgressUpdate() {
    if (progressInterval) clearInterval(progressInterval);
    progressInterval = setInterval(getCurrentPlayback, 1000);
}

function updatePlayPauseButton() {
    const playPauseButton = document.querySelector('.play-pause-btn');
    if (playPauseButton) {
        playPauseButton.innerHTML = isPlaying ? '⏸️' : '▶️';
        // Add aria-label for accessibility
        playPauseButton.setAttribute('aria-label', isPlaying ? 'Pause' : 'Play');
    }
}

function setupPlayerControls() {
    const prevButton = document.querySelector('.prev-btn');
    const playPauseButton = document.querySelector('.play-pause-btn');
    const nextButton = document.querySelector('.next-btn');

    if (prevButton) {
        prevButton.addEventListener('click', () => skipTrack('previous'));
    }
    if (playPauseButton) {
        playPauseButton.addEventListener('click', togglePlayback);
    }
    if (nextButton) {
        nextButton.addEventListener('click', () => skipTrack('next'));
    }

    // Add click handlers for tracks
    document.addEventListener('click', async (e) => {
        const trackItem = e.target.closest('.track-item');
        if (trackItem) {
            const trackUri = trackItem.dataset.trackUri;
            if (trackUri) {
                await playTrack(trackUri);
            }
        }
    });
}

function showLoginPrompt() {
    const playerCard = document.querySelector('.player-card');
    const loginSection = document.querySelector('.spotify-login');

    if (playerCard) playerCard.style.display = 'none';
    if (loginSection) loginSection.style.display = 'block';
}

function handleError(error) {
    if (error.message.includes('Token expired') || error.message.includes('No access token')) {
        showLoginPrompt();
    }
    // You can add more error handling here
}

async function transferPlayback(deviceId) {
    try {
        await spotifyFetch('/me/player', {
            method: 'PUT',
            body: JSON.stringify({
                device_ids: [deviceId],
                play: false
            })
        });
    } catch (error) {
        console.error('Error transferring playback:', error);
    }
}

// Handle preview playback
let currentPreview = null;
function handlePreviewClick(event) {
    const previewUrl = event.target.dataset.previewUrl;
    
    // Stop current preview if playing
    if (currentPreview) {
        currentPreview.pause();
        currentPreview = null;
        document.querySelectorAll('.preview-btn').forEach(btn => {
            btn.textContent = 'Preview ▶️';
        });
    }

    // Play new preview if it's a different track
    if (previewUrl) {
        currentPreview = new Audio(previewUrl);
        currentPreview.play();
        event.target.textContent = 'Stop ⏹️';
        
        // Reset button when preview ends
        currentPreview.onended = () => {
            event.target.textContent = 'Preview ▶️';
            currentPreview = null;
        };
    }
}

// Initialize
if (window.location.hash) {
    handleCallback();
} 