import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

"""
이 코드는 서강대학교의 도서 요약본 웹사이트에서 책 요약 데이터를 크롤링하는 프로그램입니다.
로그인을 수행한 후, "문학/교육" 섹션에서 도서 목록을 스크롤하며 데이터를 수집하고, PDF 요약본을 다운로드합니다.
"""

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 환경 변수 로드
load_dotenv()
ID = os.getenv("my_id")
PASSWORD = os.getenv("my_password")

# ID 및 PASSWORD 검증
if not ID or not PASSWORD:
    logging.error("환경 변수 (ID 또는 PASSWORD)가 설정되지 않았습니다. .env 파일을 확인하세요.")
    exit()

# 다운로드 폴더 설정
current_directory = os.getcwd()
download_folder = os.path.join(current_directory, "download")
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

# Chrome 드라이버 설정
options = webdriver.ChromeOptions()
preferences = {
    "download.default_directory": download_folder,
    "profile.default_content_settings.popups": 0,
    "directory_upgrade": True
}
options.add_experimental_option("prefs", preferences)

# Chrome 드라이버 실행
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def get_books():
    return driver.find_elements(By.CLASS_NAME, "card-img-top")

try:
    logging.info("로그인 페이지로 이동 중...")
    driver.get('https://sogang.bookcosmos.com/global/university_2011/new/member/login.asp')

    # 학교 탭 클릭 및 로그인
    driver.find_element(By.ID, "university-tab").click()
    driver.find_element(By.ID, "bkUnivName").send_keys("서강대학교")
    driver.find_element(By.CSS_SELECTOR, "#university .btn-access").click()
    time.sleep(2)
    
    # 로그인
    driver.find_element(By.NAME, "bkUserID").send_keys(ID)
    driver.find_element(By.NAME, "bkUserPW").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, 'input[src="/images/btn_login.gif"]').click()
    time.sleep(5)

    # 팝업 닫기
    try:
        close_button = driver.find_element(By.ID, "popup_close_btn")
        if close_button.is_displayed():
            close_button.click()
            logging.info("팝업을 닫았습니다.")
    except NoSuchElementException:
        logging.info("팝업이 없습니다.")
    time.sleep(5)

    # "도서 요약본" 섹션 이동
    main_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "dep1_txt"))
    )
    actions = ActionChains(driver)
    actions.move_to_element(main_menu).click().perform()
    literature_education = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "문학/교육"))
    )
    literature_education.click()
    logging.info("문학/교육 섹션으로 이동 완료!")
    time.sleep(3)

    # 스크롤하여 책 리스트 로드
    target_download_count = 100
    SCROLL_PAUSE_TIME = 2
    last_height = driver.execute_script("return document.body.scrollHeight")
    books = []

    while len(books) < target_download_count:
        books.extend([book for book in get_books() if book not in books])
        logging.info(f"현재 발견된 책의 수: {len(books)}")
        if len(books) >= target_download_count:
            break
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            logging.info("더 이상 스크롤할 콘텐츠가 없습니다.")
            break
        last_height = new_height

    logging.info(f"스크롤 후 최종 발견된 책의 수: {len(books)}")

    # 책 다운로드
    downloaded_count = 0
    for book in books[:target_download_count]:
        try:
            logging.info(f"책 {downloaded_count + 1} 다운로드 시작")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", book)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(book)).click()
            time.sleep(3)
            download_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "pdf-btn"))
            )
            download_button.click()
            logging.info(f"책 {downloaded_count + 1} 다운로드 완료")
            downloaded_count += 1
            driver.back()
            time.sleep(3)
        except ElementClickInterceptedException:
            logging.warning("다른 UI 요소가 클릭을 방해했습니다. 재시도 중...")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});")
            driver.execute_script("arguments[0].click();", book)
        except (NoSuchElementException, TimeoutException) as e:
            logging.error(f"책 다운로드 중 오류 발생: {e}")
            driver.back()
            time.sleep(3)

    logging.info(f"최종 다운로드된 책의 수: {downloaded_count}")

finally:
    driver.quit()
    logging.info("드라이버를 종료합니다.")
