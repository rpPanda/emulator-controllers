import time
import json
from adbutils import adb
import apkutils2

d = adb.device(serial="emulator-5554")

apk_path = '/home/ruddhi/app-debug.apk'
# print(d.install(apk_path,True))

apk = apkutils2.APK(apk_path)
package_name = apk.manifest.package_name

print(d.package_info(package_name))
# print(d.app_start(package_name))

print(d.app_stop(package_name))
print(d.app_start(package_name))
time.sleep(3)
