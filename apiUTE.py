try:
	import requests
	from bs4 import BeautifulSoup
	from prettytable import PrettyTable
except:
	import os
	# Cài đặt thư viện cần thiết
	os.system('py -m pip install requests beautifulsoup4 prettytable')

class Api_UTE:
	def __init__(self, user = None, password = None, dsMonHoc = None):
		self.user = user
		self.password = password
		self.cookies = None
		self.maDangKi = None
		self.dsMonHoc = dsMonHoc

	def getCookies(self):
		payload = {
			"maSV": self.user,
			"pw": self.password
		}

		rs = requests.get(f'http://daotao.ute.udn.vn/svlogin.asp', data = payload)
		rs.encoding = 'utf-8'
		if 'Xin chào sinh viên' in rs.text:
			# get cookie
			self.cookies = rs.cookies

		else:
			print('Không lấy được cookie')

	def getMaDangKi(self):
		ThongTinDki = requests.get('http://daotao.ute.udn.vn/viewreg.asp')
		# use utf 8
		ThongTinDki.encoding = ThongTinDki.apparent_encoding
		try:
			ThongTinDki = ThongTinDki.text[ThongTinDki.text.find(self.user):ThongTinDki.text.find('</TR>',ThongTinDki.text.find(self.user))].split('</TD><TD')

			maSV = ThongTinDki[0]
			maDki =  ThongTinDki[1][ThongTinDki[1].find('>')+1:]
			HoTen = (ThongTinDki[2] + ThongTinDki[3]).replace('>','')
			time = ThongTinDki[4][ThongTinDki[4].find('>')+1:]
			soTinChi = ThongTinDki[5][ThongTinDki[5].find('>')+1:]
			soMon = ThongTinDki[6][ThongTinDki[6].find('>')+1:]
			lop = ThongTinDki[7][ThongTinDki[7].find('>')+1:ThongTinDki[7].find('<')]

			self.maDangKi = maDki
		except:
			print('Không Tìm Thấy Mã Sinh Viên Hoạc Bạn Chưa Đăng Kí!')

	def convertMaMonHoc_MaDangKi(self):
		ds_monHoc = requests.get('http://daotao.ute.udn.vn/viewlhpdksv.asp')
		# use utf 8
		ds_monHoc.encoding = ds_monHoc.apparent_encoding
		ds_monHoc = ds_monHoc.text.split('<TR>')

		dsMaMonHoc = []
		for i in range(0, len(self.dsMonHoc)):
			if self.dsMonHoc[i] == '':
				break
			for j in range(len(ds_monHoc)):
				if ds_monHoc[j].find(self.dsMonHoc[i]) != -1:
					ma_mon_hoc = ds_monHoc[j].split('</TD><TD')[1]
					khoa = self.dsMonHoc[i][:3]
					so_lop = self.dsMonHoc[i][-2:]
					dsMaMonHoc.append(khoa+ma_mon_hoc[ma_mon_hoc.find('>')+1:]+so_lop)
					break

		return dsMaMonHoc

	def bsungmonhoc(self):
		url = 'http://daotao.ute.udn.vn/addmorelhptc.asp'
		
		header = {
			'Content-Type': 'application/x-www-form-urlencoded'
		}

		playload = {
			'mhdk': self.dsMonHoc,
			# type
			# số học kì + tên lớp học phần + số thứ tự của tên lớp học phần
			# ví dụ : 122ABC05 Trong đó số học kì là 122 + mã học phần + 05
			# mã học phần lấy ở cột mã học phần
			'mdk': self.maDangKi
		}

		rs = requests.post(url, headers = header, cookies = self.cookies, data = playload)
		print(rs)

	def xoamonhoc(cookie):
		url = 'http://daotao.ute.udn.vn/removelhptc.asp'

		header= {
			'Content-Type': 'application/x-www-form-urlencoded'
		}
		playload = {
			'mhdk': input('Mã Môn Học Muốn Xóa: '),
			'mdk': self.maDangKi,
		}

		rs = requests.post(url, headers = header, cookies = self.cookies, data = playload)
		print(rs)

	def dkmonhoc(self):
		url = 'http://daotao.ute.udn.vn/committc.asp'
		header= {
			'Content-Type': 'application/x-www-form-urlencoded'
		}
		playload = {
			'mhdk': self.dsMonHoc,
			# type
			# số học kì + tên lớp học phần + số thứ tự của tên lớp học phần
			# ví dụ : 122ABC05 Trong đó số học kì là 122 + mã học phần + 05
			# mã học phần lấy ở cột mã học phần
		}

		rs = requests.post(url, headers = header, cookies = self.cookies, data = playload)
		print(rs)

	def xemTKB(self):
		payload = {
			"maSV": self.user,
		}

		rs = requests.get(f'http://daotao.ute.udn.vn/svtkb.asp', data = payload)
		rs.encoding = 'utf-8'

		# Xử lí dữ liệu đã cào về
		soup = BeautifulSoup(rs.text, 'html.parser')
		table = soup.select('table')[1]
		rows = table.find_all('tr')

		# Tạo bảng
		table = PrettyTable()
		table.field_names = ["Lớp", "Môn học", "Thứ", "Từ tiết", "Đến tiết", "Giảng viên", "Phòng", "Ngày hiệu lực", "Ghi chú"]

		# Lặp qua các dòng trong dữ liệu và thêm vào bảng
		for row in rows:
			data = row.find_all('td')
			if len(data) == 9:  # Kiểm tra số lượng cột
				row_data = [td.get_text(strip=True) for td in data]
				table.add_row(row_data)

		print(table)
		input()

	def xemHocPhi(self):
		rs = requests.get(f'http://daotao.ute.udn.vn/hpstatus.asp', cookies = self.cookies)
		rs.encoding = 'utf-8'

		# Parse mã HTML
		soup = BeautifulSoup(rs.text, 'html.parser')

		tbs = soup.select('table')[1]
		item = ['Thông Tin Sinh Viên']+[rs.text for rs in tbs.find_all('b') if 'Mã học kỳ' in rs.text]
		for i, tb in enumerate(tbs.select('table')):
			try:
				# Trích xuất dữ liệu từ HTML
				rows = tb.find_all('tr')

				# Tạo bảng mới
				table = PrettyTable(header=False)

				# Thêm dữ liệu vào bảng
				for row in rows:
					columns = row.find_all('td')
					if len(columns) == 2:
						column1 = columns[0].text.strip().replace(':', '')
						column2 = columns[1].text.strip().replace(':', '')
						table.add_row([column1, column2])

				# Merge row đầu tiên với tiêu đề
				table_title = item[i-1]
				table.align[table_title] = 'l'
				table.title = table_title

				# In bảng
				print(table)
			except:
				pass

	def xemDiem(self):
		rs = requests.get(f'http://daotao.ute.udn.vn/svtranscript.asp', cookies = self.cookies)
		rs.encoding = 'utf-8'
		
		# Parse mã HTML
		soup = BeautifulSoup(rs.text, 'html.parser')

		tbs = soup.select('table')[1]

		# In thông tin
		print(tbs.find('div').text)

		# Lấy danh sách các trường tiêu đề
		headers = [header.text for header in tbs.select('table')[1].find_all('th')]

		# Lấy danh sách các hàng dữ liệu
		rows = []
		for row in tbs.select('table')[1].find_all('tr')[1:]:
			rows.append([data.text.replace(' ', '') for data in row.find_all('td')])

		# Tạo bảng và thêm tiêu đề
		table = PrettyTable(headers)

		# Thêm dữ liệu từ các hàng vào bảng
		for row in rows[1:]:
			table.add_row(row)

		# In bảng ra màn hình
		print(table)

		# Lấy danh sách các trường tiêu đề bảng phụ
		headers = [header.text for header in tbs.select('table')[3].find_all('th')]

		# Lấy danh sách các hàng dữ liệu
		rows = []
		for row in tbs.select('table')[3].find_all('tr')[1:]:
			rows.append([data.text.replace(' ', '') for data in row.find_all('td')])

		# Tạo bảng và thêm tiêu đề
		table = PrettyTable(headers)

		# Thêm dữ liệu từ các hàng vào bảng
		for row in rows[1:]:
			table.add_row(row)

		# In bảng ra màn hình
		print(table)

		# in kết quả
		soup = BeautifulSoup(rs.text[rs.text.find('Điểm Trung bình chung tích lũy:'):rs.text.rfind('Lưu ý:')], 'html.parser')
		print(soup.text)

	def xemLichThi(self):
		payload = {
			"maSV": self.user,
		}

		rs = requests.post(f'http://daotao.ute.udn.vn/examTimeSv.asp', cookies = self.cookies, data = payload)
		rs.encoding = 'utf-8'
		
		# in thông tin
		soup = BeautifulSoup(rs.text[rs.text.find('Lịch thi'):rs.text.rfind('Tên LHP')], 'html.parser')
		print(soup.text)

		# Parse mã HTML
		soup = BeautifulSoup(rs.text, 'html.parser')

		# Lấy danh sách các trường tiêu đề
		headers = [header.text for header in soup.select('table')[1].find_all('th')]
		# Lấy danh sách các hàng dữ liệu
		rows = []
		for row in soup.select('table')[1].find_all('tr')[1:]:
			rows.append([data.text.replace(' ', '') for data in row.find_all('td')])

		# Tạo bảng và thêm tiêu đề
		table = PrettyTable(headers)

		# Thêm dữ liệu từ các hàng vào bảng
		for row in rows[1:]:
			table.add_row(row)

		# In bảng ra màn hình
		print(table)