[app]
title = NailStudio
package.name = nailstudio
package.domain = com.nailstudio.game

source.dir = .
source.include_exts = py,png,jpg,ttf,ttc,json
source.main = main.py
source.include_patterns = assets/**/*, font/*

version = 1.0

requirements = python3,pygame==2.1.3

p4a.fork = kivy
p4a.branch = 2023.9.16
p4a.bootstrap = sdl2
android.entrypoint = org.kivy.android.PythonActivity

orientation = landscape
fullscreen = 1

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
