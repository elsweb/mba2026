class RouteMemory:
    """
    Memória de rota.
    No ESP32 isso será substituído por EEPROM/NVS.
    """

    def __init__(self):

        self.route = []


    def save_point(self, obstacle_x, offset):

        # evita duplicar o mesmo obstáculo
        for item in self.route:

            if abs(item["x"] - obstacle_x) < 30:
                return


        self.route.append({
            "x": obstacle_x,
            "offset": offset
        })


    def find_route(self, obstacle_x):

        for item in self.route:

            if abs(item["x"] - obstacle_x) < 30:
                return item


        return None