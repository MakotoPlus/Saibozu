# -*- coding: utf-8 -*- 
import os, configparser, time, shutil, sys, pathlib, datetime, platform, glob
import logging.config, logging
from selenium import webdriver
from selenium.webdriver.support.select import Select

''' 
 サイボウズにとりあえずログインして記念撮影？

 カレントディレクトリにあるsaibo.iniファイルから設定情報を読み込んで実行される。



 create 2020.07.05 m.fukuda

'''
#-------------------------------------------------------
#  設定ファイル情報取得キー
# -------------------------------------------------------
INI_SECTION_USER = 'USER'
INI_SECTION_BASE = 'BASE'
LOG_CONF ='LOG_CONF'
INI_FILE = 'saibo.ini'
INI_ID_KEY = 'ID'
CHROME_DRIVER_KEY ='CHROME_DRIVER'
WAIT_TIME_KEY = 'WAIT_TIME'
SAIBOUZU_URL_KEY='SAIBOUZU_URL'
USER_NAME_KEY='NAME'
PASSWD_KEY='PASSWD'
GROUP_NAME_KEY ='GROUP_NAME'

#
# 各ページの コントロール名
GROUP_LST_NAME = 'Group'
BTN_KIRIKAE = 'Submit'
BTN_LOGIN = 'Submit'
USER_LST_NAME = '_ID'
TXT_PASSWORD = 'Password'

#ログ名
LOG_NAME=__name__
#--------------------------------------------------------
# グローバル変数
#--------------------------------------------------------
_logger = None
_config = None

#--------------------------------------------------------
# ブラウザオプション
#--------------------------------------------------------
def build_chrome_options():
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.accept_untrusted_certs = True
    #chrome_options.assume_untrusted_cert_issuer = Truechrome_options.add_argument("--no-sandbox")
    #chrome_options.add_argument("--disable-impl-side-painting")
    #chrome_options.add_argument("--disable-setuid-sandbox")
    #chrome_options.add_argument("--disable-seccomp-filter-sandbox")
    #chrome_options.add_argument("--disable-breakpad")
    #chrome_options.add_argument("--disable-images")
    #chrome_options.add_argument("--disable-client-side-phishing-detection")
    #chrome_options.add_argument("--disable-cast")
    #chrome_options.add_argument("--disable-cast-streaming-hw-encoding")
    #chrome_options.add_argument("--disable-cloud-import")
    #chrome_options.add_argument("--disable-popup-blocking"
    #chrome_options.add_argument("--ignore-certificate-errors")
    #chrome_options.add_argument("--disable-session-crashed-bubble")
    #chrome_options.add_argument("--disable-ipv6")
    #chrome_options.add_argument("--allow-http-screen-capture")
    #chrome_options.add_argument("--start-maximized")
    #chrome_options.add_argument('--profile-directory=Default')
    #chrome_options.add_argument('--incognito')
    #chrome_options.add_argument('--noerrdialogs')
    chrome_options.add_argument('--disable-features=RendererCodeIntegrity')
    #chrome_options.add_argument("--window-size=10x10")
    return chrome_options

#--------------------------------------------------------
#
# グローバル変数のログ出力オブジェクト(_logger )を設定する
# init_log
#
#--------------------------------------------------------
def init_log():
    global _logger

    #--------------------------------------------------------
    #ログオブジェクト設定 
    # 1. ログ設定ファイル名もINIファイルから取得する
    # 2. ログオブジェクトを生成してグローバル変数に設定する
    #
    # _logger オブジェクトを利用して、ログの出力レベルを設定して出力する事が可能
    # 例：
    # _logger.critical( 'クリティカルとして出力される' )
    # _logger.error( 'エラーとして出力される' )
    # _logger.warning( 'ワーニングとして出力される' )
    # _logger.info( 'インフォメーションとして出力される' )
    # _logger.debug( 'デバッグとして出力される' )
    # _logger.exception( 'デバッグとして出力される' )
    #--------------------------------------------------------
    log_file_conf = _config.get(INI_SECTION_BASE, LOG_CONF)
    logging.config.fileConfig(log_file_conf, disable_existing_loggers=False)
    _logger = logging.getLogger(LOG_NAME)

