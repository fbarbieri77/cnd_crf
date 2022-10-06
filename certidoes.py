from selenium import webdriver
import selenium.webdriver.support.ui as ui
import csv
import os
import sys
from PIL import Image
from datetime import date

class Logger(object):
    """ get the terminal output for logging """

    def __init__(self):
        path = os.path.realpath(__file__)
        path = path[:path.index(os.path.basename(__file__))]
        log_file = path + 'logfile.log'
        self.terminal = sys.stdout
        self.input = sys.stdin
        self.log = open(log_file, "a")

    def write(self, message):
        self.terminal.write(message)
        self.flush()
        self.log.write(message)  

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass  

cnd_url = "http://servicos.receita.fazenda.gov.br/Servicos/certidao/CNDConjuntaSegVia/ResultadoSegVia.asp?Origem=1&Tipo=1&NI=%s&Senha="
#cnd_url = "http://servicos.receita.fazenda.gov.br/Servicos/certidao/ConsultaCertidaoEF/NIConsultaCertidaoEF.asp"
#	   http://servicos.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/Consultar
cnd_print_xpath = "/html/body/div[2]/table/tbody/tr/td[3]/a"
crf_url = "https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf"
crf_cnpj_xpath = '//*[@id="mainForm:txtInscricao1"]'
crf_captcha_xpath = '//*[@id="mainForm:txtCaptcha"]'
crf_consultar_button_xpath = '//*[@id="mainForm:btnConsultar"]'
crf_certidao_xpath = '//*[@id="mainForm:j_id52"]'
crf_certidao_id = 'mainForm:j_id52'
crf_visualizar_button_xpath = '//*[@id="mainForm:btnVisualizar"]'

def download_cnd(line):
    print("\n******* Download das CND \n")
    browser = webdriver.Chrome()
    for row in line:
        cnpj = row[0]
        name = row[1]
        try:
            browser.get(cnd_url % cnpj)
            frmFlag = browser.find_element_by_css_selector("p").text
            if ("Não existe certidão" in frmFlag):
                print("Não existe CND para %s " % name)
                with open('cnpj_cnd_erro.txt', 'a+') as cnpj_cnd_erro:
                    cnpj_cnd_erro.write(cnpj + '\t' + name + '\n')
            else:
                print_button = browser.find_element_by_xpath(cnd_print_xpath)
                print_button.click()
                browser.close()
                browser.switch_to.window(browser.window_handles[0])
                browser.set_window_size(750, 1000)
#                    browser.maximize_window()
                browser.save_screenshot("CND/cnd_%s.png" % name)
                with open("CND/cnd_%s.pdf" % name, 'a') as img_pdf:
                    png_image = Image.open("CND/cnd_%s.png" % name)
                    rgb = Image.new('RGB', png_image.size, (255, 255, 255))  # white background
                    rgb.paste(png_image, mask=png_image.split()[3])   
                    rgb.save("CND/cnd_%s.pdf" % name, "PDF" , resolution=100.0)
                os.remove("CND/cnd_%s.png" % name)

                print("CND de %s salva" % name)
        except:
            print("CNPJ: {} de {} provavelmente errado. Verifique, por favor.".format(cnpj, name))
            with open('cnpj_cnd_erro.txt', 'a+') as cnpj_cnd_erro:
                cnpj_cnd_erro.write(cnpj + '\t' + name + '\n')
    browser.close()

def download_crf(line):
    print("\n******* Download das CRF\n")
    browser = webdriver.Chrome()
    for row in line:
        cnpj = row[0]
        name = row[1]
        wait = ui.WebDriverWait(browser, 60)
        try:
            browser.get(crf_url)
            cnpj_form = browser.find_element_by_xpath(crf_cnpj_xpath)
            cnpj_form.send_keys(cnpj)
            browser.find_element_by_xpath(crf_captcha_xpath).click()
            wait.until(lambda browser: browser.find_elements_by_xpath(crf_certidao_xpath) )
            browser.find_elements_by_id(crf_certidao_id)[0].click()
            wait.until(lambda browser: browser.find_elements_by_xpath(crf_visualizar_button_xpath) )
            browser.find_elements_by_xpath(crf_visualizar_button_xpath)[0].click()
            browser.save_screenshot("CRF/crf_%s.png" % name)
            with open("CRF/crf_%s.pdf" % name, 'a') as img_pdf:
                png_image = Image.open("CRF/crf_%s.png" % name)
                rgb = Image.new('RGB', png_image.size, (255, 255, 255))  # white background
                rgb.paste(png_image, mask=png_image.split()[3])   
                rgb.save("CRF/crf_%s.pdf" % name, "PDF" , resolution=100.0)
            os.remove("CRF/crf_%s.png" % name)       
            print("CRF de %s salva" % name)
        except:
            print("CNPJ: {} de {} provavelmente errado. Verifique, por favor.".format(cnpj, name))
            with open('cnpj_cnd_erro.txt', 'a+') as cnpj_cnd_erro:
                cnpj_cnd_erro.write(cnpj + '\t' + name + '\n')
    browser.close()

def main():
    sys.stdout = Logger()

    print("Download das CND e CRF de cnpj.txt em {}".format(date.today()))
    
    print("Verificar CND? s/n")
    issue_cnd = input()
    if issue_cnd == 's':
        if not os.path.exists('CND'):
            os.makedirs('CND')
        with open('cnpj.txt', 'r') as cnpj_file:
            line = csv.reader(cnpj_file, delimiter='\t')
            download_cnd(line)
    print("Verificar CRF? s/n")
    issue_crf = input()
    if issue_crf == 's':
        if not os.path.exists('CRF'):
            os.makedirs('CRF')
        with open('cnpj.txt', 'r') as cnpj_file:
            line = csv.reader(cnpj_file, delimiter='\t')
            download_crf(line)

    print("Fim do processo")




if __name__ == '__main__':
    main()

    """ to open the print menu
    appState = {
        "recentDestinations": [
            {
                "id": "Save as PDF",
                "origin": "local"
            }
        ],
        "selectedDestinationId": "Save as PDF",
        "version": 2
    }
    profile = {'printing.print_preview_sticky_settings.appState': json.dumps(appState)}
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('prefs', profile)
    chrome_options.add_argument('--kiosk-printing')

    browser = webdriver.Chrome(chrome_options=chrome_options)

    browser.execute_script("window.print();")

    # another example on how to wait until a button is clicked
    #consultar_button = ui.WebDriverWait(browser, 10).until(browser.element_to_be_clickable(By.XPATH, crf_certidao_xpath))
    """