[app]
title = MiAppPydroid
package.name = miapptest
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,csv

# ESTA ES LA LÍNEA QUE FALTA Y QUE CAUSA EL ERROR:
version = 0.1

requirements = python3,kivy==2.3.0,kivymd==1.1.1,sqlite3,csv
orientation = portrait
fullscreen = 1
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.release_artifact = apk

[buildozer]
log_level = 2
p4a.branch = master
