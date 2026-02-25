#!/usr/bin/env python
"""Verifica el modelo de OpenRouter configurado y prueba conectividad"""
import os
import asyncio
from openrouter import OpenRouter
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct")

if not API_KEY:
    print("❌ OPENROUTER_API_KEY no configurada en .env")
    exit(1)

print(f"🔍 Verificando OpenRouter con modelo: {MODEL}")
print("=" * 60)

async def probar_conexion():
    client = OpenRouter(api_key=API_KEY)
    try:
        # Prueba simple con prompt mínimo
        resp = await asyncio.to_thread(
            client.chat.send,
            messages=[{"role": "user", "content": "Hola, responde 'OK'"}],
            model=MODEL,
            max_tokens=10,
            temperature=0.1
        )
        
        respuesta = resp.choices[0].message.content.strip()
        print(f"✅ Conexión exitosa")
        print(f"📝 Respuesta: {respuesta[:100]}")
        print(f"📊 Tokens usados: {resp.usage.total_tokens if resp.usage else 'N/A'}")
        print("\n🎉 El modelo está funcionando correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        print("\n💡 Posibles causas:")
        print("   - API key inválida o sin saldo")
        print("   - Modelo no disponible en tu región")
        print("   - Cuota agotada")
        return False

if __name__ == "__main__":
    success = asyncio.run(probar_conexion())
    exit(0 if success else 1)
