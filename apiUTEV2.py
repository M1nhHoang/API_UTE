import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re

def load_config(config_file="config.json"):
    """
    Load cấu hình từ file config
    
    Args:
        config_file (str): Đường dẫn file config
        
    Returns:
        dict: Config data hoặc None nếu lỗi
    """
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"Đã load config từ {config_file}")
            return config
        else:
            print(f"File config {config_file} không tồn tại")
            return None
    except Exception as e:
        print(f"Lỗi khi load config: {e}")
        return None

def get_login_page_and_token():
    """
    Lấy trang login và extract __RequestVerificationToken
    
    Returns:
        tuple: (cookies, verification_token) hoặc (None, None) nếu lỗi
    """
    url = "https://qldt1.ute.udn.vn/login"
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML để tìm __RequestVerificationToken
        soup = BeautifulSoup(response.text, 'html.parser')
        token_input = soup.find('input', {'name': '__RequestVerificationToken'})
        
        if not token_input:
            print("Không tìm thấy __RequestVerificationToken")
            return None, None
        
        verification_token = token_input.get('value')
        
        # Lấy cookies từ response
        cookies_dict = response.cookies.get_dict()
        
        print("Đã lấy verification token và cookies từ trang login")
        return cookies_dict, verification_token
        
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lấy trang login: {e}")
        return None, None
    except Exception as e:
        print(f"Lỗi parse trang login: {e}")
        return None, None

def login(student_id, password):
    """
    Đăng nhập và lấy cookie
    
    Args:
        student_id (str): Mã sinh viên (tài khoản)
        password (str): Mật khẩu
        
    Returns:
        str: Cookie string hoặc None nếu lỗi
    """
    # Lấy trang login và verification token
    initial_cookies, verification_token = get_login_page_and_token()
    
    if not verification_token:
        print("Không thể lấy verification token")
        return None
    
    # Tạo cookie string từ initial cookies
    initial_cookie_str = '; '.join([f"{key}={value}" for key, value in initial_cookies.items()])
    
    url = "https://qldt1.ute.udn.vn/Account/Login"
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        'dnt': '1',
        'origin': 'https://qldt1.ute.udn.vn',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'referer': 'https://qldt1.ute.udn.vn/login',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'cookie': initial_cookie_str
    }
    
    # Data form cho login
    data = {
        'Email': student_id,
        'Password': password,
        '__RequestVerificationToken': verification_token,
        'RememberMe': 'false'
    }
    
    try:
        response = requests.post(url, data=data, headers=headers, allow_redirects=False)
        
        # Kiểm tra response
        if response.status_code == 302:  # Redirect nghĩa là login thành công
            # Lấy tất cả cookies từ response
            all_cookies = {**initial_cookies}
            all_cookies.update(response.cookies.get_dict())
            
            # Tạo cookie string đầy đủ
            cookie_string = '; '.join([f"{key}={value}" for key, value in all_cookies.items()])
            
            print("Đăng nhập thành công!")
            return cookie_string
        else:
            print(f"Đăng nhập thất bại. Status code: {response.status_code}")
            if response.text:
                # Có thể parse HTML để lấy thông báo lỗi chi tiết
                soup = BeautifulSoup(response.text, 'html.parser')
                error_msg = soup.find('div', class_='text-danger')
                if error_msg:
                    print(f"Lỗi: {error_msg.get_text().strip()}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi đăng nhập: {e}")
        return None

