import random
from locust import FastHttpUser, task, between


class QuickStartUser(FastHttpUser):
    # Время ожидания между задачами (эмуляция реального человека)
    # Если хочешь максимальную нагрузку (DDoS) — убери эту строку или поставь 0.1
    wait_time = between(0.5, 2)

    @task
    def get_user_by_id(self):
        # Генерируем случайный ID.
        # ВАЖНО:
        # Если диапазон маленький (1-50), почти все запросы попадут в Redis (Cache Hit).
        # Если диапазон огромный (1-100000), почти все запросы пойдут в БД (Cache Miss).
        # Настрой под то количество юзеров, которое ты создал в БД.
        user_id = random.randint(1, 1000)

        # Делаем запрос
        # name="/users/[id]" нужен, чтобы в статистике все запросы
        # не слиплись в одну кучу или наоборот не разбились на тысячи строк
        self.client.get(f"/users/{user_id}", name="/users/[id]")
