import os
import requests
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
LARAVEL_API_URL = os.getenv("LARAVEL_API_URL")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola, soy el bot de pedidos.\n\n"
        "Comandos disponibles:\n"
        "/create_order Nombre|email|monto\n"
        "/orders\n"
        "/order ID\n\n"
        "Ejemplo:\n"
        "/create_order Ricardo Saucedo|ricardo@test.com|1500.50"
    )


async def create_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.replace("/create_order", "").strip()

        if not text:
            await update.message.reply_text(
                "Formato correcto:\n"
                "/create_order Nombre|email|monto"
            )
            return

        parts = text.split("|")

        if len(parts) != 3:
            await update.message.reply_text(
                "Formato inválido.\n"
                "Usa:\n"
                "/create_order Nombre|email|monto"
            )
            return

        customer_name = parts[0].strip()
        customer_email = parts[1].strip()
        total_amount = float(parts[2].strip())

        payload = {
            "customer_name": customer_name,
            "customer_email": customer_email,
            "total_amount": total_amount,
        }

        response = requests.post(
            f"{LARAVEL_API_URL}/orders",
            json=payload,
            headers={"Accept": "application/json"},
            timeout=10,
        )

        if response.status_code not in [200, 201]:
            error_text = response.text[:500]

            await update.message.reply_text(
                f"No se pudo crear la orden.\n"
                f"Status: {response.status_code}\n"
                f"Response: {error_text}"
            )
            return

        data = response.json().get("data", {})

        await update.message.reply_text(
            "Orden creada correctamente.\n\n"
            f"ID: {data.get('id')}\n"
            f"Cliente: {data.get('customer_name')}\n"
            f"Email: {data.get('customer_email')}\n"
            f"Monto: {data.get('total_amount')}\n"
            f"Estado: {data.get('status')}\n\n"
            "El procesamiento se ejecutará en segundo plano."
        )

    except ValueError:
        await update.message.reply_text("El monto debe ser numérico.")
    except Exception as e:
        error_message = str(e)[:500]
        await update.message.reply_text(f"Error: {error_message}")


async def list_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(
            f"{LARAVEL_API_URL}/orders",
            headers={"Accept": "application/json"},
            timeout=10,
        )

        if response.status_code != 200:
            await update.message.reply_text(
                f"No se pudieron obtener las órdenes.\n"
                f"Status: {response.status_code}"
            )
            return

        json_response = response.json()
        orders = json_response.get("data", json_response)

        if not orders:
            await update.message.reply_text("No hay órdenes registradas.")
            return

        message = "Órdenes registradas:\n\n"

        for order in orders[:10]:
            message += (
                f"ID: {order.get('id')}\n"
                f"Cliente: {order.get('customer_name')}\n"
                f"Monto: {order.get('total_amount')}\n"
                f"Estado: {order.get('status')}\n"
                f"External Data: {order.get('external_data')}\n"
                "----------------------\n"
            )

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


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
            await update.message.reply_text("Orden no encontrada.")
            return

        if response.status_code != 200:
            await update.message.reply_text(
                f"No se pudo consultar la orden.\n"
                f"Status: {response.status_code}"
            )
            return

        order = response.json().get("data", {})

        await update.message.reply_text(
            "Detalle de orden:\n\n"
            f"ID: {order.get('id')}\n"
            f"Cliente: {order.get('customer_name')}\n"
            f"Email: {order.get('customer_email')}\n"
            f"Monto: {order.get('total_amount')}\n"
            f"Estado: {order.get('status')}\n"
            f"External Data: {order.get('external_data')}\n"
            f"Error: {order.get('error_message')}"
        )

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create_order", create_order))
    app.add_handler(CommandHandler("orders", list_orders))
    app.add_handler(CommandHandler("order", get_order))

    app.run_polling()


if __name__ == "__main__":
    main()
