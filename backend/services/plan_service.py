import json
from core.db import get_db_connection
from utils.parse_date import parse_date


class PlanService:
    def get_all_plans(self):
        """
        Retorna a lista de todos os planos disponíveis.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT id, planos, preco, features FROM planos")
            plans = cursor.fetchall()

            for plan in plans:
                if isinstance(plan["features"], str):
                    plan["features"] = json.loads(plan["features"])
                elif not isinstance(plan["features"], list):
                    plan["features"] = []

            return plans
        except Exception as err:
            raise Exception(f"Erro ao consultar planos: {str(err)}")
        finally:
            cursor.close()
            conn.close()

    def get_user_plan(self, user_id):
        """
        Retorna o plano associado ao usuário autenticado.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT p.id, p.planos AS nome, p.preco, p.features, up.data_inicio, up.data_fim
                FROM usuarios_planos up 
                JOIN planos p ON up.plano_id = p.id 
                WHERE up.usuario_id = %s
                """,
                (user_id,),
            )
            user_plan = cursor.fetchone()

            if not user_plan:
                return None

            # Formatar as datas no padrão brasileiro usando parse_date
            if user_plan["data_inicio"]:
                user_plan["data_inicio"] = parse_date(str(user_plan["data_inicio"]))
            if user_plan["data_fim"]:
                user_plan["data_fim"] = parse_date(str(user_plan["data_fim"]))

            return user_plan
        except Exception as err:
            raise Exception(f"Erro ao consultar plano do usuário: {str(err)}")
        finally:
            cursor.close()
            conn.close()