#--------------------------------------------------------
#
# 初期処理
#
# 1. ログオブジェクト生成しグルーバル変数へ設定する
# 2. 設定ファイルから情報を取得こちらも使いそうなのでグローバル変数へ設定する
#--------------------------------------------------------
def init():

    global _config

    #--------------------------------------------------------
    # 設定ファイル読込でグローバル変数_configに設定する
    #
    # 設定ファイルオブジェクト(_config)から、get()メソッドで、設定ファイルの内容を取得する事が出来るようになる。
    #
    # 例: [BASE]
    #      CHROME_DIRVER=XXXXX.exe
    #
    #     exefile = _config.get('BASE', 'CHROME_DIRVER' )
    #     exefile  ← 'XXXXX.exe'が入る
    #
    # 1. ソースファイルのカレントディレクトリに設定ファイル(INI_FILE)はある前提なので、
    #    自分自身のフルパスを取得して、ファイル名を設定ファイル名に変更して読み込む
    # 2. 設定ファイルの文字コードはUTF-8の想定
    #
    #--------------------------------------------------------
    ini_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), INI_FILE)
    _config = configparser.SafeConfigParser()
    _config.read(ini_file, encoding='utf-8')
    #ログ設定ファイル取得
    init_log() 

#--------------------------------------------------------
# Chrome ブラウザオブジェクトを生成して返す
#--------------------------------------------------------
def create_browser():
    _logger.info('create_browser start')
    # Chrome ブラウザのオブション情報を取得する
    # はっきりいって沢山ありすぎてわけわからん
    chromeOptions = build_chrome_options()
    # Chrome Driverパス取得
    chrome_driver = _config.get(INI_SECTION_BASE, CHROME_DRIVER_KEY)
    _logger.debug('chrome_driver={0}'.format(chrome_driver))
    browser = webdriver.Chrome(executable_path=chrome_driver, chrome_options=chromeOptions)
    wait_time = _config.get(INI_SECTION_BASE, WAIT_TIME_KEY)
    browser.set_page_load_timeout(float(wait_time))
    return browser

#--------------------------------------------------------
# メイン処理
#
# 下記処理を行う
# 1. Chromeブラウザ生成
# 2. サイボウズサイトへアクセス
# 3. 組織切り替え画面へ遷移し組織を選択
# 4. ログイン画面に戻ってユーザID、パスワードを設定してログイン
# 5. 記念撮影（スクリーンショット）
# 6. ブラウザ閉じる
#--------------------------------------------------------
def run():
    _logger.info('run start')
    #--------------------------------------------------------
    # 1. Chromeブラウザ生成
    #--------------------------------------------------------
    browser = create_browser()

    #--------------------------------------------------------
    # 2. サイボウズサイトへアクセス
    #--------------------------------------------------------
    saibouzu_url = _config.get(INI_SECTION_BASE,SAIBOUZU_URL_KEY)
    browser.get(saibouzu_url)

    #--------------------------------------------------------
    # 3. 組織切り替え画面へ遷移し組織を選択
    #--------------------------------------------------------
    browser.get( saibouzu_url + '?page=LoginGroup&group=2156&bpage=' )
    group_name = _config.get(INI_SECTION_USER, GROUP_NAME_KEY)
    lst_group_name = browser.find_element_by_name(GROUP_LST_NAME)
    select = Select(lst_group_name)
    select.select_by_visible_text(group_name)
    (browser.find_element_by_name(BTN_KIRIKAE)).click()
    _logger.debug( 'サイボウズ 組織変更成功')

    #--------------------------------------------------------
    # 4. ログイン画面に戻ってユーザID、パスワードを設定してログイン
    #--------------------------------------------------------
    user_name = _config.get(INI_SECTION_USER, USER_NAME_KEY)
    user_passwd = _config.get(INI_SECTION_USER, PASSWD_KEY)
    lstUsrName = browser.find_element_by_name(USER_LST_NAME)
    select = Select(lstUsrName)
    select.select_by_visible_text(user_name)
    txtPasswd = browser.find_element_by_name(TXT_PASSWORD)
    txtPasswd.send_keys(user_passwd)
    (browser.find_element_by_name(BTN_LOGIN)).click()
    # 実際にログイン出来たのかは判断していない。ログイン出来たと仮定しているだけ
    _logger.debug( 'サイボウズ ログイン成功')
    #--------------------------------------------------------
    # 5. 記念撮影（スクリーンショット）
    #--------------------------------------------------------
    save_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saibo.png')
    browser.save_screenshot(save_file)
    
    #--------------------------------------------------------
    # 6. ブラウザ閉じる
    #--------------------------------------------------------
    browser.close()
    browser.quit()

#-------------------------------------------------------
# プログラムスタート
#-------------------------------------------------------
if __name__ == '__main__':

    #-------------------------------------------------------
    #プログラムの初期処理を実施します
    #-------------------------------------------------------
    init()
    #初期処理が終わるとログオブジェクトが利用出来るようになるので開始メッセージをログに出力する
    _logger.info('PG START')
    #-------------------------------------------------------
    # メイン処理
    #-------------------------------------------------------
    run()

    #-------------------------------------------------------
    # 終了
    #-------------------------------------------------------
    _logger.info('PG END')
    print('Bye')
    sys.exit(0)

