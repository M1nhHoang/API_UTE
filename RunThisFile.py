from apiUTE import Api_UTE
import json

def display_menu():
	print("==== MENU ====")
	print("1. Xem thời khóa biểu")
	print("2. Xem học phí")
	print("3. Xem lịch thi")
	print("4. Xem điểm")
	print("5. Đăng kí môn học")
	print("6. Thêm môn học")
	print("7. Xóa môn học")
	print("0. Thoát")
	print("================")

with open('./config.json') as f:
	config = json.load(f)

account = config["dangNhap"]
dsMonHoc_dir = config["dsDangKi"]

# get ds môn học
with open(dsMonHoc_dir, encoding='UTF-8') as f:
	data = [s.strip() for s in f.readlines()]

menu = Api_UTE(account["taikhoan"], account["matkhau"], data)
while True:
	display_menu()
	choice = input("Nhập lựa chọn của bạn (0-7): ")
	
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
	elif choice == "0":
		print("Thoát")
		break
	else:
		print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")