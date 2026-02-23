[app]
title = MiApp
package.name = apptest
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,csv
# IMPORTANTE: Sin espacios después de las comas
requirements = python3,kivy,kivymd,sqlite3,csv
orientation = portrait
fullscreen = 1
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
p4a.branch = master
