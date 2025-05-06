import subprocess
from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import HTMLResponse
import os
import glob
import uvicorn
import threading
import time
from fastapi.middleware.cors import CORSMiddleware




app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源，或指定你的前端 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ffmpeg_process = None
STREAM_DIR = os.path.abspath("stream")  # 使用絕對路徑
HLS_PLAYLIST_NAME = os.path.join(STREAM_DIR, "stream.m3u8")
HLS_PLAYLIST_NAME_PATTERN = os.path.join(STREAM_DIR, "stream_*.m3u8")
HLS_SEGMENT_MEDIA_TYPE = "video/MP2T"
HLS_PLAYLIST_MEDIA_TYPE = "application/vnd.apple.mpegurl"

def generate_hls_stream():
    """Generates HLS stream using FFmpeg in a separate thread."""
    global ffmpeg_process
    print("generate_hls_stream started in thread")

    if not os.path.exists(STREAM_DIR):
        os.makedirs(STREAM_DIR)
        print(f"Created directory: {STREAM_DIR}")

    ffmpeg_cmd = [
        "ffmpeg",
        "-f", "dshow",
        "-framerate", "15",  # 指定輸入幀率
        "-i", "video=Logitech QuickCam S5500",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-tune", "zerolatency",
        "-b:v", "500k",
        "-c:a", "aac",
        "-f", "hls",
         "-hls_time", "2",
         "-hls_list_size", "0",
         "-hls_segment_filename", os.path.join(STREAM_DIR, "stream%d.ts"),
         "-hls_base_url", "stream/",
          HLS_PLAYLIST_NAME
        ]
    

    try:
        ffmpeg_process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW  # 防止彈出控制台視窗 (Windows)
        )
        print("FFmpeg 已開始生成 HLS 串流。")

        while True:
            line = ffmpeg_process.stderr.readline().decode().strip()
            if line:
                print(f"ffmpeg stderr: {line}")
            if ffmpeg_process.poll() is not None:
                return_code = ffmpeg_process.wait()
                print(f"FFmpeg exited with code: {return_code}")
                break
            time.sleep(0.1)

    except Exception as e:
        print(f"FFmpeg 啟動失敗: {e}")

async def get_latest_hls_playlist():
    """Finds and returns the path to the latest HLS playlist."""
    playlist_files = glob.glob(HLS_PLAYLIST_NAME_PATTERN)
    if not playlist_files:
        raise HTTPException(status_code=404, detail="No HLS playlist found")
    latest_playlist = max(playlist_files, key=os.path.getmtime)
    return latest_playlist

@app.get("/stream.m3u8")
async def stream():
    """Serves the HLS playlist."""
    print(f"[/stream.m3u8] 嘗試讀取播放列表檔案: {HLS_PLAYLIST_NAME}")
    max_attempts = 5
    for _ in range(max_attempts):
        if os.path.exists(HLS_PLAYLIST_NAME):
            try:
                with open(HLS_PLAYLIST_NAME, "r") as f:
                    return Response(content=f.read(), media_type="application/vnd.apple.mpegurl")
            except Exception as e:
                print(f"[/stream.m3u8] 讀取播放列表檔案時發生錯誤: {e}")
                raise HTTPException(status_code=500, detail="Error serving playlist")
        print(f"[/stream.m3u8] 播放列表檔案尚未準備好，等待中...")
        time.sleep(0.5)
    print(f"[/stream.m3u8] 找不到播放列表檔案: {HLS_PLAYLIST_NAME}")
    raise HTTPException(status_code=404, detail="HLS playlist not found")

@app.get("/stream/{segment_file_name}")
async def get_segment(segment_file_name: str):
    """Serves the HLS video segments."""
    segment_path = os.path.join(STREAM_DIR, segment_file_name)
    print(f"嘗試存取分段檔案: {segment_path}")
    max_attempts = 5
    for _ in range(max_attempts):
        if os.path.exists(segment_path):
            try:
                with open(segment_path, "rb") as f:
                    return Response(content=f.read(), media_type=HLS_SEGMENT_MEDIA_TYPE)
            except Exception as e:
                print(f"Error serving segment: {e}")
                raise HTTPException(status_code=500, detail="Error serving segment")
        print(f"分段檔案尚未準備好: {segment_path}，等待中...")
        time.sleep(0.5)
    print(f"分段檔案不存在: {segment_path}")
    raise HTTPException(status_code=404, detail="Segment not found")

@app.get("/")
async def index():
    """提供包含影片播放器的 HTML 頁面。"""
    html_content = """
    <html>
    <body>
        <video controls></video>
        <button id="playButton">播放</button>
        <script src="https://cdn.jsdelivr.net/npm/hls.js@1.4.12"></script>
      <script>
            if(Hls.isSupported()) {
              console.log("HLS.js is supported");
              var video = document.querySelector('video');
              var hls = new Hls({
                liveSyncDurationCount: 3,
                liveMaxLatencyDurationCount: 6,
                maxBufferLength: 10,
                maxMaxBufferLength: 20
              });
              hls.config.startLevel = 0;
              console.log("嘗試加載播放列表...");
              hls.loadSource('/stream.m3u8');
              console.log("已調用 loadSource");
              hls.attachMedia(video);
              hls.startLoad();
              hls.on(Hls.Events.MANIFEST_PARSED, function() {
                console.log("MANIFEST_PARSED 事件被觸發");
                video.play().catch(function(error) {
                  console.error("嘗試在 MANIFEST_PARSED 後播放時發生錯誤:", error);
                });
              });
              hls.on(Hls.Events.ERROR, function(event, data) {
                console.error("HLS.js 錯誤:", event, data);
              });
              var playButton = document.getElementById('playButton');
              playButton.addEventListener('click', function() {
                video.play().catch(function(error) {
                  console.error("嘗試播放時發生錯誤:", error);
                });
              });
            } else {
              console.log("HLS.js is not supported by this browser");
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

def start_ffmpeg_thread():
    """Starts the FFmpeg stream generation in a separate thread."""
    thread = threading.Thread(target=generate_hls_stream)
    thread.daemon = True  # Allow the main program to exit even if the thread is still running
    thread.start()

@app.on_event("startup")
async def startup_event():
    start_ffmpeg_thread()

@app.on_event("shutdown")
async def shutdown_event():
    global ffmpeg_process
    if ffmpeg_process:
        print("終止 FFmpeg 進程...")
        ffmpeg_process.terminate()
        ffmpeg_process.wait()
        print("FFmpeg 進程已終止。")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)