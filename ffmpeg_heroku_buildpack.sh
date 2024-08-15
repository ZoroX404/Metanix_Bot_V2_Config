#!/bin/bash
FF_VERSION="4.4.1"
FF_URL="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-$FF_VERSION.tar.xz"

# Download and extract ffmpeg
curl -L $FF_URL | tar -xJ

# Move ffmpeg and ffprobe to /app/vendor directory
mv ffmpeg-*-amd64-static/ffmpeg /app/vendor/ffmpeg
mv ffmpeg-*-amd64-static/ffprobe /app/vendor/ffprobe
