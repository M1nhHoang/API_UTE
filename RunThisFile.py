from apiUTE import Api_UTE
import json, threading

def display_menu():
	print("==== MENU ====")
	print("1. Xem thời khóa biểu")
	print("2. Xem học phí")
	print("3. Xem lịch thi")
	print("4. Xem điểm")
	print("5. Đăng kí môn học")
	print("6. Thêm môn học")
	print("7. Xóa môn học")
	print("8. Thêm ...")
	print("0. Thoát")
	print("================")

def display_menuMoreOption():
	print("==== MENU ====")
	print("1. Đăng kí môn học (multi thread)")
	print("2. Thêm môn học (multi thread)")
	print("0. Back")
	print("================")

def more_option(user, pwd, data):
	while True:
		display_menuMoreOption()
		choice = input("Nhập lựa chọn của bạn (0-2): ")
		if choice == "1":
			def dangKi(user, pwd, data):
				while True:
					reg = Api_UTE(user, pwd, data)
					reg.getCookies()
					reg.dkmonhoc()

			threads = []
			for _ in range(int(input("Nhập số luồng: "))):
				thread = threading.Thread(target=dangKi, args=(user, pwd, data))
				thread.start()
				threads.append(thread)

			for thread in threads:
				thread.join()

		elif choice == "2":
			def them(user, pwd, data):
				while True:
					for d in data:
						add = Api_UTE(user, pwd, d)
						add.getCookies()
						add.getMaDangKi()
						add.bsungmonhoc()

			threads = []
			for _ in range(int(input("Nhập số luồng: "))):
				thread = threading.Thread(target=them, args=(user, pwd, data))
				thread.start()
				threads.append(thread)

			for thread in threads:
				thread.join()

		elif choice == "0":
			print("Thoát")
			break


with open('./config.json') as f:
	config = json.load(f)

account = config["dangNhap"]
dsMonHoc_dir = config["dsDangKi"]

# get ds môn học
with open(dsMonHoc_dir, encoding='UTF-8') as f:
	data = [s.strip() for s in f.readlines()]

menu = Api_UTE(account["taikhoan"], account["matkhau"], Api_UTE(dsMonHoc=data).convertMaMonHoc_MaDangKi())
while True:
	display_menu()
	choice = input("Nhập lựa chọn của bạn (0-8): ")
	
	if choice == "1":
		print("Xem thời khóa biểu")
		menu.xemTKB()
	elif choice == "2":
		print("Xem học phí")
		menu.getCookies()
		menu.xemTKB()
	elif choice == "3":
		print("Xem lịch thi")
		menu.getCookies()
		menu.xemLichThi()
	elif choice == "4":
		print("Xem điểm")
		menu.getCookies()
		menu.xemDiem()
	elif choice == "5":
		print("Đăng kí môn học")
		menu.getCookies()
		menu.dkmonhoc()
	elif choice == "6":
		print("Thêm môn học")
		menu.getCookies()
		menu.getMaDangKi()
		menu.bsungmonhoc()
	elif choice == "7":
		print("Xóa môn học")
		menu.getCookies()
		menu.getMaDangKi()
		menu.xoamonhoc()
	elif choice == "8":
		more_option(account["taikhoan"], account["matkhau"], Api_UTE(dsMonHoc=data).convertMaMonHoc_MaDangKi())
	elif choice == "0":
		print("Thoát")
		break
	else:
		print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")

# 123550533301
# 123550532602
# 123550513202
# 123550532806
# 123550517203
# 123550520606