def get_available_subjects(cookie):
    """
    Lấy danh sách môn học có thể đăng ký từ trang web
    
    Args:
        cookie (str): Cookie string cho authentication
    
    Returns:
        list: Danh sách môn học có thể đăng ký
        Mỗi môn học là dict có keys: MaHP, TenHP, TenLopHP, SoTC, MaLHP, MaGV, GiangVien
    """
    
    url = "https://qldt1.ute.udn.vn/sinh-vien/dang-ky-mon-hoc"
    
    # Headers cho GET request
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7,fr-FR;q=0.6,fr;q=0.5',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'referer': 'https://qldt1.ute.udn.vn/login?ReturnUrl=%2Fsinh-vien%2Fdang-ky-mon-hoc',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'cookie': cookie
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm table chứa danh sách môn học
        table = soup.find('table', class_='table table-bordered table-hover')
        if not table:
            print("Không tìm thấy bảng môn học")
            return []
        
        subjects = []
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 12:  # Đảm bảo row có đủ columns
                    checkbox = row.find('input', {'type': 'checkbox'})
                    if checkbox:
                        # Lấy thông tin từ HTML
                        ma_hp = cols[0].text.strip()
                        ten_hp = cols[1].text.strip()
                        ten_lop_hp = cols[2].text.strip()
                        so_tc = cols[3].text.strip()
                        giang_vien = cols[9].text.strip()
                        
                        # Lấy thông tin từ data attributes của checkbox
                        ma_lhp = checkbox.get('data-malph', '')
                        ma_gv = checkbox.get('data-malgv', '')
                        
                        subject = {
                            'MaHP': ma_hp,
                            'TenHP': ten_hp,
                            'TenLopHP': ten_lop_hp,
                            'SoTC': so_tc,
                            'MaLHP': ma_lhp,
                            'MaGV': ma_gv,
                            'GiangVien': giang_vien
                        }
                        subjects.append(subject)
        
        print(f"Tìm thấy {len(subjects)} môn học có thể đăng ký")
        return subjects
        
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lấy danh sách môn học: {e}")
        return []
    except Exception as e:
        print(f"Lỗi parse HTML: {e}")
        return []

def filter_subjects_by_names(subjects, class_names, student_id):
    """
    Lọc môn học theo tên lớp học phần
    
    Args:
        subjects (list): Danh sách tất cả môn học
        class_names (list): Danh sách tên lớp HP cần lọc
        student_id (str): Mã sinh viên
    
    Returns:
        list: Danh sách môn học đã lọc với format để đăng ký
    """
    filtered = []
    for subject in subjects:
        if subject['TenLopHP'] in class_names:
            # Convert sang format cho register_subjects
            filtered_subject = {
                'MaHP': subject['MaHP'],
                'MaSV': student_id,
                'MaHocKy': '125',    # Hard code học kỳ, có thể thay đổi
                'MaLHP': subject['MaLHP'],
                'MaGV': subject['MaGV']
            }
            filtered.append(filtered_subject)
    
    return filtered

def save_subjects_cache(subjects, cache_file="all_subjects_cache.json"):
    """
    Lưu danh sách môn học vào file cache
    
    Args:
        subjects (list): Danh sách môn học
        cache_file (str): Đường dẫn file cache
    """
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(subjects, f, ensure_ascii=False, indent=2)
        print(f"Đã lưu cache vào {cache_file}")
    except Exception as e:
        print(f"Lỗi khi lưu cache: {e}")

def load_subjects_cache(cache_file="all_subjects_cache.json"):
    """
    Load danh sách môn học từ file cache
    
    Args:
        cache_file (str): Đường dẫn file cache
        
    Returns:
        list: Danh sách môn học hoặc None nếu không load được
    """
    try:
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                subjects = json.load(f)
            print(f"Đã load {len(subjects)} môn học từ cache")
            return subjects
        else:
            print("File cache không tồn tại")
            return None
    except Exception as e:
        print(f"Lỗi khi load cache: {e}")
        return None

