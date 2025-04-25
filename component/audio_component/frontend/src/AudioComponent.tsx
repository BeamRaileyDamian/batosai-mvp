import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib";
import React, { ReactNode, useEffect, useRef } from "react";

interface AudioPlayerProps {
  audioUrl: string;
  autoplay: boolean;
}

function AudioPlayer(props: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  
  useEffect(() => {
    const audioElement = audioRef.current;
    if (!audioElement) return;
    
    // Attempt autoplay if requested
    if (props.autoplay) {
      audioElement.play();
    }
    
    const handleEnded = () => {
      // Send data back to Python when audio ends
      Streamlit.setComponentValue({
        event: "audio_ended",
        timestamp: new Date().getTime()
      });
    };
    
    // Add event listeners
    audioElement.addEventListener("ended", handleEnded);
    
    // Cleanup
    return () => {
      audioElement.removeEventListener("ended", handleEnded);
    };
  }, [props.audioUrl, props.autoplay]);
  
  return (
    <div style={{ display: "none" }}>
      <audio 
        ref={audioRef}
        src={props.audioUrl} 
        autoPlay={props.autoplay}
      />
    </div>
  );
}

class AudioComponent extends StreamlitComponentBase {
  public render = (): ReactNode => {
    return <AudioPlayer 
      audioUrl={this.props.args.audioUrl} 
      autoplay={this.props.args.autoplay ?? true}
    />;
  };
}

export default withStreamlitConnection(AudioComponent);