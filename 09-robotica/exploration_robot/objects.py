import pygame
from config import *

class Car:
    """Classe que representa o carro controlado por IA."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 90, 50)
        self.speed = 4
        self.vertical_speed = 3
        self.color = BLUE
        self.state = "DRIVING"
        self.hit_timer = 0
        self.reverse_distance = 0
        self.track_top = TRACK_TOP
        self.track_bottom = TRACK_BOTTOM
        self.rect.y = max(self.track_top, min(y, self.track_bottom - self.rect.height))
        self.lane_y = self.rect.y
        self.target_y = self.rect.y
        self.original_y = self.rect.y
        self.current_obstacle = None
        self.tried_directions = set()
        self.total_reverse = 0
        self.max_reverse_distance = 200
        self.avoid_multiplier = 1
        self.max_avoid_multiplier = 10

    # ======================================================================
    # Métodos auxiliares (inalterados)
    # ======================================================================
    def _set_y(self, y):
        self.rect.y = max(self.track_top, min(y, self.track_bottom - self.rect.height))

    def _clamp_y(self):
        self._set_y(self.rect.y)

    def _is_valid_position(self, rect, obstacles, ignore_obstacle=None):
        if rect.top < self.track_top or rect.bottom > self.track_bottom:
            return False
        for obstacle in obstacles:
            if obstacle is ignore_obstacle:
                continue
            if rect.colliderect(obstacle.rect):
                return False
        return True

    def _try_move(self, dx, dy, obstacles, ignore_obstacle=None):
        new_rect = self.rect.move(dx, dy)
        if self._is_valid_position(new_rect, obstacles, ignore_obstacle):
            self.rect = new_rect
            return True
        return False

    # ======================================================================
    # Atualização principal (inalterada)
    # ======================================================================
    def update(self, obstacles, end_x):
        if self.rect.x >= end_x:
            return
        if self.current_obstacle:
            if self.rect.left > self.current_obstacle.rect.right:
                self.current_obstacle = None
                self.tried_directions.clear()
                self.total_reverse = 0
        if self.state == "HIT":
            self._handle_hit()
        elif self.state == "REVERSE":
            self._handle_reverse(obstacles)
        elif self.state == "AVOID":
            self._handle_avoid(obstacles)
        elif self.state == "RETURN":
            self._handle_return()
        else:
            self._handle_driving(obstacles)

    # ======================================================================
    # Estados
    # ======================================================================

    def _handle_hit(self):
        """Após colisão, aguarda e depois inicia a ré com distância proporcional ao multiplicador."""
        self.hit_timer -= 1
        if self.hit_timer <= 0:
            self.state = "REVERSE"
            # A distância de ré agora é multiplicada pelo avoid_multiplier (eixo X)
            self.reverse_distance = 30

    def _handle_reverse(self, obstacles):
        """
        Recua uma distância fixa e aumenta o deslocamento vertical
        conforme o avoid_multiplier.
        """

        # Limite de recuo total
        if self.total_reverse >= self.max_reverse_distance:
            self.state = "DRIVING"
            self.current_obstacle = None
            self.tried_directions.clear()
            self.total_reverse = 0
            self.reverse_distance = 0
            self.avoid_multiplier = 1
            return

        # Ré fixa (não depende do multiplicador)
        if self.reverse_distance > 0:
            if self._try_move(-2, 0, obstacles, ignore_obstacle=self.current_obstacle):
                self.reverse_distance -= 2
                self.total_reverse += 2
            return

        # Terminou a ré, tenta desviar
        self.reverse_distance = 0

        # Agora o multiplicador controla o tamanho do desvio
        DESVIO = self.rect.height * self.avoid_multiplier
        
        print(DESVIO)

        tentativas = []

        # Tentativa para cima
        novo_y = self.rect.y - DESVIO
        if novo_y >= self.track_top:
            tentativas.append(("UP", novo_y))

        # Tentativa para baixo
        novo_y = self.rect.y + DESVIO
        if novo_y + self.rect.height <= self.track_bottom:
            tentativas.append(("DOWN", novo_y))


        escolhido = None

        for direcao, novo_y in tentativas:
            if direcao in self.tried_directions:
                continue

            teste = self.rect.copy()
            teste.y = novo_y

            if self._is_valid_position(
                teste,
                obstacles,
                ignore_obstacle=self.current_obstacle
            ):
                escolhido = (direcao, novo_y)
                break


        if escolhido:
            direcao, novo_y = escolhido

            self.target_y = novo_y
            self.tried_directions.add(direcao)
            self.state = "AVOID"

            # mantém o multiplicador para próximos desvios
            self.total_reverse = 0

        else:
            # Não conseguiu desviar:
            # aumenta o multiplicador do DESVIO
            if self.avoid_multiplier < self.max_avoid_multiplier:
                self.avoid_multiplier += 1

            # nova tentativa de ré fixa
            self.reverse_distance = 30
            self.tried_directions.clear()
    
    def _handle_avoid(self, obstacles):
        """Desvia verticalmente e avança horizontalmente (sem usar multiplicador)."""
        if abs(self.rect.y - self.target_y) > self.vertical_speed:
            if self.rect.y < self.target_y:
                self._set_y(self.rect.y + self.vertical_speed)
            else:
                self._set_y(self.rect.y - self.vertical_speed)
            self._clamp_y()
            return

        self._set_y(self.target_y)
        self._clamp_y()

        if self._try_move(self.speed, 0, obstacles):
            if self.current_obstacle:
                if self.rect.left > self.current_obstacle.rect.right:
                    self.current_obstacle = None
                    self.tried_directions.clear()
                    self.lane_y = self.target_y
                    self.state = "DRIVING"
            else:
                self.state = "DRIVING"
        else:
            self.color = RED
            self.state = "HIT"
            self.hit_timer = 20
            for obs in obstacles:
                if self.rect.move(self.speed, 0).colliderect(obs.rect):
                    self.current_obstacle = obs
                    break

    def _handle_return(self):
        """Estado de retorno (não usado ativamente)."""
        self.rect.x += self.speed
        if self.rect.y < self.original_y:
            self._set_y(self.rect.y + self.vertical_speed)
        elif self.rect.y > self.original_y:
            self._set_y(self.rect.y - self.vertical_speed)
        self._clamp_y()
        if abs(self.rect.y - self.original_y) <= self.vertical_speed:
            self.rect.y = self.original_y
            self._clamp_y()
            self.state = "DRIVING"

    def _handle_driving(self, obstacles):
        """Estado normal: avança horizontalmente."""
        self._clamp_y()
        next_rect = self.rect.move(self.speed, 0)
        for obstacle in obstacles:
            if next_rect.colliderect(obstacle.rect):
                self.color = RED
                if self.current_obstacle != obstacle:
                    self.current_obstacle = obstacle
                    self.tried_directions.clear()
                self.state = "HIT"
                self.hit_timer = 20
                return
        self.rect = next_rect
        self.color = BLUE

    # ======================================================================
    # Desenho (inalterado)
    # ======================================================================
    def draw(self, screen):
        x = self.rect.x
        y = self.rect.y
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (180, 220, 255), (x + 20, y + 8, 50, 18), border_radius=4)
        pygame.draw.circle(screen, BLACK, (x + 18, y + 5), 8)
        pygame.draw.circle(screen, BLACK, (x + 72, y + 5), 8)
        pygame.draw.circle(screen, BLACK, (x + 18, y + 45), 8)
        pygame.draw.circle(screen, BLACK, (x + 72, y + 45), 8)
        
class Obstacle:
    """Classe para obstáculos estáticos na pista."""

    def __init__(self, x, y, w=40, h=40, color=(255, 100, 0)):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def draw(self, screen):
        """Desenha o obstáculo como um retângulo arredondado."""
        pygame.draw.rect(
            screen,
            self.color,
            self.rect,
            border_radius=5
        )