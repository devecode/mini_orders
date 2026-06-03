import os
import requests
from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
LARAVEL_API_URL = os.getenv("LARAVEL_API_URL")

ASK_NAME, ASK_EMAIL, ASK_AMOUNT, ASK_DESCRIPTION = range(4)


def main_menu():
    keyboard = [
        [InlineKeyboardButton("📝 Crear orden", callback_data="create_order")],
        [InlineKeyboardButton("📦 Ver órdenes", callback_data="list_orders")],
        [InlineKeyboardButton("📊 Estadísticas", callback_data="stats")],
    ]

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hola, soy el bot de pedidos.\n\n"
        "¿Qué deseas hacer?",
        reply_markup=main_menu(),
    )


async def create_order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"] = {}

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.message.reply_text("📝 Ingresa el nombre del cliente:")
    else:
        await update.message.reply_text("📝 Ingresa el nombre del cliente:")

    return ASK_NAME


async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"]["customer_name"] = update.message.text.strip()

    await update.message.reply_text("📧 Ingresa el email del cliente:")
    return ASK_EMAIL


async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"]["customer_email"] = update.message.text.strip()

    await update.message.reply_text("💰 Ingresa el monto de la orden:")
    return ASK_AMOUNT


async def ask_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        total_amount = float(update.message.text.strip())
    except ValueError:
        await update.message.reply_text(
            "⚠️ El monto debe ser numérico. Inténtalo de nuevo:"
        )
        return ASK_AMOUNT

    context.user_data["order"]["total_amount"] = total_amount

    await update.message.reply_text("🧾 Ingresa la descripción de la orden:")
    return ASK_DESCRIPTION


async def ask_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"]["description"] = update.message.text.strip()

    payload = context.user_data["order"]

    try:
        response = requests.post(
            f"{LARAVEL_API_URL}/orders",
            json=payload,
            headers={"Accept": "application/json"},
            timeout=10,
        )

        if response.status_code not in [200, 201]:
            await update.message.reply_text(
                "❌ No se pudo crear la orden.\n\n"
                f"Status: {response.status_code}\n"
                f"Response: {response.text[:500]}",
                reply_markup=main_menu(),
            )
            return ConversationHandler.END

        data = response.json().get("data", {})

        await update.message.reply_text(
            "✅ Orden creada correctamente\n\n"
            f"🆔 ID: {data.get('id')}\n"
            f"👤 Cliente: {data.get('customer_name')}\n"
            f"📧 Email: {data.get('customer_email')}\n"
            f"💰 Monto: ${data.get('total_amount')}\n"
            f"🧾 Descripción: {data.get('description')}\n"
            f"📌 Estado: {data.get('status')}\n\n"
            "¿Qué deseas hacer ahora?",
            reply_markup=main_menu(),
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error: {str(e)[:500]}",
            reply_markup=main_menu(),
        )

    context.user_data.pop("order", None)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("order", None)

    await update.message.reply_text(
        "❌ Creación de orden cancelada.\n\n"
        "¿Qué deseas hacer?",
        reply_markup=main_menu(),
    )

    return ConversationHandler.END


async def list_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await list_orders_from_message(update.message)


async def list_orders_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await list_orders_from_message(query.message)


async def list_orders_from_message(message):
    try:
        response = requests.get(
            f"{LARAVEL_API_URL}/orders",
            headers={"Accept": "application/json"},
            timeout=10,
        )

        if response.status_code != 200:
            await message.reply_text(
                f"❌ No se pudieron obtener las órdenes.\n"
                f"Status: {response.status_code}",
                reply_markup=main_menu(),
            )
            return

        json_response = response.json()
        orders = json_response.get("data", json_response)

        if not orders:
            await message.reply_text(
                "📭 No hay órdenes registradas.",
                reply_markup=main_menu(),
            )
            return

        text = "📦 Últimas órdenes registradas\n\n"

        for order in orders[:10]:
            text += (
                f"🆔 Orden #{order.get('id')}\n"
                f"👤 Cliente: {order.get('customer_name')}\n"
                f"💰 Monto: ${order.get('total_amount')}\n"
                f"📌 Estado: {order.get('status')}\n"
                f"🧾 Descripción: {order.get('description') or 'Sin descripción'}\n"
                f"🔎 Ver detalle: /order {order.get('id')}\n"
                "━━━━━━━━━━━━━━\n"
            )

        await message.reply_text(
            text,
            reply_markup=main_menu(),
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Error: {str(e)[:500]}",
            reply_markup=main_menu(),
        )