def register_subjects(subjects_list, cookie):
    """
    Đăng ký môn học cho sinh viên
    
    Args:
        subjects_list (list): List các môn học cần đăng ký
        Mỗi môn học là dict có keys: MaHP, MaSV, MaHocKy, MaLHP, MaGV
        cookie (str): Cookie string cho authentication
    
    Returns:
        dict: Response từ API
    """
    
    url = "https://qldt1.ute.udn.vn/sinh-vien/dang-ky-mon-hoc"
    
    # Headers từ curl command
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7,fr-FR;q=0.6,fr;q=0.5',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'dnt': '1',
        'origin': 'https://qldt1.ute.udn.vn',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://qldt1.ute.udn.vn/sinh-vien/dang-ky-mon-hoc',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'cookie': cookie
    }
    
    # Tạo data form từ subjects_list
    form_data = {}
    for i, subject in enumerate(subjects_list):
        form_data[f'selectedSubjects[{i}][MaHP]'] = subject['MaHP']
        form_data[f'selectedSubjects[{i}][MaSV]'] = subject['MaSV']
        form_data[f'selectedSubjects[{i}][MaHocKy]'] = subject['MaHocKy']
        form_data[f'selectedSubjects[{i}][MaLHP]'] = subject['MaLHP']
        form_data[f'selectedSubjects[{i}][MaGV]'] = subject['MaGV']
    
    try:
        response = requests.post(url, data=form_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi đăng ký môn học: {e}")
        return None
    except ValueError as e:
        print(f"Lỗi parse JSON: {e}")
        return None

def check_registration_status(registration_id, cookie):
    """
    Kiểm tra trạng thái đăng ký môn học
    
    Args:
        registration_id (str): ID của đăng ký (lấy từ redirectUrl)
        cookie (str): Cookie string cho authentication
    
    Returns:
        dict: Response từ API với thông tin trạng thái
        {
            "isCompleted": bool,
            "isSuccess": bool, 
            "step": int,
            "maHocKy": int,
            "message": str,
            "progressPercent": int
        }
    """
    
    url = f"https://qldt1.ute.udn.vn/sinh-vien/check-dang-ky-status?id={registration_id}"
    
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': f'https://qldt1.ute.udn.vn/sinh-vien/dang-xu-ly/{registration_id}',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'cookie': cookie
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(response.text)
        data = response.text
        print(json.dumps(data, indent=4, ensure_ascii=False))
        return data
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi kiểm tra trạng thái đăng ký {registration_id}: {e}")
        return None
    except ValueError as e:
        print(f"Lỗi parse JSON: {e}")
        return None

def extract_registration_id(redirect_url):
    """
    Trích xuất registration ID từ redirectUrl
    
    Args:
        redirect_url (str): URL redirect từ response (VD: '/sinh-vien/dang-xu-ly/8385')
    
    Returns:
        str: Registration ID hoặc None nếu không tìm thấy
    """
    if not redirect_url:
        return None
    
    # Extract số từ cuối URL
    match = re.search(r'/dang-xu-ly/(\d+)', redirect_url)
    if match:
        return match.group(1)
    return None

def register_subjects_batch(subjects_list, cookie, batch_size=20):
    """
    Spam đăng ký tất cả môn học nhiều lần và trả về danh sách registration IDs
    
    Args:
        subjects_list (list): List các môn học cần đăng ký (tất cả sẽ được đăng ký mỗi lần)
        cookie (str): Cookie string cho authentication
        batch_size (int): Số lần spam đăng ký (số registration IDs sẽ tạo ra)
    
    Returns:
        list: Danh sách registration IDs để theo dõi
    """
    registration_ids = []
    
    print(f"Spam {len(subjects_list)} môn học {batch_size} lần")
    
    # Spam đăng ký batch_size lần
    for i in range(batch_size):
        print(f"Đăng ký lần {i + 1}/{batch_size}: {len(subjects_list)} môn học")
        
        # Đăng ký tất cả môn học trong danh sách
        register_result = register_subjects(subjects_list, cookie)
        
        if register_result and register_result.get('success'):
            # Extract registration ID từ redirectUrl
            registration_id = extract_registration_id(register_result.get('redirectUrl'))
            if registration_id:
                registration_ids.append({
                    'id': registration_id,
                    'subjects_count': len(subjects_list),
                    'attempt': i + 1
                })
                print(f"Lần {i + 1} - Registration ID: {registration_id}")
            else:
                print(f"Không thể lấy registration ID từ lần {i + 1}")
        else:
            print(f"Lỗi đăng ký lần {i + 1}")
    
    return registration_ids

def monitor_registration_status(registration_ids, cookie, check_interval=2):
    """
    Theo dõi trạng thái đăng ký của tất cả registration IDs
    
    Args:
        registration_ids (list): Danh sách registration IDs từ register_subjects_batch
        cookie (str): Cookie string cho authentication
        check_interval (int): Thời gian chờ giữa các lần check (giây)
    
    Returns:
        dict: Kết quả cuối cùng của tất cả registration
    """
    print(f"\nBắt đầu theo dõi {len(registration_ids)} registration...")
    
    pending_registrations = registration_ids.copy()
    completed_registrations = []
    
    while pending_registrations:
        print(f"\nKiểm tra trạng thái {len(pending_registrations)} registration đang chờ...")
        
        for reg_info in pending_registrations[:]:  # Copy list để có thể modify trong loop
            reg_id = 46994
            status = check_registration_status(reg_id, cookie)
            
            if status:
                print(f"Registration {reg_id} (Lần {reg_info['attempt']}): {status.get('message', 'N/A')} - {status.get('progressPercent', 0)}%")
                
                if status.get('isCompleted'):
                    # Registration hoàn thành
                    reg_info['final_status'] = status
                    reg_info['success'] = status.get('isSuccess', False)
                    completed_registrations.append(reg_info)
                    pending_registrations.remove(reg_info)
                    
                    if status.get('isSuccess'):
                        print("Status: {status}")
                        print(f"--------------------------------")
                        print(f"✓ Registration {reg_id} thành công!")
                        print(f"--------------------------------")
                        return completed_registrations
                    else:
                        print(f"✗ Registration {reg_id} thất bại: {status.get('message', '')}")
            else:
                print(f"Không thể kiểm tra registration {reg_id}")
        
        # Nếu còn registration chưa hoàn thành, chờ và check lại
        if pending_registrations:
            print(f"Chờ {check_interval} giây trước khi check lại...")
            time.sleep(check_interval)
    
    print(f"\nHoàn thành theo dõi tất cả registration!")
    print(f"Thành công: {len([r for r in completed_registrations if r.get('success')])}")
    print(f"Thất bại: {len([r for r in completed_registrations if not r.get('success')])}")
    
    return completed_registrations

def extract_status_id(html_response):
    if not html_response:
        return None
    
    # Tìm pattern: const statusId = '11719';
    match = re.search(r"const statusId = '(\d+)';", html_response)
    if match:
        return match.group(1)
    return None

def confirm_registration(student_id, cookie):
    """
    Gọi API xác nhận đăng ký và trả về status ID
    
    Args:
        student_id (str): Mã sinh viên
        cookie (str): Cookie string cho authentication
        
    Returns:
        str: Status ID hoặc None nếu lỗi
    """
    url = "https://qldt1.ute.udn.vn/sinh-vien/xac-nhan-dang-ky"
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7,fr-FR;q=0.6,fr;q=0.5',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        'dnt': '1',
        'origin': 'https://qldt1.ute.udn.vn',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'referer': 'https://qldt1.ute.udn.vn/sinh-vien/xac-nhan-dang-ky?maHocKy=125',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'cookie': cookie
    }

    data = {
        'MaSV': student_id,
        'MaHocKy': '125'
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        
        # Extract status ID từ HTML response
        status_id = extract_status_id(response.text)
        return status_id
        
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi xác nhận đăng ký: {e}")
        return None

def confirm_registration_batch(student_id, cookie, batch_size=20):
    """
    Spam xác nhận đăng ký nhiều lần và trả về danh sách status IDs
    
    Args:
        student_id (str): Mã sinh viên
        cookie (str): Cookie string cho authentication
        batch_size (int): Số lần spam xác nhận (số status IDs sẽ tạo ra)
    
    Returns:
        list: Danh sách status IDs để theo dõi
    """
    status_ids = []
    
    print(f"\nBắt đầu spam xác nhận đăng ký {batch_size} lần")
    
    # Spam xác nhận batch_size lần
    for i in range(batch_size):
        print(f"Xác nhận lần {i + 1}/{batch_size}")
        
        # Xác nhận đăng ký
        status_id = confirm_registration(student_id, cookie)
        
        if status_id:
            status_ids.append({
                'id': status_id,
                'attempt': i + 1
            })
            print(f"Lần {i + 1} - Status ID: {status_id}")
        else:
            print(f"Không thể lấy status ID từ lần {i + 1}")
    
    return status_ids

def check_confirmation_status(status_id, cookie):
    """
    Kiểm tra trạng thái xác nhận đăng ký
    
    Args:
        status_id (str): Status ID của xác nhận đăng ký
        cookie (str): Cookie string cho authentication
    
    Returns:
        dict: Response từ API với thông tin trạng thái
        {
            "isCompleted": bool,
            "isSuccess": bool, 
            "step": int,
            "maHocKy": int,
            "message": str,
            "progressPercent": int
        }
    """
    
    url = f"https://qldt1.ute.udn.vn/sinh-vien/check-dang-ky-status?id={status_id}"
    
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7,fr-FR;q=0.6,fr;q=0.5',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': f'https://qldt1.ute.udn.vn/sinh-vien/dang-xu-ly/{status_id}',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'cookie': cookie
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi kiểm tra trạng thái xác nhận {status_id}: {e}")
        return None
    except ValueError as e:
        print(f"Lỗi parse JSON: {e}")
        return None

def monitor_confirmation_status(status_ids, cookie, check_interval=10):
    """
    Theo dõi trạng thái xác nhận đăng ký của tất cả status IDs
    
    Args:
        status_ids (list): Danh sách status IDs từ confirm_registration_batch
        cookie (str): Cookie string cho authentication
        check_interval (int): Thời gian chờ giữa các lần check (giây)
    
    Returns:
        dict: Kết quả cuối cùng của tất cả confirmations
    """
    print(f"\nBắt đầu theo dõi {len(status_ids)} confirmation...")
    
    pending_confirmations = status_ids.copy()
    completed_confirmations = []
    
    while pending_confirmations:
        print(f"\nKiểm tra trạng thái {len(pending_confirmations)} confirmation đang chờ...")
        
        for conf_info in pending_confirmations[:]:  # Copy list để có thể modify trong loop
            conf_id = conf_info['id']
            status = check_confirmation_status(conf_id, cookie)
            
            if status:
                print(f"Confirmation {conf_id} (Lần {conf_info['attempt']}): {status.get('message', 'N/A')} - {status.get('progressPercent', 0)}%")
                
                if status.get('isCompleted'):
                    # Confirmation hoàn thành
                    conf_info['final_status'] = status
                    conf_info['success'] = status.get('isSuccess', False)
                    completed_confirmations.append(conf_info)
                    pending_confirmations.remove(conf_info)
                    
                    if status.get('isSuccess'):
                        print(f"✓ Confirmation {conf_id} thành công!")
                        # Có 1 confirmation thành công là đủ, break ngay
                        print(f"\nHoàn thành xác nhận đăng ký!")
                        return completed_confirmations
                    else:
                        print(f"✗ Confirmation {conf_id} thất bại: {status.get('message', '')}")
            else:
                print(f"Không thể kiểm tra confirmation {conf_id}")
        
        # Nếu còn confirmation chưa hoàn thành, chờ và check lại
        if pending_confirmations:
            print(f"Chờ {check_interval} giây trước khi check lại...")
            time.sleep(check_interval)
    
    print(f"\nTất cả confirmation đều thất bại!")
    print(f"Thành công: {len([c for c in completed_confirmations if c.get('success')])}")
    print(f"Thất bại: {len([c for c in completed_confirmations if not c.get('success')])}")
    
    return completed_confirmations

# Cấu hình được load từ file config.json

if __name__ == "__main__":
    # Lấy cấu hình
    config = load_config()
    if not config:
        print("Không thể tải cấu hình. Vui lòng đảm bảo file config.json tồn tại.")
        exit(1)

    # Đăng nhập
    student_id = config.get('student_id')
    password = config.get('password')

    if not student_id or not password:
        print("Vui lòng cập nhật student_id và password trong config.json")
        exit(1)

    cookie = login(student_id, password)
    if not cookie:
        print("Đăng nhập thất bại. Vui lòng kiểm tra thông tin đăng nhập.")
        exit(1)

    # Lấy các config values
    class_names_to_register = config.get('class_names_to_register', [])
    cache_file = config.get('cache_file', 'all_subjects_cache.json')
    force_refresh_cache = config.get('force_refresh_cache', False)
    batch_size = config.get('batch_size', 20)
    check_interval = config.get('check_interval', 10)
    
    # Lấy danh sách tất cả môn học có thể đăng ký
    all_subjects = None
    
    # Kiểm tra cache trước nếu không force refresh
    if not force_refresh_cache:
        print("Kiểm tra cache...")
        all_subjects = load_subjects_cache(cache_file)
    
    # Nếu không có cache hoặc force refresh, crawl từ web
    if all_subjects is None or force_refresh_cache:
        print("Đang crawl danh sách môn học từ web...")
        all_subjects = get_available_subjects(cookie)
        
        if not all_subjects:
            print("Không thể lấy danh sách môn học")
            exit(1)
        
        # Lưu vào cache
        save_subjects_cache(all_subjects, cache_file)
    else:
        print("Sử dụng dữ liệu từ cache")
    
    # Lọc môn học theo tên lớp HP được cấu hình
    subjects_to_register = filter_subjects_by_names(all_subjects, class_names_to_register, student_id)
    
    if subjects_to_register:
        print(f"\nSẽ đăng ký {len(subjects_to_register)} môn học:")
        for subject in subjects_to_register:
            # Tìm thông tin chi tiết từ all_subjects
            detail = next((s for s in all_subjects if s['MaHP'] == subject['MaHP'] and s['MaLHP'] == subject['MaLHP']), {})
            print(f"- {subject['MaHP']}: {detail.get('TenHP', '')} - {detail.get('TenLopHP', '')}")
        
        # # Đăng ký môn học
        # print("\n" + "="*50)
        # print("BƯỚC 1: ĐĂNG KÝ MÔN HỌC")
        # print("="*50)
        # registration_ids = register_subjects_batch(subjects_to_register, cookie, batch_size)
        
        # if registration_ids:
        #     completed_registrations = monitor_registration_status(registration_ids, cookie, check_interval)
                
        #     # Nếu có registration thành công, tiến hành xác nhận đăng ký
        #     if completed_registrations and any(r.get('success') for r in completed_registrations):
        #         print("\n" + "="*50)
        #         print("BƯỚC 2: XÁC NHẬN ĐĂNG KÝ")
        #         print("="*50)
                
        # Spam xác nhận đăng ký
        status_ids = confirm_registration_batch(student_id, cookie, 1)
        
        if status_ids:
            completed_confirmations = monitor_confirmation_status(status_ids, cookie, check_interval)
            
            # Kiểm tra kết quả cuối cùng
            if completed_confirmations and any(c.get('success') for c in completed_confirmations):
                print("\n🎉 HOÀN THÀNH! Đăng ký môn học thành công!")
            else:
                print("\n❌ Xác nhận đăng ký thất bại!")
        else:
            print("\nKhông thể tạo confirmation request nào!")
    # else:
    #     print("\n❌ Không có registration nào thành công!")
    else:
        print("\nKhông tìm thấy môn học nào phù hợp với danh sách cấu hình")
