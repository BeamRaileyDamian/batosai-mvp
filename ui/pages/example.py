import streamlit as st
from audio_component import audio_player

st.title("Background Audio with Completion Detection")

# Initialize session state
if 'audio_completed' not in st.session_state:
    st.session_state.audio_completed = False
if 'autoplay_failed' not in st.session_state:
    st.session_state.autoplay_failed = False

# Display content based on audio state
if not st.session_state.audio_completed:
    st.write("Audio is playing in the background...")
    
    # Add a progress spinner to indicate something's happening
    with st.spinner("Audio playing..."):
        # Use the hidden component
        result = audio_player("https://gisdypsqimhoyclwsepf.supabase.co/storage/v1/object/public/presentations/audios/test%20pls%20work/80a84024-1e24-41d7-9a00-4e1604271d34.mp3", key="hidden_player")
        
        # Check for different events
        if result:
            if result.get('event') == 'audio_ended':
                st.session_state.audio_completed = True
                st.rerun()
            elif result.get('event') == 'autoplay_failed':
                st.session_state.autoplay_failed = True
                st.rerun()

# Handle autoplay failure (common in many browsers)
if st.session_state.autoplay_failed:
    st.warning("Autoplay was blocked by your browser. Please click the button below to start audio.")
    if st.button("Play Audio"):
        st.session_state.autoplay_failed = False
        # This will trigger the component again on rerun
        st.rerun()

# Show completion message
if st.session_state.audio_completed:
    st.success("Audio playback completed!")
    if st.button("Play Again"):
        st.session_state.audio_completed = False
        st.rerun()