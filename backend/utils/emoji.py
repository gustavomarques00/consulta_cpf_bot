import sys


def supports_unicode():
    try:
        return sys.stdout.encoding and sys.stdout.encoding.lower() == "utf-8"
    except:
        return False


EMOJI = {
    "info": "📡" if supports_unicode() else "[INFO]",
    "warn": "⚠️" if supports_unicode() else "[AVISO]",
    "error": "❌" if supports_unicode() else "[ERRO]",
    "ok": "✅" if supports_unicode() else "[OK]",
    "step": "🔍" if supports_unicode() else "[ETAPA]",
    "batch": "🚀" if supports_unicode() else "[LOTE]",
    "clock": "🕒" if supports_unicode() else "[AGUARDANDO]",
    "loop": "🔄" if supports_unicode() else "[RETRY]",
    "remove": "✅" if supports_unicode() else "[REMOVIDO]",
    "retry": "⚠️" if supports_unicode() else "[RETRY]",
}
