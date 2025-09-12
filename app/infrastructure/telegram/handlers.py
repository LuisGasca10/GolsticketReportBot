import os
import asyncio # <-- 1. Importamos la librería 'asyncio' para pausas no bloqueantes
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
# Casos de uso y entidades necesarios para ambos flujos
from app.domain.entities.entities import Ticket
from app.domain.use_cases.registrar_ticket import RegistrarTicketUseCase
from app.domain.use_cases.importar_ticket import ImportarTicketUseCase
from app.domain.use_cases.generar_reporte_tickets import GenerarReporteTicketsUseCase
from app.domain.use_cases.registrar_usuario import RegistrarUsuarioUseCase
from app.domain.use_cases.obtener_usuario import ObtenerUsuarioUseCase

# Estados de la conversación para el registro manual
(
    GET_TICKET_NUM,
    GET_SERVICIO,
    GET_USUARIO,
    GET_CORREO,
    GET_EMPRESA,
) = range(5)

class BotHandlers:
    def __init__(
        self,
        registrar_ticket_use_case: RegistrarTicketUseCase,
        importar_ticket_use_case: ImportarTicketUseCase,
        generar_reporte_use_case: GenerarReporteTicketsUseCase,
        registrar_usuario_use_case: RegistrarUsuarioUseCase,
        obtener_usuario_use_case: ObtenerUsuarioUseCase
    ):
        self.registrar_ticket_use_case = registrar_ticket_use_case
        self.importar_ticket_use_case = importar_ticket_use_case
        self.generar_reporte_use_case = generar_reporte_use_case
        self.registrar_usuario_use_case = registrar_usuario_use_case
        self.obtener_usuario_use_case = obtener_usuario_use_case

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "¡Hola! Soy tu bot de gestión de tickets.\n\n"
            "Si es tu primera vez, regístrate con /registrar <Tu Nombre Completo>.\n\n"
            "Tienes dos formas de añadir tickets:\n"
            "1.  `/nuevoticket` -> Inicia una conversación para registrar un ticket manualmente.\n"
            "2.  `/importar <ID>` -> Extrae los datos de un ticket automáticamente desde la web.\n\n"
            "Usa /reporte para generar tu reporte semanal."
        )

    async def registrar_usuario(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        try:
            if not context.args:
                await update.message.reply_text("ERROR: Debes proporcionar tu nombre.\nUso: /registrar Nombre Apellido")
                return
            
            nombre_completo = " ".join(context.args)
            self.registrar_usuario_use_case.ejecutar(user_id, nombre_completo)
            await update.message.reply_text(f"✅ ¡Gracias, {nombre_completo}! Tu registro se ha completado.")
        except ValueError as e:
            await update.message.reply_text(f"⚠️ {e}")
        except Exception:
            await update.message.reply_text("❌ Ocurrió un error inesperado durante el registro.")

    # --- FLUJO 1: CONVERSACIÓN MANUAL ---
    async def nuevo_ticket_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.message.from_user.id
        usuario = self.obtener_usuario_use_case.ejecutar(user_id)
        
        if not usuario:
            await update.message.reply_text("⚠️ No estás registrado. Por favor, regístrate primero con:\n/registrar <Tu Nombre Completo>")
            return ConversationHandler.END
            
        await update.message.reply_text("Iniciando registro manual. Por favor, dime el número de ticket.")
        return GET_TICKET_NUM

    async def get_ticket_num(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["numero_ticket"] = update.message.text
        await update.message.reply_text("Gracias. Ahora, ¿cuál es el servicio afectado?")
        return GET_SERVICIO

    async def get_servicio(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["servicio"] = update.message.text
        await update.message.reply_text("Entendido. ¿Quién es el usuario que reporta?")
        return GET_USUARIO

    async def get_usuario(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["usuario_reporta"] = update.message.text
        await update.message.reply_text("OK. ¿Cuál es el correo de ese usuario?")
        return GET_CORREO

    async def get_correo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["correo_usuario"] = update.message.text
        await update.message.reply_text("Perfecto. Por último, ¿a qué empresa pertenece?")
        return GET_EMPRESA

    async def get_empresa(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["empresa"] = update.message.text
        
        ticket = Ticket(
            id=None,
            user_id=update.message.from_user.id,
            chat_id=update.message.chat_id,
            fecha=datetime.now(),
            numero_ticket=context.user_data["numero_ticket"],
            servicio=context.user_data["servicio"],
            usuario_reporta=context.user_data["usuario_reporta"],
            correo_usuario=context.user_data["correo_usuario"],
            empresa=context.user_data["empresa"],
            atendido_por="" # El caso de uso lo rellenará
        )
        
        try:
            self.registrar_ticket_use_case.ejecutar(ticket)
            await update.message.reply_text(f"✅ Ticket {ticket.numero_ticket} registrado manualmente.")
        except ValueError as e:
            await update.message.reply_text(f"⚠️ {e}")

        context.user_data.clear()
        return ConversationHandler.END

    async def cancelar(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Acción cancelada.")
        context.user_data.clear()
        return ConversationHandler.END

    # --- FLUJO 2: IMPORTACIÓN POR WEB SCRAPING ---
    async def importar_ticket(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        chat_id = update.message.chat_id
        
        usuario = self.obtener_usuario_use_case.ejecutar(user_id)
        if not usuario:
            await update.message.reply_text("⚠️ No estás registrado. Usa /registrar primero.")
            return

        try:
            if not context.args or not context.args[0].isdigit():
                await update.message.reply_text("Uso: /importar <ID del Ticket>")
                return

            ticket_id = int(context.args[0])
            await update.message.reply_text(f"⚙️ Importando ticket {ticket_id} desde la web...")
            
            ticket = self.importar_ticket_use_case.ejecutar(ticket_id, user_id, chat_id)
            
            mensaje_respuesta = (
                f"✅ Ticket #{ticket.numero_ticket} importado y guardado.\n\n"
                f"**Servicio:** {ticket.servicio}\n"
                f"**Empresa:** {ticket.empresa}\n"
                f"**Reportado por:** {ticket.usuario_reporta}\n"
                f"**Atendido por:** {ticket.atendido_por}"
            )
            await update.message.reply_text(mensaje_respuesta, parse_mode='Markdown')

        except ValueError as e:
            await update.message.reply_text(f"⚠️ {e}")
        except Exception as e:
            print(f"Error en importación: {e}")
            await update.message.reply_text("❌ Error inesperado al importar.")

    # --- FUNCIONALIDAD COMÚN ---
    async def generar_reporte(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        usuario = self.obtener_usuario_use_case.ejecutar(user_id)
        if not usuario:
            await update.message.reply_text("⚠️ No estás registrado. Usa /registrar primero.")
            return

        await update.message.reply_text(f"⚙️ Generando tu reporte semanal, {usuario.nombre_completo}...")
        
        ruta_archivo = None
        try:
            ruta_archivo = self.generar_reporte_use_case.ejecutar(user_id, "Reporte de tickets atendidos.")
            
            with open(ruta_archivo, "rb") as file:
                file_content = file.read()

            await context.bot.send_document(
                chat_id=update.message.chat_id,
                document=file_content,
                filename=os.path.basename(ruta_archivo),
            )
        
        except ValueError as e:
            await update.message.reply_text(f"⚠️ {e}")
            return # Salimos para no intentar borrar un archivo que pudo no crearse
        except Exception as e:
            print(f"Error inesperado al generar o enviar el reporte: {e}")
            await update.message.reply_text("❌ Ocurrió un error al generar el reporte.")
            return # Salimos por el mismo motivo
        
        finally:
            # --- CORRECCIÓN FINAL ---
            # Este bloque se ejecuta siempre, haya habido un error o no.
            # Su único trabajo es intentar limpiar el archivo temporal.
            if ruta_archivo and os.path.exists(ruta_archivo):
                # Usamos una pausa asíncrona que no bloquea el bot
                await asyncio.sleep(2) 
                try:
                    os.remove(ruta_archivo)
                    print(f"Archivo temporal {ruta_archivo} eliminado correctamente.")
                except OSError as e:
                    # Si la limpieza falla, solo lo mostramos en la consola del desarrollador.
                    # El usuario no recibirá este mensaje.
                    print(f"No se pudo eliminar el archivo temporal {ruta_archivo}: {e}")

    def get_conversation_handler(self) -> ConversationHandler:
        return ConversationHandler(
            entry_points=[CommandHandler("nuevoticket", self.nuevo_ticket_start)],
            states={
                GET_TICKET_NUM: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_ticket_num)],
                GET_SERVICIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_servicio)],
                GET_USUARIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_usuario)],
                GET_CORREO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_correo)],
                GET_EMPRESA: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_empresa)],
            },
            fallbacks=[CommandHandler("cancelar", self.cancelar)],
        )

