[app]
title = NailStudio
package.name = nailstudio
package.domain = com.nailstudio.game

source.dir = .
source.include_exts = py,png,jpg,ttf,ttc,json
source.main = nail_android.py
source.include_patterns = assets/**/*, font/*

version = 1.0

# 纯 pygame，不依赖 kivy
requirements = python3,pygame==2.6.1

# 使用 pygame bootstrap，跳过 kivy 整个工具链
p4a.bootstrap = pygame

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
