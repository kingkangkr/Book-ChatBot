import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()
ID = os.getenv("my_id")
PASSWORD = os.getenv("my_password")

# 다운로드 폴더 설정
current_directory = os.getcwd()
download_folder = os.path.join(current_directory, "download")

if not os.path.exists(download_folder):
    os.makedirs(download_folder)

# Chrome 드라이버 경로 및 다운로드 설정
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

try:
    # 1. 로그인 창 접속 및 학교 이름 입력
    driver.get('https://sogang.bookcosmos.com/global/university_2011/new/member/login.asp')

    # 학교 탭 클릭
    school_tab = driver.find_element(By.ID, "university-tab")
    school_tab.click()

    # 학교 이름 입력
    school_name_input = driver.find_element(By.ID, "bkUnivName")
    school_name_input.send_keys("서강대학교")

    # 검색 버튼 클릭
    search_button = driver.find_element(By.CSS_SELECTOR, "#university .btn-access")
    search_button.click()

    # 로그인 창으로 넘어가도록 대기
    time.sleep(2)

    # 2. 로그인 창에서 아이디와 비밀번호 입력
    username_input = driver.find_element(By.NAME, "bkUserID")
    password_input = driver.find_element(By.NAME, "bkUserPW")

    username_input.send_keys(ID)
    password_input.send_keys(PASSWORD)

    # 로그인 버튼 클릭
    login_button = driver.find_element(By.CSS_SELECTOR, 'input[src="/images/btn_login.gif"]')
    login_button.click()

    # 로그인 후 메인 화면으로 이동할 때까지 대기
    time.sleep(5)

    # 팝업 닫기 예외 처리
    try:
        close_button = driver.find_element(By.ID, "popup_close_btn")
        if close_button.is_displayed():
            close_button.click()
            print("팝업을 닫았습니다.")
    except NoSuchElementException:
        print("팝업이 없습니다.")

    # 팝업을 닫은 후, 메인 화면으로 이동할 수 있도록 대기
    time.sleep(5)

    # 3. "도서 요약본" 클릭
    main_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "dep1_txt"))  # 메인 메뉴 클래스
    )
    # ActionChains로 마우스를 올리기
    actions = ActionChains(driver)
    actions.move_to_element(main_menu).perform()

    # 마우스를 올린 후 나타나는 드롭다운 메뉴에서 "문학/교육" 클릭
    literature_education = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "문학/교육"))
    )
    literature_education.click()

    print("문학/교육 섹션으로 이동 완료!")

    # 문학 섹션에서 책 리스트 가져오기
    time.sleep(3)

    # 목표한 책 다운로드 수 설정
    target_download_count = 100

    SCROLL_PAUSE_TIME = 2  # 스크롤 후 로딩 대기 시간
    last_height = driver.execute_script("return document.body.scrollHeight")
    books = []

    # 스크롤하며 최대한 많은 책 리스트 로드
    while len(books) < target_download_count:
        # 현재까지 로드된 책 리스트 가져오기
        current_books = driver.find_elements(By.CLASS_NAME, "card-img-top")
        books.extend([book for book in current_books if book not in books])  # 중복 제거
        print(f"현재 발견된 책의 수: {len(books)}")

        if len(books) >= target_download_count:
            break

        # 스크롤 다운
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 대기
        time.sleep(SCROLL_PAUSE_TIME)

        # 새로운 높이 계산
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  # 더 이상 새로운 콘텐츠가 로드되지 않을 경우 종료
            print("더 이상 스크롤할 콘텐츠가 없습니다.")
            break
        last_height = new_height

    print(f"스크롤 후 최종 발견된 책의 수: {len(books)}")

    # 발견된 책 리스트에서 다운로드 시작
    downloaded_count = 0
    for index, book in enumerate(books[:target_download_count]):
        try:
            print(f"책 {downloaded_count + 1} 다운로드 시작")

            # 스크롤하여 요소를 화면 중앙으로 이동
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", book)

            # 클릭 가능 상태가 될 때까지 대기 후 클릭
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(book)).click()

            time.sleep(3)

            # 다운로드 버튼 클릭
            download_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "pdf-btn"))
            )
            download_button.click()

            print(f"책 {downloaded_count + 1} 다운로드 완료")

            downloaded_count += 1

            # 뒤로가기
            driver.back()
            time.sleep(3)

            # 책 리스트 다시 로드
            books = driver.find_elements(By.CLASS_NAME, "card-img-top")
        except ElementClickInterceptedException:
            print("다른 UI 요소가 클릭을 방해했습니다. 스크롤 또는 재시도합니다.")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", book)
            driver.execute_script("arguments[0].click();", book)
        except (NoSuchElementException, TimeoutException) as e:
            print(f"책 다운로드 중 오류 발생: {e}")
            driver.back()
            time.sleep(3)

    print(f"최종 다운로드된 책의 수: {downloaded_count}")

finally:
    # 드라이버 종료
    driver.quit()
    print("드라이버를 종료합니다.")
