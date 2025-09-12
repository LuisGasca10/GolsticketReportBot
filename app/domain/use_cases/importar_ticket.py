from app.domain.repositories.ticket_repository import ITicketRepository
from app.domain.repositories.user_repository import IUsuarioRepository
from app.domain.scraping.scraper_interface import ITicketScraper

class ImportarTicketUseCase:
    def __init__(self, scraper: ITicketScraper, ticket_repo: ITicketRepository, usuario_repo: IUsuarioRepository):
        self.scraper = scraper
        self.ticket_repo = ticket_repo
        self.usuario_repo = usuario_repo

    def ejecutar(self, ticket_id: int, user_id: int, chat_id: int):
        usuario_que_importa = self.usuario_repo.obtener_por_telegram_id(user_id)
        if not usuario_que_importa:
            raise ValueError("No estás registrado. Usa /registrar primero.")

        ticket = self.scraper.obtener_datos_ticket(ticket_id, user_id, chat_id)
        
        if not ticket:
            raise ValueError(f"No se pudo encontrar o procesar el ticket con ID {ticket_id}.")
    
        if ticket.atendido_por == 'No asignado':
            ticket.atendido_por = usuario_que_importa.nombre_completo

        self.ticket_repo.agregar(ticket, usuario_que_importa.id)
        return ticket