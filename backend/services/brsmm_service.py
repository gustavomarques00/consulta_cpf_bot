import requests
from core.config import Config

class BrsmmService:
    def __init__(self):
        self.api_url = Config.BRSMM_API_URL
        self.api_key = Config.BRSMM_API_KEY

    def _post(self, payload):
        payload["key"] = self.api_key
        try:
            response = requests.post(self.api_url, data=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def get_services(self):
        return self._post({"action": "services"})

    def add_order(self, link: str, service_id: int, quantity: int):
        payload = {
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity
        }
        return self._post(payload)

    def get_order_status(self, order_id: int):
        return self._post({
            "action": "status",
            "order": order_id
        })

    def get_balance(self):
        return self._post({"action": "balance"})

# Exemplo de uso isolado
if __name__ == "__main__":
    api = BrsmmService()

    print("💰 Consultando saldo...")
    print(api.get_balance())

    print("\n📦 Serviços disponíveis:")
    services = api.get_services()
    for s in services[:3]:  # Limita a 3 para exemplo
        print(f"ID: {s['service']} | Nome: {s['name']} | Preço: ${s['rate']}")

    print("\n🚀 Criando pedido de tráfego...")
    service_id = services[0]["service"]
    response = api.add_order(
        link="https://example.com",
        service_id=service_id,
        quantity=100
    )

    if "order" in response:
        print(f"✅ Pedido criado: {response['order']}")
        status = api.get_order_status(response["order"])
        print("📊 Status do pedido:", status)
    else:
        print("❌ Falha ao criar pedido:", response)
