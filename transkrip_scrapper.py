import json, os, signal, re
import settings
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import TimeoutException,NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import Select

def signal_handle(signalNumber, frame):
    print('Signal recieved: ', signalNumber)
    _cleanup(signalNumber)

def _cleanup(code = 1):
    try:
        global browser
        browser.quit()
    except NameError:
        print("WebDriver belum diinisialisasi.")
    exit(code)

def format_semester(teks_semester):
    bagian = re.sub(r'[()]', '', teks_semester).split()
    if(bagian[0] != 'SEMESTER'):
        return {
            "teks" : teks_semester,
            "semester" : bagian[-1],
            "tipe" : "khusus",
            "tahun_ajaran": bagian[0]
        }
    else:
        return {
            "teks" : teks_semester,
            "semester": bagian[1],
            "tipe" : bagian[-1],
            "tahun_ajaran": bagian[-2]
        }

for sig in (signal.SIGABRT, signal.SIGINT, signal.SIGTERM):
    signal.signal(sig, signal_handle)

url_halaman_depan = "https://akademik.unsri.ac.id/"

daftar_kode_mk = []
transkrip_nilai = []
riwayat_nilai_mk = []

firefox_binary = FirefoxBinary(settings.default_firefox_binary_path)
webdriver_options = Options()
webdriver_options.headless = settings.webdriver_headless

print("Memulai geckodriver")
browser = webdriver.Firefox(options=webdriver_options, firefox_binary=firefox_binary)


print("Mengakses halaman depan SIMAK")
browser.get(url_halaman_depan)
try:
    link_ke_login = browser.find_element_by_link_text(settings.default_fakultas or input('Fakultas: '))
except NoSuchElementException:
    print("Link ke halaman login fakultas tidak ditemukan.")
    _cleanup()

print("Link ke halaman login fakultas ditemukan")
url_utama = link_ke_login.get_attribute('href')[:-1]

url_halaman_gagal_login = f"{url_utama}/login/gagal.php"
url_halaman_login = f"{url_utama}/login/login.php"
url_halaman_transkrip = f"{url_utama}/module/data_akademik/transkrip/utama.php"
url_halaman_utama = f"{url_utama}/utama.php"

print("Mengakses halaman login")
browser.get(url_halaman_login)
username_field = browser.find_element_by_id("username")
password_field = browser.find_element_by_id("password3")
prodi_select = browser.find_element_by_name("id_prodi")
submit_button = browser.find_element_by_xpath("//input[@type='submit' and @value='Login']")

current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
nim = settings.default_nim or input('NIM: ')
password = settings.default_password or input('Password: ')
prodi = settings.default_prodi or input('Prodi: ')

username_field.send_keys(nim)
password_field.send_keys(password)
try:
    Select(prodi_select).select_by_visible_text(prodi)
except NoSuchElementException:
    print("Program Studi tidak valid.")
    _cleanup()

submit_button.click()
if browser.current_url == url_halaman_gagal_login:
    print("NIM/Password salah.")
    _cleanup()

print(f"Login dengan NIM {nim} berhasil")

output_dir = f"output/{nim}"
os.makedirs(output_dir, exist_ok=True)

print("Mengambil halaman transkrip")
browser.get(url_halaman_transkrip)
print("Mengambil dan memproses tabel transkrip nilai")
tabel_transkrip = browser.find_elements_by_xpath(
    "//table[@class='table-common']//tr[preceding-sibling::tr]")
for row in tabel_transkrip:
    info_nilai_mk = row.find_elements_by_tag_name("td")
    daftar_kode_mk.append(info_nilai_mk[1].text)
    transkrip_nilai.append(
        {
            "kode_mk": info_nilai_mk[1].text,
            "nama_mk": info_nilai_mk[2].text,
            "jumlah_pengambilan": info_nilai_mk[3].text,
            "huruf_mutu": info_nilai_mk[4].text,
            "angka_mutu": info_nilai_mk[5].text,
            "kredit": info_nilai_mk[6].text,
            "mutu": info_nilai_mk[7].text,
        },
    )

print("Mengambil dan memproses riwayat nilai")
for kode_mk in daftar_kode_mk:
    browser.get(
        f"{url_utama}/module/data_akademik/transkrip/history.php?kode={kode_mk}"
        )
    tabel_pengambilan_mk = browser.find_elements_by_xpath(
        "//table[@class='table-common']//tr[preceding-sibling::tr]")
    elemen_pertama = tabel_pengambilan_mk[0].find_elements_by_tag_name("td")

    daftar_nilai_mk = []
    info_mk = {
        "nama_mk" : elemen_pertama[2].text,
        "sks": elemen_pertama[3].text,
    }

    for row in tabel_pengambilan_mk:
        info_nilai_mk = row.find_elements_by_tag_name("td")
        info_semester = info_nilai_mk[4].text
        daftar_nilai_mk.append(
            {
                "semester": format_semester(info_semester),
                "dosen": list(map(lambda element: element.text, info_nilai_mk[5].find_elements_by_xpath("//ul/li"))),
                "nilai": info_nilai_mk[6].text,
            },
        )
    riwayat_nilai_mk.append({
        "kode_mk": kode_mk,
        "nama_mk": info_mk["nama_mk"],
        "sks": info_mk["sks"],
        "riwayat_nilai": daftar_nilai_mk
    })

print(f"Menulis keluaran JSON transkrip nilai")
with open(f'{output_dir}/transkrip_nilai_mk_{nim}_{current_time}.json', 'w', encoding='utf-8') as file:
    json.dump(transkrip_nilai, file, ensure_ascii=False, indent=4)

print(f"Menulis keluaran JSON riwayat nilai")
with open(f'{output_dir}/riwayat_nilai_mk_{nim}_{current_time}.json', 'w', encoding='utf-8') as file:
    json.dump(riwayat_nilai_mk, file, ensure_ascii=False, indent=4)

print(f"Proses dumping JSON transkrip nilai untuk NIM {nim} telah selesai")

_cleanup(0)
