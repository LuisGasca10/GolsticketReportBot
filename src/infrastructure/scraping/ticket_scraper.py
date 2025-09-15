from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.domain.entities.entities import Ticket
from src.domain.scraping.scraper_interface import ITicketScraper
from src.config.settings import settings

class TicketScraper(ITicketScraper):
    def __init__(self):
        self.USUARIO = settings.SCRAPER_USUARIO
        self.PASSWORD = settings.SCRAPER_PASSWORD
        self.BASE_URL = settings.SCRAPER_BASE_URL
        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)
        self._login()

    def _login(self):
        print("Iniciando sesión en el portal...")
        self.driver.get(f"{self.BASE_URL}1")
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.NAME, "userid"))).send_keys(self.USUARIO)
            self.driver.find_element(By.NAME, "passwd").send_keys(self.PASSWORD)
            self.driver.find_element(By.NAME, "submit").click()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "nav")))
            print("Sesión iniciada.")
        except Exception as e:
            print(f"Error fatal durante el login: {e}")
            self.cerrar_sesion()
            raise

    def obtener_datos_ticket(self, ticket_id: int, user_id: int, chat_id: int) -> Ticket | None:
        url = f"{self.BASE_URL}{ticket_id}"
        print(f"Scraping URL: {url}")
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 6).until(EC.visibility_of_element_located((By.CLASS_NAME, "tixTitle")))
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            if not soup.find('table', class_='ticket_info'): return None

            def get_data_by_header(header_text):
                header_th = soup.find('th', string=lambda t: t and header_text in t)
                return header_th.find_next_sibling('td').text.strip() if header_th and header_th.find_next_sibling('td') else 'N/A'

            AGENTES = { "Alan Emir Jauregui Herrera", "Ángel de Jesús Angulo Alejandro", "Erick Fabian Villarreal Lopez", "Jose Carrillo García", "Karen Naranjo Alejandro", "Luis Gerardo García Suárez", "Luis Guillermo Martinez Gasca", "Miguel Angel Hernández Hernández", "Rogelio Hernández García", "Julio Cesar Lopez Rodriguez" }
            atendido_por_encontrado = next((author.text.strip() for entry in soup.select('div#ticketThread div.thread-entry') if (author := entry.select_one('div.header > b')) and author.text.strip() in AGENTES), 'No asignado')

            # --- CORRECCIÓN FINAL PARA EL CORREO ---
            correo_element = soup.select_one("span[id$='-email']")
            correo_usuario = correo_element.text.strip() if correo_element else 'Correo no encontrado'

            ticket_entity = Ticket(
                id=None,
                user_id=user_id,
                chat_id=chat_id,
                fecha=datetime.now(),
                numero_ticket=str(ticket_id),
                servicio=soup.select_one('td#inline-answer-52 span').text.strip() if soup.select_one('td#inline-answer-52 span') else 'No definido',
                usuario_reporta=soup.select_one("span[id^='user-'][id$='-name']").text.strip(),
                correo_usuario=correo_usuario, # <-- Usamos la variable corregida
                empresa=get_data_by_header('Organización:').split('(')[0].strip(),
                atendido_por=atendido_por_encontrado
            )
            return ticket_entity

        except Exception as e:
            print(f"Error procesando ID {ticket_id}: {e}")
            return None
            
    def cerrar_sesion(self):
        if self.driver: self.driver.quit()

