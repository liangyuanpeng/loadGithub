import subprocess

#mapReduce.mp3
strcmd = "ffmpeg -re -i /Users/lanren/tmp/git.mp4 -codec:v libx264 -codec:a copy -map 0 -f hls  -hls_time 15 playlist.m3u8"
subprocess.call(strcmd, shell=True)