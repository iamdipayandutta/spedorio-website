// Spotify API Configuration
const clientId = '408562e3abcb4163bdff3f081a57f7c0'; // Your Spotify Client ID
const redirectUri = 'http://localhost:5000/callback'; // Changed to localhost since that's where Flask is running
const scope = 'user-read-private user-read-email user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private';

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
        await getCurrentPlayback();
        await loadUserPlaylists();
        await loadTopTracks();
        startProgressUpdate();
    } catch (error) {
        console.error('Error initializing player:', error);
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
        if (!accessToken) throw new Error('No access token');

        // Get current playback state
        const response = await fetch(`${SPOTIFY_API_BASE}/me/player`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to get playback state');
        }

        const data = await response.json();
        const isCurrentlyPlaying = data?.is_playing;

        // Send play/pause command based on current state
        const endpoint = isCurrentlyPlaying ? '/me/player/pause' : '/me/player/play';
        const result = await spotifyFetch(endpoint, {
            method: 'PUT'
        });

        // Update UI
        isPlaying = !isCurrentlyPlaying;
        updatePlayPauseButton();
        
        // If we're starting playback, start progress updates
        if (!isCurrentlyPlaying) {
            startProgressUpdate();
        }
    } catch (error) {
        console.error('Error toggling playback:', error);
        handleError(error);
    }
}

async function skipTrack(direction) {
    try {
        if (!accessToken) throw new Error('No access token');

        // Send skip command
        await spotifyFetch(`/me/player/${direction}`, {
            method: 'POST'
        });

        // Wait a short moment for the skip to take effect
        await new Promise(resolve => setTimeout(resolve, 500));

        // Update the player UI with new track
        await getCurrentPlayback();
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
        await spotifyFetch('/me/player/play', {
            method: 'PUT',
            body: JSON.stringify({
                uris: [trackUri]
            })
        });
        isPlaying = true;
        updatePlayPauseButton();
        await getCurrentPlayback();
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
        `;
    }).join('');

    // Add click handlers for tracks
    tracksList.querySelectorAll('.track-item').forEach(item => {
        item.addEventListener('click', () => playTrack(item.dataset.trackUri));
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
                <img src="${playlist.images[0]?.url || '/assets/default-playlist.png'}" alt="${playlist.name}" onerror="this.src='/assets/default-playlist.png'">
            </div>
            <div class="playlist-info">
                <h4>${playlist.name}</h4>
                <p>${playlist.tracks.total} tracks</p>
            </div>
        </div>
    `).join('');

    // Add click handlers for playlists
    playlistsGrid.querySelectorAll('.playlist-card').forEach(card => {
        card.addEventListener('click', async () => {
            // Remove active class from all cards
            playlistsGrid.querySelectorAll('.playlist-card').forEach(c => c.classList.remove('active'));
            // Add active class to clicked card
            card.classList.add('active');
            await loadPlaylist(card.dataset.playlistId);
        });
    });

    // Show/hide show more button based on playlist count
    const shouldShowButton = playlists.length > 8;
    showMoreBtn.classList.toggle('hidden', !shouldShowButton);

    // Add click handler for show more button
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

// Initialize
if (window.location.hash) {
    handleCallback();
} 