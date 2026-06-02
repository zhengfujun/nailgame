[app]
title = NailStudio
package.name = nailstudio
package.domain = com.nailstudio.game

source.dir = .
source.include_exts = py,png,jpg,ttf,ttc,json
source.main = main.py
source.include_patterns = assets/**/*, font/*

version = 1.0

# 只用 pygame，不含 kivy
requirements = python3,pygame==2.6.1

# 强制从源码编译 pygame，禁用预编译 ARM 不兼容的 x86 轮子
p4a.extra_args = --skip-prebuilt

# sdl2 bootstrap（pygame bootstrap 已被移除）
p4a.bootstrap = sdl2

# 使用 PythonActivity（不是 KivyActivity），pygame 可直接驱动
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
