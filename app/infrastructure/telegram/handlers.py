import os
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from app.domain.entities.entities import Ticket
from app.domain.use_cases.registrar_ticket import RegistrarTicketUseCase
from app.domain.use_cases.generar_reporte_tickets import GenerarReporteTicketsUseCase
from app.domain.use_cases.registrar_usuario import RegistrarUsuarioUseCase
from app.domain.use_cases.obtener_usuario import ObtenerUsuarioUseCase

# Estados de la conversación para registrar un ticket
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
        generar_reporte_use_case: GenerarReporteTicketsUseCase,
        registrar_usuario_use_case: RegistrarUsuarioUseCase,
        obtener_usuario_use_case: ObtenerUsuarioUseCase
    ):
        self.registrar_ticket_use_case = registrar_ticket_use_case
        self.generar_reporte_use_case = generar_reporte_use_case
        self.registrar_usuario_use_case = registrar_usuario_use_case
        self.obtener_usuario_use_case = obtener_usuario_use_case

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "¡Hola! Soy tu bot de gestión de tickets.\n\n"
            "Si es tu primera vez, regístrate con /registrar <Tu Nombre Completo>.\n"
            "Usa /nuevoticket para registrar un ticket.\n"
            "Usa /reporte para generar tu reporte semanal."
        )

    # --- NUEVO COMANDO DE REGISTRO ---
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

    # --- CONVERSACIÓN MODIFICADA CON VERIFICACIÓN ---
    async def nuevo_ticket_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.message.from_user.id
        usuario = self.obtener_usuario_use_case.ejecutar(user_id)
        
        if not usuario:
            await update.message.reply_text("⚠️ No estás registrado. Por favor, regístrate primero con:\n/registrar <Tu Nombre Completo>")
            return ConversationHandler.END
            
        await update.message.reply_text("Iniciando registro de ticket. Por favor, dime el número de ticket.")
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
            atendido_por="" # El caso de uso lo rellenará automáticamente
        )
        
        try:
            self.registrar_ticket_use_case.ejecutar(ticket)
            await update.message.reply_text(f"✅ Ticket {ticket.numero_ticket} registrado exitosamente.")
        except ValueError as e:
            await update.message.reply_text(f"⚠️ {e}")

        context.user_data.clear()
        return ConversationHandler.END

    async def cancelar(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Acción cancelada.")
        context.user_data.clear()
        return ConversationHandler.END

    # --- REPORTE MODIFICADO CON VERIFICACIÓN Y FILTRADO ---
    async def generar_reporte(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        usuario = self.obtener_usuario_use_case.ejecutar(user_id)
        
        if not usuario:
            await update.message.reply_text("⚠️ No estás registrado. Por favor, regístrate primero con /registrar <Tu Nombre Completo>.")
            return

        await update.message.reply_text(f"⚙️ Generando tu reporte semanal, {usuario.nombre_completo}...")
        
        try:
            ruta_archivo = self.generar_reporte_use_case.ejecutar(
                user_id=user_id,
                generado_por=usuario.nombre_completo,
                comentarios="Reporte de tickets atendidos."
            )
            
            with open(ruta_archivo, "rb") as file:
                await context.bot.send_document(
                    chat_id=update.message.chat_id,
                    document=file,
                    filename=os.path.basename(ruta_archivo),
                )
            os.remove(ruta_archivo)
        
        except ValueError as e:
            await update.message.reply_text(f"⚠️ {e}")
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