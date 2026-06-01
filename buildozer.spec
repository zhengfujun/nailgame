[app]
title = NailStudio
package.name = nailstudio
package.domain = com.nailstudio.game

source.dir = .
source.include_exts = py,png,jpg,ttf,ttc,json
source.main = nail_android.py
source.include_patterns = assets/**/*, font/*

version = 1.0

# pygame 2.6.x 的 p4a recipe 已支持 Python 3.14，解决 longintrepr.h 问题
requirements = python3,kivy==2.3.0,pygame==2.6.1

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
