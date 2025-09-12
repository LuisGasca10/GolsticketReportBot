import os
from datetime import datetime
from uuid import UUID
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
)
# Importamos la tarea de Celery para encolar el scraping
from src.tasks import procesar_ticket_task
# Importamos todos los casos de uso que el bot necesita directamente
from src.domain.entities.entities import Ticket
from src.domain.use_cases.registrar_ticket import RegistrarTicketUseCase
from src.domain.use_cases.generar_reporte_tickets import GenerarReporteTicketsUseCase
from src.domain.use_cases.registrar_usuario import RegistrarUsuarioUseCase
from src.domain.use_cases.obtener_usuario import ObtenerUsuarioUseCase
from src.domain.use_cases.obtener_tickets_semanales import ObtenerTicketsSemanalesUseCase
from src.domain.use_cases.eliminar_ticket import EliminarTicketUseCase

# Estados de la conversación para el registro manual
(GET_TICKET_NUM, GET_SERVICIO, GET_USUARIO, GET_CORREO, GET_EMPRESA) = range(5)

class BotHandlers:
    # El constructor ya no necesita el caso de uso de importación
    def __init__(
        self,
        registrar_ticket_use_case: RegistrarTicketUseCase,
        generar_reporte_use_case: GenerarReporteTicketsUseCase,
        registrar_usuario_use_case: RegistrarUsuarioUseCase,
        obtener_usuario_use_case: ObtenerUsuarioUseCase,
        obtener_tickets_semanales_uc: ObtenerTicketsSemanalesUseCase,
        eliminar_ticket_uc: EliminarTicketUseCase
    ):
        self.registrar_ticket_use_case = registrar_ticket_use_case
        self.generar_reporte_use_case = generar_reporte_use_case
        self.registrar_usuario_use_case = registrar_usuario_use_case
        self.obtener_usuario_use_case = obtener_usuario_use_case
        self.obtener_tickets_semanales_use_case = obtener_tickets_semanales_uc
        self.eliminar_ticket_use_case = eliminar_ticket_uc

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "¡Hola! Soy tu bot de gestión de tickets.\n\n"
            "Comandos disponibles:\n"
            "/registrar <Nombre Completo>\n"
            "/nuevoticket (registro manual)\n"
            "/importar <ID> (scraping en 2do plano)\n"
            "/eliminar (borrar ticket de la semana)\n"
            "/reporte (generar Excel semanal)"
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
        except ValueError as e: await update.message.reply_text(f"⚠️ {e}")
        except Exception: await update.message.reply_text("❌ Ocurrió un error inesperado.")

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
            procesar_ticket_task.delay(ticket_id, user_id, chat_id)
            await update.message.reply_text(f"✅ Solicitud para importar el ticket #{ticket_id} recibida. Se procesará en segundo plano y se te notificará.")
        except Exception as e:
            print(f"Error al encolar tarea de importación: {e}")
            await update.message.reply_text("❌ Ocurrió un error al enviar tu solicitud.")

    async def eliminar_ticket_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        try:
            tickets_semanales = self.obtener_tickets_semanales_use_case.ejecutar(user_id)
            if not tickets_semanales:
                await update.message.reply_text("No tienes tickets registrados esta semana para eliminar.")
                return
            keyboard = [[InlineKeyboardButton(f"#{t.numero_ticket} - {t.servicio[:25]}", callback_data=f"delete_{t.id}")] for t in tickets_semanales]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Selecciona el ticket que deseas eliminar:", reply_markup=reply_markup)
        except ValueError as e: await update.message.reply_text(f"⚠️ {e}")
        except Exception as e:
            print(f"Error en eliminar_ticket_start: {e}")
            await update.message.reply_text("❌ Ocurrió un error al buscar tus tickets.")

    async def eliminar_ticket_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        try:
            action, ticket_id_str = query.data.split('_', 1)
            if action == 'delete':
                ticket_id = UUID(ticket_id_str)
                success = self.eliminar_ticket_use_case.ejecutar(ticket_id)
                if success:
                    await query.edit_message_text(text=f"✅ Ticket eliminado correctamente.")
                else:
                    await query.edit_message_text(text="⚠️ No se pudo encontrar el ticket.")
        except Exception as e:
            print(f"Error en eliminar_ticket_callback: {e}")
            await query.edit_message_text(text="❌ Ocurrió un error al procesar tu solicitud.")

    async def nuevo_ticket_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        usuario = self.obtener_usuario_use_case.ejecutar(update.message.from_user.id)
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
            id=None, user_id=update.message.from_user.id, chat_id=update.message.chat_id, fecha=datetime.now(),
            numero_ticket=context.user_data["numero_ticket"], servicio=context.user_data["servicio"],
            usuario_reporta=context.user_data["usuario_reporta"], correo_usuario=context.user_data["correo_usuario"],
            empresa=context.user_data["empresa"], atendido_por=""
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

    async def generar_reporte(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        usuario = self.obtener_usuario_use_case.ejecutar(user_id)
        if not usuario:
            await update.message.reply_text("⚠️ No estás registrado. Usa /registrar primero.")
            return
        await update.message.reply_text(f"⚙️ Generando tu reporte semanal, {usuario.nombre_completo}...")
        try:
            nombre_archivo, file_bytes = self.generar_reporte_use_case.ejecutar(user_id, "Reporte de tickets atendidos.")
            await context.bot.send_document(
                chat_id=update.message.chat_id, document=file_bytes, filename=nombre_archivo)
        except ValueError as e: await update.message.reply_text(f"⚠️ {e}")
        except Exception as e:
            print(f"Error inesperado al generar reporte: {e}")
            await update.message.reply_text("❌ Ocurrió un error al generar el reporte.")

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