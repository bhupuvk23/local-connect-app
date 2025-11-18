[app]

title = Local Connect
package.name = localconnect
package.domain = org.localconnect
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,db,txt,ttf,mp3,ogg,wav,ini,json,zip
version = 0.1

# Main Python file
entrypoint = main.py

# (Optional) icon
icon.filename = assets/icon.png

# Supported orientation
orientation = portrait

# Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# Fullscreen (Blinkit-style)
fullscreen = 0

# Requirements
requirements = python3,kivy==2.1.0,kivymd,pillow,requests,plyer

# Minimum Android version (safe for all devices)
android.minapi = 21

# Android SDK / NDK
android.api = 33
android.sdk = 24
android.ndk = 25b
android.ndk_api = 21

# Arch
android.archs = arm64-v8a, armeabi-v7a

# Enable Java = 11
android.java_paths = /usr/lib/jvm/java-11-openjdk-amd64
android.gradle_version = 7.5
android.ndk_path =

# Hide buildozer logs
log_level = 2

# Include data folders
source.include_patterns = assets/*, data/*

# Exclude unnecessary folders
exclude_dirs = venv, __pycache__, .git

# Package format
android.accept_sdk_license = True

# Bootstraps
android.bootstrap = sdl2

# Python optimization (optional)
# pyo = True


# ------------------------
# BUILD OUTPUT
# ------------------------
[buildozer]

log_level = 2
warn_on_root = 0