async def get_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("Usa: /order ID")
            return

        order_id = context.args[0]

        response = requests.get(
            f"{LARAVEL_API_URL}/orders/{order_id}",
            headers={"Accept": "application/json"},
            timeout=10,
        )

        if response.status_code == 404:
            await update.message.reply_text(
                "⚠️ Orden no encontrada.",
                reply_markup=main_menu(),
            )
            return

        if response.status_code != 200:
            await update.message.reply_text(
                f"❌ No se pudo consultar la orden.\n"
                f"Status: {response.status_code}",
                reply_markup=main_menu(),
            )
            return

        order = response.json().get("data", {})

        await update.message.reply_text(
            "🔎 Detalle de orden\n\n"
            f"🆔 ID: {order.get('id')}\n"
            f"👤 Cliente: {order.get('customer_name')}\n"
            f"📧 Email: {order.get('customer_email')}\n"
            f"💰 Monto: ${order.get('total_amount')}\n"
            f"🧾 Descripción: {order.get('description')}\n"
            f"📌 Estado: {order.get('status')}\n"
            f"🌐 External Data: {order.get('external_data') or 'Sin datos'}\n"
            f"⚠️ Error: {order.get('error_message') or 'Sin error'}",
            reply_markup=main_menu(),
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error: {str(e)[:500]}",
            reply_markup=main_menu(),
        )


async def show_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_stats_from_message(update.message)


async def show_stats_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await show_stats_from_message(query.message)


async def show_stats_from_message(message):
    try:
        response = requests.get(
            f"{LARAVEL_API_URL}/orders",
            headers={"Accept": "application/json"},
            timeout=10,
        )

        if response.status_code != 200:
            await message.reply_text(
                f"❌ No se pudieron obtener las estadísticas.\n"
                f"Status: {response.status_code}",
                reply_markup=main_menu(),
            )
            return

        json_response = response.json()
        orders = json_response.get("data", json_response)

        total_orders = len(orders)
        total_amount = 0

        status_count = {}

        for order in orders:
            try:
                total_amount += float(order.get("total_amount") or 0)
            except ValueError:
                pass

            status = order.get("status") or "Sin estado"
            status_count[status] = status_count.get(status, 0) + 1

        status_text = ""

        for status, count in status_count.items():
            status_text += f"• {status}: {count}\n"

        await message.reply_text(
            "📊 Estadísticas de órdenes\n\n"
            f"📦 Total de órdenes: {total_orders}\n"
            f"💰 Monto total: ${total_amount:,.2f}\n\n"
            "📌 Órdenes por estado:\n"
            f"{status_text or 'Sin estados registrados'}",
            reply_markup=main_menu(),
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Error: {str(e)[:500]}",
            reply_markup=main_menu(),
        )


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    create_order_conversation = ConversationHandler(
        entry_points=[
            CommandHandler("create_order", create_order_start),
            CallbackQueryHandler(create_order_start, pattern="^create_order$"),
        ],
        states={
            ASK_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)
            ],
            ASK_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_email)
            ],
            ASK_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_amount)
            ],
            ASK_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_description)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(create_order_conversation)

    app.add_handler(CommandHandler("orders", list_orders))
    app.add_handler(CommandHandler("order", get_order))
    app.add_handler(CommandHandler("stats", show_stats_command))
    app.add_handler(CommandHandler("cancel", cancel))

    app.add_handler(CallbackQueryHandler(list_orders_button, pattern="^list_orders$"))
    app.add_handler(CallbackQueryHandler(show_stats_button, pattern="^stats$"))

    app.run_polling()


if __name__ == "__main__":
    main()
