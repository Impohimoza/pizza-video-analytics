from streaming.video_stream_processor import VideoStreamProcessor

if __name__ == "__main__":
    stream = VideoStreamProcessor(src=0, interval=3)
    stream.run()
