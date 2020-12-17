from uiautomator import Device

d=Device('localhost:5555')

# d.dump("hierarchy.xml")

d(text="").click()
# d = device('emulator-5554')
print(d.info)